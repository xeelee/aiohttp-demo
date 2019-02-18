import sys
import logging
import asyncio

from aiohttp import web

from aiohttp_demo.bootstrap import setup
from aiohttp_demo.config import ConfigBuilder, ConfigSchema


def build_config(loop):
    try:
        return loop.run_until_complete(
            ConfigBuilder(ConfigSchema(strict=True)).build(sys.argv[1:]))
    except ConfigBuilder.InvalidConfig as e:
        sys.stderr.write('INVALID CONFIG\n')
        sys.stderr.write('{}\n'.format(e))
        sys.exit(1)


log = logging.getLogger(__file__)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    config = build_config(loop)
    app = loop.run_until_complete(setup(web.Application(), config))
    if config['debug'] is True:
        logging.basicConfig(level=logging.DEBUG)
        import aioreloader
        aioreloader.start()
        logging.debug('Starting application with config: %s', config)
    web.run_app(app, port=config['port'])
