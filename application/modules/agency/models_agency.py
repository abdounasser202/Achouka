__author__ = 'wilrona'


from ..custom_model import *
from ..destination.models_destination import DestinationModel


from itertools import groupby
from operator import itemgetter


class AgencyModel(BaseModel):
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
    date_update = ndb.DateProperty(auto_now=True)

    def make_to_dict(self):
        to_dict = {}
        to_dict['agency_id'] = self.key.id()
        to_dict['agency_name'] = self.name
        to_dict['agency_country'] = self.country
        to_dict['agency_phone'] = self.phone
        to_dict['agency_fax'] = self.fax
        to_dict['agency_address'] = self.address
        to_dict['agency_reduction'] = self.reduction
        to_dict['agency_status'] = self.status
        to_dict['agency_is_achouka'] = self.is_achouka
        to_dict['agency_destination'] = self.destination.id()
        return to_dict

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
            TicketModel.selling == False,
            TicketModel.is_count == True,
            TicketModel.is_upgrade == False
        ).count()

        if ticket <= 1:
            title = 'ticket'
        else:
            title = ' tickets'

        return str(ticket)+' '+str(title)

    def DateLastPurchase(self):
        from ..ticket.models_ticket import TicketModel

        ticket = TicketModel.query(
            TicketModel.agency == self.key,
            TicketModel.is_count == True,
            TicketModel.is_upgrade == False
        ).order(-TicketModel.datecreate)

        ticket = ticket.get()

        if ticket:
            date = ticket.datecreate
        else:
            date = None

        return date

    def escrow_amount(self, value=False):
        from ..transaction.models_transaction import TransactionModel

        entry_query = TransactionModel.query(
            TransactionModel.is_payment == True,
            TransactionModel.agency == self.key,
            TransactionModel.transaction_admin == value,
            TransactionModel.destination == self.destination
        )

        entry_amount = 0
        for entry in entry_query:
            entry_amount += entry.amount

        expense_query = TransactionModel.query(
            TransactionModel.is_payment == False,
            TransactionModel.agency == self.key,
            TransactionModel.transaction_admin == False,
            TransactionModel.destination == self.destination
        )

        expense_amount = 0
        for expense in expense_query:
            expense_amount += expense.amount

        escrow = entry_amount - expense_amount

        return escrow

    # Difference de montant pour savoir combien, il y'a a verser et combien verse
    def difference_amount(self):
        difference = self.escrow_amount() - self.escrow_amount(True)
        return difference

    def difference_amount_foreign(self):
        from ..transaction.models_transaction import TransactionModel

        destination_transaction_query = TransactionModel.query(
            TransactionModel.agency == self.key,
            TransactionModel.destination != self.destination
        )

        destinations_table = []
        for transaction in destination_transaction_query:

            entry_query_manager = TransactionModel.query(
                TransactionModel.is_payment == True,
                TransactionModel.agency == self.key,
                TransactionModel.transaction_admin == False,
                TransactionModel.destination == transaction.destination
            )

            # SOMMES DES ENTRES
            entry_amount_manger = 0
            for entry in entry_query_manager:
                entry_amount_manger += entry.amount


            entry_query_admin = TransactionModel.query(
                TransactionModel.is_payment == True,
                TransactionModel.agency == self.key,
                TransactionModel.transaction_admin == True,
                TransactionModel.destination == transaction.destination
            )

            # SOMMES DES ENTRES
            entry_amount_admin = 0
            for entry in entry_query_admin:
                entry_amount_admin += entry.amount


            expense_query = TransactionModel.query(
                TransactionModel.is_payment == False,
                TransactionModel.agency == self.key,
                TransactionModel.transaction_admin == False,
                TransactionModel.destination == transaction.destination
            )

            # SOMMES DES SORTIES
            expense_amount = 0
            for expense in expense_query:
                expense_amount += expense.amount

            amount_admin = entry_amount_admin - expense_amount
            amount_manager = entry_amount_manger - expense_amount

            amount = amount_manager - amount_admin

            trans_init = {}
            trans_init['amount'] = amount
            trans_init['destination'] = transaction.destination
            trans_init['agency'] = transaction.agency

            destinations_table.append(trans_init)

        grouper = itemgetter("destination", "agency")

        # REGROUPEMENT DES MONTANTS PAR DESTINATION
        difference_amount_foreigns = []
        for key, grp in groupby(sorted(destinations_table, key=grouper), grouper):
            temp_dict = dict(zip(["destination", "agency"], key))
            temp_dict['amount'] = 0
            for item in grp:
                temp_dict['amount'] = item['amount']
            difference_amount_foreigns.append(temp_dict)

        return difference_amount_foreigns


    # Montant des tickets etrangers (defaut POS, True = Agency)
    def escrow_amount_foreign(self, value=False):
        from ..transaction.models_transaction import TransactionModel

        destination_transaction_query = TransactionModel.query(
            TransactionModel.agency == self.key,
            TransactionModel.destination != self.destination
        )

        destinations_table = []
        for transaction in destination_transaction_query:

            entry_query = TransactionModel.query(
                TransactionModel.is_payment == True,
                TransactionModel.agency == self.key,
                TransactionModel.transaction_admin == value,
                TransactionModel.destination == transaction.destination
            )

            # SOMMES DES ENTRES
            entry_amount = 0
            for entry in entry_query:
                entry_amount += entry.amount

            expense_query = TransactionModel.query(
                TransactionModel.is_payment == False,
                TransactionModel.agency == self.key,
                TransactionModel.transaction_admin == False,
                TransactionModel.destination == transaction.destination
            )

            # SOMMES DES SORTIES
            expense_amount = 0
            for expense in expense_query:
                expense_amount += expense.amount

            # TOTAL RETENU
            amount = entry_amount - expense_amount

            trans_init = {}
            trans_init['amount'] = amount
            trans_init['destination'] = transaction.destination
            trans_init['agency'] = transaction.agency

            destinations_table.append(trans_init)

        grouper = itemgetter("destination", "agency")

        # REGROUPEMENT DES MONTANTS PAR DESTINATION
        escrow_amount_foreigns = []
        for key, grp in groupby(sorted(destinations_table, key=grouper), grouper):
            temp_dict = dict(zip(["destination", "agency"], key))
            temp_dict['amount'] = 0
            for item in grp:
                temp_dict['amount'] = item['amount']
            escrow_amount_foreigns.append(temp_dict)

        return escrow_amount_foreigns
