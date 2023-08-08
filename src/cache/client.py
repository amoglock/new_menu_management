import redis

from config import REDIS_HOST

redis_client = redis.StrictRedis(host=f'{REDIS_HOST}', port=6379, db=0)
