import os
import time
import subprocess
from redis.commands.search.query import Query
from redis.commands.search.field import TextField
import docker
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

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


# def start_procs():
#     if _in_docker() is False:
#         subprocess.run(['systemctl', 'stop', 'redis-stack'], capture_output=False)  # in case started, and ignore the return code
#         cmd = ['systemctl', 'start', 'redis-stack']
#         proc = subprocess.run(cmd, capture_output=False)
#         assert proc.returncode == 0

#     else:
#         cmd = ["/bin/bash", "/build/etc/scripts/entrypoint.sh"]
#         proc = subprocess.Popen(cmd)
#         # proc = subprocess.run(cmd, capture_output=False)
#         # assert proc.returncode == 0


def stack_dockloader(cls):
    if getattr(cls, "IN_DOCKER", None) is not None:
        cls.container.reload()
        res, out = cls.container.exec_run(
            "/opt/redis-stack/bin/redis-stack-server", detach=True
        )
        time.sleep(2)


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


class RedisInsightTestMixin:
    def test_basic_redisinsight(self):
        stack_dockloader(self)
        c = urlopen("http://localhost:8001")
        content = c.read().decode()
        assert content.lower().find("redisinsight") != -1


class RedisTestMixin:
    def test_basic_redis(self, r):
        stack_dockloader(self)
        assert r.ping()

        r.set("some", "value")
        assert r.get("some") == "value"

    def test_redis_modules_loaded(self, r):
        expected = ["rejson", "timeseries", "search", "graph", "bf"]
        modules = [m.get("name").lower() for m in r.module_list()]

        modules.sort()
        expected.sort()
        assert modules == expected

    def test_json(self, r):
        stack_dockloader(self)
        r.json().set("foo", ".", "bar")
        assert r.json().get("foo") == "bar"

    def test_bloom(self, r):
        stack_dockloader(self)
        assert r.bf().create("bloom", 0.01, 1000)
        assert 1 == r.bf().add("bloom", "foo")
        assert 0 == r.bf().add("bloom", "foo")

    def test_graph(self, r):
        stack_dockloader(self)
        params = [1, 2.3, "str", True, False, None, [0, 1, 2]]
        query = "RETURN $param"
        for param in params:
            result = r.graph().query(query, {"param": param})
            expected_results = [[param]]
            assert expected_results == result.result_set

    def test_timeseries(self, r):
        stack_dockloader(self)
        name = "test"
        r.ts().create(name)
        assert r.ts().get(name) is None
        r.ts().add(name, 2, 3)
        assert 2 == r.ts().get(name)[0]
        r.ts().add(name, 3, 4)
        assert 4 == r.ts().get(name)[1]

    def test_search(self, r):
        stack_dockloader(self)
        r.ft().create_index((TextField("txt"),))

        r.ft().add_document("doc1", txt="foo baz")
        r.ft().add_document("doc2", txt="foo bar")

        q = Query("foo ~bar").with_scores()
        res = r.ft().search(q)
        assert 2 == res.total
        assert "doc2" == res.docs[0].id
        assert 3.0 == res.docs[0].score
        assert "doc1" == res.docs[1].id


class InDockerTestEnv(RedisTestMixin, object):

    IN_DOCKER = True

    @classmethod
    def teardown_class(cls):
        container = cls.env.containers.get(cls.CONTAINER_NAME)
        try:
            container.kill()
        except docker.errors.APIError:
            pass
        finally:
            container.remove()

    @property
    def container(self):
        return self.__CONTAINER__

    def test_binaries_present(self):
        res, out = self.container.exec_run("ls /opt/redis-stack/bin")
        content = out.decode().strip()
        binaries = [
            "redis-server",
            "redis-stack-server",
            "redis-cli",
            "redis-benchmark",
            "redis-check-rdb",
            "redis-sentinel",
            "redis-check-aof",
        ]
        for i in binaries:
            assert i in content

    def test_modules_present(self):
        res, out = self.container.exec_run("ls /opt/redis-stack/lib")
        content = out.decode().strip()
        libs = [
            "rejson.so",
            "redisearch.so",
            "redisgraph.so",
            "redisbloom.so",
            "redistimeseries.so",
        ]
        for i in libs:
            assert i in content

    def test_config_present(self):
        res, out = self.container.exec_run(
            "ls /etc/redis-stack.conf /opt/redis-stack/etc/redis-stack.conf"
        )
        content = out.decode().strip()
        for i in ["/etc/redis-stack.conf", "/opt/redis-stack/etc/redis-stack.conf"]:
            assert i in content

    def test_binaries_execute(self):
        binaries = [
            "redis-server",
            "redis-cli",
            "redis-benchmark",
            "redis-check-rdb",
            "redis-sentinel",
            "redis-check-aof",
        ]
        for b in binaries:
            res, out = self.container.exec_run(f"/opt/redis-stack/bin/{b} -h")
            assert res == 1  # no segfault

        res, out = self.container.exec_run("/opt/redis-stack/bin/redis-stack-server -h")
        assert out.decode().lower().find("redis-stack-server") != -1
