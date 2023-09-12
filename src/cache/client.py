import pickle

import redis

from src.config import settings

redis_client = redis.StrictRedis(host=f'{settings.REDIS_HOST}', port=settings.REDIS_PORT, db=0)


# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


class RedisClient:
    @staticmethod
    def generate_key(prefix, body):
        key = f'{prefix}:{body}'
        return key

    def get_cache(self, prefix, body):
        key = self.generate_key(prefix, body)
        value = redis_client.get(key)
        return pickle.loads(value) if value else []

    async def set_cache(self, prefix, body, value):
        key = self.generate_key(prefix, body)
        redis_client.set(key, pickle.dumps(value))

    async def clear_cache(self, prefix, body):
        key = self.generate_key(prefix, body)
        redis_client.delete(key)
