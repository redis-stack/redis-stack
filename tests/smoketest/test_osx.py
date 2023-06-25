#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
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

