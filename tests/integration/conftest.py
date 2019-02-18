import copy
import time
import hashlib

import pytest
from aiohttp import web
import motor.motor_asyncio

from aiohttp_demo.bootstrap import setup


@pytest.fixture
async def api(aiohttp_client, get_create_app):
    return await aiohttp_client(get_create_app(config))


@pytest.fixture
async def config(db_name_tests):
    cfg = {
        'mongo_uri': 'mongodb://root:toor@mongodb:27017',
        'mongo_db': db_name_tests,
        'mongo_collection_users': 'users',
        'mongo_collection_links': 'links',
        "mongo_collection_counter": "counter",
    }
    return cfg


@pytest.fixture
def collection_users(db, config):
    return db[config['mongo_collection_users']]


@pytest.fixture
def collection_links(db, config):
    return db[config['mongo_collection_links']]


@pytest.fixture
async def db(mongo_cli, config):
    yield getattr(mongo_cli, config['mongo_db'])
    await mongo_cli.drop_database(config['mongo_db'])


@pytest.fixture
def mongo_cli(config):
    return motor.motor_asyncio.AsyncIOMotorClient(config['mongo_uri']) 


@pytest.fixture
def db_name_tests():
    ts = int(time.time())
    return 'aiohttp_demo_tests_{}'.format(ts)


@pytest.fixture
async def app(config):
    return await setup(web.Application(), config)


@pytest.fixture
def get_create_app(app):
    return lambda loop: app


@pytest.fixture
def logged_user_id(db_user, session):
    user_id = str(db_user['_id'])
    session['user_id'] = user_id
    return user_id


@pytest.fixture
def user_data():
    return {
        'email': 'aaa@bbb.com',
        'password': 'some_password',
    }


@pytest.fixture
async def db_user(collection_users, user_data, encrypted_password):
    data = copy.copy(user_data)  # because mongodb driver modifies input data
    data['password'] = encrypted_password
    result = await collection_users.insert_one(data)
    return await collection_users.find_one({'_id': result.inserted_id})


@pytest.fixture
async def db_user_other(collection_users, user_data):
    data = copy.copy(user_data)
    data['email'] = 'xxx@yyy.com'
    result = await collection_users.insert_one(data)
    return await collection_users.find_one({'_id': result.inserted_id})


@pytest.fixture
def password():
    return 'some_password'


@pytest.fixture
def encrypted_password(password):
    return hashlib.sha1(password.encode()).hexdigest()
