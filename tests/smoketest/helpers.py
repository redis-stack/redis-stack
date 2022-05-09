import os
import subprocess
import time

# from urllib.request import urlopen


BASEPATH = "/opt/redis-stack"
BINDIR = os.path.join(BASEPATH, "bin")
LIBDIR = os.path.join(BASEPATH, "lib")
ETCDIR = os.path.join(BASEPATH, "etc")
SHAREDIR = os.path.join(BASEPATH, "share")
REDIS_UID = 65534
REDIS_GID = 65534

BINARIES = [
    "redis-server",
    "redis-benchmark",
    "redis-check-aof",
    "redis-check-rdb",
    "redis-cli",
    "redis-sentinel",
]

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def stack_dockloader(cls):
    if getattr(cls, "HOST_TYPE", None) == "docker":
        cls.container.reload()
        res, out = cls.container.exec_run(
            "/opt/redis-stack/bin/redis-stack-server", detach=True
        )
        time.sleep(2)


def assert_path_exists(cls, path):
    """Validate the presence of the path"""
    host_type = getattr(cls, "HOST_TYPE", None)
    if host_type is None:
        assert os.path.isfile(path)
    elif host_type == "docker":
        res, out = cls.container.exec_run(f"ls {path}")
        content = out.decode().strip()
        assert "No such file or directory" not in content
    elif host_type == "vagrant":
        cmd = ["vagrant", "ssh", "-c", f"ls -l {path}"]
        res = subprocess.run(cmd, cwd=cls.workdir)
        assert res.returncode == 0
