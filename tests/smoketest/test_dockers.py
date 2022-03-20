import pytest
import docker
import time
import os
from helpers import InDockerTestEnv, RedisInsightTestMixin
from urllib.request import urlopen


class DockerTestBase(InDockerTestEnv, object):
    @classmethod
    def setup_class(cls):

        VERSION = os.getenv("REDIS_STACK_VERSION", "edge")
        cls.env = docker.from_env()
        container = cls.env.containers.run(
            image=f"{cls.DOCKER_NAME}:{VERSION}",
            name=cls.CONTAINER_NAME,
            detach=True,
            publish_all_ports=True,
            ports=cls.PORTMAP,
        )
        cls.__CONTAINER__ = container

        # time for the docker to settle
        time.sleep(3)
        res, out = container.exec_run("apt install -y git")
        assert res == 0

        res, out = container.exec_run("apt install -y python3-pip")
        assert res == 0

@pytest.mark.dockers
class TestRedisStack(RedisInsightTestMixin, DockerTestBase):

    DOCKER_NAME = "redis/redis-stack"
    CONTAINER_NAME = "redis-stack"
    PORTMAP = {"6379/tcp": 6379, "8001/tcp": 8001}


@pytest.mark.dockers
class TestRedisStackServer(DockerTestBase):

    DOCKER_NAME = "redis/redis-stack-server"
    CONTAINER_NAME = "redis-stack-server"
    PORTMAP = {"6379/tcp": 6379, "8001/tcp": 8001}

    def test_no_redisinsight(self):
        with pytest.raises(ConnectionError):
            urlopen("http://localhost:8001")
