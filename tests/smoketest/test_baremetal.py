from helpers import RedisTestMixin, ROOT
import os
import subprocess
import time
import pytest


class VagrantBase(RedisTestMixin, object):
    """Test the pre-installed package on bare metal"""

    PACKAGE_NAME = "redis-stack-server"

    VAGRANT_BASEDIR = os.path.join(ROOT, "envs", "vagrants")

    @classmethod
    def setup_class(cls):
        cls.workdir = os.path.join(cls.VAGRANT_BASEDIR, cls.OSNICK)
        try:
            cls.teardown_class()
        except:
            pass

        if os.path.isfile(os.path.join(ROOT, "poetry.lock")):
            os.unlink(os.path.join(ROOT, "poetry.lock"))

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

    def _assertPathExists(self, path):
        cmd = ["vagrant", "ssh", "-c", f"ls -l {path}"]
        res = subprocess.run(cmd, cwd=self.workdir)
        assert res.returncode == 0

    def test_config_present(self):
        self._assertPathExists("/opt/redis-stack/etc/redis-stack.conf")

    def test_modules_present(self):
        for i in [
            "rejson.so",
            "redisgraph.so",
            "redisearch.so",
            "redisbloom.so",
            "redistimeseries.so",
        ]:
            self._assertPathExists(f"/opt/redis-stack/lib/{i}")

    def test_binaries_present(self):
        for i in [
            "redis-server",
            "redis-stack-server",
            "redis-cli",
            "redis-benchmark",
            "redis-check-rdb",
            "redis-sentinel",
            "redis-check-aof",
        ]:
            self._assertPathExists(f"/opt/redis-stack/bin/{i}")

    def test_binaries_execute(self):
        binaries = [
            "redis-server",
            "redis-cli",
            "redis-benchmark",
            "redis-check-rdb",
            "redis-sentinel",
            "redis-check-aof",
        ]

        for b in binaries:
            r = subprocess.run(
                ["vagrant", "ssh", "-c", f"/opt/redis-stack/bin/{b} -h"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            assert r.returncode in [0, 1]  # no segfault


class DebVagrant(VagrantBase):
    def install(self):
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
        cmd = [
            "vagrant",
            "ssh",
            "-c",
            "sudo yum remove -y redis-stack-server"
        ]
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
