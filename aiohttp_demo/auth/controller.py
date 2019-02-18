import logging

import datetime
from functools import wraps

from bson.objectid import ObjectId
from aiohttp import web
from aiohttp_session import get_session, new_session


log = logging.getLogger(__name__)


class Auth:

    def __init__(
            self, user_id_key: str, last_activity_key: str,
            session_timeout: datetime.timedelta):
        self._user_id_key = user_id_key
        self._last_activity_key = last_activity_key
        self._session_timeout = session_timeout

    def get_user_id(self, request):
        user_id = request.get(self._user_id_key)
        if user_id:
            return ObjectId(user_id)

    def is_current_user(self, request, user_id: str):
        return request.get(self._user_id_key) == user_id

    @web.middleware
    async def middleware(self, request, handler):
        session = await get_session(request)
        if self._user_id_key in session:
            if self._last_activity_key in session and self._is_timeout_reached(
                    datetime.datetime.fromisoformat(
                        session[self._last_activity_key]
                    )
                ):
                await self.logout(request)
            else:
                request[self._user_id_key] = session[self._user_id_key]
        response = await handler(request)
        session[self._last_activity_key] = \
            datetime.datetime.utcnow().isoformat()
        return response

    def login_required(self, fun):
        @wraps(fun)
        async def wrapper(request, **kwargs):
            session = await get_session(request)
            if self._user_id_key not in session:
                raise web.HTTPUnauthorized
            result = await fun(request, **kwargs)
            return result
        return wrapper

    async def login(self, request, user_id):
        session = await new_session(request)
        session[self._user_id_key] = str(user_id)

    async def logout(self, request):
        session = await get_session(request)
        # if some other code (especially external libraries/middlewares)
        # clears session data, method should not fail
        try:
            del session[self._user_id_key]
        except KeyError:
            log.warning('`%s` already removed from session', self._user_id_key)
        try:  # in case of application restart or more than 1 instance
            del request[self._user_id_key]
        except KeyError:
            pass

    def _is_timeout_reached(self, last_activity: datetime.datetime):
        return (
            datetime.datetime.utcnow() - last_activity > self._session_timeout
        )
