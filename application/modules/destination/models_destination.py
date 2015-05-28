__author__ = 'wilrona'


from google.appengine.ext import ndb

class DestinationModel(ndb.Model):
    code = ndb.StringProperty() # code de la ville
    name = ndb.StringProperty() # nom de la ville