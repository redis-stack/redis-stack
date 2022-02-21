# redis-stack

This repository builds redis, and downloads various components (modules, RedisInsight) in order to build redis-stack packages for it's CI process.

## Development Requirements

* Python > 3.6 (for this toolkit) and poetry
* Ruby > 2.7 (for [fpm](https://github.com/jordansissel/fpm))
* Docker (to build a docker)

## How to Build

1. Create a virtualenv and install dependencies *poetry install*
1. Install the fpm gem: *gem install fpm*
1. Clone [redis](https://github.com/redis/redis).
1. Use invoke -l to execute the various tasks you need

### Packaging

Invoke wraps fpm, in order to provide a unified packaging interface on top of fpm.  The script [assemble.py](/redis/redis-stack/tree/master/assemble.py) provides support for building each target package.  To do so, you will need to execute packaging on the target operating system.

While it's possible to build all Linux packages on Arch or Ubuntu, OSX packages must be built on a Mac.

--------

#### Modifying service initializations

Today, to modify the way a service starts, the following files all need editing:

* entrypoint.sh (for dockers)
* snapcraft.j2 (for ubuntu snaps)
* etc/services/ (for systemd services on Linux)
