__author__ = 'wilrona'

from google.appengine.ext import ndb

from ..user.models_user import UserModel
from ..agency.models_agency import AgencyModel
from ..currency.models_currency import CurrencyModel
from ..transaction.models_transaction import TransactionModel
from ..customer.models_customer import CustomerModel
from ..departure.models_departure import DepartureModel
from ..ticket_type.models_ticket_type import ClassTypeModel, TicketTypeNameModel, JourneyTypeModel


class TicketModel(ndb.Model):
    datecreate = ndb.DateTimeProperty(auto_now_add=True)

    sellpriceAg = ndb.FloatProperty()
    sellpriceAgCurrency = ndb.KeyProperty(kind=CurrencyModel)

    type_name = ndb.KeyProperty(kind=TicketTypeNameModel)
    class_name = ndb.KeyProperty(kind=ClassTypeModel)
    journey_name = ndb.KeyProperty(kind=JourneyTypeModel)

    agency = ndb.KeyProperty(kind=AgencyModel)
    payment = ndb.IntegerProperty()
    transaction_in = ndb.KeyProperty(kind=TransactionModel)
    transaction_out = ndb.KeyProperty(kind=TransactionModel)
    statusValid = ndb.BooleanProperty(default=True)

    selling = ndb.BooleanProperty(default=False)
    is_ticket = ndb.BooleanProperty()
    date_reservation = ndb.DateTimeProperty()
    sellprice = ndb.FloatProperty()
    sellpriceCurrency = ndb.KeyProperty(kind=CurrencyModel)

    customer = ndb.KeyProperty(kind=CustomerModel)
    departure = ndb.KeyProperty(kind=DepartureModel)

    ticket_seller = ndb.KeyProperty(kind=UserModel)
    e_ticket_seller = ndb.KeyProperty(kind=UserModel)