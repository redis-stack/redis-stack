#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import getpass
import os
import subprocess
import time

import pytest
from mixins import RedisTestMixin


@pytest.mark.snaps
class TestRedisStackServerSnap(RedisTestMixin, object):
    """Tests for the snap images"""

    @classmethod
    def setup_class(cls):
        if getpass.getuser() != "root":
            raise AttributeError("snap tests can only be run as root")
        if not os.path.exists("/snap"):
            os.symlink("/var/lib/snapd/snap", "/snap")
        cmd = [
            "snap",
            "install",
            "--dangerous",
            "--classic",
            "redis-stack/redis-stack-server.snap",
        ]
        subprocess.run(cmd, check=True)

        # start redis
        p = subprocess.Popen("redis-stack-server")
        cls.PID = p.pid
        time.sleep(3)

    @classmethod
    def teardown(cls):
        cmd = ["snap", "remove", "redis-stack-server"]
        subprocess.run(cmd, check=True)
