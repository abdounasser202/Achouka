# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..destination.models_destination import DestinationModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/get_destination_api")
def get_destination_api():
    
    get_destination = DestinationModel().query()
    data = {}
    for destination in get_destination:
        data[destination.key.id()] = destination.make_to_dict()
    resp = jsonify(data)
    return resp
