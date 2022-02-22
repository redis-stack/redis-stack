import os
import subprocess
from conftest import get_localhost_equiv, _in_docker
from urllib.request import urlopen


BASEPATH = "/opt/redis-stack"
BINDIR = os.path.join(BASEPATH, "bin")
LIBDIR = os.path.join(BASEPATH, "lib")
ETCDIR = os.path.join(BASEPATH, "etc")
SHAREDIR = os.path.join(BASEPATH, "share")
REDIS_UID = 65534
REDIS_GID = 65534

BINARIES = [
    "redis-server",
    "redis-benchmark",
    "redis-check-aof",
    "redis-check-rdb",
    "redis-cli",
    "redis-sentinel",
]


def start_procs():
    if _in_docker() is False:
        subprocess.run(['systemctl', 'stop', 'redis-stack'], capture_output=False)  # in case started, and ignore the return code
        cmd = ['systemctl', 'start', 'redis-stack']
        proc = subprocess.run(cmd, capture_output=False)
        assert proc.returncode == 0

    else:
        cmd = ["/bin/bash", "/build/etc/entrypoint.sh"]
        proc = subprocess.Popen(cmd)
        # proc = subprocess.run(cmd, capture_output=False)
        # assert proc.returncode == 0

class PackageTestMixin:

    def test_paths_exist(self):
        for i in [BINDIR, LIBDIR, ETCDIR, SHAREDIR]:
            assert os.path.isdir(i)

    def test_files_exist(self):
        assert os.path.isfile(os.path.join(ETCDIR, "redis-stack.conf"))
        for binary in BINARIES:

            fpath = os.path.join(BINDIR, binary)
            assert os.path.isfile(fpath)
            assert os.path.getsize(fpath) > 0

            stats = os.stat(fpath)
            assert stats.st_uid == REDIS_UID
            assert stats.st_gid == REDIS_GID

        # otherwise we can't load the modules
        for mod in [
            "rejson.so",
            "redistimeseries.so",
            "redisearch.so",
            "redisgraph.so",
            "redisbloom.so",
        ]:

            fpath = os.path.join(LIBDIR, mod)
            assert os.path.isfile(fpath)

            stats = os.stat(fpath)
            assert stats.st_uid == REDIS_UID
            assert stats.st_gid == REDIS_GID

    def test_binaries_execute(self):
        for binary in BINARIES:
            proc = subprocess.run(
                [os.path.join(BINDIR, binary), "-h"], capture_output=False
            )
            assert proc.returncode == 1


class ServiceTestMixin:
    def test_basic_redis(self, r):
        assert r.ping()

        r.set("some", "value")
        assert r.get("some") == "value"

    def test_redis_modules_loaded(self, r):
        expected = ["rejson", "timeseries", "search", "graph", "bf"]
        modules = [m.get("name").lower() for m in r.module_list()]

        modules.sort()
        expected.sort()
        assert modules == expected

    def test_basic_redisinsight(self):
        c = urlopen(f"http://{get_localhost_equiv()}:8001")
        content = c.read().decode()
        assert content.lower().find('redisinsight') != -1