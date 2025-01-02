from config import Config

c = Config()
print(str(c.get_key("versions")["redisearch"]) + "0")