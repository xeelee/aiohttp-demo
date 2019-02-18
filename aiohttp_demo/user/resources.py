from aiohttp import web
from aiohttp_apispec import docs, use_kwargs, marshal_with

from aiohttp_demo.lib.schema.decorators import json_response
from aiohttp_demo.exceptions import Duplicate
from . import schemas as sm

# Custom view class, because `web.View` doesn't allow
# injecting dependencies in `__init__`


class User:

    def __init__(self, user_repository):
        self._user_repository = user_repository

    @use_kwargs(sm.UserCreate(strict=True), locations=['json'])
    @docs(
        tags=['user'],
        summary='Create user',
    )
    @marshal_with(sm.User(strict=True), 200)
    async def create(self, request):
        router = request.app.router['user']
        try:
            obj_id = await self._user_repository.create(
                request['data']['email'], request['data']['password'])
        except Duplicate:
            # do not attach details due to security reasons
            raise web.HTTPConflict()

        location = router.url_for(id=str(obj_id))
        raise web.HTTPFound(location)

    @docs(
        tags=['user'],
        summary='Get user',
    )
    @json_response(sm.User(strict=True))
    async def single(self, request):
        user = await self._user_repository.find(request.match_info['id'])
        return user
