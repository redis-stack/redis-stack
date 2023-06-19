#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import os
import subprocess
from urllib.request import urlopen

import yaml
from helpers import CONFIGYAML, assert_path_exists, stack_dockloader
from redis.commands.search.field import TextField
from redis.commands.search.query import Query


class RedisInsightTestMixin:
    def test_basic_redisinsight(self):
        stack_dockloader(self)
        c = urlopen("http://localhost:8001")
        content = c.read().decode()
        assert content.lower().find("redisinsight") != -1


class RedisTestMixin:

    def test_basic_redis(self, r):
        stack_dockloader(self)
        r.flushdb()
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
        r.flushdb()
        r.json().set("foo", ".", "bar")
        assert r.json().get("foo") == "bar"

    def test_bloom(self, r):
        stack_dockloader(self)
        r.flushdb()
        assert r.bf().create("bloom", 0.01, 1000)
        assert 1 == r.bf().add("bloom", "foo")
        assert 0 == r.bf().add("bloom", "foo")

    def test_gears(self, r):
        stack_dockloader(self)
        r.flushdb()
        r.execute_command("TFUNCTION LIST")

    def test_graph(self, r):
        stack_dockloader(self)
        r.flushdb()
        params = [1, 2.3, "str", True, False, None, [0, 1, 2]]
        query = "RETURN $param"
        for param in params:
            result = r.graph().query(query, {"param": param})
            expected_results = [[param]]
            assert expected_results == result.result_set

    def test_timeseries(self, r):
        stack_dockloader(self)
        r.flushdb()
        name = "test"
        r.ts().create(name)
        assert r.ts().get(name) is None
        r.ts().add(name, 2, 3)
        assert 2 == r.ts().get(name)[0]
        r.ts().add(name, 3, 4)
        assert 4 == r.ts().get(name)[1]

    def test_search(self, r):
        stack_dockloader(self)
        r.flushdb()
        r.ft().create_index((TextField("txt"),))

        r.ft().add_document("doc1", txt="foo baz")
        r.ft().add_document("doc2", txt="foo bar")

        q = Query("foo ~bar").with_scores()
        res = r.ft().search(q)
        assert 2 == res.total
        docs = [i.id for i in res.docs]
        assert "doc2" in docs
        assert "doc1" in docs

#    def test_versions_match(self, r):
#        stack_dockloader(r)
#        modmap = {
#            "redisearch": "search",
#            "redisgraph": "graph",
#            "redistimeseries": "timeseries",
#            "redisbloom": "bf",
#            "rejson": "rejson",
#        }
#
#        with open(CONFIGYAML, "r") as fp:
#            data = yaml.load(fp, yaml.SafeLoader)
#            versions = data.get("versions")
#
#        modlist = r.module_list()
#        modules = {m.get("name").lower(): m.get("ver") for m in modlist}
#        for k, v in modmap.items():
#            yamlversion = versions.get(k)
#
#            # remap
#            parts = yamlversion.split(".")
#            version = ""
#            if len(parts[1]) == 2:
#                base = f"{parts[0]}"
#            else:
#                base = f"{parts[0]}0"
#            if len(parts[2]) == 2:
#                patch = parts[2]
#            else:
#                patch = f"0{parts[2]}"
#            version = f"{base}{parts[1]}{patch}"
#
#            remoteversion = modules.get(v)
#            assert str(version) == str(remoteversion)
#

class RedisPackagingMixin:
    @property
    def basepath(self):
        basepath = getattr(self, "BASEPATH", None)
        if basepath is None:
            return "/opt/redis-stack"
        return basepath

    def test_binaries_present(self):
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
            assert_path_exists(self, os.path.join(self.basepath, "bin", i))

    def test_modules_present(self):
        libs = [
            "rejson.so",
            "redisearch.so",
            "redisgraph.so",
            "redisbloom.so",
            "redistimeseries.so",
        ]
        for i in libs:
            assert_path_exists(self, os.path.join(self.basepath, "lib", i))

    def test_config_present(self):
        assert_path_exists(self, os.path.join(self.basepath, "etc", "redis-stack.conf"))

    def test_binaries_execute(self):
        binaries = [
            "redis-server",
            "redis-cli",
            "redis-benchmark",
            "redis-check-rdb",
            "redis-sentinel",
            "redis-check-aof",
        ]

        host_type = getattr(self, "HOST_TYPE", None)
        if host_type == "docker":
            for b in binaries:
                res, out = self.container.exec_run(f"{self.basepath}/bin/{b} -h")
                assert res in [0, 1]  # no segfault

            res, out = self.container.exec_run(
                f"{self.basepath}/bin/redis-stack-server -h"
            )
            assert out.decode().lower().find("redis-stack-server") != -1
        elif host_type == "vagrant":
            for b in binaries:
                r = subprocess.run(
                    ["vagrant", "ssh", "-c", f"/opt/redis-stack/bin/{b} -h"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                assert r.returncode in [0, 1]  # no segfault
