__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..destination.models_destination import DestinationModel
from ..currency.models_currency import CurrencyModel

class AgencyModel(ndb.Model):
    name = ndb.StringProperty(required=True)
    country = ndb.StringProperty()
    phone = ndb.StringProperty()
    fax = ndb.StringProperty()
    address = ndb.StringProperty()
    reduction = ndb.FloatProperty()
    agency = ndb.IntegerProperty()
    status = ndb.BooleanProperty(default=False)
    destination = ndb.KeyProperty(kind=DestinationModel)
    currency = ndb.KeyProperty(kind=CurrencyModel)