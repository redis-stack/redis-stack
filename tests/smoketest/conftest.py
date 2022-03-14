import pytest
import redis

# def _in_docker():
#     if os.path.isfile("/.dockerenv"):
#         return True
#     else:
#         return False

# def get_localhost_equiv():
#     if _in_docker():
#         return '172.17.0.1'
#     else:
#         return 'localhost'


@pytest.fixture
def r():
    return redis.Redis(decode_responses=True)
