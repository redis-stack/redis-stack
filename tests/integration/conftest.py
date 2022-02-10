import pytest
import redis


@pytest.fixture
def r():
    return redis.Redis(password='stack', decode_responses=True)