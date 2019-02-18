from marshmallow import Schema

from .fields import ObjId


class WithID(Schema):
    id = ObjId(required=True, attribute='_id')
