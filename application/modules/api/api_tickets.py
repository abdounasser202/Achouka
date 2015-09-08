# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..agency.models_agency import AgencyModel
from ..ticket_type.models_ticket_type import TicketTypeModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/tickets/get/<token>")
def get_tickets_api(token):

    try:
        date = function.date_convert(request.args.get('last_update'))
    except:
        date = None

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    if date:
        get_tickets = TicketTypeModel().query(
            TicketTypeModel.date_update >= date
        )
    else:
        get_tickets = TicketTypeModel().query()

    data = {'status': 200, 'tickets': []}
    for tickets in get_tickets:
        data['tickets'].append(tickets.make_to_dict())
    resp = jsonify(data)
    return resp


@app.route('/send_change_status_ticket_api')
def send_change_status_ticket_api():

    from ..ticket.models_ticket import TicketModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    ticket_status = TicketModel.query(
        TicketModel.statusValid == True,
        TicketModel.selling == True
    )

    for ticket in ticket_status:
        date_valid = ticket.date_reservation - function.datetime_convert(date_auto_nows)
        if date_valid.days >= 30 and not ticket.is_return:
            ticket.statusValid = False
            ticket.put()

        if date_valid.days >= 60 and ticket.is_return:
            ticket.statusValid = False
            ticket.put()

    return "True"
