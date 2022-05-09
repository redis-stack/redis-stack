import pytest
from env import DockerTestEnv
from mixins import RedisPackagingMixin, RedisTestMixin


class DEBTestBase(DockerTestEnv, RedisTestMixin, RedisPackagingMixin, object):
    def install(self, container):
        res, out = container.exec_run("apt update -q")
        assert res == 0

        res, out = container.exec_run("apt install -yq gdebi-core")
        assert res == 0

        # make sure gdebi is present
        res, out = container.exec_run("ls /usr/bin/gdebi")
        assert "/usr/bin/gdebi" in out.decode()

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


@pytest.mark.bionic
class TestBionic(DEBTestBase):

    DOCKER_NAME = "ubuntu:bionic"
    CONTAINER_NAME = "redis-stack-bionic"


@pytest.mark.focal
class TestFocal(DEBTestBase):

    DOCKER_NAME = "ubuntu:focal"
    CONTAINER_NAME = "redis-stack-focal"
