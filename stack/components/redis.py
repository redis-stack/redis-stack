import os
import shutil
import tarfile
from typing import Union

import requests
from loguru import logger

from ..config import Config
from ..paths import Paths


class Redis(object):
    """Helper for fetching redis for S3 and inserting into position."""

    def __init__(
        self, package: str, osnick: str, arch: str = "x86_64", osname: str = "Linux"
    ):

        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.__PATHS__ = Paths(package, osnick, arch, osname)
        self.C = Config()

    def generate_url(self, version: str):
        url = f"https://redismodules.s3.amazonaws.com/redis-stack/dependencies/redis-{version}-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.tgz"
        return url

    def _fetch_and_unzip(self, url: str, destfile: str):
        logger.debug(f"Package URL: {url}")

        if os.path.isfile(destfile):
            return

        r = requests.get(url, stream=True)
        if r.status_code > 204:
            logger.error(f"{url} could not be retrieved")
            raise requests.HTTPError
        open(destfile, "wb").write(r.content)

        logger.debug(f"Unzipping {destfile} and storing in {self.__PATHS__.DESTDIR}")
        with tarfile.open(destfile) as tar:
            tar.extractall(path=self.__PATHS__.DESTDIR)

    def prepare(self, version: Union[str, None] = None):
        if version is None:
            version = self.C.get_key("versions")["redis"]
        logger.info("Fetching redis")
        destfile = os.path.join(
            self.__PATHS__.EXTERNAL,
            f"redis-{version}-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.tar.gz",
        )
        self._fetch_and_unzip(self.generate_url(version), destfile)

        destdir = self.__PATHS__.BINDIR
        for i in [
            "redis-benchmark",
            "redis-check-aof",
            "redis-check-rdb",
            "redis-cli",
            "redis-sentinel",
            "redis-server",
        ]:
            src = os.path.join(
                self.__PATHS__.DESTDIR,
                f"redis-{version}-{self.OSNAME}-{self.OSNICK}-{self.ARCH}",
                i,
            )
            destfile = os.path.join(destdir, i)
            shutil.copy2(src, destfile)
            os.chmod(destfile, mode=0o755)
