from stack.paths import Paths
import os


BASEPATH = "/opt/redis-stack"
BINDIR = os.path.join(BASEPATH, "bin")
LIBDIR = os.path.join(BASEPATH, "lib")
ETCDIR = os.path.join(BASEPATH, "etc")
SHAREDIR = os.path.join(BASEPATH, "share")
REDIS_UID = 999
REDIS_GID = 999

def test_paths_exist():
    for i in [BASEPATH, BINDIR, LIBDIR, ETCDIR, SHAREDIR]:
        assert os.path.isdir(i)


def test_files_exist():
    assert os.path.isfile(os.path.join(ETCDIR, "redis-stack.conf"))
    for i in ['redis-server', 'redis-benchmark', 'redis-check-aof', 'redis-check-rdb', 'redis-cli', 'redis-sentinel']:

        fpath = os.path.join(BINDIR, i)
        assert os.path.isfile(fpath)
        stats = os.stat(fpath)
        assert stats.st_uid == REDIS_UID
        assert stats.st_gid == REDIS_GID
        assert os.access(i, os.X_OK)

    # otherwise we can't load the modules
    for i in ['rejson.so', 'redistimeseries.so', 'redisearch.so']:  # 'redisgraph.so', 'redisbloom.so']:

        fpath = os.path.join(LIBDIR, i)
        assert os.path.isfile(fpath)
        stats = os.stat(fpath)
        assert stats.st_uid == REDIS_UID
        assert stats.st_gid == REDIS_GID
        assert os.access(i, os.X_OK)