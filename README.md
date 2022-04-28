# redis-stack

This repository builds redis, and downloads various components (modules, RedisInsight) in order to build redis-stack packages for it's CI process.

## Development Requirements

* Python > 3.9 (for this toolkit) and [poetry](https://python-poetry.org)
* Ruby > 2.7 (for [fpm](https://github.com/jordansissel/fpm))
* Docker (to build a docker)
* zip/apt/deb/tar depending on your target outputs.

## Building

1. Create a virtualenv and install dependencies *poetry install*
1. Install the fpm gem: *gem install fpm*

    *  Based on your Linux distribution you may need to install a debian tools package (i.e something providing dpkg), something to provide zip, tar, and rpm package tools.

1. Clone [redis](https://github.com/redis/redis) if you're developing changes to the redis builds.
1. Use invoke -l to list, and then execute the various tasks you need (below, an example on packaging).

*To build a focal package*
```
invoke package -o Linux -p redis-stack-server -s ubuntu20.04 -t deb -d focal
```

*To build a xenial package*
```
invoke package -o Linux -p redis-stack-server -s ubuntu16.04 -t deb -d xenial
```

*To build a macos (x86_64) zip, prior to homebrew*
```
invoke package -o macos -p redis-stack-server -s catalina -t zip -d catalina
```

*To build a macos (m1) zip, prior to homebrew*
```
invoke package -o macos -p redis-stack-server -s monterey -t zip -d monterey -a arm64
```

For more examples, see github workflows for how CI reuses invoke.

### Packaging

Invoke wraps fpm, in order to provide a unified packaging interface on top of fpm.  The script [assemble.py](/redis/redis-stack/tree/master/assemble.py) provides support for building each target package.  To do so, you will need to execute packaging on the target operating system.

While it's possible to build all Linux packages on Arch or Ubuntu, OSX packages must be built on a Mac.

### Testing

Tests are run via pytest. Linux tests create and destroy dockers, validating their contents. In order to validate the individual packages (i.e foo.rpm), packages be built, via *invoke*, then copied to a folder called *redis-stack* and renamed, so as not to include the version number.

For example to test *redis-stack-server-99.99.99-1.x86_64.rpm*:

``` bash
mkdir redis-stack
cp *redis-stack-server-99.99.99-1.x86_64.deb* redis-stack/redis-stack-server.deb
pytest tests/smoketest/test_debs.py::TestXenial
```

For the various pytest markers, see the *pyproject.toml*

--------

### Releasing

1. To make a release, use the GitHub release drafter. By creating a tag, in the release drafter, a release is made. Versions are taken from the *config.yaml*.

    The process of releasing copies existing built artifacts (dockers, rpms, snaps, etc) from the snapshot directories, and re-uploading them to the root s3 folder (s3://redismodules/redis-stack/). No compilation or testing of releases occur, as that has already happened as part of the continuous integration process. As of this writing, this repository releases the dockers as well.

2. Tag the [rpm repository](https://github.com/redis-stack/redis-stack-rpm) and wait for the [publish action to complete](https://github.com/redis-stack/redis-stack-rpm/actions/workflows/release.yml).
3. Tag the [debian repository](https://github.com/redis-stack/redis-stack-deb)
4. Update [homebrew](https://github.com/redis-stack/homebrew-redis-stack) with the latest version

------------------------

#### Modifying service initializations

Today, to modify the way a service starts, the following files all need editing:

* entrypoint.sh (for dockers)
* snapcraft.j2 (for ubuntu snaps)
* etc/services/ (for systemd services on Linux)

#### Changing package versions and sources

Versions for all packages are defined in the config.yaml file, and within a function named *generate_url* for each source type. In the case where you need to test a package that has been built to a custom location, set a variable named <module>-url-override in the config file at the top level.  For example, to override the rejson package location create a variable named *rejson-url-override*.  In the case of RedisInsight, all packages would derive from *redisinsight-url-override*.

Do not commit this change to a mainline branch.

