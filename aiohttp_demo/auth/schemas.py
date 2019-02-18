
from marshmallow import Schema, fields

from aiohttp_demo.lib.schema.fields import Password, ObjId


class AuthLogin(Schema):
    email = fields.Email(required=True)
    password = Password(required=True)


class AuthUser(Schema):
    user_id = ObjId(required=True)
