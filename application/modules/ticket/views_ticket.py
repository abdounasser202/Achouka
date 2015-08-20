__author__ = 'wilrona'

from ...modules import *

from models_ticket import AgencyModel, TicketTypeNameModel, ClassTypeModel, JourneyTypeModel
from ..ticket_type.models_ticket_type import TicketTypeModel, TravelModel
from ..transaction.models_transaction import TransactionModel, TicketModel, ExpensePaymentTransactionModel

from ..ticket_type.forms_ticket_type import FormSelectTicketType
from forms_ticket import FormTicket

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/manage/ticket')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Ticket_Index():
    menu = 'recording'
    submenu = 'ticket'

    if not current_user.has_roles(('admin','super_admin')) and current_user.has_roles('manager_agency'):
        agency_user = AgencyModel.get_by_id(int(session.get('agence_id')))
        return redirect(url_for('Stat_View', agency_id=agency_user.key.id()))

    # Utiliser pour afficher la liste des agences avec leur ticket
    ticket_list = AgencyModel.query(
        AgencyModel.status == True
    )

    return render_template('ticket/index.html', **locals())


@app.route('/manage/ticket/statistics/<int:agency_id>')
@login_required
@roles_required(('super_admin', 'employee_POS'))
def Stat_View(agency_id):
    menu = 'recording'
    submenu = 'ticket'

    current_agency = AgencyModel.get_by_id(agency_id)

    # Traitement pour l'affichage du nombre de dernier ticket achete
    purchases_query = TicketModel.query(
        TicketModel.agency == current_agency.key,
        TicketModel.is_count == True,
        TicketModel.is_upgrade == False
    )

    ticket_purchase_tab = []
    for ticket in purchases_query:
        tickets = {}
        tickets['date'] = ticket.datecreate
        tickets['type'] = ticket.type_name
        tickets['class'] = ticket.class_name
        tickets['journey'] = ticket.journey_name
        tickets['number'] = 1
        tickets['travel'] = ticket.travel_ticket
        ticket_purchase_tab.append(tickets)

    grouper = itemgetter("date", "type", "class", "journey", "travel")

    ticket_purchase = []
    for key, grp in groupby(sorted(ticket_purchase_tab, key=grouper), grouper):
        temp_dict = dict(zip(["date", "type", "class", "journey", "travel"], key))
        temp_dict['number'] = 0
        for item in grp:
            temp_dict['number'] += item['number']
        ticket_purchase.append(temp_dict)

    # TYPE DE TICKET EN POSSESSION PAR L'AGENCE (etranger ou local)
    ticket_type_query = TicketTypeModel.query(
        TicketTypeModel.active == True
    )

    ticket_type_purchase_tab = []
    for ticket_type in ticket_type_query:
            tickets_type = {}
            tickets_type['name_ticket'] = ticket_type.name
            tickets_type['type'] = ticket_type.type_name
            tickets_type['class'] = ticket_type.class_name
            tickets_type['journey'] = ticket_type.journey_name
            tickets_type['number'] = TicketModel.query(
                TicketModel.travel_ticket == ticket_type.travel,
                TicketModel.class_name == ticket_type.class_name,
                TicketModel.journey_name == ticket_type.journey_name,
                TicketModel.type_name == ticket_type.type_name,
                TicketModel.selling == False,
                TicketModel.agency == current_agency.key
            ).count_async().get_result()
            tickets_type['travel'] = ticket_type.travel
            ticket_type_purchase_tab.append(tickets_type)

    grouper = itemgetter("name_ticket", "type", "class", "journey", "travel")

    ticket_type_purchase = []
    for key, grp in groupby(sorted(ticket_type_purchase_tab, key=grouper), grouper):
        temp_dict = dict(zip(["name_ticket", "type", "class", "journey", "travel"], key))
        temp_dict['number'] = 0
        for item in grp:
            temp_dict['number'] += item['number']
        ticket_type_purchase.append(temp_dict)

    return render_template('ticket/stat-view.html', **locals())


