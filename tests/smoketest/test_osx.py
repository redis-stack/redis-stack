import os
from helpers import RedisTestMixin
import platform
import subprocess


class TestOSX(RedisTestMixin, object):

    if platform in ["i386", "x86_64"]:
        BASEPATH = "/usr/local"
    else:
        BASEPATH = "/opt/homebrew"

    @classmethod
    def setup_class(cls):
        try:
            cls.teardown_class()
        except Exception:
            pass

        x = os.system("brew tap redis-stack/redis-stack")
        if x != 0:
            raise IOError("Failed to provision brew tap")

        x = os.system("brew install redis-stack")
        if x != 0:
            raise IOError("Failed to install redis-stack")

        # start redis-stack
        r = subprocess.run(
            [f"{cls.BASEPATH}/bin/redis-stack-server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        cls.PROC = r.pid

    @classmethod
    def teardown_class(cls):

        # try to kill redis-stack if it is running
        try:
            os.kill(cls.PROC, 9)
        except ProcessLookupError:
            pass

        x = os.system("brew uninstall redis-stack-server")
        if x != 0:
            raise IOError("Uninstall of redis-stack-server failed")

        x = os.system("brew uninstall redis-stack-redisinsight")
        if x != 0:
            raise IOError("Uninstall of redis-stack-redisinsight failed")

        x = os.system("brew uninstall redis-stack")
        if x != 0:
            raise IOError("Uninstall of redis-stack failed")

        x = os.system("brew untap redis-stack/redis-stack")
        if x != 0:
            raise IOError("Could not remove brew tap")

    def test_redisinsight_is_installed(self):
        assert os.path.exists("/Applications/RedisInsight-v2.app")

    def test_modules_present(self):
        for i in [
            "rejson.so",
            "redisgraph.so",
            "redisearch.so",
            "redisbloom.so",
            "redistimeseries.so",
        ]:
            assert os.path.exists(f"{self.BASEPATH}/lib/{i}")

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
            print(i)
            assert os.path.exists(f"{self.BASEPATH}/bin/{i}")

    def test_config_present(self):
        assert os.path.exists(f"{self.BASEPATH}/etc/redis-stack.conf")

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
                [f"{self.basepath}/bin/{b}", "-h"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            assert r.returncode in [0, 1]  # no segfault

        out = subprocess.run(
            [f"{self.basepath}/bin/redis-stack-server", "-h"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert out.stdout.decode().lower().find("redis-stack-server") != -1

    def test_modules_present(self):
        res, out = self.container.exec_run(f"ls {self.basepath}/lib")
        content = out.decode().strip()
        libs = [
            "rejson.so",
            "redisearch.so",
            "redisgraph.so",
            "redisbloom.so",
            "redistimeseries.so",
        ]
        for i in libs:
            assert i in content
