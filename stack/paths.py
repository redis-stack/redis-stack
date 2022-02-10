import os


class Paths:
    """Paths used throughout"""

    def __init__(self, osnick: str, arch: str = "x86_64", osname: str = "Linux"):

        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname

        # general pathing
        self.HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.EXTERNAL = os.path.join(self.HERE, "deps", "external")
        self.DISTDIR = os.path.join(self.HERE, "dist")
        self.BUILDROOT = os.path.join(self.HERE, "build")
        self.SCRIPTDIR = os.path.join(self.HERE, "scripts")

        # used throughout
        self.DESTDIR = os.path.join(
            self.EXTERNAL, f"{self.OSNAME}-{self.OSNICK}-{self.ARCH}"
        )
        self.WORKDIR = os.path.join(
            self.BUILDROOT, f"{self.OSNAME}-{self.OSNICK}-{self.ARCH}"
        )

        # package paths
        self.BASEDIR = os.path.join(self.WORKDIR, "opt", "redis-stack")
        self.USRBINDIR = os.path.join(self.WORKDIR, "usr", "bin")
        self.LIBDIR = os.path.join(self.BASEDIR, "lib")
        self.BINDIR = os.path.join(self.BASEDIR, "bin")
        self.ETCDIR = os.path.join(self.BASEDIR, "etc")
        self.SVCDIR = os.path.join(self.ETCDIR, "systemd", "system")
        self.CONFDIR = os.path.join(self.ETCDIR, "redis-stack")
