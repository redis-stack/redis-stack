#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import os
import re
import shutil
import tempfile
from typing import Union

import jinja2
import requests
from loguru import logger

from ..components.modules import Modules
from ..components.redis import Redis
from ..config import Config
from ..paths import Paths
from . import AbstractRecipe


class RedisStackBase(AbstractRecipe):
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
        if len(ver) != 1:
            for idx, v in enumerate(fpmargs):
                if v.find("--version") != -1:
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


class RedisStackServer(RedisStackBase):
    """A recipe, to build the redis-stack-server package"""

    PACKAGE_NAME = "redis-stack"

    def __init__(self, osnick, arch="x86_64", osname="Linux"):
        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.__PATHS__ = Paths(self.PACKAGE_NAME, osnick, arch, osname)
        self.C = Config()

    def prepackage(
        self,
        binary_dir: Union[str, None],
        ignore: bool = False,
        version_override: str = None,
    ):
        for i in [
            self.__PATHS__.EXTERNAL,
            self.__PATHS__.DESTDIR,
            self.__PATHS__.LIBDIR,
            self.__PATHS__.BINDIR,
            self.__PATHS__.SHAREDIR,
            self.__PATHS__.BASEETCDIR,
            self.__PATHS__.BASEVARDBDIR,
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

        # per os
        logger.debug("Copying redis-stack-server script")
        stackdest = os.path.join(self.__PATHS__.BINDIR, "redis-stack-server")
        shutil.copyfile(
            os.path.join(self.__PATHS__.SCRIPTDIR, "scripts", "redis-stack-server"),
            stackdest,
        )
        os.chmod(stackdest, mode=0o755)

        if binary_dir is not None:
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

        # linux only - copy to /etc
        if self.OSNAME == "Linux":
            confdest = os.path.join(self.__PATHS__.BASEETCDIR, "redis-stack.conf")
            shutil.copy(
                os.path.join(
                    self.__PATHS__.SCRIPTDIR, "conf", "redis-stack-service.conf"
                ),
                confdest,
            )
            os.chmod(confdest, mode=0o640)

        # copy configuration files
        shutil.copytree(
            os.path.join(self.__PATHS__.SCRIPTDIR, "conf"),
            self.__PATHS__.ETCDIR,
            dirs_exist_ok=True,
        )

        # license files
        shutil.copytree(
            os.path.join(self.__PATHS__.SCRIPTDIR, "licenses"),
            os.path.join(self.__PATHS__.SHAREDIR),
            dirs_exist_ok=True,
        )


# HISTORIC this is a placeholder for the package depending on packages, in Linux
# This is not a real package - unless it comes back to life, again.
class RedisStack(RedisStackBase):
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
