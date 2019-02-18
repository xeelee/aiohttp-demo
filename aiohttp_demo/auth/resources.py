from aiohttp import web
from aiohttp_apispec import docs, use_kwargs, marshal_with

from aiohttp_demo.lib.schema.decorators import json_response
from . import schemas as sm


class Auth:

    def __init__(self, user_repository, auth):
        self._user_repository = user_repository
        self._auth = auth

    @use_kwargs(sm.AuthLogin(strict=True), locations=['json'])
    @docs(
        tags=['auth'],
        summary='Login',
    )
    @marshal_with(sm.AuthLogin(strict=True), 200)
    async def login(self, request):
        router = request.app.router['auth']
        data = request['data']
        user_id = self._auth.get_user_id(request)
        if user_id:
            raise web.HTTPFound(router.url_for())
        user = await self._user_repository.find_by_email(data['email'])
        if user['password'] == data['password']:
            await self._auth.login(request, user['_id'])
        raise web.HTTPFound(router.url_for())

    @docs(
        tags=['auth'],
        summary='Logout',
    )
    async def logout(self, request):
        router = request.app.router['auth']
        await self._auth.logout(request)
        raise web.HTTPNoContent()

    @json_response(sm.AuthUser(strict=True))
    async def single(self, request):
        user_id = self._auth.get_user_id(request)
        return {'user_id': user_id}
