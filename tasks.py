from invoke import run, task
import os
import shutil
import sys

@task
def build_redis(c, redis_repo_path="redis", build_args="all BUILD_TLS=yes"):
    """compile redis"""
    redispath = os.path.join(os.getcwd(), redis_repo_path, "src")

    # fnames = [os.path.join(redispath, "server.c")]
    # # build redis
    # for fname in fnames:
    #     with open(fname, "r") as fp:
    #         data = fp.read()
    #         contents = data.replace("redis-server", "redis-stack")
    #     with open(fname, "w+") as fp:
    #         fp.write(contents)
    run(f"make -C {redispath} -j `nproc` {build_args}")


@task
def clean(c):
    from assemble import DISTDIR, EXTERNAL, WORKDIR

    for i in [DISTDIR, EXTERNAL, WORKDIR]:
        shutil.rmtree(i, ignore_errors=True)
    run("rm *.deb *.rpm *.ospkg")


@task(help={
    'osname': 'operating system name (eg: Linux)',
    'osnick': 'osnick for packages to fetch (eg: ubuntu18.04)',
    'dist': 'package distribution to generate (eg: bionic)',
    'redis_bin': 'path to pre-build redis binaries',
    'package': 'package type to build (eg: deb)',
    'arch': 'architecture (eg: x86_64)',
    'build_number': 'build number (defaults to 1)',
})
def package(
    c, osname='Linux', osnick='', dist='',
    redis_bin='../redis',
    package="deb",
    arch='x86_64',
    build_number=1,
):
    """Create a redis-stack package"""

    # TODO remove the -I once all modules are stable
    cmd = [
        sys.executable,
        "assemble.py",
        f"-o {osname}",
        f"-s {osnick}",
        f"-d {dist}",
        f"-a {arch}",
        f"-r {redis_bin}",
        f"-b {build_number}",
        f"-p {package}",
        f"-x",
        f"-I",
    ]
    run(' '.join(cmd))
