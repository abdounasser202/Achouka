# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..user.models_user import RoleModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/get_role_api")
def get_role_api():
    
    get_role = RoleModel().query()
    data = {}
    for role in get_role:
        data[role.key.id()] = role.make_to_dict()
    resp = jsonify(data)
    return resp
