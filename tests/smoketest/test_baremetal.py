# from helpers import RedisTestMixin, ROOT
# import os
import subprocess

# import time
import pytest
from env import VagrantTestEnv
from mixins import RedisPackagingMixin, RedisTestMixin

# class VagrantBase(RedisTestMixin, object):
#     """Test the pre-installed package on bare metal"""
#
# PACKAGE_NAME = "redis-stack-server"
# HOST_TYPE = "vagrant"


# def _assert_path_exists(self, path):
#     cmd = ["vagrant", "ssh", "-c", f"ls -l {path}"]
#     res = subprocess.run(cmd, cwd=self.workdir)
#     assert res.returncode == 0

# def test_config_present(self):
#     # self._assert_path_exists("/opt/redis-stack/etc/redis-stack.conf")

# def test_modules_present(self):
#     for i in [
#         "rejson.so",
#         "redisgraph.so",
#         "redisearch.so",
#         "redisbloom.so",
#         "redistimeseries.so",
#     ]:
#         self._assert_path_exists(f"/opt/redis-stack/lib/{i}")

# def test_binaries_present(self):
#     for i in [
#         "redis-server",
#         "redis-stack-server",
#         "redis-cli",
#         "redis-benchmark",
#         "redis-check-rdb",
#         "redis-sentinel",
#         "redis-check-aof",
#     ]:
#         self._assert_path_exists(f"/opt/redis-stack/bin/{i}")

# def test_binaries_execute(self):
#     binaries = [
#         "redis-server",
#         "redis-cli",
#         "redis-benchmark",
#         "redis-check-rdb",
#         "redis-sentinel",
#         "redis-check-aof",
#     ]

#     for b in binaries:
#         r = subprocess.run(
#             ["vagrant", "ssh", "-c", f"/opt/redis-stack/bin/{b} -h"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#         )
#         assert r.returncode in [0, 1]  # no segfault


class VagrantBase(VagrantTestEnv, RedisPackagingMixin, RedisTestMixin):
    pass


class DebVagrant(VagrantBase):
    def install(self):

        res = subprocess.run(
            ["vagrant", "ssh", "-c", "sudo apt-get update"], cwd=self.workdir
        )
        assert res.returncode == 0

        res = subprocess.run(
            ["vagrant", "ssh", "-c", "sudo apt install -y gdebi-core"],
            cwd=self.workdir,
        )
        assert res.returncode == 0

        cmd = [
            "vagrant",
            "ssh",
            "-c",
            "sudo gdebi -n /data/redis-stack/redis-stack-server*.deb",
        ]
        res = subprocess.run(cmd, cwd=self.workdir)
        assert res.returncode == 0

    def uninstall(self):
        cmd = [
            "vagrant",
            "ssh",
            "-c",
            "sudo apt remove -y redis-stack-server",
        ]
        res = subprocess.run(cmd, cwd=self.workdir)
        assert res.returncode == 0


class RPMVagrant(VagrantBase):
    def install(self):
        cmd = [
            "vagrant",
            "ssh",
            "-c",
            "sudo rpm -i /data/redis-stack/redis-stack-server*.rpm",
        ]
        res = subprocess.run(cmd, cwd=self.workdir)
        assert res.returncode in [0, 1]

    def uninstall(self):
        cmd = ["vagrant", "ssh", "-c", "sudo yum remove -y redis-stack-server"]
        res = subprocess.run(cmd, cwd=self.workdir)
        assert res.returncode == 0


@pytest.mark.focal
@pytest.mark.physical
class TestFocal(DebVagrant):

    OSNICK = "focal"


@pytest.mark.bionic
@pytest.mark.physical
class TestBionic(VagrantBase):

    OSNICK = "bionic"


@pytest.mark.xenial
@pytest.mark.physical
class TestXenial(VagrantBase):

    OSNICK = "xenial"


@pytest.mark.rhel7
@pytest.mark.physical
class TestCentos7(RPMVagrant):

    OSNICK = "centos7"


@pytest.mark.rhel8
@pytest.mark.physical
class TestCentos8(RPMVagrant):

    OSNICK = "centos8"
