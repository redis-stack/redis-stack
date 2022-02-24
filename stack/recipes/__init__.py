import abc
from ..config import Config
from loguru import logger

class Recipe(object):
    
    @abc.abstractmethod
    def prepackage(self):
        raise NotImplementedError("To be implemented in child classes.")
    
    @abc.abstractmethod
    def package(
        self,
        package_type: str = "deb",
        build_number: int = 1,
        distribution: str = "bionic",
    ):
        raise NotImplementedError("To be implemented in child classes.")
    
    @property
    def __package_base_args__(self) -> list:
        """Return base arguments for the package."""
        c = Config()
        return [
            "fpm",
            "-s dir",
            f"-C {self.__PATHS__.WORKDIR}",
            f"-n {c.get_key(self.PACKAGE_NAME)['product']}",
            "--provides redis",
            "--provides redis-server",
            f"--architecture {self.ARCH}",
            f"--vendor '{c.get_key('vendor')}'",
            f"--version {c.get_key(self.PACKAGE_NAME)['version']}",
            f"--url '{c.get_key('url')}'",
            f"--license {c.get_key('license')}",
            f"--category server",
            f"--maintainer '{c.get_key('email')}'",
            f"--description '{c.get_key(self.PACKAGE_NAME)['description']}'",
            f"--directories '/opt/redis-stack'",
        ]