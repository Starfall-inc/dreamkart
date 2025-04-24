import redis
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
redis_clients = {}


def init_redis(app):
    redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")
    for db_index in range(16):
        redis_clients[db_index] = redis.StrictRedis.from_url(redis_url, db=db_index)
