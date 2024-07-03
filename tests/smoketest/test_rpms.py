#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import pytest
from env import DockerTestEnv
from mixins import RedisPackagingMixin, RedisTestMixin


class RPMTestBase(DockerTestEnv, RedisTestMixin, RedisPackagingMixin, object):
    """Tests for RPM packages"""

    def install(self, container):
        res, out = container.exec_run("yum install -y epel-release tar wget")
        assert res == 0

        # validate we properly get bad outputs as bad
        res, out = container.exec_run("iamnotarealcommand")
        assert res != 0

        # fetch the rdb
        target = "/var/lib/redis-stack/dumb.rdb"
        cmd = f"wget -q https://redismodules.s3.amazonaws.com/redis-stack/testdata/dump-with-graph.rdb -O {target}"
        res, _ = container.exec_run(cmd)
        assert res != 0
        res, out = container.exec_run("mkdir -p /data")

        # now, install our package
        res, out = container.exec_run(
            "yum install -y /build/redis-stack/redis-stack-server.rpm"
        )
        if res != 0:
            raise IOError(out)

        # fetch the rdb testdata

    def uninstall(self, container):
        res, out = container.exec_run("yum remove -y redis-stack-server")
        if res != 0:
            raise IOError(out)


@pytest.mark.rhel7
class TestRHEL7(RPMTestBase):

    DOCKER_NAME = "centos:7"
    CONTAINER_NAME = "redis-stack-centos7"
    PLATFORM = "linux/amd64"

    def install(self, container):
        yum_mirror_fix_cmd = "bash -c \"for file in /etc/yum.repos.d/*.repo; do $MODE sed -i 's/^mirrorlist=/#mirrorlist=/g' $file $MODE sed -i 's/^#[[:space:]]*baseurl=http:\/\/mirror/baseurl=http:\/\/vault/g' $file \ done\""
        res, out = container.exec_run(yum_mirror_fix_cmd)
        print(out)
        assert res == 0

        # validate we properly get bad outputs as bad
        res, out = container.exec_run("iamnotarealcommand")
        assert res != 0

        # fetch the rdb
        target = "/var/lib/redis-stack/dumb.rdb"
        cmd = f"wget -q https://redismodules.s3.amazonaws.com/redis-stack/testdata/dump-with-graph.rdb -O {target}"
        res, _ = container.exec_run(cmd)
        assert res != 0
        res, out = container.exec_run("mkdir -p /data")

        # now, install our package
        res, out = container.exec_run(
            "yum install -y /build/redis-stack/redis-stack-server.rpm"
        )
        if res != 0:
            raise IOError(out)


@pytest.mark.rhel8
class TestRHEL8(RPMTestBase):

    DOCKER_NAME = "oraclelinux:8"
    CONTAINER_NAME = "redis-stack-centos8"
    PLATFORM = "linux/amd64"


@pytest.mark.amzn2
class TestAmazonLinux2(RPMTestBase):
    DOCKER_NAME = "amazonlinux:2"
    CONTAINER_NAME = "redis-stack-aml2"
    PLATFORM = "linux/amd64"

    def install(self, container):

        res, out = container.exec_run("yum install -y wget")
        assert res == 0

        res, out = container.exec_run("amazon-linux-extras install epel -y")
        assert res == 0

        res, out = container.exec_run("iamnotarealcommand")
        assert res != 0

        res, out = container.exec_run(
            "yum install -y openssl11-libs",
        )
        if res != 0:
            raise IOError(out)

        # now, install our package
        res, out = container.exec_run(
            "yum install -y /build/redis-stack/redis-stack-server.rpm"
        )
        if res != 0:
            raise IOError(out)

    def uninstall(self, container):
        res, out = container.exec_run("yum remove -y redis-stack-server")
        if res != 0:
            raise IOError(out)
