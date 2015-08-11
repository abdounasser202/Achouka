__author__ = 'Vercossa'

from api_function import *
from ..ticket.models_ticket import TicketModel, AgencyModel, CurrencyModel, TravelModel, DepartureModel, UserModel, CustomerModel,\
    TicketQuestion

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route("/tickets_allocated/get/<token>")
def get_ticket_allocated(token):

    try:
        date = datetime.datetime.combine(request.args.get('last_update'), datetime.datetime.min.time())
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

    data = {'status': 200, 'ticket_allocated': []}
    for tickets in get_ticket_allocated:
        data['ticket_allocated'].append(tickets.make_to_dict_poly())
    resp = jsonify(data)
    return resp


@app.route('/tickets_doublons_ticket_return_sale/get/<token>')
def get_doublon_ticket_return_sale(token):

    try:
        date = datetime.datetime.combine(request.args.get('last_update'), datetime.datetime.min.time())
    except:
        date = None

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    from ..travel.models_travel import TravelModel

    travel_destination = TravelModel.query(
        TravelModel.destination_check == get_agency.destination.get().key
    )

    data = {'status': 200, 'tickets_return_sale': []}

    for travel in travel_destination:
        if date:
            ticket_for_travel = TicketModel.query(
                TicketModel.travel_ticket == travel.key,
                TicketModel.is_return == True,
                TicketModel.selling == True,
                TicketModel.is_boarding == True,
                TicketModel.date_reservation >= date
            )
        else:
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


@app.route('/ticket_local_sale_put/put/<token>', methods=['POST'])
def ticket_local_sale_put(token):
    import unicodedata, ast

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    # recuperation de nos valeurs envoye par POST
    ticket_sale = request.form.getlist('ticket_sale')
    # convertion du tableau en Unicode

    for ticket_sale in ticket_sale:
        unicodedata.normalize('NFKD', ticket_sale).encode('ascii', 'ignore')

    # transformation de notre unicode en dictionnaire
    ticket_sale = ast.literal_eval(ticket_sale)

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    save = None
    count = 0

    for data_get in ticket_sale:
        old_data = TicketModel.get_by_id(int(data_get['ticket_id']))
        if old_data:
            old_data.date_reservation = function.datetime_convert(data_get['date_reservation'])
            old_data.sellprice = data_get['sellprice']

            currency_ticket = CurrencyModel.get_by_id(data_get['sellpriceCurrency'])
            old_data.sellpriceCurrency = currency_ticket.key

            customer_ticket = CustomerModel.get_by_id(data_get['customer'])
            old_data.customer = customer_ticket.key

            departure_ticket = DepartureModel.get_by_id(data_get['departure'])
            old_data.departure = departure_ticket.key

            user_seller = UserModel.get_by_id(data_get['ticket_seller'])
            old_data.ticket_seller = user_seller.key

            agency_ticket = AgencyModel.get_by_id(data_get['agency'])
            old_data.agency = agency_ticket.key

            travel_ticket = TravelModel.get_by_id(data_get['travel_ticket'])
            old_data.travel_ticket = travel_ticket.key

            old_data.is_prepayment = data_get['is_prepayment']
            old_data.statusValid = data_get['statusValid']
            old_data.is_boarding = data_get['is_boarding']


            old_data.is_return = data_get['is_return']

            if data_get['is_return']:
                duplicate_ticket = TicketModel()
                duplicate_ticket.type_name = old_data.type_name
                duplicate_ticket.class_name = old_data.class_name
                duplicate_ticket.is_count = False
                duplicate_ticket.datecreate = function.datetime_convert(date_auto_nows)
                duplicate_ticket.customer = customer_ticket.key
                duplicate_ticket.parent_return = old_data.key
                duplicate_ticket.put()

            if data_get['child_upgrade']:
                old_data.is_upgrade = data_get['is_upgrade']
                old_data.is_count = data_get['is_count']

                upgrade_parent = TicketModel.get_by_id(data_get['upgrade_parent'])
                old_data.upgrade_parent = upgrade_parent.key

            from ..transaction.models_transaction import ExpensePaymentTransactionModel,TransactionModel

            for transaction in data_get['transaction']:
                new_transaction = TransactionModel()
                new_transaction.agency = agency_ticket.key
                new_transaction.amount = transaction['amount']
                new_transaction.destination = travel_ticket.destination_start
                new_transaction.is_payment = transaction['is_payment']
                new_transaction.reason = transaction['reason']
                new_transaction.transaction_date = function.datetime_convert(data_get['date_reservation'])
                new_transaction.user = user_seller.key
                put_transaction = new_transaction.put()

                new_transaction_line = ExpensePaymentTransactionModel()
                new_transaction_line.amount = transaction['amount']
                new_transaction_line.is_difference = True
                new_transaction_line.ticket = old_data.key
                new_transaction_line.transaction = put_transaction
                new_transaction_line.put()

            from ..question.models_question import QuestionModel
            for question in data_get['ticket_question']:
                question_id = QuestionModel.get_by_id(question['question_id'])
                if question_id:
                    answer = TicketQuestion()
                    answer.ticket_id = old_data.key
                    answer.question_id = question_id.key
                    answer.response = question['response']
                    answer.put()

            save = old_data.put()
            count += 1

    if save:
        return not_found(error=200, message="You have send "+str(count)+" tickets sales in online apps")
    else:
        return not_found(error=404, message="You have send "+str(count)+" ticket sale in online apps")