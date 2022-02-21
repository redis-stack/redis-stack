import semantic_version
from loguru import logger
import zipfile
import requests
import shutil
import urllib
import os
from ..paths import Paths


class Modules(object):
    """Helper class for handling redis modules"""

    AWS_S3_BUCKET = "redismodules.s3.amazonaws.com"
    MODULE_VERSIONS = {
        "REJSON": "2.0.6",
        "REDISGRAPH": "2.8.8",
        "REDISTIMESERIES": "1.6.7",
        "REDISEARCH": "2.4.0",
        "REDISGEARS": "1.2.2",
        "REDISBLOOM": "2.2.12",
        "REDISAI": None,
    }

    def __init__(self, osnick: str, arch: str = "x86_64", osname: str = "Linux"):
        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.__PATHS__ = Paths(osnick, arch, osname)

    def generate_url(self, module: str, version: str):
        """Assuming the module follows the standard, return the URL from
        which to grab it"""
        try:
            semantic_version.Version(version)
            return urllib.parse.urljoin(
                f"https://{self.AWS_S3_BUCKET}",
                f"{module}/{module}.{self.OSNAME}-{self.OSNICK}-{self.ARCH}.{version}.zip",
            )
        except ValueError:
            return urllib.parse.urljoin(
                f"https://{self.AWS_S3_BUCKET}",
                f"{module}/snapshots/{module}.{self.OSNAME}-{self.OSNICK}-{self.ARCH}.{version}.zip",
            )

    def rejson(self, version: str = MODULE_VERSIONS["REJSON"]):
        """rejson specific fetch"""
        logger.info("Fetching rejson")
        destfile = os.path.join(
            self.__PATHS__.EXTERNAL,
            f"rejson-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip",
        )
        url = self.generate_url("rejson", version)
        self._fetch_and_unzip(url, destfile)
        shutil.copyfile(
            os.path.join(self.__PATHS__.DESTDIR, "rejson.so"),
            os.path.join(self.__PATHS__.LIBDIR, "rejson.so"),
        )
        os.chmod(os.path.join(self.__PATHS__.LIBDIR, "rejson.so"), mode=0o755)

    def redisgraph(self, version: str = MODULE_VERSIONS["REDISGRAPH"]):
        """redisgraph specific fetch"""
        logger.info("Fetching redisgraph")
        destfile = os.path.join(
            self.__PATHS__.EXTERNAL,
            f"redisgraph-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip",
        )
        url = self.generate_url("redisgraph", version)
        self._fetch_and_unzip(url, destfile)
        shutil.copyfile(
            os.path.join(self.__PATHS__.DESTDIR, "redisgraph.so"),
            os.path.join(self.__PATHS__.LIBDIR, "redisgraph.so"),
        )
        os.chmod(os.path.join(self.__PATHS__.LIBDIR, "redisgraph.so"), mode=0o755)

    def redisearch(self, version: str = MODULE_VERSIONS["REDISEARCH"]):
        """redisearch specific fetch"""
        logger.info("Fetching redisearch")
        destfile = os.path.join(
            self.__PATHS__.EXTERNAL,
            f"redisearch-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip",
        )
        url = f"https://{self.AWS_S3_BUCKET}/redisearch-oss/redisearch-oss.{self.OSNAME}-{self.OSNICK}-{self.ARCH}.{version}.zip"
        self._fetch_and_unzip(url, destfile)
        shutil.copyfile(
            os.path.join(self.__PATHS__.DESTDIR, "redisearch.so"),
            os.path.join(self.__PATHS__.LIBDIR, "redisearch.so"),
        )
        os.chmod(os.path.join(self.__PATHS__.LIBDIR, "redisearch.so"), mode=0o755)

    def redistimeseries(self, version: str = MODULE_VERSIONS["REDISTIMESERIES"]):
        """redistimeseries specific fetch"""
        logger.info("Fetching redistimeseries")
        destfile = os.path.join(
            self.__PATHS__.EXTERNAL,
            f"redistimeseries-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip",
        )
        url = self.generate_url("redistimeseries", version)
        self._fetch_and_unzip(url, destfile)
        shutil.copyfile(
            os.path.join(self.__PATHS__.DESTDIR, "redistimeseries.so"),
            os.path.join(self.__PATHS__.LIBDIR, "redistimeseries.so"),
        )
        os.chmod(os.path.join(self.__PATHS__.LIBDIR, "redistimeseries.so"), mode=0o755)

    def redisbloom(self, version: str = MODULE_VERSIONS["REDISBLOOM"]):
        """bloom specific fetch"""
        logger.info("Fetching redisbloom")
        destfile = os.path.join(
            self.__PATHS__.EXTERNAL,
            f"redisbloom-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip",
        )
        url = self.generate_url("redisbloom", version)
        self._fetch_and_unzip(url, destfile)
        shutil.copyfile(
            os.path.join(self.__PATHS__.DESTDIR, "redisbloom.so"),
            os.path.join(self.__PATHS__.LIBDIR, "redisbloom.so"),
        )
        os.chmod(os.path.join(self.__PATHS__.LIBDIR, "redisbloom.so"), mode=0o755)

    def _fetch_and_unzip(self, url: str, destfile: str, custom_dest: str = None):

        logger.debug(f"Package URL: {url}")

        if os.path.isfile(destfile):
            return

        r = requests.get(url, stream=True)
        if r.status_code > 204:
            logger.error(f"{url} could not be retrieved")
            raise requests.HTTPError
        open(destfile, "wb").write(r.content)

        if custom_dest is None:
            dest = self.__PATHS__.DESTDIR
        else:
            dest = custom_dest

        logger.debug(f"Unzipping {destfile} and storing in {self.__PATHS__.DESTDIR}")
        with zipfile.ZipFile(destfile, "r") as zp:
            zp.extractall(dest)

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
    #         os.path.join(self.DESTDIR, "redisgears.so"),
    #         os.path.join(self.LIBDIR, "redisgears.so"),
    #     )

    # logger.info("Fetching redisbloom")

    # def redisai(self, version: str = MODULE_VERSIONS["REDISAI"]):
    #     """bloom specific fetch"""
    #     # logger.info("Fetching redisai")
    #     pass
