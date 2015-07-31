# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..currency.models_currency import CurrencyModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/currency/get/<token>")
def get_currency_api(token):

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    get_currency = CurrencyModel().query()
    data = {}
    data['status'] = 200
    data['currency'] = []
    for currency in get_currency:
        data['currency'].append(currency.make_to_dict())
    resp = jsonify(data)
    return resp
