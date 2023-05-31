#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import os
import subprocess
import time

import pytest
from mixins import RedisTestMixin


class DockerComposeBase(RedisTestMixin, object):
    """Test running our dockers through docker compose"""

    VERSION = os.getenv("VERSION", "edge")
    COMPOSEFILE = "/tmp/docker-compose.yml"

    @classmethod
    def setup_class(cls):
        content = cls.generate(cls)
        with open(cls.COMPOSEFILE, "w") as fp:
            fp.write(content)

        cmd = ["docker-compose", "-f", cls.COMPOSEFILE, "up", "-d"]
        subprocess.run(cmd)

        # coalesce
        c = 0
        while c < 10:
            import redis

            r = redis.Redis(port=9379)
            try:
                assert r.ping()
                return
            except redis.exceptions.ConnectionError:
                time.sleep(1)
            c += 1
            if c == 9:
                raise redis.exceptions.ConnectionError(
                    "Could not connect to redis, after waiting"
                )

    @classmethod
    def teardown_class(cls):
        cmd = ["docker-compose", "-f", cls.COMPOSEFILE, "down"]
        subprocess.run(cmd)


@pytest.mark.dockers_redis_stack_server
class TestDockerComposeRedisStackServer(DockerComposeBase):

    DOCKER_IMAGE = "redis-stack-server"

    def generate(self):
        content = f"""
version: "3.9"
services:
  redis:
    container_name: {self.DOCKER_IMAGE}-dockercompose
    image: "redisfab/{self.DOCKER_IMAGE}:{self.VERSION}"
    ports:
      - 9379:6379
"""
        return content


@pytest.mark.dockers_redis_stack_server
class TestDockerComposeRedisStackServerEnvVars(DockerComposeBase):

    DOCKER_IMAGE = "redis-stack-server"

    def generate(self):
        content = f"""
version: "3.9"
services:
  redis:
    container_name: {self.DOCKER_IMAGE}-dockercompose
    image: "redisfab/{self.DOCKER_IMAGE}:{self.VERSION}"
    ports:
      - 9379:6379
    environment:
        REDIS_ARGS: "--maxmemory 100mb"
"""
        return content


@pytest.mark.dockers_redis_stack
class TestDockerComposeRedisStackEnvVars(DockerComposeBase):

    DOCKER_IMAGE = "redis-stack"

    def generate(self):
        content = f"""
version: "3.9"
services:
  redis:
    container_name: {self.DOCKER_IMAGE}-dockercompose
    image: "redisfab/{self.DOCKER_IMAGE}:{self.VERSION}"
    ports:
      - 9379:6379
    environment:
        REDIS_ARGS: "--maxmemory 100mb"
"""
        return content


@pytest.mark.dockers_redis_stack
class TestDockerComposeRedisStack(DockerComposeBase):

    DOCKER_IMAGE = "redis-stack"

    def generate(self):
        content = f"""
version: "3.9"
services:
  redis:
    container_name: {self.DOCKER_IMAGE}-dockercompose
    image: "redisfab/{self.DOCKER_IMAGE}:{self.VERSION}"
    ports:
      - 9379:6379
      - 8001:8001
"""
        return content
