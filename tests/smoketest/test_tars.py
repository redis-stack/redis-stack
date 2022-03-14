import docker
import pytest

from helpers import InDockerTestEnv, ROOT


class TARTestBase(InDockerTestEnv, object):
    @classmethod
    def setup_class(cls):
        cls.env = docker.from_env()

        # cleanup attempt, in case one was running previously
        try:
            cls.teardown_class()
        except Exception:
            pass

        m = docker.types.Mount("/build", ROOT, read_only=True, type="bind")
        container = cls.env.containers.run(
            image=cls.DOCKER_NAME,
            name=cls.CONTAINER_NAME,
            detach=True,
            mounts=[m],
            command="sleep 1200",
            publish_all_ports=True,
            ports={"6379/tcp": 6379},
        )
        cls.__CONTAINER__ = container

        if getattr(cls, "__precommands__", None):
            for cmd in cls.__precommands__(cls):
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

    # need to override this test for the tar case because system integration
    # does not apply
    def test_config_present(self):
        res, out = self.container.exec_run("ls /opt/redis-stack/etc/redis-stack.conf")
        assert res == 0


@pytest.mark.bionic
class TestBionic(TARTestBase):

    DOCKER_NAME = "ubuntu:bionic"
    CONTAINER_NAME = "redis-stack-bionic"

    def __precommands__(self):
        return [
            "apt-get update -yq",
            "apt-get install -yq libssl-dev libgomp1",
        ]

@pytest.mark.xenial
class TestXenial(TARTestBase):

    DOCKER_NAME = "ubuntu:xenial"
    CONTAINER_NAME = "redis-stack-xenial"

    def __precommands__(self):
        return [
            "apt-get update -yq",
            "apt-get install -yq libssl-dev libgomp1",
        ]


@pytest.mark.focal
class TestFocal(TARTestBase):

    DOCKER_NAME = "ubuntu:focal"
    CONTAINER_NAME = "redis-stack-focal"

    def __precommands__(self):
        return [
            "apt-get update -yq",
            "apt-get install -yq libssl-dev libgomp1",
        ]


@pytest.mark.rhel7
class TestCentos7(TARTestBase):

    DOCKER_NAME = "centos:7"
    CONTAINER_NAME = "redis-stack-centos7"

    def __precommands__(self):
        return [
            "yum install -y epel-release",
            "yum install -y openssl-devel jemalloc-devel libgomp",
        ]


@pytest.mark.rhel8
class TestCentos8(TARTestBase):

    DOCKER_NAME = "oraclelinux:8"
    CONTAINER_NAME = "redis-stack-centos8"

    def __precommands__(self):
        return [
            "yum install -y epel-release",
            "yum install -y openssl-devel jemalloc-devel libgomp",
        ]
