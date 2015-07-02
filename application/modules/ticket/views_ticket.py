__author__ = 'wilrona'

from ...modules import *

from models_ticket import AgencyModel, TicketTypeNameModel, ClassTypeModel, JourneyTypeModel
from ..ticket_type.models_ticket_type import TicketTypeModel, TravelModel
from ..transaction.models_transaction import TransactionModel, DetailsTransactionModel, TicketModel, ExpensePaymentTransactionModel

from ..ticket_type.forms_ticket_type import FormSelectTicketType
from forms_ticket import FormTicket

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/recording/ticket')
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


@login_required
@roles_required(('super_admin', 'employee_POS'))
@app.route('/recoding/ticket/statistics/<int:agency_id>')
def Stat_View(agency_id):
    menu = 'recording'
    submenu = 'ticket'
    current_agency = AgencyModel.get_by_id(agency_id)

    # Traitement pour l'affichage du nombre
    purchases_query = TicketModel.query(
        TicketModel.agency == current_agency.key,
        projection=[TicketModel.datecreate, TicketModel.type_name, TicketModel.journey_name, TicketModel.class_name, TicketModel.travel_ticket],
        distinct=True
    )

    counts = {}
    for purchase in purchases_query:
        counts[purchase.datecreate] = {
            "number": TicketModel.query(
                TicketModel.agency == current_agency.key,
                TicketModel.datecreate == purchase.datecreate
            ).count_async().get_result(),
            "type_name": purchase.type_name.get().name,
            "class_name": purchase.class_name.get().name,
            "journey_name": purchase.journey_name.get().name,
            "destination_start": purchase.travel_ticket.get().destination_start.get().name,
            "destination_check": purchase.travel_ticket.get().destination_check.get().name
        }

    Ticket_type = TicketTypeModel.query(
        TicketTypeModel.active == True,
        projection=[TicketTypeModel.name, TicketTypeModel.class_name, TicketTypeModel.type_name, TicketTypeModel.journey_name, TicketTypeModel.travel],
        distinct=True
    )

    counts_ticket = {}
    for type in Ticket_type:
        counts_ticket[type.name] = {
            "number": TicketModel.query(
                TicketModel.travel_ticket == type.travel,
                TicketModel.class_name == type.class_name,
                TicketModel.journey_name == type.journey_name,
                TicketModel.type_name == type.type_name,
                TicketModel.agency == current_agency.key
            ).count_async().get_result(),
            "class": type.class_name,
            "journey": type.journey_name,
            "type": type.type_name,
            "travel": type.travel
        }

    return render_template('ticket/stat-view.html', **locals())


@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/Select_Travel/<int:agency_id>')
def Select_Travel(agency_id):

    current_agency = AgencyModel.get_by_id(agency_id)

    travellist = TravelModel.query(
        TravelModel.destination_start == current_agency.destination.get().key
    )

    return render_template('ticket/select-travel.html', **locals())


@login_required
@roles_required(('super_admin', 'admin'))
@app.route('/Select_Foreign_Travel/<int:agency_id>')
def Select_Foreign_Travel(agency_id):
    foreign_view = 'True'
    title = "Foreign"
    current_agency = AgencyModel.get_by_id(agency_id)

    travellist = TravelModel.query(
        TravelModel.destination_start != current_agency.destination.get().key
    )

    return render_template('ticket/select-travel.html', **locals())


@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/Select_TicketType/<int:travel_id>/<int:agency_id>', methods=['GET', 'POST'])
def Select_TicketType(travel_id, agency_id):

    travel_select = TravelModel.get_by_id(travel_id)

    title = request.args.get('title')

    ticket_type = TicketTypeModel.query(
        TicketTypeModel.travel == travel_select.key,
        TicketTypeModel.active == True
    )

    return render_template('ticket/select-tickettype.html', **locals())


@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/recording/ticket/edit/<int:agency_id>/<int:tickettype>', methods=['GET', 'POST'])
@app.route('/recording/ticket/edit/<int:agency_id>', methods=['GET', 'POST'])
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
        insert_transaction.reason = 'Expense'
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
                detail_transaction = DetailsTransactionModel()
                detail_transaction.amount = TicketType.price
                detail_transaction.agency = info_agency.key
                detail_transaction.reason = 'Expense detail'
                detail_transaction.is_payment = False
                detail_transaction.destination = TicketType.travel.get().destination_start
                detail_transaction.transaction_date = function.datetime_convert(date_auto_nows)
                detail_transaction.transaction_parent = last_transaction.key
                detail_transaction.user = user_id.key

                save_detail_transaction = detail_transaction.put()
                detail_transaction_create = DetailsTransactionModel.get_by_id(save_detail_transaction.id())

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
                ticket_transaction.transaction = detail_transaction_create.key
                ticket_transaction.ticket = ticket_create.key
                ticket_transaction.is_difference = False
                ticket_transaction.put()

                i += 1

            flash(''+str(number)+' Ticket(s) created succesfully', 'success')
            refresh = 'true'
        else:
            flash('Ticket don\'t saved', 'danger')

    return render_template('ticket/edit.html', **locals())