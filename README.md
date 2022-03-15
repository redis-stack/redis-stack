# redis-stack

This repository builds redis, and downloads various components (modules, RedisInsight) in order to build redis-stack packages for it's CI process.

## Development Requirements

* Python > 3.9 (for this toolkit) and [poetry](https://python-poetry.org)
* Ruby > 2.7 (for [fpm](https://github.com/jordansissel/fpm))
* Docker (to build a docker)
* zip/apt/deb/tar depending on your target outputs.  

## How to Build

1. Create a virtualenv and install dependencies *poetry install*
1. Install the fpm gem: *gem install fpm*

    *  Based on your Linux distribution you may need to install a debian tools package (i.e something providing dpkg), something to provide zip, tar, and rpm package tools.

1. Clone [redis](https://github.com/redis/redis).
1. Use invoke -l to execute the various tasks you need (below, an example on packaging).

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

See github workflows for how CI reuses invoke.

### Packaging

Invoke wraps fpm, in order to provide a unified packaging interface on top of fpm.  The script [assemble.py](/redis/redis-stack/tree/master/assemble.py) provides support for building each target package.  To do so, you will need to execute packaging on the target operating system.

While it's possible to build all Linux packages on Arch or Ubuntu, OSX packages must be built on a Mac.

### Testing

Tests are run via pytest. Linux tests create and destroy dockers, validating their contents. In order to validate the individual packages (i.e foo.rpm), packages must be copied to a folder called *redis-stack* and renamed, so as not to include the version number.

For example to test *redis-stack-server-99.99.99-1.x86_64.rpm*:

``` bash
mkdir redis-stack
cp *redis-stack-server-99.99.99-1.x86_64.deb* redis-stack/redis-stack-server.deb
pytest tests/smoketest/test_debs.py::TestXenial
```
--------

#### Modifying service initializations

Today, to modify the way a service starts, the following files all need editing:

* entrypoint.sh (for dockers)
* snapcraft.j2 (for ubuntu snaps)
* etc/services/ (for systemd services on Linux)
