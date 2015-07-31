# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..ticket_type.models_ticket_type import JourneyTypeModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/get_journey_api")
def get_journey_api():
    
    get_journey = JourneyTypeModel().query()
    data = {}
    for journey in get_journey:
        data[journey.key.id()] = journey.make_to_dict()
    resp = jsonify(data)
    return resp
