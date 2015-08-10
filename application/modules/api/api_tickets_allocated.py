__author__ = 'Vercossa'

from api_function import *
from ..agency.models_agency import AgencyModel
from ..ticket.models_ticket import TicketModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route("/tickets_allocated/get/<token>")
def get_ticket_allocated(token):

    try:
        date = function.datetime_convert(request.args.get('last_update'))
    except:
        date = None

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    if date:
        get_ticket_allocated = TicketModel.query(
            TicketModel.datecreate >= date,
            TicketModel.selling == False,
            TicketModel.agency == get_agency.key
        )
    else:
        get_ticket_allocated = TicketModel.query(
            TicketModel.selling == False,
            TicketModel.agency == get_agency.key
        )

    data = {'status': 200, 'tickets_allocated': []}
    for tickets in get_ticket_allocated:
        data['tickets_allocated'].append(tickets.make_to_dict_poly())
    resp = jsonify(data)
    return resp


@app.route('/tickets_doublons_ticket_return_sale/get/<token>')
def get_doublon_ticket_return_sale(token):

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    from ..travel.models_travel import TravelModel

    travel_destination = TravelModel.query(
        TravelModel.destination_check == get_agency.destination.get().key
    )

    data = {'status': 200, 'tickets_return_sale': []}

    for travel in travel_destination:
        ticket_for_travel = TicketModel.query(
            TicketModel.travel_ticket == travel.key,
            TicketModel.is_return == True,
            TicketModel.selling == True,
            TicketModel.is_boarding == True
        )

        for ticket in ticket_for_travel:
            data['tickets_return_sale'].append(ticket.make_to_dict())

    resp = jsonify(data)
    return resp