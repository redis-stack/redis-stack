import os
import subprocess
import time

import pytest
from helpers import ROOT
from mixins import RedisPackagingMixin, RedisTestMixin


class OSXTestBase(RedisPackagingMixin, RedisTestMixin, object):
    """Tests for OSX"""

    @classmethod
    def setup_class(cls):
        for i in ["/opt/homebrew/redis-stack", "/usr/local/"]:
            if os.path.isfile(f"{i}/var/db/redis-stack/dump.rdb"):
                os.unlink(f"{i}/var/db/redis-stack/dump.rdb")

        rss_binary = f"{cls.BASEPATH}/bin/redis-stack-server"
        r = subprocess.Popen(
            [rss_binary],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        cls.PROC = r.pid
        time.sleep(2)
        assert cls.PROC > 0

    @classmethod
    def teardown_class(cls):
        subprocess.run(["pkill", "-TERM", "-P", str(cls.PROC)])
        for i in ["/opt/homebrew/redis-stack", "/usr/local/"]:
            if os.path.isfile(f"{i}/var/db/redis-stack/dump.rdb"):
                os.unlink(f"{i}/var/db/redis-stack/dump.rdb")


@pytest.mark.macos
class TestOSXZip(OSXTestBase):

    BASEPATH = os.path.abspath(os.path.join(ROOT, "redis-stack", "redis-stack-server"))


# class TestOSXHomebrew(RedisTestMixin, object):

#     if platform in ["i386", "x86_64"]:
#         BASEPATH = "/usr/local"
#     else:
#         BASEPATH = "/opt/homebrew"

#     @classmethod
#     def setup_class(cls):
#         try:
#             cls.teardown_class()
#         except Exception:
#             pass

#         rdbfile = f"{cls.BASEPATH}/var/db/redis-stack/dump.rdb"
#         if os.path.isfile(rdbfile):
#             os.unlink(rdbfile)

#         x = os.system("brew tap redis-stack/redis-stack")
#         if x != 0:
#             raise IOError("Failed to provision brew tap")

#         x = os.system("brew install redis-stack")
#         if x != 0:
#             raise IOError("Failed to install redis-stack")

#         # start redis-stack
#         r = subprocess.Popen(
#             [f"{cls.BASEPATH}/bin/redis-stack-server"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#         )
#         cls.PROC = r.pid
#         time.sleep(2)
#         assert cls.PROC > 0

#     @classmethod
#     def teardown_class(cls):

#         # try to kill redis-stack if it is running
#         try:
#             os.kill(cls.PROC, 9)
#         except (ProcessLookupError, TypeError, NameError):
#             pass

#         x = os.system("brew uninstall redis-stack-server")
#         if x != 0:
#             raise IOError("Uninstall of redis-stack-server failed")

#         x = os.system("brew uninstall redis-stack-redisinsight")
#         if x != 0:
#             raise IOError("Uninstall of redis-stack-redisinsight failed")

#         x = os.system("brew uninstall redis-stack")
#         if x != 0:
#             raise IOError("Uninstall of redis-stack failed")

#         x = os.system("brew untap redis-stack/redis-stack")
#         if x != 0:
#             raise IOError("Could not remove brew tap")

#     def test_redisinsight_is_installed(self):
#         assert os.path.exists("/Applications/RedisInsight-v2.app")

#     def test_modules_present(self):
#         for i in [
#             "rejson.so",
#             "redisgraph.so",
#             "redisearch.so",
#             "redisbloom.so",
#             "redistimeseries.so",
#         ]:
#             assert os.path.exists(f"{self.BASEPATH}/lib/{i}")

#     def test_binaries_present(self):
#         for i in [
#             "redis-server",
#             "redis-stack-server",
#             "redis-cli",
#             "redis-benchmark",
#             "redis-check-rdb",
#             "redis-sentinel",
#             "redis-check-aof",
#         ]:
#             assert os.path.exists(f"{self.BASEPATH}/bin/{i}")

#     def test_config_present(self):
#         assert os.path.exists(f"{self.BASEPATH}/etc/redis-stack.conf")

#     def test_binaries_execute(self):
#         binaries = [
#             "redis-server",
#             "redis-cli",
#             "redis-benchmark",
#             "redis-check-rdb",
#             "redis-sentinel",
#             "redis-check-aof",
#         ]

#         for b in binaries:
#             r = subprocess.run(
#                 [f"{self.BASEPATH}/bin/{b}", "-h"],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#             )
#             assert r.returncode in [0, 1]  # no segfault
