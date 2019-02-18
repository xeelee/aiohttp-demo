from pymongo import ReturnDocument


class UIDGenerator:

    def __init__(
            self, collection, ns_val,
            ns_key='ns', val_key='val', initial_val=0, step=1):
        self._collection = collection
        self._ns_val = ns_val
        self._ns_key = ns_key
        self._val_key = val_key
        self._initial_val = initial_val
        self._step = step

    async def gen_uid(self) -> int:
        result = await self._collection.find_one_and_update(
            {self._ns_key: self._ns_val},
            {'$inc': {self._val_key: self._step}},
            return_document=ReturnDocument.AFTER
        )
        return result[self._val_key]

    async def configure(self):
        await self._collection.update_one(
            {self._ns_key: self._ns_val},
            {
                '$set': {
                    self._ns_key: self._ns_val,
                    self._val_key: self._initial_val,
                }
            },
            upsert=True
        )
        await self._collection.create_index(self._ns_key, unique=True)
