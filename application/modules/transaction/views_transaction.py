__author__ = 'wilrona'

from ...modules import *

from ..transaction.models_transaction import TransactionModel, AgencyModel, UserModel, TicketModel, ExpensePaymentTransactionModel, DetailsTransactionModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/recording/transaction')
def Transaction_Index():
    menu = 'recording'
    submenu = 'transaction'

    if not current_user.has_roles(('admin','super_admin')) and current_user.has_roles('manager_agency'):
        agency_user = AgencyModel.get_by_id(int(session.get('agence_id')))
        return redirect(url_for('Transaction_Agency', agency_id=agency_user.key.id()))

    List_agency = AgencyModel.query()

    return render_template('/transaction/index.html', **locals())


@app.route('/recording/transaction/stat/<int:agency_id>')
def Transaction_Agency(agency_id):
    menu = 'recording'
    submenu = 'transaction'

    current_agency = AgencyModel.get_by_id(agency_id)

    destination_transaction_query = TransactionModel.query(
        TransactionModel.agency == current_agency.key,
        TransactionModel.destination != current_agency.destination,
        projection=[TransactionModel.destination],
        distinct=True
    )
    #liste des transaction de l'agence
    transaction_agency_query = TransactionModel.query(
        TransactionModel.agency == current_agency.key
    )

    # Liste des utilisateurs de l'agence
    user_agency = UserModel.query(
        UserModel.agency == current_agency.key
    )

    ticket_travel_query = TicketModel.query(
        TicketModel.selling == True,
        projection=[TicketModel.travel_ticket, TicketModel.ticket_seller],
        distinct=True
    )

    return render_template('/transaction/stat-views.html', **locals())


