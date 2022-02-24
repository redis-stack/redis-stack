from . import Recipe
from ..paths import Paths
from ..components.modules import Modules
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
        super()
        
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
            fpmargs.append("--depends libssl-dev")
            fpmargs.append("--depends libgomp1")  # redisgraph
            fpmargs.append(
                f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.C.get_key(self.PACKAGE_NAME)['version']}-{build_number}.{distribution}.{self.ARCH}.deb"
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
                # "redis-stack.service",
                "redis-stack-server.service",
            ]:
                shutil.copyfile(
                    os.path.join(self.__PATHS__.SCRIPTDIR, "services", i),
                    os.path.join(self.__PATHS__.SVCDIR, i),
                )
                fpmargs.append(
                    f"--config-files {(os.path.join(self.__PATHS__.SVCDIR, i))}"
                )

        elif package_type == "rpm":
            fpmargs.append("--depends openssl-devel")
            fpmargs.append("--depends jemalloc-devel")
            fpmargs.append(
                f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.C.get_key(self.PACKAGE_NAME)['version']}-{build_number}.{distribution}.{self.ARCH}.rpm"
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
                # "redis-stack.service",
                "redis-stack-server.service",
                # "redisinsight.service",
            ]:
                shutil.copyfile(
                    os.path.join(self.__PATHS__.SCRIPTDIR, "services", i),
                    os.path.join(self.__PATHS__.SVCDIR, i),
                )
                fpmargs.append(
                    f"--config-files {(os.path.join(self.__PATHS__.SVCDIR, i))}"
                )

        elif package_type == "osxpkg":
            fpmargs.append(
                f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.C.get_key(self.PACKAGE_NAME)['version']}-{build_number}.{distribution}.osxpkg"
            )
            fpmargs.append("-t osxpkg")
            
        elif package_type == "pacman":
            fpmargs.append(
                f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.C.get_key(self.PACKAGE_NAME)['version']}-{build_number}.{distribution}.{self.ARCH}.pacman"
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
            
        else:
            raise AttributeError(f"{package_type} is an invalid package type")

        cmd = " ".join(fpmargs)
        logger.debug(f"Packaging: {cmd}")
        return os.system(cmd)
