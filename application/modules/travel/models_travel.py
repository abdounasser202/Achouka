__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..destination.models_destination import DestinationModel

class TravelModel(ndb.Model):
    time = ndb.TimeProperty()
    destination_start = ndb.KeyProperty(kind=DestinationModel)
    destination_check = ndb.KeyProperty(kind=DestinationModel)
    datecreate = ndb.DateTimeProperty(auto_now_add=True)
    date_update = ndb.DateProperty(auto_now=True)
    
    def make_to_dict(self):
        to_dict = {}
        to_dict['travel_id'] = self.key.id()
        to_dict['travel_time'] = str(self.time)
        to_dict['travel_start'] = self.destination_start.id()
        to_dict['travel_check'] = self.destination_check.id()        
        return to_dict
