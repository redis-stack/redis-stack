#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import os
import platform
import subprocess
import time

import pytest
from helpers import ROOT
from mixins import RedisPackagingMixin, RedisTestMixin


# OSX tests assume a wget is installed
class OSXTestBase(RedisPackagingMixin, RedisTestMixin, object):
    """Tests for OSX"""

    _stacktrees = ["/opt/homebrew/redis-stack/var/db/redis-stack", "/usr/local/var/db/redis-stack"]

    @classmethod
    def setup_class(cls):
        for i in cls._stacktrees:
            if os.path.isfile(f"{i}/dump.rdb"):
                os.unlink(f"{i}/redis-stack/dump.rdb")

        if platform.machine().lower().find("x86") != -1 or platform.machine().lower().find("amd") != -1:
            os.makedirs("/usr/local/var/db/redis-stack", exist_ok=True)
        else:
            os.makedirs("/opt/homebrew/redis-stack/var/db/redis-stack", exist_ok=True)

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
        for i in cls._stacktrees:
            if os.path.isfile(f"{i}/dump.rdb"):
                os.unlink(f"{i}/dump.rdb")


@pytest.mark.macos
class TestOSXZip(OSXTestBase):

    BASEPATH = os.path.abspath(os.path.join(ROOT, "redis-stack", "redis-stack-server"))
