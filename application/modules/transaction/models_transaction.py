__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..agency.models_agency import AgencyModel
from ..currency.models_currency import CurrencyModel


class TransactionModel(ndb.Model):
    reason = ndb.StringProperty()
    amount = ndb.FloatProperty()
    transaction_date = ndb.DateTimeProperty(auto_now_add=True)
    transaction_type = ndb.IntegerProperty()
    agency = ndb.KeyProperty(kind=AgencyModel)
    currency = ndb.KeyProperty(kind=CurrencyModel)
