__author__ = 'wilrona'

from ...modules import *

from models_customer import CustomerModel
from forms_customer import FormCustomer

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/recording/customer')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Customer_Index():
    menu = 'recording'
    submenu = 'customer'

    customers = CustomerModel.query()

    return render_template('customer/index.html', **locals())


@app.route('/recording/customer/edit', methods=['GET', 'POST'])
@app.route('/recording/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Customer_Edit(customer_id=None):
    menu = 'recording'
    submenu = 'customer'

    number_list = global_dial_code_custom
    nationalList = global_nationality_contry

    customer = CustomerModel.get_by_id(customer_id)
    form = FormCustomer(obj=customer)

    # Nbre de voyage
    num_journey = journey_number(customer)

    #Nbre de voyage
    nbr_travels = nbr_travel(customer)

    #Pour chaque trajet son nombre
    travel_line = travel_number(customer)

    #Nombre de ticket vendu en cours
    ticket_num = ticket_number(customer)

    #Nre de ticket deja achete
    nbr_tickets = nbr_ticket(customer)

    # Nbre de ticket par class
    ticket_type = ticket_type_number(customer)

    return render_template('customer/edit.html', **locals())


@app.route('/Active_Customer/<int:customer_id>')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Active_Customer(customer_id):
    custom = CustomerModel.get_by_id(customer_id)
    if custom.status is False:
        custom.status = True

    else:
        custom.status = False

    custom.put()

    flash(u' Customer Updated. ', 'success')
    return redirect(url_for("Customer_Index"))


def journey_number(customer_key=None):
    from ..ticket.models_ticket import TicketModel

    if customer_key:
        customer_journey = TicketModel.query(
            TicketModel.customer == customer_key.key,
            TicketModel.selling == True,
            TicketModel.is_boarding == True
        ).count()
    else:
        journey_num = 0
        return journey_num

    return customer_journey


def ticket_number(customer_key=None):
    from ..ticket.models_ticket import TicketModel

    if customer_key:
        customer_journey = TicketModel.query(
            TicketModel.customer == customer_key.key,
            TicketModel.selling == True,
            TicketModel.is_boarding == False
        ).count()
    else:
        journey_num = 0
        return journey_num

    return customer_journey


def nbr_travel(customer_key=None):
    from ..ticket.models_ticket import TicketModel

    if customer_key:
        customer_travel_line = TicketModel.query(
            TicketModel.customer == customer_key.key,
            TicketModel.selling == True,
            TicketModel.is_boarding == True
        ).count()
    else:
        user_travel = 0
        return user_travel

    return customer_travel_line


def travel_number(customer_key=None):
    from ..ticket.models_ticket import TicketModel

    if customer_key:
        customer_travel_line = TicketModel.query(
            TicketModel.customer == customer_key.key,
            TicketModel.selling == True,
            TicketModel.is_boarding == True
        )
    else:
        user_travel = 0
        return user_travel

    travel_line_tab = []
    for travel in customer_travel_line:
        trav = {}
        trav['travel_ticket'] = travel.travel_ticket
        trav['departure'] = travel.departure
        travel_line_tab.append(trav)

    grouper = itemgetter("travel_ticket", "departure")

    user_travel = []
    for key, grp in groupby(sorted(travel_line_tab, key=grouper), grouper):
        temp_dict = dict(zip(["travel_ticket", "departure"], key))
        temp_dict['number'] = 0
        for item in grp:
            temp_dict['number'] += 1
        user_travel.append(temp_dict)

    return user_travel

# Nombre de ticket achete
def nbr_ticket(customer_key=None):
    from ..ticket.models_ticket import TicketModel

    if customer_key:
        customer_travel_line = TicketModel.query(
            TicketModel.customer == customer_key.key
        ).count()
    else:
        user_travel = 0
        return user_travel

    return customer_travel_line


def ticket_type_number(customer_key=None):
    from ..ticket.models_ticket import TicketModel

    if customer_key:
        customer_travel_line = TicketModel.query(
            TicketModel.customer == customer_key.key,
            TicketModel.selling == True
        )
    else:
        user_travel = 0
        return user_travel

    travel_line_tab = []
    for travel in customer_travel_line:
        trav = {}
        trav['travel_number'] = 1
        trav['class_name'] = travel.class_name.get().name
        trav['journey_name'] = travel.journey_name.get().name
        travel_line_tab.append(trav)

    grouper = itemgetter("class_name", "travel_number")

    user_travel = []
    for key, grp in groupby(sorted(travel_line_tab, key=grouper), grouper):
        temp_dict = dict(zip(["class_name", "travel_number"], key))
        temp_dict['number'] = 0

        temp_dict['journey_query'] = []
        under_grouper = itemgetter("class_name", "journey_name")

        for key, grp in groupby(sorted(grp, key=under_grouper), under_grouper):
            temp_dict_under = dict(zip(["class_name", "journey_name"], key))
            temp_dict['number'] += 1
            temp_dict_under['numbers'] = 0
            for item in grp:
                temp_dict_under['journey'] = item['journey_name']
                temp_dict_under['numbers'] += 1
            temp_dict['journey_query'].append(temp_dict_under)

        user_travel.append(temp_dict)

    return user_travel


