# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..departure.models_departure import DepartureModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/departure/get/<token>')
def get_departure_api():
    
    get_departure = DepartureModel().query()
    data = {}
    data['status'] = 200
    for departure in get_departure:
        data['departure'] = departure.make_to_dict()
    resp = jsonify(data)
    return resp
