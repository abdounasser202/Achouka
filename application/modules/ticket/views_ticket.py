__author__ = 'wilrona'

from ...modules import *

from models_ticket import AgencyModel, TicketTypeNameModel, ClassTypeModel, JourneyTypeModel
from ..ticket_type.models_ticket_type import TicketTypeModel
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
@app.route('/Select_TicketType/<int:agency_id>', methods=['GET', 'POST'])
def Select_TicketType(agency_id):

    type_ticket = TicketTypeNameModel.query()
    class_ticket = ClassTypeModel.query()
    journey_ticket = JourneyTypeModel.query()

    form = FormSelectTicketType(request.form)

    if form.validate_on_submit():
        class_ticket_form = ClassTypeModel.get_by_id(int(form.class_name.data))
        type_ticket_form = TicketTypeNameModel.get_by_id(int(form.type_name.data))
        journey_type_form = JourneyTypeModel.get_by_id(int(form.journey_name.data))

        ticket_type = TicketTypeModel.query(
            TicketTypeModel.class_name == class_ticket_form.key,
            TicketTypeModel.journey_name == journey_type_form.key,
            TicketTypeModel.type_name == type_ticket_form.key,
            TicketTypeModel.active == True
        )
        exist = ticket_type.count()
        if exist >= 1:
            ticket_type = ticket_type.get()
            return redirect(url_for('Ticket_Edit', tickettype=ticket_type.key.id(), agency_id=agency_id))
        else:
            flash(u'Any ticket type with either setting information is activated ', 'danger')

    return render_template('ticket/select-tickettype.html', **locals())


@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/recording/ticket/edit/<int:tickettype>/<int:agency_id>', methods=['GET', 'POST'])
def Ticket_Edit(tickettype, agency_id):
    menu = 'recording'
    submenu = 'ticket'
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