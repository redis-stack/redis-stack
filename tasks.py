from invoke import run, task
import os
import shutil
import sys
import jinja2
from stack.paths import Paths
from fabric import Connection
from fabric.transfer import Transfer


@task(
    help={
        "dockerfile": "path to docker file",
        "tag": "docker tag name",
        "arch": "architecture (eg: x86_64)",
        "root": "root for docker build",
        "buildx_push": "Set, to push during a buildx build",
    }
)
def dockerbuild(
    c,
    dockerfile="envs/dockers/Dockerfile.redis-stack-server",
    tag="redisfab/redis-stack-server:testing",
    arch="x86_64",
    root=".",
    buildx_push=False,
):
    """build the docker"""
    if arch == "x86_64":
        platform = "linux/amd64"
    elif arch == "arm64":
        platform = "linux/arm64"
    else:
        sys.stderr.write(f"{arch} is an unsupported platform.\n")
        sys.exit(3)

    if buildx_push:
        cmd = f"docker buildx build --push --platform {platform} -f {dockerfile} -t {tag} {root}"
    else:
        cmd = f"docker buildx build --platform {platform} -f {dockerfile} -t {tag} {root}"
    sys.stderr.write("Building docker using the command: \n")
    sys.stderr.write(cmd)
    run(cmd)

def markhandler(marker=[], notmarker=[]):
    markers = " and ".join(marker)
    nots = " and not ".join(notmarker)
    markstr = ""
    if markers:
        markstr += markers
        if nots:
            markstr += f" and not {nots}"
    if nots and not markers:
        markstr = f"not {nots}"
    return markstr

@task(
    help={
        "marker": "the pytest markers to run",
        "notmarker": "pytest markers to not run",
        "version": "Version to run, if applicable",
        "filter": "Set to a specific pytest testing to filter further",
    }
)
def test(c, marker=[], notmarker=[], filter="", version=None):
    """Run unit tests"""
    markstr = markhandler(marker, notmarker)
    cmd = f"pytest -m '{markstr}' {filter} --junit-xml=results.xml -s"
    if version is not None:
        cmd = f"VERSION={version} {cmd}"
    sys.stderr.write(f"Running: {cmd}\n")
    run(cmd)


@task(
    help={
        "docker": "docker to test",
        "version": "version",
        "arch": "architecture (x86_64, arm)",
    }
)
def test_ci_dockers(c, docker="redis-stack-server", version=None, arch="x86_64"):
    """Helper wrapper for testing within github actions"""
    if arch == "arm64":
        test(
            c,
            marker=[f'dockers_{docker.replace("-", "_")}', "arm"],
            filter="tests/smoketest/test_dockers.py",
            version=version,
        )
    elif arch == "x86_64":
        test(
            c,
            marker=[f'dockers_{docker.replace("-", "_")}'],
            notmarker=["arm"],
            version=version,
        )
    else:
        sys.stderr.write(f"{arch} is an unsupported arch.\n")
        sys.exit(3)

@task(
    help={
        "ip": "IP address of the server",
        "user": "ssh user name",
        "version": "redis-stack version",
        "ssh_key_path": "path to ssh key",
        "binary": "path to binaries",
        "git_branch": "name of current git branch",
        "package": "name of the build package [redis-stack, redis-stack-server]",
        "marker": "pytest markers",
        "notmarker": "pytest markers to not run",
    }
)
def test_over_ssh(c, ip="", user="", ssh_key_path="", version="", binary="", git_branch="HEAD", package="redis-stack-server", marker=["macos"], notmarker=[]):
    markstr = markhandler(marker, notmarker)
    tests = f"/tmp/{package}-tests/{version}"
    c = Connection(host=ip, user=user, connect_kwargs={"key_filename": ssh_key_path})
    t = Transfer(c)
    dest = f"/tmp/{package}-{version}.zip"
    c.run(f"rm -rf {tests} {dest} /opt/homebrew/var/db/redis-stack/dump.rdb")
    t.put(binary, dest)
    c.run(f"mkdir -p {tests}")
    c.run(f"git clone https://github.com/redis-stack/redis-stack {tests}")
    c.run(f"mkdir -p {tests}/redis-stack/redis-stack-server")
    c.run(f"unzip -d {tests}/redis-stack/redis-stack-server {dest}")
    c.run(f"python3 -m venv {tests}/.venv")
    print("===== VENV CREATED =====")
    c.run(f"cd {tests} && git checkout {git_branch}")
    print("===== PIP INSTALLING =====")
    print(f"{tests}/.venv/bin/python -m pip install --upgrade pip")
    c.run(f"{tests}/.venv/bin/python -m pip install --upgrade pip")
    c.run(f"{tests}/.venv/bin/python -m pip install --upgrade poetry")
    print(f"=======POETRY TIME: cd {tests} && .venv/bin/python -m poetry install --no-root")
    c.run(f"cd {tests} && .venv/bin/python -m poetry install --no-root")
    c.run(f"cd {tests} && .venv/bin/pytest -m macos")

