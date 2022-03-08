import os
import shutil
import urllib
import zipfile
from typing import Union

import requests
import semantic_version
from loguru import logger

from ..config import Config
from ..paths import Paths


class Modules(object):
    """Helper class for handling redis modules"""

    AWS_S3_BUCKET = "redismodules.s3.amazonaws.com"

    def __init__(
        self, package: str, osnick: str, arch: str = "x86_64", osname: str = "Linux"
    ):
        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.__PATHS__ = Paths(package, osnick, arch, osname)
        self.C = Config()

    def generate_url(self, module: str, version: str):
        """Assuming the module follows the standard, return the URL from
        which to grab it"""
        
        if module == 'redisearch':
            module = 'redisearch-oss'
        
        # FIXME mac M1 temporary hack until it moves
        if self.ARCH == 'arm64':
            if module == 'redisearch-oss':
                version = '2.2.9'
            if module == 'redisgraph':
                version = '2.8.8'
            return urllib.parse.urljoin(
                f"https://{self.AWS_S3_BUCKET}",
                f"lab/23-macos-m1/{module}.{self.OSNAME}-{self.OSNICK}-arm64v8.{version}.zip",
            )
       
        return urllib.parse.urljoin(
            f"https://{self.AWS_S3_BUCKET}",
            f"{module}/{module}.{self.OSNAME}-{self.OSNICK}-{self.ARCH}.{version}.zip",
        )

    def rejson(self, version: Union[str, None] = None):
        """rejson specific fetch"""
        if version is None:
            version = self.C.get_key("versions")["rejson"]
        self._run("rejson", version)

    def redisgraph(self, version: Union[str, None] = None):
        """redisgraph specific fetch"""
        if version is None:
            version = self.C.get_key("versions")["redisgraph"]
        self._run("redisgraph", version)

    def redisearch(self, version: Union[str, None] = None):
        """redisearch specific fetch"""
        
        if version is None:
            version = self.C.get_key("versions")["redisearch"]
        self._run("redisearch", version) #None, url)

    def redistimeseries(self, version: Union[str, None] = None):
        """redistimeseries specific fetch"""
        if version is None:
            version = self.C.get_key("versions")["redistimeseries"]
        self._run("redistimeseries", version)

    def redisbloom(self, version: Union[str, None] = None):
        """bloom specific fetch"""
        if version is None:
            version = self.C.get_key("versions")["redisbloom"]
        self._run("redisbloom", version)

    def _run(self, modulename: str, version: str, url: Union[str, None] = None):
        if url is None:
            url = self.generate_url(modulename, version)
        logger.info(f"Fetching {modulename}")
        destfile = os.path.join(
            self.__PATHS__.EXTERNAL,
            f"{modulename}-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.zip",
        )
        self._fetch_and_unzip(url, destfile)
        shutil.copyfile(
            os.path.join(self.__PATHS__.DESTDIR, f"{modulename}.so"),
            os.path.join(self.__PATHS__.LIBDIR, f"{modulename}.so"),
        )
        os.chmod(os.path.join(self.__PATHS__.LIBDIR, f"{modulename}.so"), mode=0o755)

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
