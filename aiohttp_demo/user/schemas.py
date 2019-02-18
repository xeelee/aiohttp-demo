from marshmallow import Schema, fields

from aiohttp_demo.lib.schema.mixins import WithID
from aiohttp_demo.lib.schema.fields import Password


class UserBase(Schema):
    email = fields.Email(required=True)


class User(UserBase, WithID):
    email = fields.Email(required=True)


class UserCreate(UserBase):
    password = Password(required=True)
