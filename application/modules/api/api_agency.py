__author__ = 'Vercossa'

from api_function import *
from ..agency.models_agency import AgencyModel
# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route("/agency/get/<token>")
def get_agency_api(token):

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    data = {}
    data['status'] = 200
    data['agency'] = get_agency.make_to_dict()
    resp = jsonify(data)
    return resp