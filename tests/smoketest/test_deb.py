from helpers import BASEPATH, PackageTestMixin
import pytest
import subprocess
import os


@pytest.mark.deb
class TestDebianPackages(PackageTestMixin):
    @classmethod
    def setup_class(cls):
        subprocess.run(["apt", "install", "-y", "libssl-dev"])
        cmd = ["dpkg", "-i", "redis-stack/redis-stack*.deb"]
        r = subprocess.run(cmd)
        assert r.returncode == 0

    @classmethod
    def teardown_class(cls):
        cmd = ["apt-get", "remove", "-y", "redis-stack"]
        r = subprocess.run(cmd)
        assert r.returncode == 0

        # make sure trees are dead
        assert not os.path.isdir(BASEPATH)
