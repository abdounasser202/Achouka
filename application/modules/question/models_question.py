__author__ = 'wilrona'

from google.appengine.ext import ndb

class QuestionModel(ndb.Model):
    question = ndb.StringProperty()
    is_pos = ndb.BooleanProperty() # Appartenance
    is_obligate = ndb.BooleanProperty(default=False)
    active = ndb.BooleanProperty(default=True)
    date_update = ndb.DateProperty(auto_now=True)
    
    def make_to_dict(self):
        to_dict = {}
        to_dict['question_id'] = self.key.id()
        to_dict['question_is_pos'] = str(self.is_pos)
        to_dict['question_is_obligate'] = str(self.is_obligate)
        to_dict['question_active'] = str(self.active)        
        return to_dict
