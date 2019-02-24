import datetime
from bson.objectid import ObjectId
from aiohttp_demo.lib.repository.mixins import CollectionBase


class LinkRepository(CollectionBase):

    async def create(
            self, url: str, shortcut: str,
            user_id: ObjectId, is_public: bool):
        now = datetime.datetime.utcnow()
        data = {
            'url': url,
            'shortcut': shortcut,
            'created_by': user_id,
            'created_at': now,
            'updated_at': now,
            'is_public': is_public,
        }
        result = await self._collection.insert_one(data)
        return result.inserted_id

    async def find_by_shortcut(self, shortcut):
        doc = await self._collection.find_one({'shortcut': shortcut})
        return doc

    def find_many_public_factory(self, is_public: bool):
        return lambda query: self._collection.find(
            {**{'is_public': is_public}, **query})

    def find_many_for_user_factory(self, user_id: str):
        def _find(query):
            return self._collection.find(
                {**{'created_by': ObjectId(user_id)}, **query})
        return _find
    
    async def configure(self):
        await self._collection.create_index('created_by')
        await self._collection.create_index('shortcut')
        await self._collection.create_index(
            'expires_at', expireAfterSeconds=0)
