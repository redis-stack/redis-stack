from optparse import OptionParser
import sys
from loguru import logger


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
        help="[Optional] Path to redis binaries",
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
        "-t",
        "--target",
        dest="TARGET",
        help="Target package type (eg dpkg)",
        default="deb",
        type="choice",
        choices=["rpm", "deb", "osxpkg", "pacman", "zip", "tar", "snap"],
    )
    p.add_option(
        "-p",
        "--package",
        dest="PACKAGE",
        help="Package recipe to build",
        default="redis-stack-server",
        type="choice",
        choices=[
            "redis-stack",
            "redis-stack-server",
            "redisinsight",
            "redisinsight-web",
        ],
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

    if not opts.VARIANT:
        opts.VARIANT = f"{opts.OSNICK}-{opts.ARCH}"

    # default to info logging
    logger.remove()
    if opts.DEBUG is True:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="INFO")

    # a = Package(opts.OSNICK, opts.ARCH, opts.OSNAME)
    if opts.PACKAGE == "redis-stack-server":
        from stack.recipes.redis_stack_server import RedisStackServer as pkgklass
    elif opts.PACKAGE == "redis-stack":
        from stack.recipes.redis_stack import RedisStack as pkgklass
    elif opts.PACKAGE == "redisinsight":
        from stack.recipes.redisinsight import RedisInsight as pkgklass
    elif opts.PACKAGE == "redisinsight-web":
        from stack.recipes.redisinsight import RedisInsightWeb as pkgklass
    else:
        sys.stderr.write(f"{opts.PACKAGE} is an unsupported package recipe.\n")
        sys.exit(3)

    a = pkgklass(opts.OSNICK, opts.ARCH, opts.OSNAME)

    if opts.SKIP is None or opts.SKIP != "fetch":
        a.prepackage(opts.REDISBIN, opts.IGNORE, opts.VERSION_OVERRIDE)

    if opts.SKIP is None or opts.SKIP != "package":
        sys.exit(a.package(opts.TARGET, opts.DIST))
