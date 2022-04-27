from invoke import run, task
import os
import shutil
import sys
import jinja2
from stack.paths import Paths


@task
def build_redis(c, redis_repo_path="redis", build_args="all build_tls=yes"):
    """compile redis"""
    redispath = os.path.join(os.getcwd(), redis_repo_path, "src")
    run(f"make -C {redispath} -j `nproc` {build_args}")

@task(
    help={
        "osname": "operating system name (eg: Linux)",
        "dist": "package distribution to generate (eg: bionic)",
        "redis_repo_path": "path to pre-build redis binaries",
        "arch": "architecture (eg: x86_64)",
        "version": "the version string for this redis build",
        "publish": "upload to s3, via aws s3 cp, if set",
    }
)
def package_redis(c, version="", osname='macos', dist='monterey', publish=False, arch="amd64", redis_repo_path="redis"):
    """package, a compiled redis"""
    redispath = os.path.abspath(os.path.join(os.getcwd(), redis_repo_path, "src"))
    dest = f"redis-{version}-{osname}-{dist}-{arch}"
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.mkdir(dest)
    binaries = ['redis-cli', 'redis-server', 'redis-sentinel', 'redis-benchmark', 'redis-check-rdb', 'redis-check-aof']

    for b in binaries:
        shutil.copyfile(os.path.join(redispath, b), os.path.join(dest, b))

    tarball = f"{dest}.tgz"
    tarcmd = f"tar -czvf {tarball} {dest}"
    run(tarcmd)

    if publish:
        cmd = ["aws",
               "s3",
               "cp",
               "-P",
               "--public-acl",
               tarball,
               f"s3://redismodules/redis-stack/dependencies/{tarball}",
        ]
        run(cmd)


@task(
    help={
        "docker_type": "docker type [redis-stack, redis-stack-server]",
    }
)
def dockergen(c, docker_type="redis-stack"):
    """Generate docker compile files"""
    here = os.path.abspath(os.path.dirname(__file__))
    src = os.path.join("dockers", "dockerfile.tmpl")
    dest = os.path.join(here, "dockers", f"Dockerfile.{docker_type}")
    loader = jinja2.FileSystemLoader(here)
    env = jinja2.Environment(loader=loader)
    tmpl = loader.load(name=src, environment=env)

    p = Paths(None, None)
    vars = {"docker_type": docker_type, "SHAREDIR": p.SHAREDIR}
    with open(dest, "w+") as fp:
        fp.write(tmpl.render(vars))


@task(
    help={
        "osname": "operating system name (eg: Linux)",
        "osnick": "osnick for packages to fetch (eg: ubuntu18.04)",
        "dist": "package distribution to generate (eg: bionic)",
        "redis_bin": "path to pre-build redis binaries",
        "target": "target package type to build (eg: deb)",
        "arch": "architecture (eg: x86_64)",
        "package": "package to build {redis-stack|redis-stack-server|redisinsight|redisinsight-web}",
        "skip": "[Optional] set to fetch or package to determine which step to skip",
        "redismodule_version": "[Optional] set to use a single, specified version for all redis modules",
    }
)
def package(
    c,
    osname="Linux",
    osnick="",
    dist="",
    redis_bin="../redis",
    target="deb",
    arch="x86_64",
    package="redis-stack-server",
    skip="",
    redismodule_version="",
):
    """Create a redis-stack package"""

    # TODO remove the -I once all modules are stable on all platforms
    cmd = [
        sys.executable,
        "-m",
        "stack",
        f"-o {osname}",
        f"-s {osnick}",
        f"-d {dist}",
        f"-a {arch}",
        f"-r {redis_bin}",
        f"-t {target}",
        f"-p {package}",
        f"-x",
    ]
    if skip:
        cmd.append(f"-S {skip}")

    if redismodule_version:
        cmd.append(f"-V {redismodule_version}")
    run(" ".join(cmd))


@task(
    help={
        "package": "package to build {redis_stack|redis_stack_server}",
        "docker": "if set to any value replace 99.99.99 for docker version with edge",
    }
)
def version(c, package="redis-stack-server", docker=None):
    """Return the version, according to our rules"""
    from stack import get_version

    print(get_version(package, docker))


@task
def linters(c):
    """Run linters against the codebase"""
    run("flake8 --ignore E501 stack tests")
    run("black --target-version py39 --check --diff stack tests")
