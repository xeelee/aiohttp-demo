from aiohttp import web

from .resources import Auth


def configure(user_repository, auth):
    auth_res = Auth(user_repository, auth)
    return [
        web.post('/api/auth', auth_res.login),
        web.get(
            '/api/auth',
            auth.login_required(auth_res.single), name='auth'),
        web.delete('/api/auth', auth_res.logout)
    ]
