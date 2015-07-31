__author__ = 'wilrona'


from google.appengine.ext import ndb


class CurrencyModel(ndb.Model):
    code = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    date_update = ndb.DateProperty(auto_now=True)
    
    def make_to_dict(self):
        to_dict = {}
        to_dict['currency_id'] = self.key.id()
        to_dict['currency_name'] = self.name
        to_dict['currency_code'] = self.code
        return to_dict


class EquivalenceModel(ndb.Model):
    currencyRate = ndb.KeyProperty(kind=CurrencyModel)
    value = ndb.FloatProperty(required=True)
    currencyEqui = ndb.KeyProperty(kind=CurrencyModel)
