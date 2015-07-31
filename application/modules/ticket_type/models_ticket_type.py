__author__ = 'wilrona'


from google.appengine.ext import ndb
from ..currency.models_currency import CurrencyModel, EquivalenceModel
from ..travel.models_travel import TravelModel


class TicketTypeNameModel(ndb.Model): # category of tickets
    name = ndb.StringProperty()
    is_child = ndb.BooleanProperty(default=False)
    default = ndb.BooleanProperty(default=False)
    special = ndb.BooleanProperty(default=False)
    date_update = ndb.DateProperty(auto_now=True)
    
    def make_to_dict(self):
        to_dict = {}
        to_dict['category_id'] = self.key.id()
        to_dict['category_is_child'] = str(self.is_child)
        to_dict['category_default'] = str(self.default)
        to_dict['category_special'] = str(self.special)        
        return to_dict


class JourneyTypeModel(ndb.Model):
    name = ndb.StringProperty()
    default = ndb.BooleanProperty(default=False)
    returned = ndb.BooleanProperty(default=False)
    date_update = ndb.DateProperty(auto_now=True)
    
    def make_to_dict(self):
        to_dict = {}
        to_dict['journey_id'] = self.key.id()
        to_dict['journey_returned'] = str(self.returned)
        to_dict['journey_default'] = str(self.default)
        to_dict['journey_name'] = self.name        
        return to_dict


class ClassTypeModel(ndb.Model):
    name = ndb.StringProperty()
    default = ndb.BooleanProperty(default=False)
    date_update = ndb.DateProperty(auto_now=True)
    
    def make_to_dict(self):
        to_dict = {}
        to_dict['class_id'] = self.key.id()
        to_dict['class_default'] = str(self.default)
        to_dict['class_name'] = self.name        
        return to_dict


class TicketTypeModel(ndb.Model):
    name = ndb.StringProperty()
    type_name = ndb.KeyProperty(kind=TicketTypeNameModel)
    journey_name = ndb.KeyProperty(kind=JourneyTypeModel)
    class_name = ndb.KeyProperty(kind=ClassTypeModel)
    price = ndb.FloatProperty()
    currency = ndb.KeyProperty(kind=CurrencyModel)
    active = ndb.BooleanProperty(default=False)
    travel = ndb.KeyProperty(kind=TravelModel)
    date_update = ndb.DateProperty(auto_now=True)
    
    def make_to_dict(self):
        to_dict = {}
        to_dict['ticket_id'] = self.key.id()
        to_dict['ticket_name'] = self.name
        to_dict['ticket_type_name'] = self.type_name.id()
        to_dict['ticket_journey_name'] = self.journey_name.id()
        to_dict['ticket_class_name'] = self.class_name.id()
        to_dict['ticket_price'] = str(self.price)
        to_dict['ticket_currency'] = self.currency.id()
        to_dict['ticket_active'] = str(self.active)
        to_dict['ticket_travel'] = self.travel.id()           
        return to_dict

    def get_price(self, current_user):

        #Traitement des prix en fonction de la devise.
        db_currency = CurrencyModel.get_by_id(self.currency.id())
        us_currency = current_user.get_currency_info()


        custom_equi = EquivalenceModel.query(
            EquivalenceModel.currencyRate == db_currency.key,
            EquivalenceModel.currencyEqui == us_currency.key
        ).get()

        if not custom_equi:
            price = self.price
            currency = db_currency.code
        else:
            price = self.price*custom_equi.value
            currency = us_currency.code

        new_price = str(price)+" "+currency

        return new_price
