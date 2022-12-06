#
# Copyright Redis Ltd. [2022] - present
# Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
# the Server Side Public License v1 (SSPLv1).
#
import pytest
import redis


@pytest.fixture
def r():
    return redis.Redis(decode_responses=True)
