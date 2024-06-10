#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import os
from urllib.request import urlopen

import pytest
from env import DockerTestEnv
from mixins import RedisInsightTestMixin, RedisTestMixin


@pytest.mark.dockers_redis_stack
class TestRedisStack(RedisInsightTestMixin, RedisTestMixin, DockerTestEnv):

    VERSION = os.getenv("VERSION", "edge")
    CONTAINER_NAME = "redis-stack"
    DOCKER_NAME = f"redisfab/{CONTAINER_NAME}:{VERSION}"
    PORTMAP = {"6379/tcp": 6379, "8001/tcp": 8001}
    PLATFORM = "linux/amd64"


@pytest.mark.dockers_redis_stack_server
class TestRedisStackServer(RedisTestMixin, DockerTestEnv):

    VERSION = os.getenv("VERSION", "edge")
    CONTAINER_NAME = "redis-stack-server"
    DOCKER_NAME = f"redisfab/{CONTAINER_NAME}:{VERSION}"
    PORTMAP = {"6379/tcp": 6379, "8001/tcp": 8001}
    PLATFORM = "linux/amd64"

    def test_no_redisinsight(self):
        with pytest.raises(ConnectionError):
            urlopen("http://localhost:8001")


@pytest.mark.dockers_redis_stack
@pytest.mark.arm
class TestARMRedisStack(TestRedisStack):
    PLATFORM = "linux/arm64"

    def test_basic_redisinsight(self):
        # override redisinsight test due to limitations
        # in github actions within qemu
        try:
            c = urlopen("http://localhost:8001")
            content = c.read().decode()
            assert content.lower().find("Redis Insight") != -1
        except ConnectionResetError:  # fine, qemu break case attempt
            self.container.exec_run("apt install -y curl")
            res, out = self.container.exec_run("curl http://localhost:8001")
            try:
                assert out.decode().strip().lower().find("Redis Insight") != -1
            except AssertionError:  # if in docker we can't, validate process runs, trust team tests
                res, out = self.container.exec_run(
                    "ps -ef"
                )  # there are no pipes in exec_run contexts
                assert out.decode().strip().lower().find("nodejs") != -1


@pytest.mark.dockers_redis_stack_server
@pytest.mark.arm
class TestARMRedisStackServer(TestRedisStackServer):
    PLATFORM = "linux/arm64"
