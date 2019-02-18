from aiohttp import web
from aiohttp_apispec import docs, use_kwargs, marshal_with

from aiohttp_demo.lib.schema.decorators import json_response
from aiohttp_demo.lib.paginator import MongoPaginator
from . import schemas as sm


class Link:

    paginator = MongoPaginator('updated_at')

    def __init__(
            self, link_repository, auth, url_encoder, uid_generator):
        self._link_repository = link_repository
        self._auth = auth
        self._url_encoder = url_encoder
        self._uid_generator = uid_generator

    async def redirect(self, request):
        shortcut = request.match_info['shortcut']
        link = await self._link_repository.find_by_shortcut(shortcut)
        if link:
            raise web.HTTPMovedPermanently(link['url'])
        raise web.HTTPNotFound

    @use_kwargs(sm.LinkCreate(strict=True), locations=['json'])
    @docs(
        tags=['link'],
        summary='Create link',
    )
    @marshal_with(sm.Link(strict=True), 200)
    async def create(self, request):
        router = request.app.router['link']
        data = request['data']
        user_id = self._auth.get_user_id(request)
        uid = await self._uid_generator.gen_uid()
        shortcut = self._url_encoder.encode_url(uid)
        obj_id = await self._link_repository.create(
            data['url'], shortcut, user_id, data['is_public'])
        location = router.url_for(id=str(obj_id))
        raise web.HTTPFound(location)

    @docs(
        tags=['link'],
        summary='Get link',
    )
    @json_response(sm.Link(strict=True))
    async def single(self, request):
        link = await self._link_repository.find(request.match_info['id'])
        return link

    @docs(
        tags=['link'],
        summary='Delete link',
    )
    @json_response(sm.Link(strict=True))
    async def remove(self, request):
        doc = await self._link_repository.find(request.match_info['id'])
        if not doc:
            return
        if not self._auth.is_current_user(request, str(doc['created_by'])):
            raise web.HTTPForbidden
        was_removed = await self._link_repository.remove(
            request.match_info['id'])
        if was_removed:
            raise web.HTTPNoContent
        raise web.HTTPNotFound

    @use_kwargs(sm.LinkUpdate(strict=True), locations=['json'])
    @docs(
        tags=['link'],
        summary='Modify link',
    )
    @json_response(sm.Link(strict=True))
    async def update(self, request):
        doc = await self._link_repository.find(request.match_info['id'])
        if not doc:
            return
        if not self._auth.is_current_user(
                request, str(doc['created_by'])):
            raise web.HTTPForbidden
        data = request['data']
        if 'expiration' in data:
            expiration_time = doc['created_at'] + data['expiration']
        else:
            expiration_time = self._link_repository.OMITTED
        updated_doc = await self._link_repository.update(
            request.match_info['id'],
            is_public=data.get('is_public', self._link_repository.OMITTED),
            expires_at=expiration_time
        )
        return updated_doc

    @use_kwargs(sm.LinkQuery(strict=True), locations=['query'])
    @docs(
        tags=['link'],
        summary='Public list of links',
    )
    @json_response(sm.PaginatedLinkResult(strict=True))
    async def list(self, request):
        router = request.app.router['links']
        format_url = lambda x: '{}?limit={}'.format(
            router.url_for(last=x),
            request['data']['limit'],
        )
        return await self._list(
            request,
            self._link_repository.find_many_public_factory(True),
            format_url)

    @use_kwargs(sm.LinkQuery(strict=True), locations=['query'])
    @docs(
        tags=['link', 'user'],
        summary='User list of links',
    )
    @json_response(sm.PaginatedLinkResult(strict=True))
    async def list_for_user(self, request):
        if not self._auth.is_current_user(
                request, request.match_info['user_id']):
            raise web.HTTPForbidden
        router = request.app.router['links_for_user']
        # TODO: refactor
        format_url = lambda x: '{}?limit={}'.format(
            router.url_for(user_id=request.match_info['user_id'], last=x),
            request['data']['limit'],
        )
        return await self._list(
            request,
            self._link_repository.find_many_for_user_factory(
                request.match_info['user_id']),
                format_url,
            )

    async def _list(self, request, find, format_url):
        start_after = \
            request.match_info['last'] if 'last' in request.match_info else None
        paginated = await self.paginator.process(
            find, {}, request['data']['limit'],
            start_after=start_after
        )
        return paginated.as_dict(format_url)
