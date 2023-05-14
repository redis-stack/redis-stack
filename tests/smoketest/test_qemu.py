from tests.smoketest.env import PhysicalBaseEnv
from tests.smoketest.mixins import RedisPackagingMixin, RedisTestMixin
import pytest
import os


class QEMUTestBase(PhysicalBaseEnv, RedisTestMixin, RedisPackagingMixin, object):
    
    def install(self):
        if getattr(self, "__precommands__", None):
            for cmd in self.__precommands__(self):
                out = os.system(cmd)
                assert out == 0
        
class ARMDEBTestBase(QEMUTestBase):
    
    def __precommands__(self):
        return ["apt update -yq",
            "apt install -yq gdebi-core",
            "gdebi -n /build/redis-stack/redis-stack-server.deb",
        ]
        
    def uninstall(self):
        os.system("apt remove -y redis-stack-server")
        
class ARMTarTestBase(QEMUTestBase):
    
    def __precommands__(self):
        return ["apt update -yq",
            "apt-get install -yq libssl-dev libgomp1",
            "tar -zxpf /build/redis-stack/redis-stack-server.tar.gz",
            "mv /build/redis-stack/redis-stack* /opt/redis-stack"
        ] 
    
    def uninstall(self):
        os.system("rm -rf /opt/redis-stack")
    
@pytest.mark.jammy
@pytest.mark.arm
@pytest.mark.qemu
class TestArmJammyDeb(ARMDEBTestBase):
    pass

@pytest.mark.bionic
@pytest.mark.arm
@pytest.mark.qemu
class TestArmBionicDeb(ARMDEBTestBase):
    pass

@pytest.mark.focal
@pytest.mark.arm
@pytest.mark.qemu
class TestArmFocalDeb(ARMDEBTestBase):
    pass

@pytest.mark.jammy
@pytest.mark.arm
@pytest.mark.qemu
class TestArmJammyTar(ARMTarTestBase):
    pass

@pytest.mark.bionic
@pytest.mark.arm
@pytest.mark.qemu
class TestArmBionicTar(ARMTarTestBase):
    pass

@pytest.mark.focal
@pytest.mark.arm
@pytest.mark.qemu
class TestArmFocalTar(ARMTarTestBase):
    pass