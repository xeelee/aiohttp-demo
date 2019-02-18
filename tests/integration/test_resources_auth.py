import pytest


class TestUsersResource:

    async def test_login(self, api, auth_data, db_user):
        response = await api.post('/api/auth', json=auth_data)
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        assert json == {
            'user_id': str(db_user['_id']),
        }

    async def test_get_single(self, api, logged_user_id):
        response = await api.get('/api/auth')
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        assert json == {'user_id': logged_user_id}

    async def test_get_single_unauthenticated(self, api):
        response = await api.get('/api/auth')
        text = await response.text()
        assert response.status == 401, text

    async def test_logout(self, api, session):
        response = await api.delete('/api/auth')
        text = await response.text()
        assert response.status == 204, text
        assert 'user_id' not in session


@pytest.fixture
def auth_data(db_user, user_data):
    return {
        'email': db_user['email'],
        'password': user_data['password'],
    }
