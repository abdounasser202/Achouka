# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..vessel.models_vessel import VesselModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/vessel/get/<token>")
def get_vessel_api(token):

    try:
        date = function.date_convert(request.args.get('last_update'))
    except:
        date = None

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    if date:
        get_vessel = VesselModel().query(
            VesselModel.date_update >= date
        )
    else:
        get_vessel = VesselModel().query()

    data = {}
    data['status'] = 200
    data['vessel'] = []
    for vessel in get_vessel:
        data['vessel'].append(vessel.make_to_dict())
    resp = jsonify(data)
    return resp
