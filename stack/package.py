#!/usr/bin/env python3

from abc import abstractclassmethod
import inspect
import os
import shutil
import requests
import jinja2
import tempfile
from loguru import logger
from stack.paths import Paths
from stack.components.modules import Modules
from stack.components.nodejs import NodeJS
from stack.components.insight import RedisInsight


# REDIS STACK PACKAGE RULES
PRODUCT = "redis-stack"
VENDOR = "Redis Inc"
VERSION = "1.0.0"
EMAIL = "Redis OSS <oss@redislabs.com>"
LICENSE = "MIT"
PRODUCT_USER = "nobody"
PRODUCT_GROUP = "nobody"

# TODO need to edit these
SUMMARY = "Some king od siummary, I too am a placeholder"
DESCRIPTION = "A placeholder for some sort of description"


class Package:
    def __init__(self, osnick, arch="x86_64", osname="Linux"):
        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.__PATHS__ = Paths(osnick, arch, osname)

    @property
    def __package_base_args__(self) -> list:
        """Return base arguments for the package."""
        return [
            "fpm",
            "-s dir",
            f"-C {self.__PATHS__.WORKDIR}",
            f"-n {PRODUCT}",
            "--provides redis",
            "--provides redis-server",
            f"--architecture {self.ARCH}",
            f"--vendor '{VENDOR}'",
            f"--version {VERSION}",
            f"--url 'https://redistack.io'",
            f"--license {LICENSE}",
            f"--category server",
            f"--maintainer '{EMAIL}'",
            f"--description '{DESCRIPTION}'",
        ]

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

        m = Modules(self.OSNICK, self.ARCH, self.OSNAME)
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

        for i in [NodeJS, RedisInsight]:
            n = i(self.OSNICK, self.ARCH, self.OSNAME)
            n.prepare()
            
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
                f"-p {PRODUCT}-{VERSION}-{build_number}.{distribution}.{self.ARCH}.deb"
            )
            fpmargs.append(f"--deb-user {PRODUCT_USER}")
            fpmargs.append(f"--deb-group {PRODUCT_GROUP}")
            fpmargs.append(f"--deb-dist {distribution}")
            fpmargs.append("-t deb")

            if not os.path.isdir(self.__PATHS__.SVCDIR):
                os.makedirs(self.__PATHS__.SVCDIR)
                
            for i in ['redis-stack.service', 'redis-stack-redis.service', 'redisinsight.service']:
                shutil.copyfile(
                    os.path.join(self.__PATHS__.SCRIPTDIR, i),
                    os.path.join(self.__PATHS__.SVCDIR, i),
                )
                fpmargs.append(
                    f"--config-files {(os.path.join(self.__PATHS__.SVCDIR, 'i'))}"
                )

        elif package_type == "rpm":
            fpmargs.append("--depends openssl-devel")
            fpmargs.append("--depends jemalloc-devel")
            fpmargs.append(
                f"-p {PRODUCT}-{VERSION}-{build_number}.{distribution}.{self.ARCH}.rpm"
            )
            fpmargs.append(f"--rpm-user {PRODUCT_USER}")
            fpmargs.append(f"--rpm-group {PRODUCT_GROUP}")
            fpmargs.append(f"--rpm-dist {distribution}")
            fpmargs.append("-t rpm")

            if not os.path.isdir(self.__PATHS__.SVCDIR):
                os.makedirs(self.__PATHS__.SVCDIR)
                
            for i in ['redis-stack.service', 'redis-stack-redis.service', 'redisinsight.service']:
                shutil.copyfile(os.path.join(self.__PATHS__.SCRIPTDIR, i),
                    os.path.join(self.__PATHS__.SVCDIR, i),
                )
                fpmargs.append(
                    f"--config-files {(os.path.join(self.__PATHS__.SVCDIR, 'i'))}"
                )

        elif package_type == "osxpkg":
            fpmargs.append(
                f"-p {PRODUCT}-{VERSION}-{build_number}.{distribution}.{self.ARCH}.osxpkg"
            )
            fpmargs.append("-t osxpkg")
        elif package_type == "pacman":
            fpmargs.append(f"-p {PRODUCT}-{VERSION}-{build_number}.{self.ARCH}.pacman")
            fpmargs.append(f"--pacman-user {PRODUCT_USER}")
            fpmargs.append(f"--pacman-group {PRODUCT_GROUP}")
            fpmargs.append("--pacman-compression gz")
            fpmargs.append("-t pacman")
        elif package_type == "snap":
            snap_grade = "stable"
            snap_confinement = "classic"

            vars = {
                "PRODUCT": PRODUCT,
                "VERSION": VERSION,
                "SUMMARY": SUMMARY,
                "DESCRIPTION": DESCRIPTION,
                "SNAP_GRADE": snap_grade,
                "SNAP_CONFINEMENT": snap_confinement,
            }

            # generate the snapcraft.yaml from the template
            dest = os.path.join(self.__PATHS__.HERE, "snapcraft.yaml")
            dest = tempfile.mktemp(suffix=".yaml", prefix="snapcraft")
            src = "snapcraft.j2"

            loader = jinja2.FileSystemLoader(self.__PATHS__.HERE)
            env = jinja2.Environment(loader=loader)
            tmpl = loader.load(name=src, environment=env)
            generated = tmpl.render(vars)
            with open(dest, "w+") as fp:
                fp.write(generated)

            fpmargs.append(f"-p {PRODUCT}-{VERSION}-{build_number}.{self.ARCH}.snap")
            fpmargs.append(f"--snap-confinement {snap_confinement}")
            fpmargs.append(f"--snap-grade {snap_grade}")
            fpmargs.append(f"--snap-yaml {dest}")
            fpmargs.append("-t snap")

        else:
            raise AttributeError(f"{package_type} is an invalid package type")

        cmd = " ".join(fpmargs)
        logger.debug(f"Packaging: {cmd}")
        return os.system(cmd)
