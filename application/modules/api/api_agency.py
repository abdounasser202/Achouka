__author__ = 'Vercossa'

from api_function import *
from ..agency.models_agency import AgencyModel
# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route("/agency/get/<token>")
def get_agency_api(token):

    try:
        date = function.date_convert(request.args.get('last_update'))
    except:
        date = None

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    if date:
        update_agency = AgencyModel.query(
            AgencyModel.date_update >= date,
            AgencyModel.key == get_agency.key
        ).get()

        if update_agency:
            data = {'status': 200, 'agency': update_agency.make_to_dict()}
            resp = jsonify(data)
            return resp
        else:
            return not_found(message="Agency Not Updated")
    else:
        data = {'status': 200, 'agency': get_agency.make_to_dict()}
        resp = jsonify(data)
        return resp