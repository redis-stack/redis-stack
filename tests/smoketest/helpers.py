import os
import time
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


def stack_dockloader(cls):
    if getattr(cls, "IN_DOCKER", None) is not None:
        cls.container.reload()
        res, out = cls.container.exec_run(
            "/opt/redis-stack/bin/redis-stack-server", detach=True
        )
        time.sleep(2)


class RedisInsightTestMixin:
    def test_basic_redisinsight(self):
        c = 0
        while c < 9:
            stack_dockloader(self)
            try:
                c = urlopen("http://localhost:8001")
                content = c.read().decode()
                assert content.lower().find("redisinsight") != -1
                break
            except ConnectionResetError:
                time.sleep(0.5)
                c += 1


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
        docs = [i.id for i in res.docs]
        assert "doc2" in docs
        assert "doc1" in docs


class RedisPackagingMixin:
    @property
    def basepath(self):
        basepath = getattr(self, "BASEPATH", None)
        if basepath is None:
            return "/opt/redis-stack"
        return basepath

    def test_binaries_present(self):
        res, out = self.container.exec_run(f"ls {self.basepath}/bin")
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
        res, out = self.container.exec_run(f"ls {self.basepath}/lib")
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
            f"ls /etc/redis-stack.conf {self.basepath}/etc/redis-stack.conf"
        )
        content = out.decode().strip()
        for i in ["/etc/redis-stack.conf", f"{self.basepath}/etc/redis-stack.conf"]:
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
            res, out = self.container.exec_run(f"{self.basepath}/bin/{b} -h")
            assert res in [0, 1]  # no segfault

        res, out = self.container.exec_run(f"{self.basepath}/bin/redis-stack-server -h")
        assert out.decode().lower().find("redis-stack-server") != -1


class InDockerTestEnv(RedisTestMixin, RedisPackagingMixin, object):

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
