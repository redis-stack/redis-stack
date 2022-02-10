import redis
import requests


def test_basic_redis(r):
    assert r.ping()

    r.set('some', 'value')
    assert r.get('some') == 'value'

def test_redis_modules_loaded(r):
    expected = ['rejson', 'timeseries', 'search']  # 'graph', 'bloom'
    modules = [m.get('name').lower() for m in r.module_list()]

    modules.sort()
    expected.sort()
    assert modules == expected

def test_basic_redisinsight():
    r = requests.get('http://localhost:8081')
    assert r.status_code == 200
    assert r.content.decode().find('RedisInsight') != -1