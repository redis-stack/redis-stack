#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import os
import shutil

import pytest
from env import DockerTestEnv
from mixins import RedisTestMixin


class AppImageTestBase(DockerTestEnv, RedisTestMixin, object):
    """The AppImage base - in theory as we add support for arm
    (as that becomes possible) this will follow the rest of the
    pattern.

    """

    REDIS_STACK_BINARY = "/build/redis-stack/squashfs-root/usr/bin/redis-stack-server"

    def install(self, container):  # irrelevant in the appimage case

        # clean the squashfs export each run"
        here = os.getcwd()
        stackdir = os.path.join(here, "redis-stack")
        squashdir = os.path.join(stackdir, "squashfs-root")
        if os.path.isdir(squashdir):
            shutil.rmtree(squashdir)

        # AppImages cannot be run within a docker, due to the lack of FUSE.
        # here, we extract the raw image, and run our tests against it
        os.chdir(stackdir)
        x = os.system("./redis-stack-server.AppImage --appimage-extract")
        assert x == 0
        os.chdir(here)

        if getattr(self, "__precommands__", None):
            for cmd in self.__precommands__(self):
                out, run = container.exec_run(cmd)
                assert out == 0

    def uninstall(self, container):  # irrelevant in this case
        pass

    def __precommands__(self):
        return [
            "apt-get update -yq",
            "apt-get install -yq libssl-dev libgomp1",
        ]


@pytest.mark.appimage
class TestAppImageX86(AppImageTestBase):
    DOCKER_NAME = "ubuntu:focal"
    CONTAINER_NAME = "redis-stack-appimage"
    PLATFORM = "linux/amd64"
