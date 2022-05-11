import os
import time
from urllib.request import urlopen

import docker
import pytest
from mixins import RedisInsightTestMixin, RedisPackagingMixin, RedisTestMixin


class DockerTestBase(RedisPackagingMixin, RedisTestMixin, object):
    
    @classmethod
    def setup_class(cls):

        VERSION = os.getenv("VERSION", "edge")
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

@pytest.mark.dockers_redis_stack
class TestRedisStack(RedisInsightTestMixin, DockerTestBase):

    DOCKER_NAME = "redis/redis-stack"
    CONTAINER_NAME = "redis-stack"
    PORTMAP = {"6379/tcp": 6379, "8001/tcp": 8001}


@pytest.mark.dockers_redis_stack_server
class TestRedisStackServer(DockerTestBase):

    DOCKER_NAME = "redis/redis-stack-server"
    CONTAINER_NAME = "redis-stack-server"
    PORTMAP = {"6379/tcp": 6379, "8001/tcp": 8001}

    def test_no_redisinsight(self):
        with pytest.raises(ConnectionError):
            urlopen("http://localhost:8001")
