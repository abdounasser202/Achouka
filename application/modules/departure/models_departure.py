__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..travel.models_travel import TravelModel
from ..vessel.models_vessel import VesselModel


class DepartureModel(ndb.Model):
    departure_date = ndb.DateProperty()
    schedule = ndb.TimeProperty()
    time_delay = ndb.TimeProperty()
    destination = ndb.KeyProperty(kind=TravelModel)
    vessel = ndb.KeyProperty(kind=VesselModel)