@task
def build_redis(c, redis_repo_path="redis", build_args="all build_tls=yes"):
    """compile redis"""
    redispath = os.path.join(os.getcwd(), redis_repo_path, "src")
    run(f"make -C {redispath} -j `nproc` {build_args}")

@task(
    help={
        "ip": "IP address of the server",
        "user": "ssh user name",
        "version": "redis version",
        "ssh_key_path": "path to ssh key",
        "osname": "operating system name (eg: macos)",
        "osnick": "osnick for packages to fetch (eg: monterey)",
        "arch": "architecture (eg: arm64)",
        "packagedversion": "version to package this as",
    }
)
def build_m1_over_ssh(c, ip="", user="", ssh_key_path="", version="", packagedversion="", osname="macos", osnick="sonoma", arch="arm64"):
    """Triggering the m1 build, via ssh and fetch the outputs"""
    dest = f"depos/redis-{version}"
    argsdest = f"redis-{packagedversion}-{osname}-{osnick}-{arch}"
    os.mkdir(os.path.join(os.getcwd(), argsdest))
    c = Connection(host=ip, user=user, connect_kwargs={"key_filename": ssh_key_path})
    c.run(f"rm -rf {dest}")
    c.run(f"git clone https://github.com/redis/redis -b {version} depos/redis-{version}")
    c.run(f"""make -C {dest} all BUILD_TLS=yes
            FINAL_LIBS="-lm -ldl ../deps/hiredis/libhiredis_ssl.a /opt/homebrew/opt/openssl/lib/libssl.a /opt/homebrew/opt/openssl/lib/libcrypto.a"
            CFLAGS="-I /opt/homebrew/opt/openssl@3/include"
          """)

    t = Transfer(c)
    for b in ['redis-server', 'redis-sentinel', 'redis-check-aof', 'redis-check-rdb', 'redis-benchmark', 'redis-cli']:
        src = f"{dest}/src/{b}"
        ldest = os.path.join(argsdest, b)
        t.get(src, ldest)
        os.chmod(ldest, 0o755)

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
def package_redis(
    c,
    version="",
    osname="macos",
    dist="sonoma",
    publish=False,
    arch="amd64",
    redis_repo_path="redis",
):
    """package, a compiled redis"""
    redispath = os.path.abspath(os.path.join(os.getcwd(), redis_repo_path, "src"))
    dest = f"redis-{version}-{osname}-{dist}-{arch}"
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.mkdir(dest)
    binaries = [
        "redis-cli",
        "redis-server",
        "redis-sentinel",
        "redis-benchmark",
        "redis-check-rdb",
        "redis-check-aof",
    ]

    for b in binaries:
        shutil.copyfile(os.path.join(redispath, b), os.path.join(dest, b))

    tarball = f"{dest}.tgz"
    tarcmd = f"tar -czvf {tarball} {dest}"
    run(tarcmd)

    if publish:
        cmd = [
            "aws",
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
        "product": "docker type [redis-stack, redis-stack-server]",
        "arch": "architectures [x86_64, arm64]",
    }
)
def dockergen(c, product="redis-stack", arch="x86_64"):
    """Generate docker compile files"""
    here = os.path.abspath(os.path.dirname(__file__))
    src = os.path.join("envs", "dockers", "dockerfile.tmpl")
    dest = os.path.join(here, "envs", "dockers", f"Dockerfile.{product}")
    loader = jinja2.FileSystemLoader(here)
    env = jinja2.Environment(loader=loader)
    tmpl = loader.load(name=src, environment=env)

    p = Paths(None, None)
    vars = {"docker_type": product, "SHAREDIR": p.SHAREDIR, "arch": arch}
    with open(dest, "w+") as fp:
        fp.write(tmpl.render(vars))
    sys.stdout.write(f"Docker file generated: {dest}\n")


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
