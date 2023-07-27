#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import os
import shutil
from typing import Union

import requests
from loguru import logger

from ..components.modules import Modules
from ..config import Config
from ..paths import Paths
from . import Recipe

# FUTURE this is a placeholder for the package depending on packages, in Linux
# This is not a real package


class RedisStack(Recipe):
    """A recipe to build the redis-stack package"""

    PACKAGE_NAME = "redis-stack"

    def __init__(self, osnick, arch="x86_64", osname="Linux"):
        self.ARCH = arch
        self.OSNAME = osname
        self.OSNICK = osnick
        self.__PATHS__ = Paths(self.PACKAGE_NAME, osnick, arch, osname)
        self.C = Config()

    def prepackage(
        self,
        binary_dir: Union[str, None],
        ignore: bool = False,
        version_override: str = None,
    ):

        raise NotImplementedError("DISABLED FOR NOW, INTENTIONALLY")

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
            m.redisgears,
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
        shutil.copyfile(
            os.path.join(
                self.__PATHS__.SCRIPTDIR, "scripts", f"redis-stack-server.{self.OSNAME}"
            ),
            stackdest,
        )

        os.chmod(stackdest, mode=0o755)

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
