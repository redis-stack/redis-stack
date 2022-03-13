import pytest
import docker
import os
from helpers import ROOT

class TestXenial():
    
    DOCKER_NAME = "ubuntu:xenial"
    CONTAINER_NAME = "redis-stack-xenial"
    
    @property
    def container(self):
        return self.__CONTAINER__
    
    def test_binaries_present(self):
        res, out = self.container.exec_run("ls /opt/redis-stack/bin")
        content = out.decode().strip()
        binaries = ['redis-server', 'redis-stack-server', 'redis-cli', 'redis-benchmark', 'redis-check-rdb', 'redis-sentinel', 'redis-check-aof']
        for i in binaries:
            assert i in content
            
    def test_modules_present(self):
        res, out = self.container.exec_run("ls /opt/redis-stack/lib")
        content = out.decode().strip()
        libs = ['rejson.so', 'redisearch.so', 'redisgraph.so', 'redisbloom.so', 'redistimeseries.so']
        for i in libs:
            assert i in content
            
    def test_config_present(self):
        res, out = self.container.exec_run("ls /etc/redis-stack.conf /opt/redis-stack/etc/redis-stack.conf")
        content = out.decode().strip()
        for i in ['/etc/redis-stack.conf', '/opt/redis-stack/etc/redis-stack.conf']:
            assert i in content
            
    def test_binaries_execute(self):
        binaries = ['redis-server', 'redis-stack-server', 'redis-cli', 'redis-benchmark', 'redis-check-rdb', 'redis-sentinel', 'redis-check-aof']
        for b in binaries:
            res, out = self.container.exec_run(f"/opt/redis-stack/bin/{b} -h")
            print(out)
            print(res)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    @classmethod
    def setup_class(cls):
        cls.env = docker.from_env()
        
        # cleanup attempt, in case one was running previously
        try:
            cls.teardown_class()
        except:
            pass
        
        m = docker.types.Mount("/build", ROOT, read_only=True, type="bind")
        container = cls.env.containers.run(
            image=cls.DOCKER_NAME,
            name=cls.CONTAINER_NAME,
            detach=True,
            mounts=[m],
            command="sleep 1200",
        )
        cls.__CONTAINER__ = container
        
        res, out = container.exec_run("apt update -q")
        assert res == 0
        
        res, out = container.exec_run("apt install -yq gdebi-core")
        assert res == 0
        
        # make sure gdebi is present
        res, out = container.exec_run("ls /usr/bin/gdebi")
        assert "/usr/bin/gdebi" in out.decode()
        
        # validate we properly get bad outputs as bad
        res, out = container.exec_run("iamnotarealcommand")
        assert res != 0
        
        # now, install our package
        res, out = container.exec_run("gdebi -n /build/redis-stack/redis-stack-server.deb")
        if res != 0:
            raise IOError(out)
        assert res == 0

    @classmethod
    def teardown_class(cls):
        container = cls.env.containers.get(cls.CONTAINER_NAME)
        container.kill()
        container.remove()