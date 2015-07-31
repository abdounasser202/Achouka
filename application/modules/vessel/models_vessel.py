__author__ = 'wilrona'


from google.appengine.ext import ndb


class VesselModel(ndb.Model):
    name = ndb.StringProperty(required=True)
    capacity = ndb.IntegerProperty(required=True)
    immatricul = ndb.StringProperty()
    date_update = ndb.DateProperty(auto_now=True)
    
    def make_to_dict(self):
        to_dict = {}
        to_dict['vessel_id'] = self.key.id()
        to_dict['vessel_name'] = self.name
        to_dict['vessel_capacity'] = self.capacity
        to_dict['vessel_immatricul'] = self.immatricul
        return to_dict  
