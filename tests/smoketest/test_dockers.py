import os
import time
from urllib.request import urlopen

import docker
import pytest
from mixins import RedisInsightTestMixin, RedisTestMixin
from env import DockerTestEnv


@pytest.mark.dockers_redis_stack
class TestRedisStack(RedisInsightTestMixin, RedisTestMixin, DockerTestEnv):

    VERSION = os.getenv("VERSION", "edge")
    CONTAINER_NAME = "redis-stack-server"
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


@pytest.mark.dockers_redis_stack_server
@pytest.mark.arm
class TestARMRedisStackServer(TestRedisStackServer):
    PLATFORM = "linux/arm64"
