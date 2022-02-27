def get_version(product):
    if product == 'redis-stack':
        from .recipes.redis_stack import RedisStack as recipe
    elif product == 'redis-stack-server':
        from .recipes.redis_stack_server import RedisStackServer as recipe
    elif product == 'redisinsight':
        from .recipes.redisinsight import RedisInsight as recipe
        
    r = recipe("Linux")
    return r.version