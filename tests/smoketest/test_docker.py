import pytest
import docker
from helpers import ServiceTestMixin

@pytest.mark.docker
class TestDocker(ServiceTestMixin):
    
    DOCKER_NAME = 'redis-stack'
    
    @classmethod
    def setup_class(cls):
        cls.env = docker.from_env()
        container = cls.env.containers.run(
            image="redislabs/redis-stack:latest",
            name=cls.DOCKER_NAME,
            detach=True,
            publish_all_ports=True,
            ports={'6379/tcp': 6379, '8081/tcp': 8081}
        )
        container.reload()
    
    def teardown_class(cls):
        container = cls.env.containers.get(cls.DOCKER_NAME)
        container.stop()
        container.remove()