__author__ = 'wilrona'

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel

from ..user.models_user import UserModel
from ..agency.models_agency import AgencyModel
from ..currency.models_currency import CurrencyModel, EquivalenceModel
from ..customer.models_customer import CustomerModel
from ..departure.models_departure import DepartureModel, TravelModel
from ..ticket_type.models_ticket_type import ClassTypeModel, TicketTypeNameModel, JourneyTypeModel
from ..question.models_question import QuestionModel


class TicketPoly(polymodel.PolyModel):
    sellpriceAg = ndb.FloatProperty()
    sellpriceAgCurrency = ndb.KeyProperty(kind=CurrencyModel)

    type_name = ndb.KeyProperty(kind=TicketTypeNameModel)
    class_name = ndb.KeyProperty(kind=ClassTypeModel)
    journey_name = ndb.KeyProperty(kind=JourneyTypeModel)
    travel_ticket = ndb.KeyProperty(kind=TravelModel)

    agency = ndb.KeyProperty(kind=AgencyModel)
    is_prepayment = ndb.BooleanProperty(default=True)
    statusValid = ndb.BooleanProperty(default=True)
    is_return = ndb.BooleanProperty(default=False)

    selling = ndb.BooleanProperty(default=False)
    is_ticket = ndb.BooleanProperty()
    date_reservation = ndb.DateTimeProperty()
    sellprice = ndb.FloatProperty()
    sellpriceCurrency = ndb.KeyProperty(kind=CurrencyModel)

    customer = ndb.KeyProperty(kind=CustomerModel)
    departure = ndb.KeyProperty(kind=DepartureModel)

    ticket_seller = ndb.KeyProperty(kind=UserModel)
    e_ticket_seller = ndb.KeyProperty(kind=UserModel)
    is_boarding = ndb.BooleanProperty(default=False)

    datecreate = ndb.DateTimeProperty()

    def make_to_dict_poly(self):
        to_dict = {}
        to_dict['ticket_allocated_id'] = self.key.id()
        to_dict['sellpriceAg'] = self.sellpriceAg
        to_dict['sellpriceAgCurrency'] = self.sellpriceAgCurrency.id()

        to_dict['type_name'] = self.type_name.id()
        to_dict['class_name'] = self.class_name.id()
        to_dict['journey_name'] = self.journey_name.id()
        to_dict['travel_ticket'] = self.travel_ticket.id()

        to_dict['agency'] = self.agency.id()
        to_dict['is_prepayment'] = self.is_prepayment
        to_dict['statusValid'] = self.statusValid
        to_dict['is_return'] = self.is_return

        to_dict['selling'] = self.selling
        to_dict['is_ticket'] = self.is_ticket

        if self.customer:
            to_dict['customer'] = self.customer.id()
        if self.departure:
            to_dict['departure'] = self.departure.id()

        return to_dict


class TicketModel(TicketPoly):
    upgrade_parent = ndb.KeyProperty(kind=TicketPoly)
    is_upgrade = ndb.BooleanProperty(default=False)
    is_count = ndb.BooleanProperty(default=True)
    parent_return = ndb.KeyProperty(kind=TicketPoly)

    def answer_question(self):
        answer = TicketQuestion.query(
            TicketQuestion.ticket_id == self.key
        )
        return answer

    def make_to_dict(self):
        to_dict = self.make_to_dict_poly()

        to_dict['child_upgrade'] = []
        if self.is_upgrade:
            to_dict['is_upgrade'] = self.is_upgrade
            to_dict['upgrade_parent'] = self.upgrade_parent.id()
        else:

            child = TicketModel.query(
                TicketModel.upgrade_parent == self.key.id()
            )
            for child in child:
                to_dict['child_upgrade'].append(child.make_to_dict())

        to_dict['child_return'] = []
        if self.parent_return:
            to_dict['parent_return'] = self.parent_return.id()
            to_dict['is_count'] = self.is_count
        else:
            if not self.is_upgrade:
                child = TicketModel.query(
                    TicketModel.parent_return == self.key.id()
                )
                for child in child:
                    to_dict['child_return'].append(child.make_to_dict())

        return to_dict


# class TicketParent(TicketPoly): #TICKET VIRTUEL GENERE PAR UN TICKET ALLE ET RETOUR. IL N'EST PAS COMPTABILISE
# parent = ndb.KeyProperty(kind=TicketModel)

class TicketQuestion(ndb.Model):
    question_id = ndb.KeyProperty(kind=QuestionModel)
    ticket_id = ndb.KeyProperty(kind=TicketModel)
    response = ndb.BooleanProperty(default=False)
