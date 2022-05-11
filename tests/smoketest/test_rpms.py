import pytest
from env import DockerTestEnv
from mixins import RedisPackagingMixin, RedisTestMixin


class RPMTestBase(DockerTestEnv, RedisTestMixin, RedisPackagingMixin, object):

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


@pytest.mark.rhel8
class TestRHEL8(RPMTestBase):

    DOCKER_NAME = "oraclelinux:8"
    CONTAINER_NAME = "redis-stack-centos8"
