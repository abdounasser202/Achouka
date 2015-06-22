__author__ = 'wilrona'

from google.appengine.ext import ndb


class CustomerModel(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    birthday = ndb.DateProperty()
    profession = ndb.StringProperty()
    nationality = ndb.StringProperty()
    phone = ndb.StringProperty()
    dial_code = ndb.StringProperty()
    email = ndb.StringProperty()
    status = ndb.BooleanProperty(default=True)
