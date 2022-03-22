def get_version(product, docker=None):
    if product == "redis-stack":
        from .recipes.redis_stack import RedisStack as recipe
    elif product == "redis-stack-server":
        from .recipes.redis_stack_server import RedisStackServer as recipe
    elif product == "redisinsight":
        from .recipes.redisinsight import RedisInsight as recipe
    else:
        raise AttributeError("Unsupported product")

    r = recipe("Linux")
    if r.version == "99.99.99" and docker is not None:
        return "edge"
    return r.version
