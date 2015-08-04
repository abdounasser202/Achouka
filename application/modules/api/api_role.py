# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..user.models_user import RoleModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/role/get/<token>")
def get_role_api(token):

    try:
        date = function.date_convert(request.args.get('last_update'))
    except:
        date = None

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    if date:
        get_role = RoleModel().query(
            RoleModel.date_update >= date
        )
    else:
        get_role = RoleModel().query()

    data = {}
    data['status'] = 200
    data['role'] = []
    for role in get_role:
        data['role'].append(role.make_to_dict())
    resp = jsonify(data)
    return resp
