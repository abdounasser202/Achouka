# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..ticket_type.models_ticket_type import ClassTypeModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/get_class_api")
def get_class_api():
    
    get_class = ClassTypeModel().query()
    data = {}
    for _class in get_class:
        data[_class.key.id()] = _class.make_to_dict()
    resp = jsonify(data)
    return resp
