# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..ticket_type.models_ticket_type import JourneyTypeModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/journey/get/<token>")
def get_journey_api(token):

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    get_journey = JourneyTypeModel().query()
    data = {}
    data['status'] = 200
    data['journey'] = []
    for journey in get_journey:
        data['journey'].append(journey.make_to_dict())
    resp = jsonify(data)
    return resp
