# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..ticket_type.models_ticket_type import ClassTypeModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/class/get/<token>")
def get_class_api(token):

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found()

    get_class = ClassTypeModel().query()
    data = {}
    data['status'] = 200
    data['class'] = []
    for _class in get_class:
        data['class'].append(_class.make_to_dict())
    resp = jsonify(data)
    return resp
