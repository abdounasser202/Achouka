__author__ = 'Vercossa'


from google.appengine.ext import ndb

class CronModel(ndb.Model):
    keys = ndb.IntegerProperty()
    model = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now=True)