# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..profil.models_profil import ProfilModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/profil/get/<token>")
def get_profil_api(token):

    try:
        date = function.date_convert(request.args.get('last_update'))
    except:
        date = None

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    if date:
        get_profil = ProfilModel().query(
            ProfilModel.date_update >= date
        )
    else:
        get_profil = ProfilModel().query()

    data = {}
    data['status'] = 200
    data['profils'] = []
    for profil in get_profil:
        data['profils'].append(profil.make_to_dict())
    resp = jsonify(data)
    return resp
