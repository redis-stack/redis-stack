import os
import subprocess
import time

import docker
from helpers import ROOT


class DockerTestEnv:

    HOST_TYPE = "docker"

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
        cls.install(cls, container)

    @classmethod
    def teardown_class(cls):
        container = cls.env.containers.get(cls.CONTAINER_NAME)
        cls.uninstall(cls, container)
        try:
            container.kill()
        except docker.errors.APIError:
            pass
        finally:
            container.remove()

    @property
    def container(self):
        return self.__CONTAINER__


class VagrantTestEnv:

    HOST_TYPE = "vagrant"
    VAGRANT_BASEDIR = os.path.join(ROOT, "envs", "vagrants")

    @classmethod
    def setup_class(cls):
        cls.workdir = os.path.join(cls.VAGRANT_BASEDIR, cls.OSNICK)
        try:
            cls.teardown_class()
        except Exception:
            pass

        cmd = ["vagrant", "up", "--provision"]
        res = subprocess.run(cmd, cwd=cls.workdir)
        assert res.returncode == 0

        cls.install(cls)

        # start redis-stack
        subprocess.Popen(
            ["vagrant", "ssh", "-c", "/opt/redis-stack/bin/redis-stack-server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cls.workdir,
        )
        time.sleep(5)

    @classmethod
    def teardown_class(cls):
        cls.uninstall(cls)
        cmd = ["vagrant", "destroy", "-f"]
        res = subprocess.run(cmd, cwd=cls.workdir)
        assert res.returncode == 0
