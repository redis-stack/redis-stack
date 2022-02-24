import os
import shutil
import zipfile
from typing import Union

import requests
from loguru import logger

from ..config import Config
from ..paths import Paths


class RedisInsight(object):
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
            osname = "Mac"
        else:
            osname = self.OSNAME
        return f"https://s3.amazonaws.com/redisinsight.test/public/rs-ri-builds/RedisInsight-{osname}.{version}.{self.ARCH}.zip"

    def _fetch_and_unzip(self, url: str, destfile: str, custom_dest: str = None):
        logger.debug(f"Package URL: {url}")

        if not os.path.isfile(destfile):
            r = requests.get(url, stream=True)
            if r.status_code > 204:
                logger.error(f"{url} could not be retrieved")
                raise requests.HTTPError
            open(destfile, "wb").write(r.content)

        logger.debug(f"Unzipping {destfile} and storing in {self.__PATHS__.DESTDIR}")
        with zipfile.ZipFile(destfile, "r") as zp:
            zp.extractall(path=os.path.join(self.__PATHS__.DESTDIR, "redisinsight"))

    def prepare(self, version: Union[str, None] = None):
        if version is None:
            version = self.C.get_key("redisinsight")
        logger.info("Fetching redisinsight")
        url = self.generate_url(version)
        destfile = os.path.join(
            self.__PATHS__.EXTERNAL,
            f"redisinsight-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip",
        )
        pkg_unzip_dest = os.path.join(self.__PATHS__.DESTDIR, "redisinsight")
        self._fetch_and_unzip(url, destfile, pkg_unzip_dest)
        shutil.copytree(
            pkg_unzip_dest, os.path.join(self.__PATHS__.SHAREDIR, "redisinsight")
        )
        with open(
            os.path.join(self.__PATHS__.SHAREDIR, "redisinsight", ".env"), "w+"
        ) as fp:
            fp.write("SERVER_STATIC_CONTENT=1\n")
            fp.write("API_PORT=8001\n")
