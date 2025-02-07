#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import os
import shutil

# import zipfile
import tarfile
import urllib
from typing import Union

from loguru import logger

from ..config import Config
from ..paths import Paths
from .get import get_stream_and_store


class RedisInsightBase(object):
    def __init__(
        self, package: str, osnick: str, arch: str = "x86_64", osname: str = "Linux"
    ):

        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.__PATHS__ = Paths(package, osnick, arch, osname)
        self.C = Config()

    def generate_url(self, version):
        if self.OSNAME == "macos":
            osname = "darwin"
        else:
            osname = self.OSNAME.lower()
        if self.ARCH == "x86_64":
            arch = "x64"
        else:
            arch = self.ARCH

        url_base_override = self.C.get_key("redisinsight-url-override")
        if url_base_override is not None:
            return urllib.parse.urljoin(
                f"{url_base_override}",
                f"Redis-Insight-{self.APPTYPE}.{osname}-{arch}.tar.gz",
            )

        return f"https://s3.amazonaws.com/redisinsight.download/public/releases/{version}/{self.APPTYPE}/RedisInsight-{self.APPTYPE}-{osname}.{arch}.tar.gz"

    def _fetch_and_unzip(self, url: str, destfile: str):
        logger.debug(f"Package URL: {url}")

        if not os.path.isfile(destfile):
            get_stream_and_store(url, destfile)

        # logger.debug(f"Unzipping {destfile} and storing in {self.__PATHS__.DESTDIR}")
        # with zipfile.ZipFile(destfile, "r") as zp:
        #     zp.extractall(path=os.path.join(self.__PATHS__.DESTDIR, "redisinsight"))
        logger.debug(f"Untarring {destfile} and storing in {self.__PATHS__.DESTDIR}")
        with tarfile.open(destfile) as f:
            f.extractall(path=os.path.join(self.__PATHS__.DESTDIR, "redisinsight"))

    def prepare(self, version: Union[str, None] = None):
        if version is None:
            version = self.C.get_key("versions")["redisinsight"]
        logger.info("Fetching redisinsight")
        url = self.generate_url(version)
        destfile = os.path.join(
            self.__PATHS__.EXTERNAL,
            f"redisinsight-{self.OSNAME}-{self.OSNICK}-{self.ARCH}-{self.APPTYPE}.zip",
        )
        if os.path.isfile(destfile):
            return
        pkg_unzip_dest = os.path.join(self.__PATHS__.DESTDIR, "redisinsight")
        self._fetch_and_unzip(url, destfile)  # , pkg_unzip_dest)
        shutil.copytree(
            pkg_unzip_dest, os.path.join(self.__PATHS__.SHAREDIR, "redisinsight")
        )


class RedisInsight(RedisInsightBase):

    APPTYPE = "app"


class RedisInsightWeb(RedisInsightBase):

    APPTYPE = "web"
