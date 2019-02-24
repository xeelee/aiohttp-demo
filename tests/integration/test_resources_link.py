import copy
import datetime

import pytest
from freezegun import freeze_time
from bson.objectid import ObjectId


NOW = datetime.datetime(
    2018, 2, 17, 14, 25, 12, tzinfo=datetime.timezone.utc)


@freeze_time(NOW)
class TestUsersResource:

    async def test_redirect(self, api, db_link):
        response = await api.get(
            '/{}'.format(db_link['shortcut']), allow_redirects=False)
        text = await response.text()
        assert response.status == 301, text
        assert response.headers['Location'] == db_link['url']

    async def test_redirect_inexistent(self, api, inexistent_link_shortcut):
        response = await api.get(
            '/{}'.format(inexistent_link_shortcut), allow_redirects=False)
        text = await response.text()
        assert response.status == 404, text

    async def test_create(
            self, api, link_data_minimal, collection_links, logged_user_id):
        response = await api.post('/api/link', json=link_data_minimal)
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        doc = await collection_links.find_one(
            {'url': link_data_minimal['url']})
        assert json == {
            'id': str(doc['_id']),
            'url': link_data_minimal['url'],
            'shortcut': '867nv',  # for uid=1
            'created_by': logged_user_id,
            'created_at': NOW.isoformat(),
            'updated_at': NOW.isoformat(),
            'is_public': True,
        }
        assert doc['created_by'] == ObjectId(logged_user_id)

    async def test_create_unauthenticated(
            self, api, link_data_minimal, collection_links):
        response = await api.post('/api/link', json=link_data_minimal)
        text = await response.text()
        assert response.status == 401, text

    async def test_update(self, api, db_link, logged_user_id):
        data = {
            'is_public': False,
            'expiration': '1h'
        }
        response = await api.put(
            '/api/link/{}'.format(db_link['_id']), json=data)
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        assert json['is_public'] is False
        assert json['expires_at'] == '2018-02-17T15:25:12+00:00'

    async def test_update_single_value(self, api, db_link, logged_user_id):
        data = {
            'expiration': '12h'
        }
        response = await api.put(
            '/api/link/{}'.format(db_link['_id']), json=data)
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        assert json['is_public'] is True
        assert json['expires_at'] == '2018-02-18T02:25:12+00:00'

    async def test_update_invalid_value(self, api, db_link, logged_user_id):
        data = {
            'expiration': 'xxx'
        }
        response = await api.put(
            '/api/link/{}'.format(db_link['_id']), json=data)
        text = await response.text()
        assert response.status == 422, text

    async def test_update_unauthenticated(self, api, db_link):
        data = {
            'is_public': False,
            'expiration': '1h'
        }
        response = await api.put(
            '/api/link/{}'.format(db_link['_id']), json=data)
        text = await response.text()
        assert response.status == 401, text

    async def test_update_other_user(
            self, api, db_link_other_user, logged_user_id):
        data = {
            'is_public': False,
            'expiration': '1h'
        }
        response = await api.put(
            '/api/link/{}'.format(db_link_other_user['_id']), json=data)
        text = await response.text()
        assert response.status == 403, text

    async def test_update_inexistent(
            self, api, inexistent_link_id, logged_user_id):
        data = {
            'is_public': False,
            'expiration': '1h'
        }
        response = await api.put(
            '/api/link/{}'.format(inexistent_link_id), json=data)
        text = await response.text()
        assert response.status == 404, text

    async def test_remove(self, api, db_link, logged_user_id):
        response = await api.delete('/api/link/{}'.format(db_link['_id']))
        text = await response.text()
        assert response.status == 204, text

    async def test_remove_other_user(
            self, api, db_link_other_user, logged_user_id):
        response = await api.delete(
            '/api/link/{}'.format(db_link_other_user['_id']))
        text = await response.text()
        assert response.status == 403, text

    async def test_remove_unauthenticated(self, api, db_link):
        response = await api.delete('/api/link/{}'.format(db_link['_id']))
        text = await response.text()
        assert response.status == 401, text

    async def test_remove_inexistent(
            self, api, inexistent_link_id, logged_user_id):
        response = await api.delete('/api/link/{}'.format(inexistent_link_id))
        text = await response.text()
        assert response.status == 404, text

    async def test_get_single(self, api, db_link, db_user):
        response = await api.get('/api/link/{}'.format(db_link['_id']))
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        assert json == {
            'id': str(db_link['_id']),
            'url': db_link['url'],
            'shortcut': 'some_shortcut',
            'created_by': str(db_user['_id']),
            'created_at': NOW.isoformat(),
            'updated_at': NOW.isoformat(),
            'is_public': True,
        }

    async def test_get_single_inexistent(self, api, inexistent_link_id):
        response = await api.get('/api/link/{}'.format(inexistent_link_id))
        text = await response.text()
        assert response.status == 404, text

    async def test_get_list(self, api, db_link):
        response = await api.get('/api/link?limit=10')
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        assert json == {
            'result': [
                {
                    'id': str(db_link['_id']),
                    'url': db_link['url'],
                    'shortcut': 'some_shortcut',
                    'created_by': str(db_link['created_by']),
                    'created_at': NOW.isoformat(),
                    'updated_at': NOW.isoformat(),
                    'is_public': True,
                }
            ]
        }

    async def test_get_list_for_user(self, api, db_link, logged_user_id):
        response = await api.get('/api/link-user/{}?limit=10'.format(
            logged_user_id
        ))
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        assert len(json['result']) == 1
        assert json['result'][0]['created_by'] == logged_user_id

    async def test_get_list_for_user_different_id(
            self, api, db_link, logged_user_id, db_user_other):
        another_user_id = str(db_user_other['_id'])
        response = await api.get('/api/link-user/{}?limit=10'.format(
            another_user_id
        ))
        text = await response.text()
        assert response.status == 403, text

    async def test_get_list_for_user_unauthenticated(self, api, db_link):
        response = await api.get('/api/link-user/{}?limit=10'.format(
            str(db_link['created_by'])
        ))
        text = await response.text()
        assert response.status == 401, text

    async def test_get_list_page_first(self, api, sorted_db_links):
        response = await api.get('/api/link?limit=3')
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        last = str(sorted_db_links[2]['_id'])
        assert json['next'] == '/api/link/last/{}?limit=3'.format(
            last
        )
        assert [x['id'] for x in json['result']] == [
            str(x['_id']) for x in sorted_db_links[:3]
        ]

    async def test_get_list_page_second(self, api, sorted_db_links):
        response = await api.get('/api/link/last/{}?limit=3'.format(
            sorted_db_links[2]['_id']
        ))
        text = await response.text()
        assert response.status == 200, text
        json = await response.json()
        assert 'next' not in json
        assert len(json['result']) == 2
        assert [x['id'] for x in json['result']] == [
            str(x['_id']) for x in sorted_db_links[3:]
        ]


