import os
import shutil
import subprocess
import tempfile
import re

import jinja2
from loguru import logger

from ..config import Config


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
            f"--license '{c.get_key('license')}'",
            "--category server",
            f"--maintainer '{c.get_key('email')}'",
            f"--description '{c.get_key(self.PACKAGE_NAME)['description']}'",
            "--directories '/opt/redis-stack'",
        ]

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
        fpmargs.append("--depends libssl-dev")
        fpmargs.append("--depends libgomp1")  # redisgraph
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.{self.ARCH}.deb"
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

    def rpm(self, fpmargs, distribution):
        fpmargs.append("--depends openssl-devel")
        fpmargs.append("--depends jemalloc-devel")
        fpmargs.append("--depends libgomp")
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.{self.ARCH}.rpm"
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

    def pacman(self, fpmargs, distribution):
        
        # replace the version, due to an awesome - archlinux packaging bug
        # we can't rely on the split in semver
        # so, if we have a non-master (or non fixed) release (i.e 6.2.4-v5)
        # we split accordingly, and reseed the version
        config = Config()
        ver = config.get_key("versions")[self.PACKAGE_NAME].split("-")
        if len(ver) != 0:
            for idx, v in enumerate(fpmargs):
                if v.find('--version') != -1:
                    break
            f = re.findall("[0-9]{1,3}", ver[1])
            fpmargs[idx] = f"--version {ver[0]}"
            fpmargs.append(f"--iteration {f[0]}")
        
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{self.ARCH}.pkg"
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
        fpmargs.append("--depends openssl")
        fpmargs.append("--depends gcc-libs")
        fpmargs.append(f"--pacman-user {self.C.get_key('product_user')}")
        fpmargs.append(f"--pacman-group {self.C.get_key('product_group')}")
        fpmargs.append("--pacman-compression xz")
        fpmargs.append("-t pacman")
        return fpmargs

    def osxpkg(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.{self.ARCH}.osxpkg"
        )
        fpmargs.append("-t osxpkg")
        return fpmargs

    def zip(self, fpmargs, distribution):

        # zipfiles really just include the root of the package
        fpmargs.remove(f"-C {self.__PATHS__.WORKDIR}")
        fpmargs.append(f"-C {self.__PATHS__.BASEDIR}")
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.{self.ARCH}.zip"
        )
        fpmargs.append("-t zip")
        return fpmargs

    def tar(self, fpmargs, distribution):

        # tar, like zip begins at the root of the package
        # fpm compresses the output only if it ends in .tar.gz
        fpmargs.remove(f"-C {self.__PATHS__.WORKDIR}")
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.{self.ARCH}.tar.gz"
        )
        fpmargs.append("-t tar")

        # the tarball, unlike a package requires a workdir name 'redis-stack-<version>'
        # since this is the expectation
        # we prepare that extra step here
        tartree = f"{self.__PATHS__.WORKDIR}-tar"
        tarbase = os.path.join(tartree, f"{self.PACKAGE_NAME}-{self.version}")
        shutil.rmtree(tartree, ignore_errors=True)
        shutil.copytree(self.__PATHS__.BASEDIR, tarbase)
        fpmargs.append(f"-C {tartree}")

        return fpmargs

    def snap(self, fpmargs, distribution):
        snap_grade = "stable"
        snap_confinement = "classic"

        # this can change, once we build focal for arm
        if self.ARCH == "arm64":
            snap_arch = "arm64"
            snap_base = "core18"
        else:
            snap_arch = "amd64"
            snap_base = "core20"

        vars = {
            "PRODUCT": self.C.get_key(self.PACKAGE_NAME)["product"],
            "VERSION": self.version,
            "SUMMARY": self.C.get_key(self.PACKAGE_NAME)["summary"],
            "DESCRIPTION": self.C.get_key(self.PACKAGE_NAME)["description"],
            "SNAP_GRADE": snap_grade,
            "SNAP_CONFINEMENT": snap_confinement,
            "SNAP_BASE": snap_base,
            "SNAP_ARCH": snap_arch,
            "basedir": self.__PATHS__.BASEDIR,
        }

        # generate the snapcraft.yaml from the template
        dest = tempfile.mktemp(suffix=".yaml", prefix="snapcraft")
        src = "snapcraft.j2"

        loader = jinja2.FileSystemLoader(self.__PATHS__.SCRIPTDIR)
        env = jinja2.Environment(loader=loader)
        tmpl = loader.load(name=src, environment=env)
        generated = tmpl.render(vars)
        with open(dest, "w+") as fp:
            fp.write(generated)

        fpmargs.append(f"-p {self.PACKAGE_NAME}-{self.version}.{self.ARCH}.snap")
        fpmargs.append(f"--snap-confinement {snap_confinement}")
        fpmargs.append(f"--snap-grade {snap_grade}")
        fpmargs.append(f"--snap-yaml {dest}")
        fpmargs.append("-t snap")
        return fpmargs

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
        else:
            raise AttributeError(f"{package_type} is an invalid package type")

        cmd = " ".join(fpmargs)
        logger.debug(f"Packaging: {cmd}")
        return os.system(cmd)
