__author__ = 'wilrona'

from ...modules import *

from ..customer.models_customer import CustomerModel
from ..ticket.models_ticket import TicketModel, TicketTypeNameModel, JourneyTypeModel, ClassTypeModel, AgencyModel

from ..customer.forms_customer import FormCustomerPOS
cache = Cache(app)


@app.route('/search_customer_pos', methods=['GET', 'POST'])
def search_customer_pos():
    birtday = request.form['birthday']
    customer = CustomerModel.query(
        CustomerModel.birthday == function.date_convert(birtday)
    )
    return render_template('/pos/search_customer.html', **locals())


@app.route('/search_ticket_pos', methods=['GET', 'POST'])
def search_ticket_pos():
    number_ticket = request.form['number_ticket']
    ticket = TicketModel.get_by_id(int(number_ticket))
    return render_template('/pos/search_ticket.html', **locals())


@app.route('/create_customer_and_ticket_pos', methods=['GET', 'POST'])
@app.route('/create_customer_and_ticket_pos/<int:customer_id>', methods=['GET', 'POST'])
def create_customer_and_ticket_pos(customer_id=None):

    nationalList = global_nationality_contry

    if customer_id:
        customer = CustomerModel.get_by_id(customer_id)
        form = FormCustomerPOS(obj=customer)
    else:
        customer = CustomerModel()
        form = FormCustomerPOS(request.form)

    journey_ticket = JourneyTypeModel.query()
    class_ticket = ClassTypeModel.query()
    ticket_type_name = TicketTypeNameModel.query()

    return render_template('/pos/create_customer_and_ticket.html', **locals())


@app.route('/Search_Ticket_Type', methods=['POST'])
def Search_Ticket_Type():

    from ..ticket_type.models_ticket_type import TicketTypeModel

    type_name = request.json['type_name']
    class_name = request.json['class_name']
    journey_name = request.json['journey_name']

    typeticket = TicketTypeNameModel.get_by_id(int(type_name))
    journeyticket = JourneyTypeModel.get_by_id(int(journey_name))
    classticket = ClassTypeModel.get_by_id(int(class_name))

    agency_user = AgencyModel.get_by_id(int(session.get('agence_id')))

    priceticket = TicketTypeModel.query(
        TicketTypeModel.type_name == typeticket.key,
        TicketTypeModel.class_name == classticket.key,
        TicketTypeModel.journey_name == journeyticket.key,
        TicketTypeModel.active == True
    ).get()

    Agency_ticket = TicketModel.query(
        TicketModel.class_name == classticket.key,
        TicketModel.type_name == typeticket.key,
        TicketModel.journey_name == journeyticket.key,
        TicketModel.agency == agency_user.key,
        TicketModel.selling == False
    ).count()

    not_tickket = 'true'
    if Agency_ticket >= 1:
        not_tickket = 'false'


    if priceticket:
        data = json.dumps({
            'statut': 'OK',
            'price': priceticket.price,
            'currency': priceticket.currency.get().code,
            'notticket': str(not_tickket)
        }, sort_keys=True)
    else:
        data = json.dumps({
            'statut': 'error',
            'value': 'Undefined',
            'notticket': str(not_tickket)
        }, sort_keys=True)

    return data
