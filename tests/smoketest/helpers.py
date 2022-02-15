import os
import subprocess
import requests


BASEPATH = "/opt/redis-stack"
BINDIR = os.path.join(BASEPATH, "bin")
LIBDIR = os.path.join(BASEPATH, "lib")
ETCDIR = os.path.join(BASEPATH, "etc")
SHAREDIR = os.path.join(BASEPATH, "share")
REDIS_UID = 999
REDIS_GID = 999

BINARIES = [
    "redis-server",
    "redis-benchmark",
    "redis-check-aof",
    "redis-check-rdb",
    "redis-cli",
    "redis-sentinel",
]


class PackageTestMixin:

    # @classmethod
    # def setup_class(cls):
    #     cmd = ['dpkg', '-i', cls.PACKAGE_NAME]
    #     r = subprocess.run(cmd)
    #     assert r.returncode == 0

    def test_paths_exist(self):
        for i in [BINDIR, LIBDIR, ETCDIR, SHAREDIR]:
            assert os.path.isdir(i)

    def test_files_exist(self):
        assert os.path.isfile(os.path.join(ETCDIR, "redis-stack.conf"))
        for binary in BINARIES:

            fpath = os.path.join(BINDIR, binary)
            assert os.path.isfile(fpath)
            assert os.path.getsize(fpath) > 0

            # TODO once uid/gid is figured out re-enable
            # stats = os.stat(fpath)
            # assert stats.st_uid == REDIS_UID
            # assert stats.st_gid == REDIS_GID
            # assert os.access(binary, os.X_OK)

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

            # TODO once uid/gid is figured out re-enable
            # stats = os.stat(fpath)
            # assert stats.st_uid == REDIS_UID
            # assert stats.st_gid == REDIS_GID
            # assert os.access(mod, os.X_OK)

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
        expected = ["rejson", "timeseries", "search", "graph", "bloom"]
        modules = [m.get("name").lower() for m in r.module_list()]

        modules.sort()
        expected.sort()
        assert modules == expected

    def test_basic_redisinsight(self):
        r = requests.get("http://localhost:8081")
        assert r.status_code == 200
        assert r.content.decode().find("RedisInsight") != -1
