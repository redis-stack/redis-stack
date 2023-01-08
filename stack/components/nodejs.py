#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import os
import shutil
import tarfile
from typing import Union

import requests
from loguru import logger

from ..config import Config
from ..paths import Paths


class NodeJS(object):
    """Helper class for handling nodejs"""

    def __init__(
        self, package: str, osnick: str, arch: str = "x86_64", osname: str = "Linux"
    ):

        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.__PATHS__ = Paths(package, osnick, arch, osname)
        self.C = Config()

    @property
    def node_arch(self):
        if self.ARCH == "x86_64":
            return "x64"
        return self.ARCH

    @property
    def node_osname(self):
        if self.OSNAME == "macos":
            return "darwin"
        else:
            return self.OSNAME.lower()

    def generate_url(self, version: str):
        url = f"https://nodejs.org/dist/{version}/node-{version}-{self.node_osname}-{self.node_arch}.tar.gz"
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
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner) 
                
            
            safe_extract(tar, path=self.__PATHS__.DESTDIR)

    def prepare(self, version: Union[str, None] = None):
        logger.info("Fetching nodejs")
        destfile = os.path.join(
            self.__PATHS__.EXTERNAL,
            f"nodejs-{self.OSNAME}-{self.OSNICK}-{self.ARCH}.tar.gz",
        )
        if version is None:
            version = self.C.get_key("versions")["nodejs"]
        self._fetch_and_unzip(self.generate_url(version), destfile)

        node_base = os.path.join(
            self.__PATHS__.DESTDIR,
            f"node-{version}-{self.node_osname}-{self.node_arch}",
        )

        destdir = os.path.join(self.__PATHS__.BASEDIR, "nodejs")
        if os.path.isdir(destdir):
            return
        shutil.copytree(node_base, destdir)
