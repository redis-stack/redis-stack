#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import pytest
from env import DockerTestEnv
from mixins import RedisPackagingMixin, RedisTestMixin


class DEBTestBase(DockerTestEnv, RedisTestMixin, RedisPackagingMixin, object):
    def install(self, container):
        res, out = container.exec_run("apt update -q")
        assert res == 0

        res, out = container.exec_run("apt install -yq gdebi-core wget")
        assert res == 0

        # make sure gdebi is present
        res, out = container.exec_run("ls /usr/bin/gdebi")
        assert "/usr/bin/gdebi" in out.decode()

        res, out = container.exec_run("mkdir -p /data")

        self.fetch_db()

        # validate we properly get bad outputs as bad
        res, out = container.exec_run("iamnotarealcommand")
        assert res != 0

        # now, install our package
        res, out = container.exec_run(
            "gdebi -n /build/redis-stack/redis-stack-server.deb"
        )
        if res != 0:
            raise IOError(out)

    def uninstall(self, container):
        res, out = container.exec_run("apt remove -y redis-stack-server")
        if res != 0:
            raise IOError(out)


@pytest.mark.xenial
class TestXenial(DEBTestBase):

    DOCKER_NAME = "ubuntu:xenial"
    CONTAINER_NAME = "redis-stack-xenial"
    PLATFORM = "linux/amd64"


@pytest.mark.bionic
class TestBionic(DEBTestBase):

    DOCKER_NAME = "ubuntu:bionic"
    CONTAINER_NAME = "redis-stack-bionic"
    PLATFORM = "linux/amd64"


@pytest.mark.jammy
class TestJammy(DEBTestBase):

    DOCKER_NAME = "ubuntu:jammy"
    CONTAINER_NAME = "redis-stack-jammy"
    PLATFORM = "linux/amd64"


@pytest.mark.bionic
@pytest.mark.arm
class TestARMBionic(TestBionic):
    PLATFORM = "linux/arm64"


@pytest.mark.jammy
@pytest.mark.arm
class TestARMJammy(TestJammy):
    PLATFORM = "linux/arm64"


@pytest.mark.focal
class TestFocal(DEBTestBase):

    DOCKER_NAME = "ubuntu:focal"
    CONTAINER_NAME = "redis-stack-focal"
    PLATFORM = "linux/amd64"


@pytest.mark.focal
@pytest.mark.arm
class TestARMFocal(TestFocal):
    PLATFORM = "linux/arm64"


@pytest.mark.bullseye
class TestBullseye(DEBTestBase):

    DOCKER_NAME = "debian:bullseye-slim"
    CONTAINER_NAME = "redis-stack-bullseye"
    PLATFORM = "linux/amd64"
