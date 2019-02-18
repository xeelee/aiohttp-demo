from datetime import timedelta

from marshmallow import fields


class Expiration(fields.Field):

    CHOICES = {
        '1h' : timedelta(hours=1),
        '12h': timedelta(hours=12),
        '24h': timedelta(hours=24),
        '7d' : timedelta(days=7),
    }

    def _serialize(self, value, attr, obj, **kwargs):
        raise NotImplementedError

    def deserialize(self, value, attr=None, data=None):
        deserialized = super().deserialize(value, attr=attr, data=data)
        return self.CHOICES[deserialized]
