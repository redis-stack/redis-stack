import docker
import pytest
from helpers import ROOT
from env import DockerTestEnv
from mixins import RedisPackagingMixin, RedisTestMixin


class TARTestBase(DockerTestEnv, RedisPackagingMixin, RedisTestMixin, object):
    """Tests, in dockers for the downloadable tarballs"""

    def uninstall(self, container):  # no relevence here
        pass

    def install(self, container):

        if getattr(self, "__precommands__", None):
            for cmd in self.__precommands__(self):
                out, run = container.exec_run(cmd)
                assert out == 0

        # untar the package in default location
        res, out = container.exec_run(
            "tar -zxpf /build/redis-stack/redis-stack-server.tar.gz",
        )
        if res != 0:
            raise IOError(out)

        # fetch the tree
        res, out = container.exec_run("ls /")
        stackdir = None
        for dir in out.decode().split():
            if dir.find("redis-stack-server") != -1:
                stackdir = dir
                break
        assert stackdir is not None

        # ensure the docker bridge, properly fails
        res, out = container.exec_run("ls /opt/redis-stack")
        assert res != 0

        # move it
        res, out = container.exec_run(f"mv /{stackdir} /opt/redis-stack")
        if res != 0:
            raise IOError(out)

        # validate the path now exists
        res, out = container.exec_run("ls /opt/redis-stack")
        assert res == 0


@pytest.mark.bionic
class TestBionic(TARTestBase):

    DOCKER_NAME = "ubuntu:bionic"
    CONTAINER_NAME = "redis-stack-bionic"
    PLATFORM = "linux/amd64"

    def __precommands__(self):
        return [
            "apt-get update -yq",
            "apt-get install -yq libssl-dev libgomp1",
        ]


@pytest.mark.bionic
@pytest.mark.arm
class TestARMBionic(TestBionic):
    PLATFORM = "linux/arm64"


@pytest.mark.jammy
@pytest.mark.arm
class TestARMJammy(TestJammy):
    PLATFORM = "linux/arm64"


@pytest.mark.xenial
class TestXenial(TARTestBase):

    DOCKER_NAME = "ubuntu:xenial"
    CONTAINER_NAME = "redis-stack-xenial"
    PLATFORM = "linux/amd64"

    def __precommands__(self):
        return [
            "apt-get update -yq",
            "apt-get install -yq libssl-dev libgomp1",
        ]


@pytest.mark.focal
class TestFocal(TARTestBase):

    DOCKER_NAME = "ubuntu:focal"
    CONTAINER_NAME = "redis-stack-focal"
    PLATFORM = "linux/amd64"

    def __precommands__(self):
        return [
            "apt-get update -yq",
            "apt-get install -yq libssl-dev libgomp1",
        ]


@pytest.mark.jammy
class TestJammy(TARTestBase):

    DOCKER_NAME = "ubuntu:jammy"
    CONTAINER_NAME = "redis-stack-jammy"
    PLATFORM = "linux/amd64"

    def __precommands__(self):
        return [
            "apt-get update -yq",
            "apt-get install -yq libssl-dev libgomp1",
        ]


@pytest.mark.rhel7
class TestCentos7(TARTestBase):

    DOCKER_NAME = "centos:7"
    CONTAINER_NAME = "redis-stack-centos7"
    PLATFORM = "linux/amd64"

    def __precommands__(self):
        return [
            "yum install -y epel-release",
            "yum install -y openssl-devel jemalloc-devel libgomp",
        ]


@pytest.mark.rhel8
class TestCentos8(TARTestBase):

    DOCKER_NAME = "oraclelinux:8"
    CONTAINER_NAME = "redis-stack-centos8"
    PLATFORM = "linux/amd64"

    def __precommands__(self):
        return [
            "yum install -y epel-release tar",
            "yum install -y openssl-devel jemalloc-devel libgomp",
        ]


@pytest.mark.archlinux
class TestArchLinux(TARTestBase):

    DOCKER_NAME = "archlinux:latest"
    CONTAINER_NAME = "redis-stack-centos8"
    PLATFORM = "linux/amd64"

    def __precommands__(self):
        return ["pacman -Fy"]


@pytest.mark.amazonlinux2
class TestAmazonLinuxTar(TARTestBase):
    DOCKER_NAME = "amazonlinux:2"
    CONTAINER_NAME = "redis-stack-aml2"
    PLATFORM = "linux/amd64"

    def __precommands__(self):

        return [
            "amazon-linux-extras install epel -y",
            "yum install -y openssl-devel jemalloc-devel libgomp tar gzip",
        ]
