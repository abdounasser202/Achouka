# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..vessel.models_vessel import VesselModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/get_vessel_api')
def get_vessel_api():

    get_vessel = VesselModel().query()
    data = {}
    for vessel in get_vessel:
        data[vessel.key.id()] = vessel.make_to_dict()
    resp = jsonify(data)
    return resp
        
