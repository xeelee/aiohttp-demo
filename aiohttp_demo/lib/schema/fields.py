import hashlib

from marshmallow import fields
from bson.objectid import ObjectId


class ObjId(fields.Field):

    def _serialize(self, value, attr, obj, **kwargs):
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):
        return ObjectId(value)


class Password(fields.Field):

    def _serialize(self, value, attr, obj, **kwargs):
        raise NotImplementedError

    def _deserialize(self, value, attr, data, **kwargs):
        # TODO: use secure sha256 with randomly generated salt
        return hashlib.sha1(value.encode()).hexdigest()
