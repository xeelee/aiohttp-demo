import json
from typing import List, AsyncGenerator

import aiofiles
from marshmallow import Schema, fields, ValidationError



class ConfigBuilder:

    class InvalidConfig(Exception):
        pass

    def __init__(self, schema: Schema):
        self._schema = schema

    async def build(self, files: List[str]) -> dict:
        output = {}
        async for result in self._gen_results(files):
            output = {**output, **json.loads(result)}
        try:
            return self._schema.load(output)[0]
        except ValidationError as e:
            raise self.InvalidConfig(e)

    async def _gen_results(self, files: List[str]) -> AsyncGenerator[str, None]:
        for file in files:
            async with aiofiles.open(file, mode='r') as f:
                yield await f.read()


class ConfigSchema(Schema):
    debug = fields.Boolean(required=True)
    port = fields.Integer(required=True)
    mongo_uri = fields.String(required=True)
    mongo_db = fields.String(required=True)
    mongo_collection_users = fields.String(required=True)
    mongo_collection_links = fields.String(required=True)
    mongo_collection_counter = fields.String(required=True)
