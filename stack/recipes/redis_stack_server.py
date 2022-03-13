from . import Recipe
from ..paths import Paths
from ..components.modules import Modules
from ..components.redis import Redis
from ..config import Config
import requests
import os
import shutil
from loguru import logger


class RedisStackServer(Recipe):
    """A recipe, to build the redis-stack-server package"""

    PACKAGE_NAME = "redis-stack-server"

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
            self.__PATHS__.USRBINDIR,
        ]:
            os.makedirs(i, exist_ok=True, mode=0o755)

        m = Modules(self.PACKAGE_NAME, self.OSNICK, self.ARCH, self.OSNAME)
        for i in [
            m.redisearch,
            m.redisgraph,
            m.redistimeseries,
            m.rejson,
            m.redisbloom,
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

        logger.debug("Copying redis-stack-server script")
        stackdest = os.path.join(self.__PATHS__.BINDIR, "redis-stack-server")
        shutil.copyfile(os.path.join(self.__PATHS__.SCRIPTDIR, "redis-stack-server"), stackdest)
        logger.debug(stackdest)
        os.chmod(stackdest, mode=0o755)
        
        if binary_dir is not None and not os.path.isdir(binary_dir):
            r = Redis(self.PACKAGE_NAME, self.OSNICK, self.ARCH, self.OSNAME)
            r.prepare()
        else:
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

        shutil.copyfile(
            os.path.join(self.__PATHS__.SCRIPTDIR, 'RSAL_LICENSE'),
            os.path.join(self.__PATHS__.SHAREDIR, 'RSAL_LICENSE'),
        )