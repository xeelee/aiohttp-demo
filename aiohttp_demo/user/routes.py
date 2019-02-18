from aiohttp import web

from .resources import User


def configure(user_repository, auth):
    user = User(user_repository)
    return [
        web.post('/api/user', user.create),
        web.get('/api/user/{id}', user.single, name='user'),
    ]
