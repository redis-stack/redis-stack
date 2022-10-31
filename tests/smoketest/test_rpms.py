import pytest
from env import DockerTestEnv
from mixins import RedisPackagingMixin, RedisTestMixin


class RPMTestBase(DockerTestEnv, RedisTestMixin, RedisPackagingMixin, object):
    """Tests for RPM packages"""

    def install(self, container):
        res, out = container.exec_run("yum install -y epel-release tar")
        assert res == 0

        # validate we properly get bad outputs as bad
        res, out = container.exec_run("iamnotarealcommand")
        assert res != 0

        # now, install our package
        res, out = container.exec_run(
            "yum install -y /build/redis-stack/redis-stack-server.rpm"
        )
        if res != 0:
            raise IOError(out)

    def uninstall(self, container):
        res, out = container.exec_run("yum remove -y redis-stack-server")
        if res != 0:
            raise IOError(out)


@pytest.mark.rhel7
class TestRHEL7(RPMTestBase):

    DOCKER_NAME = "centos:7"
    CONTAINER_NAME = "redis-stack-centos7"
    PLATFORM = "linux/amd64"


@pytest.mark.rhel8
class TestRHEL8(RPMTestBase):

    DOCKER_NAME = "oraclelinux:8"
    CONTAINER_NAME = "redis-stack-centos8"
    PLATFORM = "linux/amd64"

@pytest.mark.amazonlinux2
class TestAmazonLinux2(RPMTestBase):
    DOCKER_NAME = "amazonlinux:2"
    CONTAINER_NAME = "redis-stack-aml2"
    PLATFORM = "linux/amd64"

    def install(self, container):

        res, out = container.exec_run("amazon-linux-extras install epel -y")
        assert res == 0

        res, out = container.exec_run("iamnotarealcommand")
        assert res != 0

        # now, install our package
        res, out = container.exec_run(
            "yum install -y /build/redis-stack/redis-stack-server.rpm"
        )
        if res != 0:
            raise IOError(out)

    def uninstall(self, container):
        res, out = container.exec_run("yum remove -y redis-stack-server")
        if res != 0:
            raise IOError(out)
