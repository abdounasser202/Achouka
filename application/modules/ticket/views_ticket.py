__author__ = 'wilrona'

from ...modules import *

from models_ticket import AgencyModel, TicketTypeNameModel, ClassTypeModel, JourneyTypeModel
from ..ticket_type.models_ticket_type import TicketTypeModel, TravelModel
from ..transaction.models_transaction import TransactionModel, TicketModel, ExpensePaymentTransactionModel

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

    # Utiliser pour afficher la liste des agences avec leur ticket
    ticket_list = AgencyModel.query()

    return render_template('ticket/index.html', **locals())


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
@roles_required(('super_admin', 'manager_agency'))
@app.route('/Select_TicketType/<int:travel_id>/<int:agency_id>', methods=['GET', 'POST'])
def Select_TicketType(travel_id, agency_id):

    travel_select = TravelModel.get_by_id(travel_id)

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
        insert_transaction.currency = TicketType.currency
        insert_transaction.transaction_date = function.datetime_convert(date_auto_nows)

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
                ticket.sellpriceAg = TicketType.price
                ticket.sellpriceAgCurrency = TicketType.currency
                ticket.datecreate = function.datetime_convert(date_auto_nows)

                ticket_create = ticket.put()

                ticket_create = TicketModel.get_by_id(ticket_create.id())

                # creation du type de transaction entre la transaction et le ticket
                ticket_transaction = ExpensePaymentTransactionModel()
                ticket_transaction.transaction = last_transaction.key
                ticket_transaction.ticket = ticket_create.key
                ticket_transaction.is_difference = False
                ticket_transaction.put()

                i += 1

            flash(''+str(number)+' Ticket(s) created succesfully', 'success')
            refresh = 'true'
        else:
            flash('Ticket don\'t saved', 'danger')

    return render_template('ticket/edit.html', **locals())