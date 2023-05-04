#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import os
import subprocess
from abc import ABC
from typing import Union

from loguru import logger

from ..config import Config


class AbstractRecipe(ABC):
    """The abstract base for packaging recipes"""

    def prepackage(
        self,
        binary_dir: Union[str, None],
        ignore: bool = False,
        version_override: str = None,
    ):
        """Describes the steps to perform prior to packaging"""
        raise NotImplementedError("implement this in child classes")

    @property
    def __package_base_args__(self) -> list:
        """Return base arguments for the package."""
        raise NotImplementedError("implement this in child classes")

    @property
    def version(self):
        r = subprocess.run(
            ["git", "branch", "--show-current"], stdout=subprocess.PIPE, text=True
        )
        branch = r.stdout.strip()
        if branch in ["master", "main"]:
            return "99.99.99"

        # get the current tag
        config = Config()
        return config.get_key("versions")[self.PACKAGE_NAME]

    def deb(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.{self.ARCH}.deb"
        )
        fpmargs.append(f"--deb-user {self.C.get_key('product_user')}")
        fpmargs.append(f"--deb-group {self.C.get_key('product_group')}")
        fpmargs.append(f"--deb-dist {distribution}")
        fpmargs.append("-t deb")

        return fpmargs

    def rpm(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.{self.ARCH}.rpm"
        )
        fpmargs.append(f"--rpm-user {self.C.get_key('product_user')}")
        fpmargs.append(f"--rpm-group {self.C.get_key('product_group')}")
        fpmargs.append(f"--rpm-dist {distribution}")
        fpmargs.append("-t rpm")
        return fpmargs

    def pacman(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.{self.ARCH}.pacman"
        )
        fpmargs.append(f"--pacman-user {self.C.get_key('product_user')}")
        fpmargs.append(f"--pacman-group {self.C.get_key('product_group')}")
        fpmargs.append("--pacman-compression gz")
        fpmargs.append("-t pacman")

        return fpmargs

    def osxpkg(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.osxpkg"
        )
        fpmargs.append("-t osxpkg")
        return fpmargs

    def zip(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.zip"
        )
        fpmargs.append("-t zip")
        return fpmargs

    def tar(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.tar.gz"
        )
        fpmargs.append("-t tar")
        return fpmargs

    def snap(self, fpmargs, distribution):
        raise NotImplementedError("requires a custom implementation in subclasses")

    def package(
        self,
        package_type: str = "deb",
        distribution: str = "bionic",
    ):
        logger.info(f"Building {package_type} package")
        fpmargs = self.__package_base_args__

        if package_type == "deb":
            fpmargs = self.deb(fpmargs, distribution)

        elif package_type == "rpm":
            fpmargs = self.rpm(fpmargs, distribution)

        elif package_type == "osxpkg":
            fpmargs = self.osxpkg(fpmargs, distribution)

        elif package_type == "pkg":
            fpmargs = self.pacman(fpmargs, distribution)
        elif package_type == "zip":
            fpmargs = self.zip(fpmargs, distribution)
        elif package_type == "tar":
            fpmargs = self.tar(fpmargs, distribution)
        elif package_type == "snap":
            fpmargs = self.snap(fpmargs, distribution)
        elif package_type == "pacman":
            fpmargs = self.pacman(fpmargs, distribution)
        else:
            raise AttributeError(f"{package_type} is an invalid package type")

        cmd = " ".join(fpmargs)
        logger.debug(f"Packaging: {cmd}")
        return os.system(cmd)
