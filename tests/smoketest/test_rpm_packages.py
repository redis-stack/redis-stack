from helpers import InDockerTestEnv, ROOT
import docker


class RPMTestBase(InDockerTestEnv, object):
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

        res, out = container.exec_run("yum install -y epel-release")
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
        assert res == 0


class TestRHEL7(RPMTestBase, object):

    DOCKER_NAME = "centos:7"
    CONTAINER_NAME = "redis-stack-centos7"


class TestRHEL8(RPMTestBase, object):

    DOCKER_NAME = "oraclelinux:8"
    CONTAINER_NAME = "redis-stack-centos8"
