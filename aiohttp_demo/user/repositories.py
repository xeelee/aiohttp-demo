from pymongo.errors import DuplicateKeyError

from aiohttp_demo.lib.repository.mixins import CollectionBase
from aiohttp_demo.exceptions import Duplicate


class UserRepository(CollectionBase):

    async def create(self, email, password):
        data = {
            'email': email,
            'password': password,
        }
        try:
            result = await self._collection.insert_one(data)
        except DuplicateKeyError:
            doc = await self._collection.find_one({'email': email})
            raise Duplicate(doc['_id'])
        return result.inserted_id

    async def find_by_email(self, email: str):
        doc = await self._collection.find_one({'email': email})
        return doc


    async def configure(self):
        await self._collection.create_index('email', unique=True)
