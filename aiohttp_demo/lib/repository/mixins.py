import datetime
from bson.objectid import ObjectId


class CollectionBase:

    OMITTED = object()
    UPDATED_AT = 'updated_at'

    def __init__(self, collection):
        self._collection = collection

    async def find(self, id_: str):
        doc = await self._collection.find_one({'_id': ObjectId(id_)})
        return doc

    async def remove(self, id_: str) -> bool:
        result = await self._collection.delete_one({'_id': ObjectId(id_)})
        return result.deleted_count > 0

    async def update(self, id_: str, **kwargs):
        to_be_updated = {
            k:v for (k, v) in kwargs.items() if not v is self.OMITTED
        }
        to_be_updated[self.UPDATED_AT] = datetime.datetime.utcnow()
        await self._collection.update_one(
            {'_id': ObjectId(id_)},
            {'$set': to_be_updated}
        )
        return await self.find(id_)
