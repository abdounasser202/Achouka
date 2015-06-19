__author__ = 'wilrona'

from google.appengine.ext import ndb

from ..user.models_user import UserModel
from ..agency.models_agency import AgencyModel
from ..currency.models_currency import CurrencyModel, EquivalenceModel
from ..customer.models_customer import CustomerModel
from ..departure.models_departure import DepartureModel, TravelModel
from ..ticket_type.models_ticket_type import ClassTypeModel, TicketTypeNameModel, JourneyTypeModel
from ..question.models_question import QuestionModel

class TicketModel(ndb.Model):

    sellpriceAg = ndb.FloatProperty()
    sellpriceAgCurrency = ndb.KeyProperty(kind=CurrencyModel)

    type_name = ndb.KeyProperty(kind=TicketTypeNameModel)
    class_name = ndb.KeyProperty(kind=ClassTypeModel)
    journey_name = ndb.KeyProperty(kind=JourneyTypeModel)
    travel_type_ticket = ndb.KeyProperty(kind=TravelModel)

    agency = ndb.KeyProperty(kind=AgencyModel)
    is_prepayment = ndb.BooleanProperty(default=True)
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

    datecreate = ndb.DateTimeProperty()

    def get_price_sell(self, current_user):

        #Traitement des prix en fonction de la devise.
        db_currency = CurrencyModel.get_by_id(self.sellpriceCurrency.id())
        us_currency = current_user.get_currency_info()


        custom_equi = EquivalenceModel.query(
            EquivalenceModel.currencyRate == db_currency.key,
            EquivalenceModel.currencyEqui == us_currency.key
        ).get()

        if not custom_equi:
            price = self.sellprice
            currency = db_currency.code
        else:
            price = self.sellprice*custom_equi.value
            currency = us_currency.code

        new_price = str(price)+" "+currency

        return new_price


class TicketQuestion(ndb.Model):
    question_id = ndb.KeyProperty(kind=QuestionModel)
    ticket_id = ndb.KeyProperty(kind=TicketModel)
    response = ndb.BooleanProperty(default=False)
