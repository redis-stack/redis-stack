#!/usr/bin/env python3

from abc import abstractclassmethod
from optparse import OptionParser
import inspect
import os
import sys
import shutil
import zipfile
import urllib
import requests
import jinja2
import tempfile
from loguru import logger
import semantic_version


HERE = os.path.abspath(os.path.dirname(__file__))
EXTERNAL = os.path.join(HERE, "deps", "external")
DISTDIR = os.path.join(HERE, "dist")
WORKDIR = os.path.join(HERE, "build")
SCRIPTDIR = os.path.join(HERE, "scripts")

MODULE_VERSIONS = {
    "REJSON": "2.0.6",
    "REDISGRAPH": "2.8.7",
    "REDISTIMESERIES": "1.6.7",
    "REDISEARCH": "2.2.7",
    "REDISGEARS": "1.2.2",
    "REDISBLOOM": "2.2.9",
    "REDISAI": None,
    "REDISINSIGHT": None,
}
AWS_S3_BUCKET = "redismodules.s3.amazonaws.com"

# REDIS STACK PACKAGE RULES
PRODUCT = "redis-stack"
VENDOR = "Redis Inc"
VERSION = "1.0.0"
EMAIL = "Redis OSS <oss@redislabs.com>"
LICENSE = "MIT"
PRODUCT_USER = "redis"
PRODUCT_GROUP = "redis"

# TODO need to edit these
SUMMARY = "Some king od siummary, I too am a placeholder"
DESCRIPTION = "A placeholder for some sort of description"


