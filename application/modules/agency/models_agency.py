__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..destination.models_destination import DestinationModel
from ..currency.models_currency import CurrencyModel

class AgencyModel(ndb.Model):
    name = ndb.StringProperty()
    country = ndb.StringProperty()
    phone = ndb.StringProperty()
    fax = ndb.StringProperty()
    address = ndb.StringProperty()
    reduction = ndb.FloatProperty()
    status = ndb.BooleanProperty(default=False)
    destination = ndb.KeyProperty(kind=DestinationModel)
    is_achouka = ndb.BooleanProperty()
    is_coorporate = ndb.BooleanProperty()

    def TicketCount(self):
        from ..ticket.models_ticket import TicketModel

        ticket = TicketModel.query(
            TicketModel.agency == self.key
        ).count()

        if ticket <= 1:
            title = 'ticket'
        else:
            title = ' tickets'

        return str(ticket)+' '+title

    def TicketUnsold(self):
        from ..ticket.models_ticket import TicketModel

        ticket = TicketModel.query(
            TicketModel.agency == self.key,
            TicketModel.selling == False
        ).count()

        if ticket <= 1:
            title = 'ticket'
        else:
            title = ' tickets'

        return str(ticket)+' '+str(title)

    def DateLastPurchase(self):
        from ..ticket.models_ticket import TicketModel

        ticket = TicketModel.query(
            TicketModel.agency == self.key
        ).order(-TicketModel.datecreate)

        ticket = ticket.get()

        if ticket:
            date = ticket.datecreate
        else:
            date = None

        return date

    def escrow_amount_employee(self):
        from ..transaction.models_transaction import TransactionModel

        entry_query = TransactionModel.query(
            TransactionModel.is_payment == True,
            TransactionModel.agency == self.key,
            TransactionModel.transaction_admin == False
        )

        entry_amount = 0
        for entry in entry_query:
            if self.destination == entry.destination:
                entry_amount += entry.amount

        expense_query = TransactionModel.query(
            TransactionModel.is_payment == False,
            TransactionModel.agency == self.key,
            TransactionModel.transaction_admin == False
        )

        expense_amount = 0
        for expense in expense_query:
            if self.destination == expense.destination:
                expense_amount += expense.amount

        escrow = entry_amount - expense_amount

        return escrow