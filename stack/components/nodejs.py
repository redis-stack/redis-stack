from ..paths import Paths
import os
from loguru import logger
import requests
import tarfile
import shutil


class NodeJS(object):
    """Helper class for handling nodejs"""

    DEFAULT_NODE_VERSION = "v14.19.0"

    def __init__(self, osnick: str, arch: str = "x86_64", osname: str = "Linux"):

        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.__PATHS__ = Paths(osnick, arch, osname)

    @property
    def node_arch(self):
        if self.ARCH == "x86_64":
            return "x64"
        else:
            raise AttributeError(
                f"Fetching NodeJS for {self.OSNICK} {self.ARCH} {self.OSNAME} is unsupported."
            )

    @property
    def node_osname(self):
        if self.OSNAME == "macos":
            return "darwin"
        else:
            return self.OSNAME.lower()

    def generate_url(self, version):
        url = f"https://nodejs.org/dist/{self.DEFAULT_NODE_VERSION}/node-{self.DEFAULT_NODE_VERSION}-{self.node_osname}-{self.node_arch}.tar.gz"
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

    def prepare(self, version: str = DEFAULT_NODE_VERSION):
        logger.info("Fetching nodejs")
        destfile = os.path.join(
            self.__PATHS__.EXTERNAL,
            f"nodejs-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.tar.gz",
        )
        self._fetch_and_unzip(self.generate_url(version), destfile)

        node_base = os.path.join(
            self.__PATHS__.DESTDIR,
            f"node-{self.DEFAULT_NODE_VERSION}-{self.node_osname}-{self.node_arch}",
        )
        shutil.copytree(node_base, os.path.join(self.__PATHS__.BASEDIR, "nodejs"))
