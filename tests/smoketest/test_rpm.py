from re import A
from helpers import BASEPATH, PackageTestMixin
import pytest
import subprocess
import os


@pytest.mark.rpm
class TestRPMPackages(PackageTestMixin):
    @classmethod
    def setup_class(cls):
        subprocess.run(["yum", "install", "-y", "libssl-dev"])
        cmd = ["rpm", "-i", "redis-stack.rpm"]
        r = subprocess.run(cmd)
        assert r.returncode == 0

    @classmethod
    def teardown_class(cls):
        cmd = ["rpm", "remove", "-y", "redis-stack"]
        r = subprocess.run(cmd)
        assert r.returncode == 0

        # make sure trees are dead
        assert not os.path.isdir(BASEPATH)
