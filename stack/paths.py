import os


class Paths:
    """Paths used throughout"""

    def __init__(
        self, package: str, osnick: str, arch: str = "x86_64", osname: str = "Linux"
    ):

        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.PACKAGE = package

        # general pathing
        self.HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.EXTERNAL = os.path.join(self.HERE, "deps", "external")
        self.BUILDROOT = os.path.join(self.HERE, "build")
        self.SCRIPTDIR = os.path.join(self.HERE, "etc")

        # used throughout
        self.DESTDIR = os.path.join(
            self.EXTERNAL, f"{self.OSNAME}-{self.OSNICK}-{self.ARCH}"
        )
        self.WORKDIR = os.path.join(
            self.BUILDROOT, f"{self.OSNAME}-{self.OSNICK}-{self.ARCH}.{self.PACKAGE}"
        )

        # package paths
        self.BASEDIR = os.path.join(self.WORKDIR, "opt", "redis-stack")
        self.BASEETCDIR = os.path.join(self.WORKDIR, "etc")
        
        self.LIBDIR = os.path.join(self.BASEDIR, "lib")
        self.BINDIR = os.path.join(self.BASEDIR, "bin")
        self.SHAREDIR = os.path.join(self.BASEDIR, "share")
        self.ETCDIR = os.path.join(self.BASEDIR, "etc")
        self.SVCDIR = os.path.join(self.WORKDIR, "etc", "systemd", "system")
        self.USRBINDIR = os.path.join(self.WORKDIR, "usr", "bin")