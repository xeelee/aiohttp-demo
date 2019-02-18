from marshmallow import Schema, fields, validate

from aiohttp_demo.lib.schema.mixins import WithID
from aiohttp_demo.lib.schema.fields import ObjId

from .fields import Expiration


class LinkBase(Schema):
    url = fields.Url(required=True)
    is_public = fields.Bool(default=False, missing=False)


class Link(LinkBase, WithID):
    shortcut = fields.Str(required=True)
    created_by = ObjId(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    expires_at = fields.DateTime(required=True)


class LinkCreate(LinkBase):
    pass


class LinkUpdate(Schema):
    is_public = fields.Bool()
    expiration = Expiration(
        validate=validate.OneOf(Expiration.CHOICES.keys()))


class PaginatedLinkResult(Schema):
    next = fields.Str()
    result = fields.List(fields.Nested(Link), required=True)


class LinkQuery(Schema):
    limit = fields.Integer(
        required=True, validate=validate.Range(min=1, max=250))
