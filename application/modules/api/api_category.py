# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..ticket_type.models_ticket_type import TicketTypeNameModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route("/category/get/<token>")
def get_category_api(token):

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    get_category = TicketTypeNameModel().query()
    data = {}
    data['status'] = 200
    data['category'] = []
    for category in get_category:
        data['category'].append(category.make_to_dict())
    resp = jsonify(data)
    return resp
