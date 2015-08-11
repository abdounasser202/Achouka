__author__ = 'wilrona'

from google.appengine.ext import ndb

from ..agency.models_agency import AgencyModel, DestinationModel
from ..ticket.models_ticket import TicketModel, UserModel


class TransactionModel(ndb.Model):
    reason = ndb.StringProperty()
    amount = ndb.FloatProperty()
    is_payment = ndb.BooleanProperty()
    agency = ndb.KeyProperty(kind=AgencyModel)
    destination = ndb.KeyProperty(kind=DestinationModel)
    transaction_date = ndb.DateTimeProperty()
    user = ndb.KeyProperty(kind=UserModel)
    transaction_admin = ndb.BooleanProperty(default=False)

    def relation_parent_child(self):
        relation = ExpensePaymentTransactionModel.query(
            ExpensePaymentTransactionModel.transaction == self.key
        )
        return relation

    def make_to_dict(self):
        to_dict = {}
        to_dict['transaction_id'] = self.key.id()
        to_dict['reason'] = self.reason
        to_dict['amount'] = self.amount
        to_dict['is_payment'] = self.is_payment
        to_dict['agency'] = self.agency.id()
        to_dict['destination'] = self.destination.id()
        to_dict['transaction_date'] = str(self.transaction_date)
        to_dict['user'] = {
            'user_id': self.user.id(),
            'email': self.user.get().email,
            'password': self.user.get().password
        }
        to_dict['transaction_admin'] = self.transaction_admin

        to_dict['relation_parent_child'] = []
        for relation in self.relation_parent_child():
            line = {}
            line['ticket'] = relation.ticket.id()
            line['is_difference'] = relation.is_difference
            line['amount'] = relation.amount
            to_dict['relation_parent_child'].append(line)

        return to_dict


class ExpensePaymentTransactionModel(ndb.Model):
    transaction = ndb.KeyProperty(kind=TransactionModel)
    ticket = ndb.KeyProperty(kind=TicketModel)
    amount = ndb.FloatProperty()
    is_difference = ndb.BooleanProperty(default=False) # si la transaction est different du montant du ticket
