import datetime

from aiohttp_apispec import (
    setup_aiohttp_apispec,
    validation_middleware,
    validation_middleware,
)
from aiohttp_swagger import setup_swagger
import motor.motor_asyncio
from aiohttp_session import SimpleCookieStorage, session_middleware

from aiohttp_demo.lib.uid_generator import UIDGenerator
from aiohttp_demo.auth.controller import Auth
from .user.repositories import UserRepository
from .link.repositories import LinkRepository
from .user.routes import configure as cfg_user
from .link.routes import configure as cfg_link
from .auth.routes import configure as cfg_auth


async def setup(app, config):
    cli = motor.motor_asyncio.AsyncIOMotorClient(config['mongo_uri'])
    db = getattr(cli, config['mongo_db'])

    auth = Auth('user_id', 'last_activity', datetime.timedelta(minutes=15))

    collection_users = db[config['mongo_collection_users']]
    user_repo = UserRepository(collection_users)
    await user_repo.configure()

    collection_links = db[config['mongo_collection_links']]
    link_repo = LinkRepository(collection_links)
    await link_repo.configure()

    collection_counter = db[config['mongo_collection_counter']]
    uid_generator = UIDGenerator(collection_counter, 'links')
    await uid_generator.configure()

    app.add_routes(cfg_user(user_repo, auth))
    app.add_routes(cfg_link(link_repo, auth, uid_generator))
    app.add_routes(cfg_auth(user_repo, auth))

    # aiohttp-apispec
    setup_aiohttp_apispec(app)
    app.middlewares.append(validation_middleware)

    # swagger web ui
    async def swagger(app):
        setup_swagger(
            app=app, swagger_url="/api/doc", swagger_info=app["swagger_dict"]
        )

    app.on_startup.append(swagger)

    # TODO: encrypted cookie and session storage
    app.middlewares.append(session_middleware(SimpleCookieStorage()))
    app.middlewares.append(auth.middleware)

    return app