class Assemble:
    def __init__(self, osnick, arch="x86_64", osname="Linux"):
        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname

        self.BASEDIR = os.path.join(self.__workdir__, "opt", PRODUCT)
        self.USRBINDIR = os.path.join(self.__workdir__, "usr", "bin")
        self.LIBDIR = os.path.join(self.BASEDIR, "lib")
        self.BINDIR = os.path.join(self.BASEDIR, "bin")
        self.ETCDIR = os.path.join(self.BASEDIR, "etc")
        self.SVCDIR = os.path.join(self.ETCDIR, "systemd", "system")
        self.CONFDIR = os.path.join(self.ETCDIR, PRODUCT)

    @property
    def __destdir__(self) -> str:
        """The name of the destination directory for our intermediate files"""
        return os.path.join(EXTERNAL, f"{self.OSNAME}-{self.OSNICK}-{self.ARCH}")

    @property
    def __workdir__(self) -> str:
        """The working directory for package assemble"""
        return os.path.join(WORKDIR, f"{self.OSNAME}-{self.OSNICK}-{self.ARCH}")

    @property
    def __package_base_args__(self) -> list:
        """Return base arguments for the package."""
        return [
            "fpm",
            "-s dir",
            f"-C {self.__workdir__}",
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

    def generate_url(self, module: str, version: str):
        """Assuming the module follows the standard, return the URL from
        which to grab it"""
        try:
            semantic_version.Version(version)
            return urllib.parse.urljoin(
                f"https://{AWS_S3_BUCKET}",
                f"{module}/{module}.{self.OSNAME}-{self.OSNICK}-{self.ARCH}.{version}.zip",
            )
        except ValueError:
            return urllib.parse.urljoin(
                f"https://{AWS_S3_BUCKET}",
                f"{module}/snapshots/{module}.{self.OSNAME}-{self.OSNICK}-{self.ARCH}.{version}.zip",
            )

    def rejson(self, version: str = MODULE_VERSIONS["REJSON"]):
        """rejson specific fetch"""
        logger.info("Fetching rejson")
        destfile = os.path.join(
            EXTERNAL, f"rejson-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip"
        )
        url = self.generate_url("rejson", version)
        self._fetch_and_unzip(url, destfile)
        shutil.copyfile(
            os.path.join(self.__destdir__, "rejson.so"),
            os.path.join(self.LIBDIR, "rejson.so"),
        )

    def redisgraph(self, version: str = MODULE_VERSIONS["REDISGRAPH"]):
        """redisgraph specific fetch"""
        logger.info("Fetching redisgraph")
        destfile = os.path.join(
            EXTERNAL, f"redisgraph-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip"
        )
        url = self.generate_url("redisgraph", version)
        self._fetch_and_unzip(url, destfile)
        shutil.copyfile(
            os.path.join(self.__destdir__, "redisgraph.so"),
            os.path.join(self.LIBDIR, "redisgraph.so"),
        )

    def redisearch(self, version: str = MODULE_VERSIONS["REDISEARCH"]):
        """redisearch specific fetch"""
        logger.info("Fetching redisearch")
        destfile = os.path.join(
            EXTERNAL, f"redisearch-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip"
        )
        url = self.generate_url("redisearch", version)
        self._fetch_and_unzip(url, destfile)
        shutil.copyfile(
            os.path.join(self.__destdir__, "module-enterprise.so"),
            os.path.join(self.LIBDIR, "redisearch.so"),
        )

    def redistimeseries(self, version: str = MODULE_VERSIONS["REDISTIMESERIES"]):
        """redistimeseries specific fetch"""
        logger.info("Fetching redistimeseries")
        destfile = os.path.join(
            EXTERNAL, f"redistimeseries-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip"
        )
        url = self.generate_url("redistimeseries", version)
        self._fetch_and_unzip(url, destfile)
        shutil.copyfile(
            os.path.join(self.__destdir__, "redistimeseries.so"),
            os.path.join(self.LIBDIR, "redistimeseries.so"),
        )

    # FUTURE include in the future, when gears is part of redis stack
    # def redisgears(self, version: str = MODULE_VERSIONS["REDISGEARS"]):
    #     """gears specific fetch"""
    #     logger.info("Fetching redisgears")
    #     destfile = os.path.join(
    #         EXTERNAL, f"redisgears-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip"
    #     )
    #     url = self.generate_url("redisgears", version)
    #     self._fetch_and_unzip(url, destfile)
    #     shutil.copyfile(
    #         os.path.join(self.__destdir__, "redisgears.so"),
    #         os.path.join(self.LIBDIR, "redisgears.so"),
    #     )

    def redisbloom(self, version: str = MODULE_VERSIONS["REDISBLOOM"]):
        """bloom specific fetch"""
        logger.info("Fetching redisbloom")
        destfile = os.path.join(
            EXTERNAL, f"redisbloom-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip"
        )
        url = self.generate_url("redisbloom", version)
        self._fetch_and_unzip(url, destfile)
        shutil.copyfile(
            os.path.join(self.__destdir__, "redisbloom.so"),
            os.path.join(self.LIBDIR, "redisbloom.so"),
        )

        # logger.info("Fetching redisbloom")

    # def redisai(self, version: str = MODULE_VERSIONS["REDISAI"]):
    #     """bloom specific fetch"""
    #     # logger.info("Fetching redisai")
    #     pass

    def redisinsight(self, version: str = MODULE_VERSIONS["REDISINSIGHT"]):
        """bloom specific fetch"""
        # logger.info("Fetching redisinsight")
        URLS = {
            "macos": "https://download.redisinsight.redis.com/latest/RedisInsight-preview-mac-x64.dmg",
            "windows": "https://download.redisinsight.redis.com/latest/RedisInsight-preview-win-installer.exe",
            "Linux": "https://d3fyopse48vfpi.cloudfront.net/latest/redisinsight-linux64",
        }
        pass

    def _fetch_and_unzip(self, url: str, destfile: str):

        logger.debug(f"Package URL: {url}")

        if os.path.isfile(destfile):
            return

        r = requests.get(url, stream=True)
        if r.status_code > 204:
            logger.error(f"{url} could not be retrieved")
            raise requests.HTTPError
        open(destfile, "wb").write(r.content)

        logger.debug(f"Unzipping {destfile} and storing in {self.__destdir__}")
        with zipfile.ZipFile(destfile, "r") as zp:
            zp.extractall(self.__destdir__)

    def prepackage(self, binary_dir: str, ignore: bool = False, version_override: str=None):
        for i in [EXTERNAL, self.__destdir__, self.LIBDIR, self.BINDIR, self.USRBINDIR]:
            os.makedirs(i, exist_ok=True, mode=0o755)

        for i in [
            self.redisearch,
            self.redisgraph,
            self.redistimeseries,
            self.rejson,
            # self.redisbloom,
            # self.redisinsight,
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
            dest = os.path.join(self.BINDIR, i)
            shutil.copy2(os.path.join(binary_dir, i), dest)
            os.chmod(dest, mode=0o755)

            # copy configuration files
            shutil.copytree(
                os.path.join(SCRIPTDIR, "conf"), self.CONFDIR, dirs_exist_ok=True
            )

        # symlink redis-stack to the target
        # TODO change to redis-stack once we build a redis-stack binary
        os.symlink(
            os.path.join(self.BINDIR, "redis-server"),
            os.path.join(self.USRBINDIR, "redis-stack"),
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
            fpmargs.append(
                f"-p {PRODUCT}-{VERSION}-{build_number}.{distribution}.{self.ARCH}.deb"
            )
            fpmargs.append(f"--deb-user {PRODUCT_USER}")
            fpmargs.append(f"--deb-group {PRODUCT_GROUP}")
            fpmargs.append(f"--deb-dist {distribution}")
            fpmargs.append("-t deb")

            if not os.path.isdir(self.SVCDIR):
                os.makedirs(self.SVCDIR)
            shutil.copyfile(
                os.path.join(SCRIPTDIR, "redis-stack.service"),
                os.path.join(self.SVCDIR, "redis-stack.service"),
            )
            fpmargs.append(
                f"--config-files {(os.path.join(self.SVCDIR, 'redis-stack.service'))}"
            )

        elif package_type == "rpm":
            fpmargs.append(
                f"-p {PRODUCT}-{VERSION}-{build_number}.{distribution}.{self.ARCH}.rpm"
            )
            fpmargs.append(f"--rpm-user {PRODUCT_USER}")
            fpmargs.append(f"--rpm-group {PRODUCT_GROUP}")
            fpmargs.append(f"--rpm-dist {distribution}")
            fpmargs.append("-t rpm")

            if not os.path.isdir(self.SVCDIR):
                os.makedirs(self.SVCDIR)
            shutil.copyfile(
                os.path.join(SCRIPTDIR, "redis-stack.service"),
                os.path.join(self.SVCDIR, "redis-stack.service"),
            )
            fpmargs.append(
                f"--config-files {(os.path.join(self.SVCDIR, 'redis-stack.service'))}"
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
            dest = os.path.join(HERE, "snapcraft.yaml")
            dest = tempfile.mktemp(suffix=".yaml", prefix="snapcraft")
            src = "snapcraft.j2"

            loader = jinja2.FileSystemLoader(HERE)
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


if __name__ == "__main__":
    p = OptionParser()

    # package arguments
    p.add_option(
        "-o",
        "--osname",
        dest="OSNAME",
        help="Operating System (eg: Linux)",
        default="Linux",
    )
    p.add_option(
        "-s",
        "--osnick",
        dest="OSNICK",
        help="OSNICK internally used for binary naming",
        default="ubuntu18.04",
    )
    p.add_option(
        "-d", "--distribution", dest="DIST", help="Distribution name", default="bionic"
    )
    p.add_option(
        "-r",
        "--redis-binaries",
        dest="REDISBIN",
        help="Path to redis binaries",
        default=os.path.join(HERE, "redis", "src"),
        metavar="DIR",
    )
    p.add_option(
        "-a", "--arch", dest="ARCH", help="Dependency architecture", default="x86_64"
    )
    p.add_option("-v", "--variant", dest="VARIANT", help="[Optional] package variant")
    p.add_option(
        "-V",
        "--version-override",
        dest="VERSION_OVERRIDE",
        help="[Optional] Version with which to override all package versions",
    )
    p.add_option(
        "-b",
        "--build-number",
        dest="BUILD_NUMBER",
        help="[optional] build number",
        metavar=int,
        default=1,
    )
    p.add_option(
        "-p",
        "--package-type",
        dest="TARGET",
        help="Target package type (eg dpkg)",
        default="deb",
        type="choice",
        choices=["rpm", "deb", "osxpkg", "pacman", "snap"],
    )

    # run time argumetns
    p.add_option(
        "-S",
        "--skip",
        type="choice",
        dest="SKIP",
        choices=["fetch", "package"],
        help="[Optional] skip either fetch or package action",
    )
    p.add_option(
        "-I",
        "--ignore-missing",
        dest="IGNORE",
        action="store_true",
        default=False,
        help="[Optional] ignore missing package, but log",
    )

    p.add_option(
        "-x",
        "--debug",
        action="store_true",
        default=False,
        dest="DEBUG",
        help="Enable debug logs",
    )
    opts, args = p.parse_args()

    if opts.REDISBIN is None or not os.path.isdir(opts.REDISBIN):
        sys.stderr.write("Path to redis binaries does not exist. \n")
        sys.exit(3)

    if not opts.VARIANT:
        opts.VARIANT = f"{opts.OSNICK}-{opts.ARCH}"

    # default to info logging
    logger.remove()
    if opts.DEBUG is True:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="INFO")

    a = Assemble(opts.OSNICK, opts.ARCH, opts.OSNAME)

    if opts.SKIP is None or opts.SKIP != "fetch":
        a.prepackage(opts.REDISBIN, opts.IGNORE, opts.VERSION_OVERRIDE)

    if opts.SKIP is None or opts.SKIP != "package":
        sys.exit(a.package(opts.TARGET, opts.BUILD_NUMBER, opts.DIST))
