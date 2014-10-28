from sqlalchemy.orm.interfaces import MapperExtension
from datetime import datetime


class TimestampExtension(MapperExtension):

    def before_insert(self, mapper, connection, instance):
        instance.created_at = datetime.now()

    def before_update(self, mapper, connection, instance):
        instance.updated_at = datetime.now()
