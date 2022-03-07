from . import Recipe
from ..config import Config
from ..paths import Paths
from ..components.nodejs import NodeJS
import os
import shutil
from loguru import logger

class RedisInsightBase(Recipe):

    def __init__(self, osnick, arch="x86_64", osname="Linux"):
        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.__PATHS__ = Paths(self.PACKAGE_NAME, osnick, arch, osname)
        self.C = Config()
        
    @property
    def __package_base_args__(self) -> list:
        """Return base arguments for the package."""
        c = Config()
        return [
            "fpm",
            "-s dir",
            f"-C {self.__PATHS__.WORKDIR}",
            f"-n {c.get_key(self.PACKAGE_NAME)['product']}",
            f"--architecture {self.ARCH}",
            f"--vendor '{c.get_key('vendor')}'",
            f"--version {self.version}",
            f"--url '{c.get_key('url')}'",
            f"--license {c.get_key('license')}",
            f"--category server",
            f"--maintainer '{c.get_key('email')}'",
            f"--description '{c.get_key(self.PACKAGE_NAME)['description']}'",
            f"--directories /opt/redis-stack",
        ]

    def deb(self, fpmargs, build_number, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}-{build_number}.{distribution}.{self.ARCH}.deb"
        )
        fpmargs.append(f"--deb-user {self.C.get_key('product_user')}")
        fpmargs.append(f"--deb-group {self.C.get_key('product_group')}")
        fpmargs.append(f"--deb-dist {distribution}")
        fpmargs.append("-t deb")
        fpmargs.append(
            f"--after-install {os.path.join(self.__PATHS__.SCRIPTDIR, 'package', 'postinstall')}"
        )
        fpmargs.append(
            f"--after-remove {os.path.join(self.__PATHS__.SCRIPTDIR, 'package', 'postremove')}"
        )
        fpmargs.append(
            f"--before-remove {os.path.join(self.__PATHS__.SCRIPTDIR, 'package', 'preremove')}"
        )

        if not os.path.isdir(self.__PATHS__.SVCDIR):
            os.makedirs(self.__PATHS__.SVCDIR)

        for i in [
            "redisinsight.service",
        ]:
            shutil.copyfile(
                os.path.join(self.__PATHS__.SCRIPTDIR, "services", i),
                os.path.join(self.__PATHS__.SVCDIR, i),
            )
            fpmargs.append(f"--config-files {(os.path.join(self.__PATHS__.SVCDIR, i))}")

        return fpmargs

    def rpm(self, fpmargs, build_number, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}-{build_number}.{distribution}.{self.ARCH}.rpm"
        )
        fpmargs.append(f"--rpm-user {self.C.get_key('product_user')}")
        fpmargs.append(f"--rpm-group {self.C.get_key('product_group')}")
        fpmargs.append(f"--rpm-dist {distribution}")
        fpmargs.append("-t rpm")
        fpmargs.append(
            f"--after-install {os.path.join(self.__PATHS__.SCRIPTDIR, 'package', 'postinstall')}"
        )
        fpmargs.append(
            f"--after-remove {os.path.join(self.__PATHS__.SCRIPTDIR, 'package', 'postremove')}"
        )
        fpmargs.append(
            f"--before-remove {os.path.join(self.__PATHS__.SCRIPTDIR, 'package', 'preremove')}"
        )

        if not os.path.isdir(self.__PATHS__.SVCDIR):
            os.makedirs(self.__PATHS__.SVCDIR)

        for i in [
            "redisinsight.service",
        ]:
            shutil.copyfile(
                os.path.join(self.__PATHS__.SCRIPTDIR, "services", i),
                os.path.join(self.__PATHS__.SVCDIR, i),
            )
            fpmargs.append(f"--config-files {(os.path.join(self.__PATHS__.SVCDIR, i))}")
        return fpmargs

    def pacman(self, fpmargs, build_number, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}-{build_number}.{distribution}.{self.ARCH}.pacman"
        )
        fpmargs.append(
            f"--after-install {os.path.join(self.__PATHS__.SCRIPTDIR, 'package', 'postinstall')}"
        )
        fpmargs.append(
            f"--after-remove {os.path.join(self.__PATHS__.SCRIPTDIR, 'package', 'postremove')}"
        )
        fpmargs.append(
            f"--before-remove {os.path.join(self.__PATHS__.SCRIPTDIR, 'package', 'preremove')}"
        )
        fpmargs.append(f"--pacman-user {self.C.get_key('product_user')}")
        fpmargs.append(f"--pacman-group {self.C.get_key('product_group')}")
        fpmargs.append("--pacman-compression gz")
        fpmargs.append("-t pacman")

        if not os.path.isdir(self.__PATHS__.SVCDIR):
            os.makedirs(self.__PATHS__.SVCDIR)
        for i in [
            "redisinsight.service",
        ]:
            shutil.copyfile(
                os.path.join(self.__PATHS__.SCRIPTDIR, "services", i),
                os.path.join(self.__PATHS__.SVCDIR, i),
            )
            fpmargs.append(f"--config-files {(os.path.join(self.__PATHS__.SVCDIR, i))}")

        return fpmargs

    def osxpkg(self, fpmargs, build_number, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}-{build_number}.{distribution}.osxpkg"
        )
        fpmargs.append("-t osxpkg")
        return fpmargs

    def package(
        self,
        package_type: str = "deb",
        build_number: int = 1,
        distribution: str = "bionic",
    ):
        logger.info(f"Building {package_type} package")
        fpmargs = self.__package_base_args__
        fpmargs.append(f"--iteration {build_number}")

        if package_type == "deb":
            fpmargs = self.deb(fpmargs, build_number, distribution)

        elif package_type == "rpm":
            fpmargs = self.rpm(fpmargs, build_number, distribution)

        elif package_type == "osxpkg":
            fpmargs = self.osxpkg(fpmargs, build_number, distribution)

        elif package_type == "pacman":
            fpmargs = self.pacman()(fpmargs, build_number, distribution)
        else:
            raise AttributeError(f"{package_type} is an invalid package type")

        cmd = " ".join(fpmargs)
        logger.debug(f"Packaging: {cmd}")
        return os.system(cmd)

class RedisInsight(RedisInsightBase):
    """A recipe to build a redisinsight package from the native app"""

    PACKAGE_NAME = "redisinsight"
    
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
            
        from ..components.insight import RedisInsight as RI

 
        for i in [NodeJS, RI]:
            n = i(self.PACKAGE_NAME, self.OSNICK, self.ARCH, self.OSNAME)
            n.prepare()
    
class RedisInsightWeb(RedisInsightBase):
    """A recipe to build a redisinsight package for the web application"""

    PACKAGE_NAME = "redisinsight-web"
    
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
            
        from ..components.insight import RedisInsightWeb as RI

 
        for i in [NodeJS, RI]:
            n = i(self.PACKAGE_NAME, self.OSNICK, self.ARCH, self.OSNAME)
            n.prepare()
