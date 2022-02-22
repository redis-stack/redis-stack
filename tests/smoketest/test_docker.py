import pytest
import docker
import time
from helpers import ServiceTestMixin


@pytest.mark.docker
class TestDocker(ServiceTestMixin):

    DOCKER_NAME = "redis-stack"

    @classmethod
    def setup_class(cls):
        cls.env = docker.from_env()
        container = cls.env.containers.run(
            image="redislabs/redis-stack:latest",
            name=cls.DOCKER_NAME,
            detach=True,
            publish_all_ports=True,
            ports={"6379/tcp": 6379, "8001/tcp": 8001},
        )
        container.reload()
        
        # time for the docker to settle
        time.sleep(3)

    def teardown_class(cls):
        container = cls.env.containers.get(cls.DOCKER_NAME)
        container.stop()
        container.remove()
