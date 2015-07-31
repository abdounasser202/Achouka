# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..profil.models_profil import ProfilModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/get_profil_api")
def get_profil_api():
    
    get_profil = ProfilModel().query()
    data = {}
    for profil in get_profil:
        data[profil.key.id()] = profil.make_to_dict()
    resp = jsonify(data)
    return resp
