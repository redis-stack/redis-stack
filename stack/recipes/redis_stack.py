from . import Recipe
from ..config import Config
from ..components.modules import Modules
from ..paths import Paths
import requests
from loguru import logger
import shutil
import os


class RedisStack(Recipe):
    """A recipe to build the redis-stack package"""
    
    PACKAGE_NAME = "redis-stack"
    
    def __init__(self, osnick, arch="x86_64", osname="Linux"):
        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.__PATHS__ = Paths(self.PACKAGE_NAME, osnick, arch, osname)
        self.C = Config()
        
    def prepackage(
        self, binary_dir: str, ignore: bool = False, version_override: str = None
    ):
        
        for i in [
            self.__PATHS__.EXTERNAL,
            self.__PATHS__.DESTDIR,
            self.__PATHS__.LIBDIR,
            self.__PATHS__.BINDIR,
            self.__PATHS__.SHAREDIR,
        ]:
            os.makedirs(i, exist_ok=True, mode=0o755)

        m = Modules(self.PACKAGE_NAME, self.OSNICK, self.ARCH, self.OSNAME)
        for i in [
            m.redisearch,
            m.redisgraph,
            m.redistimeseries,
            m.rejson,
            m.redisbloom,
            # self.redisgears, self.redisai
        ]:
            try:
                if version_override is None:
                    i()
                else:
                    i(version_override)
            except requests.HTTPError:
                if ignore:
                    pass
                else:
                    raise

        logger.debug(f"Copying redis binaries from {binary_dir}")
        for i in [
            "redis-benchmark",
            "redis-check-aof",
            "redis-check-rdb",
            "redis-cli",
            "redis-sentinel",
            "redis-server",
        ]:
            dest = os.path.join(self.__PATHS__.BINDIR, i)
            shutil.copy2(os.path.join(binary_dir, i), dest)
            os.chmod(dest, mode=0o755)

            # copy configuration files
            shutil.copytree(
                os.path.join(self.__PATHS__.SCRIPTDIR, "conf"),
                self.__PATHS__.ETCDIR,
                dirs_exist_ok=True,
            )