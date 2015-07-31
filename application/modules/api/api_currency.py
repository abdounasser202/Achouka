# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..currency.models_currency import CurrencyModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/get_currency_api")
def get_currency_api():
    
    get_currency = CurrencyModel().query()
    data = {}
    for currency in get_currency:
        data[currency.key.id()] = currency.make_to_dict()
    resp = jsonify(data)
    return resp
