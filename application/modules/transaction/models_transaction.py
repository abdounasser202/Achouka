__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..agency.models_agency import AgencyModel
from ..currency.models_currency import CurrencyModel
from ..ticket.models_ticket import TicketModel


class TransactionModel(ndb.Model):
    reason = ndb.StringProperty()
    amount = ndb.FloatProperty()
    is_payment = ndb.BooleanProperty()
    agency = ndb.KeyProperty(kind=AgencyModel)
    currency = ndb.KeyProperty(kind=CurrencyModel)
    transaction_date = ndb.DateTimeProperty(auto_now_add=True)


class DetailsTransactionModel(ndb.Model):
    transaction_parent = ndb.KeyProperty(kind=TransactionModel)
    transaction_child = ndb.KeyProperty(kind=TransactionModel)
    amount = ndb.FloatProperty()


class ExpensePaymentTransactionModel(ndb.Model):
    transaction = ndb.KeyProperty(kind=TransactionModel)
    ticket = ndb.KeyProperty(kind=TicketModel)
    is_difference = ndb.BooleanProperty(default=False)