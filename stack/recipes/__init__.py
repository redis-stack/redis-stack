import abc
from ..config import Config
from loguru import logger
import os
import shutil
from semver.version import Version
import subprocess


class Recipe(object):
    """A base class for building packages"""

    @property
    def __package_base_args__(self) -> list:
        """Return base arguments for the package."""
        c = Config()
        return [
            "fpm",
            "-s dir",
            f"-C {self.__PATHS__.WORKDIR}",
            f"-n {c.get_key(self.PACKAGE_NAME)['product']}",
            "--provides redis-stack",
            f"--architecture {self.ARCH}",
            f"--vendor '{c.get_key('vendor')}'",
            f"--version {self.version}",
            f"--url '{c.get_key('url')}'",
            f"--license {c.get_key('license')}",
            f"--category server",
            f"--maintainer '{c.get_key('email')}'",
            f"--description '{c.get_key(self.PACKAGE_NAME)['description']}'",
            f"--directories '/opt/redis-stack'",
        ]

    @property
    def version(self):
        r = subprocess.run(["git", "branch", "--show-current"], stdout=subprocess.PIPE, text=True)
        branch = r.stdout.strip()
        if branch in ["master", "main"]:
            return "99.99.99"
        
        # get the current tag
        tagcmd = ["git", "tag", "--points-at", "HEAD"]
        r = subprocess.run(tagcmd, stdout=subprocess.PIPE, text=True)
        version = r.stdout.strip().replace('v', '')
        if version != "":
            return version
       
        # any branch - just takes the version
        config = Config()
        return config.get_key(self.PACKAGE_NAME)['version']

    def deb(self, fpmargs, build_number, distribution):
        fpmargs.append("--depends libssl-dev")
        fpmargs.append("--depends libgomp1")  # redisgraph
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
            # "redis-stack.service",
            "redis-stack-server.service",
        ]:
            shutil.copyfile(
                os.path.join(self.__PATHS__.SCRIPTDIR, "services", i),
                os.path.join(self.__PATHS__.SVCDIR, i),
            )
            fpmargs.append(f"--config-files {(os.path.join(self.__PATHS__.SVCDIR, i))}")

        return fpmargs

    def rpm(self, fpmargs, build_number, distribution):
        fpmargs.append("--depends openssl-devel")
        fpmargs.append("--depends jemalloc-devel")
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
            # "redis-stack.service",
            "redis-stack-server.service",
            # "redisinsight.service",
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
        return fpmargs

    def osxpkg(self, fpmargs, build_number, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}-{build_number}.{distribution}.osxpkg"
        )
        fpmargs.append("-t osxpkg")
        return fpmargs
    
    def zip(self, fpmargs, build_number, distribution):
        
        # zipfiles really just include the root of the package
        fpmargs.remove(f"-C {self.__PATHS__.WORKDIR}")
        fpmargs.append(f"-C {self.__PATHS__.BASEDIR}")
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}-{build_number}.{distribution}.zip"
        )
        fpmargs.append("-t zip")
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
            fpmargs = self.pacman(fpmargs, build_number, distribution)
        elif package_type == "zip":
            fpmargs = self.zip(fpmargs, build_number, distribution)
        else:
            raise AttributeError(f"{package_type} is an invalid package type")

        cmd = " ".join(fpmargs)
        logger.debug(f"Packaging: {cmd}")
        return os.system(cmd)
