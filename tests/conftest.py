from unittest import mock

import pytest
from asynctest import CoroutineMock


@pytest.fixture
def session():
    session_ = {}
    with mock.patch(
            'aiohttp_demo.auth.controller.get_session',
            new=CoroutineMock()) as gs:
        gs.return_value = session_
        yield session_

