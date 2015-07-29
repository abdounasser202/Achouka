__author__ = 'wilrona'


from google.appengine.ext import ndb
from ..currency.models_currency import CurrencyModel


class DestinationModel(ndb.Model):
    code = ndb.StringProperty() # code de la ville
    name = ndb.StringProperty() # nom de la ville
    currency = ndb.KeyProperty(kind=CurrencyModel)

    def make_to_dict(self):
        to_dict = {}
        to_dict['destination_id'] = self.key.id()
        to_dict['destination_code'] = self.code
        to_dict['destination_name'] = self.name
        to_dict['destination_currency'] = {
            "currency_id": self.currency.id(),
            "currency_name": self.currency.get().name,
            "currency_code": self.currency.get().code
        }
        return to_dict