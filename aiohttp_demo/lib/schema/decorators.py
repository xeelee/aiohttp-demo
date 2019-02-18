from functools import wraps

from aiohttp import web
from aiohttp_apispec import marshal_with


def json_response(schema, status_code=200):
    def decorator(fun):
        @marshal_with(schema, status_code)
        @wraps(fun)
        async def wrapper(*args, **kwargs):
            obj = await fun(*args, **kwargs)
            if obj is None:
                raise web.HTTPNotFound
            serialized = schema.dump(obj)
            return web.json_response(serialized.data)
        return wrapper
    return decorator
