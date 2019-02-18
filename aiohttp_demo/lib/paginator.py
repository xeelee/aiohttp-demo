import pymongo
from bson.objectid import ObjectId


class PaginatedResult:

    def __init__(self, items, next_=None):
        self._items = items
        self._next = next_

    def as_dict(self, next_url_formatter):
        result = {
            'result': self._items,
        }
        if self._next is not None:
            result['next'] = next_url_formatter(str(self._next))
        return result


class MongoPaginator:

    def __init__(self, order_by: str):
        self._order_by = order_by

    async def process(
            self, find, query, limit, start_after=None) -> PaginatedResult:
        query_dict = {}
        query_dict.update(query)
        if start_after is not None:
            query_dict.update({'_id': {'$gt': ObjectId(start_after)}})
        cursor = find(query_dict)
        cursor = cursor.limit(limit + 1)
        cursor = cursor.sort([(self._order_by, pymongo.ASCENDING)])
        items = await cursor.to_list(limit + 1)
        if len(items) > limit:
            next_ = items[-2]['_id']
        else:
            next_ = None
        return PaginatedResult(
            items[:limit],
            next_=next_,
        )
