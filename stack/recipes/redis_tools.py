import os
from typing import Union

from ..components.redis import Redis
from ..config import Config
from ..paths import Paths
from . import AbstractRecipe


class RedisTools(AbstractRecipe):
    """A recipe, for building the redis-tools package"""

    PACKAGE_NAME = "redis-tools"

    def __init__(self, osnick, arch="x86_64", osname="Linux"):
        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self._basedirname = "redis"
        self.__PATHS__ = Paths(
            self.PACKAGE_NAME, osnick, arch, osname, basedirname=self._basedirname
        )
        self.C = Config()

    @property
    def __package_base_args__(self) -> list:
        """Return base arguments for the package."""
        c = Config()
        print(self.PACKAGE_NAME)
        return [
            "fpm",
            "-s dir",
            f"-C {self.__PATHS__.WORKDIR}",
            f"-n {c.get_key(self.PACKAGE_NAME)['product']}",
            "--provides redis-tools",
            f"--architecture {self.ARCH}",
            f"--vendor '{c.get_key('vendor')}'",
            f"--version {self.version}",
            f"--url '{c.get_key('url')}'",
            f"--license '{c.get_key('license')}'",
            "--category server",
            f"--maintainer '{c.get_key('email')}'",
            f"--description '{c.get_key(self.PACKAGE_NAME)['description']}'",
            "--directories '/opt/redis-stack'",
        ]

    def prepackage(
        self,
        binary_dir: Union[str, None],
        ignore: bool = False,
        version_override: str = None,
    ):

        for i in [
            self.__PATHS__.EXTERNAL,
            self.__PATHS__.BINDIR,
        ]:
            os.makedirs(i, exist_ok=True, mode=0o755)

        r = Redis(
            self.PACKAGE_NAME,
            self.OSNICK,
            self.ARCH,
            self.OSNAME,
            basedirname=self._basedirname,
        )
        r.prepare()
        for i in [
            "redis-server",
            "redis-benchmark",
            "redis-sentinel",
        ]:
            fname = os.path.join(self.__PATHS__.BINDIR, i)
            os.unlink(fname)
