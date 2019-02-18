import short_url
from aiohttp import web

from .resources import Link


def configure(link_repository, auth, uid_generator):
    link = Link(link_repository, auth, short_url, uid_generator)
    return [
        web.get('/{shortcut}', link.redirect),
        web.post('/api/link', auth.login_required(link.create)),
        web.get('/api/link', link.list),
        web.get(
            '/api/link-user/{user_id}',
            auth.login_required(link.list_for_user)),
        web.get('/api/link/last/{last}', link.list, name='links'),
        web.get(
            '/api/link-user/{user_id}/last/{last}',
            auth.login_required(link.list_for_user), name='links_for_user'),
        web.get('/api/link/{id}', link.single, name='link'),
        web.put('/api/link/{id}', auth.login_required(link.update)),
        web.delete('/api/link/{id}', auth.login_required(link.remove)),
    ]
