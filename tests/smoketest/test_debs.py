import docker
import pytest
from helpers import InDockerTestEnv, ROOT


class DEBTestBase(InDockerTestEnv, object):
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

        res, out = container.exec_run("apt update -q")
        assert res == 0

        res, out = container.exec_run("apt install -yq gdebi-core")
        assert res == 0

        res, out = container.exec_run("apt install -y git")
        assert res == 0

        res, out = container.exec_run("apt install -y python3-pip")
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