@app.route('/Transaction_user', methods=["GET", "POST"])
@app.route('/Transaction_user/<int:user_id>', methods=["GET", "POST"])
def Transaction_user(user_id=None):

    user_get_id = UserModel.get_by_id(user_id)

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    if request.method == "POST":

        amount = float(request.form['amount'])

        user_ticket_query = TicketModel.query(
            TicketModel.ticket_seller == user_get_id.key,
            TicketModel.selling == True
        )

        user_tickets_tab = []
        user_tickets_tab_unsolved_payment = []

        amount_ticket_to_sold = 0
        amount_ticket_unsold = 0
        for ticket in user_ticket_query:
            if ticket.travel_ticket.get().destination_start == user_get_id.agency.get().destination:
                expensepayment_query = ExpensePaymentTransactionModel.query(
                    ExpensePaymentTransactionModel.ticket == ticket.key
                )
                #RECUPERATION DES TICKETS QUE L'ON VA SOLDER
                number_attend_payment = 0
                for transaction_line in expensepayment_query:
                    if transaction_line.transaction.get().is_payment is True and transaction_line.is_difference is False:
                        number_attend_payment += 1

                tickets = {}
                if number_attend_payment == 0:
                    tickets['id'] = ticket.key.id()
                    user_tickets_tab.append(tickets)

                #RECUPERATION DES TICKETS NON SOLDE
                number_unsolved_payment = 0
                transaction_amount = 0
                for transaction_line in expensepayment_query:
                    if transaction_line.transaction.get().is_payment is True and transaction_line.is_difference is False:
                        number_unsolved_payment += 1
                        transaction_amount += transaction_line.transaction.get().amount

                tickets = {}
                if number_unsolved_payment >= 1 and ticket.sellprice > transaction_amount:
                    tickets['id'] = ticket.key.id()
                    tickets['balance'] = ticket.sellprice - transaction_amount
                    user_tickets_tab_unsolved_payment.append(tickets)

        amount_to_save = amount
        if not user_tickets_tab:
            for unsold in user_tickets_tab_unsolved_payment:
                if (amount - unsold['balance']) > 0:
                    amount -= unsold['balance']
            amount_to_save = amount_to_save - amount

        #Traitement de la transaction parente

        parent_transaction = TransactionModel()
        parent_transaction.reason = "payment"
        parent_transaction.amount = amount_to_save
        parent_transaction.agency = user_get_id.agency
        parent_transaction.is_payment = True
        parent_transaction.destination = user_get_id.agency.get().destination
        parent_transaction.transaction_date = function.datetime_convert(date_auto_nows)

        user_current_id = UserModel.get_by_id(int(session.get('user_id')))
        parent_transaction.user = user_current_id.key

        parent_transaction = parent_transaction.put()
        parent_transaction = TransactionModel.get_by_id(parent_transaction.id())

        # TRAITEMENT DES TICKETS NON SOLDE
        for unsold in user_tickets_tab_unsolved_payment:
            if amount > 0:
                ticket_unsold = TicketModel.get_by_id(int(unsold['id']))

                ticket_transaction_line = DetailsTransactionModel()
                ticket_transaction_line.agency = parent_transaction.agency
                ticket_transaction_line.reason = 'Detail payment'
                ticket_transaction_line.is_payment = parent_transaction.is_payment
                ticket_transaction_line.destination = parent_transaction.destination
                ticket_transaction_line.transaction_date = function.datetime_convert(date_auto_nows)
                ticket_transaction_line.user = parent_transaction.user

                # verifie si le montant est tjrs decrementable
                if amount > unsold['balance']:
                    ticket_transaction_line.amount = float(unsold['balance'])
                    amount_to_save -= float(unsold['balance'])
                else:
                    ticket_transaction_line.amount = amount_to_save
                    amount_to_save -= amount_to_save

                ticket_transaction_line.transaction_parent = parent_transaction.key

                ticket_transaction_line_create = ticket_transaction_line.put()
                ticket_transaction_line_create = DetailsTransactionModel.get_by_id(ticket_transaction_line_create.id())



                link_ticket_transaction_line = ExpensePaymentTransactionModel()
                link_ticket_transaction_line.ticket = ticket_unsold.key
                link_ticket_transaction_line.transaction = ticket_transaction_line_create.key

                link_ticket_transaction_line.put()
            else:
                break

        # TRAITEMENT DES NOUVEAUX TICKETS
        for wait_to_sold_ticket in user_tickets_tab:
            if amount > 0:
                ticket_sold = TicketModel.get_by_id(int(wait_to_sold_ticket['id']))

                ticket_transaction_line_sold = DetailsTransactionModel()
                ticket_transaction_line_sold.agency = parent_transaction.agency
                ticket_transaction_line_sold.reason = 'Details payment'
                ticket_transaction_line_sold.is_payment = parent_transaction.is_payment
                ticket_transaction_line_sold.destination = parent_transaction.destination
                ticket_transaction_line_sold.transaction_date = function.datetime_convert(date_auto_nows)
                ticket_transaction_line_sold.user = parent_transaction.user

                #verifie si le montant est tjrs decrementable
                if amount > ticket_sold.sellprice:
                    ticket_transaction_line_sold.amount = ticket_sold.sellprice
                    amount_to_save -= ticket_sold.sellprice
                else:
                    ticket_transaction_line_sold.amount = amount_to_save
                    amount_to_save -= amount_to_save

                ticket_transaction_line_sold.transaction_parent = parent_transaction.key
                ticket_transaction_line_sold_create = ticket_transaction_line_sold.put()

                ticket_transaction_line_sold_create = DetailsTransactionModel.get_by_id(ticket_transaction_line_sold_create.id())

                link_ticket_transaction_line = ExpensePaymentTransactionModel()
                link_ticket_transaction_line.ticket = ticket_sold.key
                link_ticket_transaction_line.transaction = ticket_transaction_line_sold_create.key

                link_ticket_transaction_line.put()
            else:
                break

    return render_template('/transaction/transaction_user.html', **locals())


@app.route('/Transaction_foreign_user')
@app.route('/Transaction_foreign_user/<int:user_id>/<int:travel_id>')
def Transaction_foreign_user(user_id=None, travel_id=None):

    user_get_id = UserModel.get_by_id(user_id)

    return render_template('/transaction/transaction_foreign_user.html', **locals())