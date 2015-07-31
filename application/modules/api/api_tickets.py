# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..ticket_type.models_ticket_type import TicketTypeModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/get_tickets_api")
def get_tickets_api():
    
    get_tickets = TicketTypeModel().query()
    data = {}
    for tickets in get_tickets:
        data[tickets.key.id()] = tickets.make_to_dict()
    resp = jsonify(data)
    return resp
