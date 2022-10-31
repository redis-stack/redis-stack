import os
import subprocess
import sys
import time

import docker
from helpers import ROOT


class DockerTestEnv:
    """An environment for use with docker. This version of the environment
    creates a docker mount of the current directory in /build.

    All instances must implement:
    DOCKER_NAME - The docker image name
    CONTAINER_NAME - The name to associate with the running container

    Optionally classes can implement:
    PORTMAP - A dictionary of docker port mappings eg: {"6379/tcp": 6379}
    """

    HOST_TYPE = "docker"

    @classmethod
    def setup_class(cls):
        cls.env = docker.from_env()

        # cleanup attempt, in case one was running previously
        try:
            cls.teardown_class()
        except Exception:
            pass

        portmap = getattr(cls, "PORTMAP", {"6379/tcp": 6379})

        m = docker.types.Mount("/build", ROOT, read_only=True, type="bind")
        container = cls.env.containers.run(
            image=cls.DOCKER_NAME,
            name=cls.CONTAINER_NAME,
            detach=True,
            mounts=[m],
            stdin_open=True,
            publish_all_ports=True,
            ports=portmap,
        )
        cls.__CONTAINER__ = container
        if getattr(cls, "install", None) is not None:
            cls.install(cls, container)

    @classmethod
    def teardown_class(cls):
        container = cls.env.containers.get(cls.CONTAINER_NAME)
        if getattr(cls, "uninstall", None) is not None:
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
    """Environments provisioned using Vagrant"""

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
