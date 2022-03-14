import pytest
import redis


@pytest.fixture
def r():
    return redis.Redis(decode_responses=True)
