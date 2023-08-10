import pickle

import redis

from config import REDIS_HOST

redis_client = redis.StrictRedis(host=f'{REDIS_HOST}', port=6379, db=0)


def generate_key(prefix, body):
    key = f'{prefix}:{body}'
    return key


def get_cache(prefix, body):
    key = generate_key(prefix, body)
    value = redis_client.get(key)
    return pickle.loads(value) if value else None


def set_cache(prefix, body, value):
    key = generate_key(prefix, body)
    redis_client.set(key, pickle.dumps(value))


def clear_cache(prefix, body):
    key = generate_key(prefix, body)
    redis_client.delete(key)
