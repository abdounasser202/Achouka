__author__ = 'wilrona'


from google.appengine.ext import ndb
from ..currency.models_currency import CurrencyModel

class TicketTypeNameModel(ndb.Model):
    name = ndb.StringProperty()
    is_child = ndb.BooleanProperty(default=False)
    default = ndb.BooleanProperty(default=False)
    special = ndb.BooleanProperty(default=False)


class JourneyTypeModel(ndb.Model):
    name = ndb.StringProperty()
    default = ndb.BooleanProperty(default=False)


class ClassTypeModel(ndb.Model):
    name = ndb.StringProperty()
    default = ndb.BooleanProperty(default=False)


class TicketTypeModel(ndb.Model):
    name = ndb.StringProperty()
    type_name = ndb.KeyProperty(kind=TicketTypeNameModel)
    journey_name = ndb.KeyProperty(kind=JourneyTypeModel)
    class_name = ndb.KeyProperty(kind=ClassTypeModel)
    price = ndb.FloatProperty()
    currency = ndb.KeyProperty(kind=CurrencyModel)
    active = ndb.BooleanProperty(default=False)