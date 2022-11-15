#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import pytest
from env import DockerTestEnv
from mixins import RedisPackagingMixin, RedisTestMixin


@pytest.mark.archlinux
class TestArchPackage(DockerTestEnv, RedisTestMixin, RedisPackagingMixin, object):

    PLATFORM = "linux/amd64"
    DOCKER_NAME = "archlinux:latest"
    CONTAINER_NAME = "redis-stack-archlinux"

    def install(self, container):

        res, out = container.exec_run("pacman -Fy")
        assert res == 0

        res, out = container.exec_run(
            "pacman -U --noconfirm /build/redis-stack/redis-stack-server.pkg"
        )
        if res != 0:
            raise IOError(out)

    def uninstall(self, container):
        res, out = container.exec_run("pacman -R --noconfirm redis-stack-server")
        if res != 0:
            raise IOError(out)