@pytest.fixture
async def db_link(collection_links, link_data):
    data = copy.copy(link_data)
    result = await collection_links.insert_one(data)
    return await collection_links.find_one({'_id': result.inserted_id})


@pytest.fixture
async def db_link_other_user(collection_links, link_data, db_user_other):
    data = copy.copy(link_data)
    data['created_by'] = db_user_other['_id']
    result = await collection_links.insert_one(data)
    return await collection_links.find_one({'_id': result.inserted_id})


@pytest.fixture
async def db_links(collection_links, link_data):
    links = []
    for x in range(5):
        data = copy.copy(link_data)
        data['updated_at'] = NOW + datetime.timedelta(minutes=x+1)
        result = await collection_links.insert_one(data)
        link = await collection_links.find_one({'_id': result.inserted_id})
        links.append(link)
    return links


@pytest.fixture
def sorted_db_links(db_links):
    return sorted(
        db_links,
        key=lambda x: x['_id'],
    )


@pytest.fixture
async def inexistent_link_id(collection_links, db_link):
    id_ = db_link['_id']
    await collection_links.delete_one({'_id': db_link['_id']})
    return id_


@pytest.fixture
async def inexistent_link_shortcut(collection_links, db_link):
    shortcut = db_link['shortcut']
    await collection_links.delete_one({'_id': db_link['_id']})
    return shortcut


@pytest.fixture
def link_data(link_data_minimal, db_user):
    data = {
        'shortcut': 'some_shortcut',
        'created_by': db_user['_id'],
        'created_at': NOW,
        'updated_at': NOW,
    }
    data.update(link_data_minimal)
    return data


@pytest.fixture
def link_data_minimal():
    return {
        'url': 'http://some.testing.url.com/some-page',
        'is_public': True,
    }