@app.route('/Select_Travel/<int:agency_id>')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Select_Travel(agency_id):

    current_agency = AgencyModel.get_by_id(agency_id)

    travellist = TravelModel.query(
        TravelModel.destination_start == current_agency.destination.get().key
    )

    return render_template('ticket/select-travel.html', **locals())


@app.route('/Select_Foreign_Travel/<int:agency_id>')
@login_required
@roles_required(('super_admin', 'admin'))
def Select_Foreign_Travel(agency_id):
    foreign_view = 'True'
    title = "Foreign"
    current_agency = AgencyModel.get_by_id(agency_id)

    travellist = TravelModel.query(
        TravelModel.destination_start != current_agency.destination.get().key
    )

    return render_template('ticket/select-travel.html', **locals())


@app.route('/Select_TicketType/<int:agency_id>/<int:travel_id>', methods=['GET', 'POST'])
@app.route('/Select_TicketType/<int:agency_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Select_TicketType(agency_id, travel_id=None):

    travel_select = TravelModel.get_by_id(travel_id)

    title = request.args.get('title')

    ticket_type = TicketTypeModel.query(
        TicketTypeModel.travel == travel_select.key,
        TicketTypeModel.active == True
    )

    return render_template('ticket/select-tickettype.html', **locals())


@app.route('/manage/ticket/edit/<int:agency_id>/<int:tickettype>', methods=['GET', 'POST'])
@app.route('/manage/ticket/edit/<int:agency_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Ticket_Edit(agency_id, tickettype):
    refresh = 'false'

    #information du type de ticket pour les tickets
    TicketType = TicketTypeModel.get_by_id(tickettype)

    #information de l'agence
    info_agency = AgencyModel.get_by_id(agency_id)

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    form = FormTicket(request.form)

    if form.validate_on_submit():

        number = int(form.number.data)
        price = TicketType.price

        #montant des tickets pour la transaction
        montant_ticket = price*number


        insert_transaction = TransactionModel()

        insert_transaction.amount = montant_ticket
        insert_transaction.agency = info_agency.key
        insert_transaction.reason = 'Ticket Purchase'
        insert_transaction.is_payment = False
        insert_transaction.destination = TicketType.travel.get().destination_start
        insert_transaction.transaction_date = function.datetime_convert(date_auto_nows)

        from ..user.models_user import UserModel
        user_id = UserModel.get_by_id(int(session.get('user_id')))
        insert_transaction.user = user_id.key

        key_transaction = insert_transaction.put()

        if key_transaction:

            last_transaction = TransactionModel.get_by_id(key_transaction.id())
            i = 1
            while i <= number:

                ticket = TicketModel()
                ticket.type_name = TicketType.type_name
                ticket.journey_name = TicketType.journey_name
                ticket.class_name = TicketType.class_name
                ticket.is_prepayment = False
                ticket.agency = info_agency.key
                ticket.travel_ticket = TicketType.travel
                ticket.sellpriceAg = TicketType.price
                ticket.sellpriceAgCurrency = TicketType.currency
                ticket.datecreate = function.datetime_convert(date_auto_nows)
                if TicketType.journey_name.get().returned:
                    ticket.is_return = True

                ticket_create = ticket.put()

                ticket_create = TicketModel.get_by_id(ticket_create.id())

                # creation du type de transaction entre la transaction et le ticket
                ticket_transaction = ExpensePaymentTransactionModel()
                ticket_transaction.transaction = last_transaction.key
                ticket_transaction.ticket = ticket_create.key
                ticket_transaction.amount = TicketType.price
                ticket_transaction.put()

                i += 1

            flash(''+str(number)+' Ticket(s) created succesfully', 'success')
            refresh = 'true'
        else:
            flash('Ticket don\'t saved', 'danger')

    return render_template('ticket/edit.html', **locals())