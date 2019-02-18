import pytest


class TestUsersResource:

    async def test_create(
            self, api, user_data, collection_users, encrypted_password):
        response = await api.post('/api/user', json=user_data)
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        doc = await collection_users.find_one({'email': user_data['email']})
        assert json == {
            'id': str(doc['_id']),
            'email': user_data['email'],
        }
        assert doc['password'] == encrypted_password 

    async def test_create_existing(
            self, api, user_data, collection_users, db_user):
        response = await api.post('/api/user', json=user_data)
        text = await response.text()
        assert response.status == 409, text

    async def test_get_single(self, api, db_user):
        response = await api.get('/api/user/{}'.format(db_user['_id']))
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        assert json == {
            'id': str(db_user['_id']),
            'email': db_user['email'],
        }

    async def test_get_single_inexistent(self, api, inexistent_user_id):
        response = await api.get('/api/user/{}'.format(inexistent_user_id))
        text = await response.text()
        assert response.status == 404, text


@pytest.fixture
async def inexistent_user_id(collection_users, db_user):
    id_ = db_user['_id']
    await collection_users.delete_one({'_id': db_user['_id']})
    return id_
