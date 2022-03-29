import os
from helpers import RedisPackagingMixin, RedisTestMixin
import platform


class TestOSX(RedisPackagingMixin, RedisTestMixin, object):
    
    if platform in ['i386', 'x86_64']:
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
        
    @classmethod
    def teardown_class(cls):
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
        assert os.path.exists("/Applications/RedisInsight-v2")