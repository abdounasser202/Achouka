# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..ticket_type.models_ticket_type import TicketTypeNameModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/get_category_api")
def get_category_api():
    
    get_category = TicketTypeNameModel().query()
    data = {}
    for category in get_category:
        data[category.key.id()] = category.make_to_dict()
    resp = jsonify(data)
    return resp
