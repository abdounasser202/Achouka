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
    status = ndb.BooleanProperty(default=True)
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