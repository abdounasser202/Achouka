__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..agency.models_agency import AgencyModel, DestinationModel
from ..currency.models_currency import CurrencyModel
from ..ticket.models_ticket import TicketModel, UserModel


class TransactionModel(ndb.Model):
    reason = ndb.StringProperty()
    amount = ndb.FloatProperty()
    is_payment = ndb.BooleanProperty()
    agency = ndb.KeyProperty(kind=AgencyModel)
    destination = ndb.KeyProperty(kind=DestinationModel)
    transaction_admin = ndb.BooleanProperty(default=False)
    transaction_date = ndb.DateTimeProperty()
    user = ndb.KeyProperty(kind=UserModel)


class DetailsTransactionModel(ndb.Model):
    transaction_parent = ndb.KeyProperty(kind=TransactionModel)
    transaction_child = ndb.KeyProperty(kind=TransactionModel)
    amount = ndb.FloatProperty()


class ExpensePaymentTransactionModel(ndb.Model):
    transaction = ndb.KeyProperty(kind=TransactionModel)
    ticket = ndb.KeyProperty(kind=TicketModel)
    is_difference = ndb.BooleanProperty(default=False) # si la transaction est different du montant du ticket