import datetime
from unittest import mock

import pytest
from asynctest import CoroutineMock
from freezegun import freeze_time
from bson.objectid import ObjectId


from aiohttp_demo.auth.controller import Auth


class TestAuth:

    def test_get_user_id(self, controller, req, user_id):
        req['user_id'] = user_id
        assert controller.get_user_id(req) == ObjectId(user_id)

    def test_get_user_id_empty_request(self, controller, req):
        assert controller.get_user_id(req) is None


class TestAuthMiddleware:

    async def test_unauthenticated(
            self, frozen_time, controller, req, handler, session):
        await controller.middleware(req, handler)
        assert session['last_activity'] == \
            datetime.datetime.utcnow().isoformat()

    async def test_authenticated_timeout(
            self, frozen_time, controller, req, handler,
            session_with_user_id_activity, user_id):
        now = datetime.datetime.utcnow()
        after_5s = now + datetime.timedelta(seconds=5)
        frozen_time.move_to(after_5s)
        with mock.patch.object(
                controller, 'logout',
                new=CoroutineMock()) as logout: 
            await controller.middleware(req, handler)
        logout.assert_called_with(req)
        session_with_user_id_activity['last_activity'] = after_5s.isoformat()


@pytest.fixture
def frozen_time():
    with freeze_time('2019-02-16 10:15:25') as frozen:
        yield frozen


@pytest.fixture
def controller():
    return Auth('user_id', 'last_activity', datetime.timedelta(seconds=2))


@pytest.fixture
def req():
    return {}


@pytest.fixture
def handler():
    return CoroutineMock()


@pytest.fixture
def user_id():
    return '5c6ac39ba085222807f87f6b'


@pytest.fixture
def session_with_user_id(session, user_id):
    session['user_id'] = user_id
    yield session
    try:
        del session['user_id']
    except KeyError:
        pass

@pytest.fixture
def session_with_user_id_activity(frozen_time, session_with_user_id):
    session_with_user_id['last_activity'] = \
        datetime.datetime.utcnow().isoformat()
    yield session_with_user_id
    del session_with_user_id['last_activity']
