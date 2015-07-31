# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..travel.models_travel import TravelModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/get_travel_api")
def get_travel_api():
    
    get_travel = TravelModel().query()
    data = {}
    for travel in get_travel:
        data[travel.key.id()] = travel.make_to_dict()
    resp = jsonify(data)
    return resp
