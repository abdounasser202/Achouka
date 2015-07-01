__author__ = 'wilrona'

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel

from ..agency.models_agency import AgencyModel, DestinationModel
from ..currency.models_currency import CurrencyModel
from ..ticket.models_ticket import TicketModel, UserModel


class TransactionPoly(polymodel.PolyModel):
    reason = ndb.StringProperty()
    amount = ndb.FloatProperty()
    is_payment = ndb.BooleanProperty()
    agency = ndb.KeyProperty(kind=AgencyModel)
    destination = ndb.KeyProperty(kind=DestinationModel)
    transaction_date = ndb.DateTimeProperty()
    user = ndb.KeyProperty(kind=UserModel)


class TransactionModel(TransactionPoly):
    transaction_admin = ndb.BooleanProperty(default=False)


class DetailsTransactionModel(TransactionPoly):
    transaction_parent = ndb.KeyProperty(kind=TransactionModel)


class ExpensePaymentTransactionModel(ndb.Model):
    transaction = ndb.KeyProperty(kind=DetailsTransactionModel)
    ticket = ndb.KeyProperty(kind=TicketModel)
    is_difference = ndb.BooleanProperty(default=False) # si la transaction est different du montant du ticket