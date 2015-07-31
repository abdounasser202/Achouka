# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..profil.models_profil import ProfilModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/profil/get/<token>")
def get_profil_api(token):

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    get_profil = ProfilModel().query()
    data = {}
    data['status'] = 200
    data['profils'] = []
    for profil in get_profil:
        data['profils'].append(profil.make_to_dict())
    resp = jsonify(data)
    return resp
