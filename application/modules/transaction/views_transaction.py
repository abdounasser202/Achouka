__author__ = 'wilrona'

from ...modules import *

from ..transaction.models_transaction import TransactionModel, AgencyModel, UserModel, TicketModel, ExpensePaymentTransactionModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/manage/transaction')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Transaction_Index():
    menu = 'recording'
    submenu = 'transaction'

    if not current_user.has_roles(('admin','super_admin')) and current_user.has_roles('manager_agency'):
        agency_user = AgencyModel.get_by_id(int(session.get('agence_id')))
        return redirect(url_for('Transaction_Agency', agency_id=agency_user.key.id()))

    List_agency = AgencyModel.query()

    return render_template('/transaction/index.html', **locals())

@app.route('/manage/transaction/stat/<int:agency_id>')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Transaction_Agency(agency_id):
    menu = 'recording'
    submenu = 'transaction'

    current_agency = AgencyModel.get_by_id(agency_id)

    #liste des transaction de l'agence
    transaction_agency_query = TransactionModel.query(
        TransactionModel.agency == current_agency.key,
        TransactionModel.transaction_admin == False
    )

    # Liste des utilisateurs de l'agence
    user_agency = UserModel.query(
        UserModel.agency == current_agency.key
    )

    return render_template('/transaction/stat-views.html', **locals())


@app.route('/Transaction_detail')
@app.route('/Transaction_detail/<int:transaction_id>')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Transaction_detail(transaction_id=None):

    current_transaction_get_id = TransactionModel.get_by_id(transaction_id)

    transaction_detail = []
    for transaction in current_transaction_get_id.relation_parent_child():
        transactions = {}
        transactions['type'] = transaction.ticket.get().type_name
        transactions['journey'] = transaction.ticket.get().journey_name
        transactions['class'] = transaction.ticket.get().class_name
        transactions['travel'] = transaction.ticket.get().travel_ticket
        transactions['amount'] = transaction.amount
        transactions['currency'] = transaction.ticket.get().sellpriceAgCurrency.get().code
        transaction_detail.append(transactions)

    grouper = itemgetter("type", "class", "journey", "travel", "currency")

    detail_transaction = []
    for key, grp in groupby(sorted(transaction_detail, key=grouper), grouper):
        temp_dict = dict(zip(["type", "class", "journey", "travel", "currency"], key))
        temp_dict['number'] = 0
        temp_dict['amount'] = 0
        for item in grp:
            temp_dict['number'] += 1
            temp_dict['amount'] += item['amount']
        detail_transaction.append(temp_dict)

    return render_template('/transaction/transaction_details.html', **locals())


@app.route('/Transaction_user', methods=["GET", "POST"])
@app.route('/Transaction_user/<int:user_id>', methods=["GET", "POST"])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Transaction_user(user_id=None):

    user_get_id = UserModel.get_by_id(user_id)

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")
    received = False

    # TRAITEMENT DE LA REQUETE POST
    if request.method == "POST":

        amount = float(request.form['amount'])

        user_ticket_query = TicketModel.query(
            TicketModel.ticket_seller == user_get_id.key,
            TicketModel.selling == True,
            TicketModel.is_count == True
        )

        user_tickets_tab = []
        user_tickets_tab_unsolved_payment = []

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
                        transaction_amount += transaction_line.amount

                tickets = {}
                if number_unsolved_payment >= 1 and ticket.sellprice > transaction_amount:
                    tickets['id'] = ticket.key.id()
                    tickets['balance'] = ticket.sellprice - transaction_amount
                    user_tickets_tab_unsolved_payment.append(tickets)

        amount_to_save = amount
        if not user_tickets_tab:
            for unsold in user_tickets_tab_unsolved_payment:
                if (amount - unsold['balance']) > 0:
                    amount_to_save -= unsold['balance']

        #Traitement de la transaction parente

        parent_transaction = TransactionModel()
        parent_transaction.reason = "Ticket Sale"
        parent_transaction.amount = amount_to_save
        parent_transaction.pre_amount = user_get_id.escrow_amount(full=True)
        parent_transaction.agency = user_get_id.agency
        parent_transaction.is_payment = True
        parent_transaction.destination = user_get_id.agency.get().destination
        parent_transaction.transaction_date = function.datetime_convert(date_auto_nows)
        parent_transaction.employe = user_get_id.key

        user_current_id = UserModel.get_by_id(int(session.get('user_id')))
        parent_transaction.user = user_current_id.key

        parent_transaction = parent_transaction.put()

        # TRAITEMENT DES TICKETS NON SOLDE
        for unsold in user_tickets_tab_unsolved_payment:
            if amount_to_save > 0:
                ticket_unsold = TicketModel.get_by_id(int(unsold['id']))

                link_ticket_transaction_line = ExpensePaymentTransactionModel()
                link_ticket_transaction_line.ticket = ticket_unsold.key
                link_ticket_transaction_line.transaction = parent_transaction

                # verifie si le montant est tjrs decrementable
                if amount > unsold['balance']:
                    link_ticket_transaction_line.amount = float(unsold['balance'])
                    amount_to_save -= float(unsold['balance'])
                else:
                    link_ticket_transaction_line.amount = amount_to_save
                    amount_to_save -= amount_to_save

                link_ticket_transaction_line.put()
            else:
                break

        # TRAITEMENT DES NOUVEAUX TICKETS
        for wait_to_sold_ticket in user_tickets_tab:
            if amount_to_save > 0:
                ticket_sold = TicketModel.get_by_id(int(wait_to_sold_ticket['id']))

                link_ticket_transaction_line = ExpensePaymentTransactionModel()
                link_ticket_transaction_line.ticket = ticket_sold.key
                link_ticket_transaction_line.transaction = parent_transaction

                #verifie si le montant est tjrs decrementable
                if amount_to_save > ticket_sold.sellprice:
                    link_ticket_transaction_line.amount = ticket_sold.sellprice
                    amount_to_save -= ticket_sold.sellprice
                else:
                    link_ticket_transaction_line.amount = amount_to_save
                    amount_to_save -= amount_to_save

                link_ticket_transaction_line.put()
            else:
                break
        received = True

    # Traitement de l'envoie d'email et de la facture
    if received:
        transaction_get = TransactionModel.get_by_id(int(parent_transaction.id()))
        detail_transaction = calcul_transaction(transaction_get)

        #content = StringIO('contenu')
        content = render_template('/transaction/facture.html', **locals())
        output = StringIO()
        pisa.log.setLevel('DEBUG')
        pdf = pisa.CreatePDF(content, output, encoding='utf-8')
        pdf_data = pdf.dest.getvalue()
        output.close()
        name_pdf = str(parent_transaction.id())+"_received.pdf"

        from google.appengine.api import mail
        mail.send_mail(sender="no-reply@comantrans-online-2015.appspotmail.com",
                   to=user_get_id.email,
                   subject="Your received for transaction "+str(parent_transaction.id()),
                   body="Your message for your received",
                   attachments=[(name_pdf, pdf_data)])

        detail_transaction = calcul_transaction(transaction_get)

    return render_template('/transaction/transaction_user.html', **locals())


@app.route('/print_receipt/<int:transaction_id>')
def print_receipt(transaction_id):

    transaction_get = TransactionModel.get_by_id(transaction_id)
    detail_transaction = calcul_transaction(transaction_get)

    admin = False
    if request.args.get('admin'):
        admin = True

    content = render_template('/transaction/recu.html', **locals())
    output = StringIO()
    pisa.log.setLevel('DEBUG')
    pdf = pisa.CreatePDF(content, output, encoding='utf-8')
    pdf_data = pdf.dest.getvalue()
    output.close()


    response = make_response(pdf_data)
    response.headers['Content-Type'] = "application/pdf"

    return response

# fonction de regroupement des tickets payes
def calcul_transaction(transaction_get):
    transaction_detail = []
    for transaction in transaction_get.relation_parent_child():
        transactions = {}
        transactions['type'] = transaction.ticket.get().type_name
        transactions['journey'] = transaction.ticket.get().journey_name
        transactions['class'] = transaction.ticket.get().class_name
        transactions['travel'] = transaction.ticket.get().travel_ticket
        transactions['amount'] = transaction.amount
        transactions['currency'] = transaction.ticket.get().sellpriceAgCurrency.get().code
        transaction_detail.append(transactions)

    grouper = itemgetter("type", "class", "journey", "travel", "currency")

    detail_transaction = []
    for key, grp in groupby(sorted(transaction_detail, key=grouper), grouper):
        temp_dict = dict(zip(["type", "class", "journey", "travel", "currency"], key))
        temp_dict['number'] = 0
        temp_dict['amount'] = 0
        for item in grp:
            temp_dict['number'] += 1
            temp_dict['amount'] += item['amount']
        detail_transaction.append(temp_dict)

    return detail_transaction

@app.route('/Transaction_foreign_user', methods=["GET", "POST"])
@app.route('/Transaction_foreign_user/<int:user_id>/<int:travel_id>', methods=["GET", "POST"])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Transaction_foreign_user(user_id=None, travel_id=None):

    from ..travel.models_travel import TravelModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    user_get_id = UserModel.get_by_id(user_id)
    travel_get_id = TravelModel.get_by_id(int(travel_id))

    ticket_user_query = TicketModel.query(
        TicketModel.ticket_seller == user_get_id.key,
        TicketModel.travel_ticket == travel_get_id.key,
        TicketModel.is_count == True
    )

    user_tickets_tab = []
    user_tickets_tab_unsolved_payment = []

    for ticket in ticket_user_query:
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
            tickets['type'] = ticket.type_name
            tickets['class'] = ticket.class_name
            tickets['journey'] = ticket.journey_name
            tickets['number'] = 1
            tickets['amount'] = ticket.sellprice
            tickets['currency'] = ticket.sellpriceCurrency
            user_tickets_tab.append(tickets)

        #RECUPERATION DES TICKETS NON SOLDE
        number_unsolved_payment = 0
        transaction_amount = 0
        for transaction_line in expensepayment_query:
            if transaction_line.transaction.get().is_payment is True and transaction_line.is_difference is False:
                number_unsolved_payment += 1
                transaction_amount += transaction_line.amount

        tickets = {}
        if number_unsolved_payment >= 1 and ticket.sellprice > transaction_amount:
            tickets['id'] = ticket.key.id()
            tickets['type'] = ticket.type_name
            tickets['class'] = ticket.class_name
            tickets['journey'] = ticket.journey_name
            tickets['number'] = 1
            tickets['amount'] = ticket.sellprice
            tickets['balance'] = ticket.sellprice - transaction_amount
            tickets['currency'] = ticket.sellpriceCurrency
            user_tickets_tab_unsolved_payment.append(tickets)

    grouper = itemgetter("type", "class", "journey", "currency")

    user_tickets = []
    for key, grp in groupby(sorted(user_tickets_tab, key=grouper), grouper):
        temp_dict = dict(zip(["type", "class", "journey", "currency"], key))
        temp_dict['number'] = 0
        temp_dict['amount'] = 0
        for item in grp:
            temp_dict['number'] += item['number']
            temp_dict['amount'] += item['amount']
        user_tickets.append(temp_dict)

    received = False
    # Traitement du POST
    if request.method == "POST":
        amount = float(request.form['amount'])

        amount_to_save = amount
        if not user_tickets_tab:
            for unsold in user_tickets_tab_unsolved_payment:
                if (amount - unsold['balance']) > 0:
                    amount_to_save -= unsold['balance']

        #Traitement de la transaction parente
        parent_transaction = TransactionModel()
        parent_transaction.reason = "Payment"
        parent_transaction.amount = amount_to_save
        parent_transaction.pre_amount = user_get_id.escrow_amount(True)
        parent_transaction.agency = user_get_id.agency
        parent_transaction.employe = user_get_id.key
        parent_transaction.is_payment = True
        parent_transaction.destination = travel_get_id.destination_start
        parent_transaction.transaction_date = function.datetime_convert(date_auto_nows)

        user_current_id = UserModel.get_by_id(int(session.get('user_id')))
        parent_transaction.user = user_current_id.key

        parent_transaction = parent_transaction.put()

        # TRAITEMENT DES TICKETS NON SOLDE
        for unsold in user_tickets_tab_unsolved_payment:
            if amount_to_save > 0:
                ticket_unsold = TicketModel.get_by_id(int(unsold['id']))

                link_ticket_transaction_line = ExpensePaymentTransactionModel()
                link_ticket_transaction_line.ticket = ticket_unsold.key
                link_ticket_transaction_line.transaction = parent_transaction

                # verifie si le montant est tjrs decrementable
                if amount_to_save > unsold['balance']:
                    link_ticket_transaction_line.amount = float(unsold['balance'])
                    amount_to_save -= float(unsold['balance'])
                else:
                    link_ticket_transaction_line.amount = amount_to_save
                    amount_to_save -= amount_to_save

                link_ticket_transaction_line.put()
            else:
                break

        # TRAITEMENT DES NOUVEAUX TICKETS
        for wait_to_sold_ticket in user_tickets_tab:
            if amount_to_save > 0:
                ticket_sold = TicketModel.get_by_id(int(wait_to_sold_ticket['id']))

                link_ticket_transaction_line = ExpensePaymentTransactionModel()
                link_ticket_transaction_line.ticket = ticket_sold.key
                link_ticket_transaction_line.transaction = parent_transaction

                #verifie si le montant est tjrs decrementable
                if amount_to_save > ticket_sold.sellprice:
                    link_ticket_transaction_line.amount = ticket_sold.sellprice
                    amount_to_save -= ticket_sold.sellprice
                else:
                    link_ticket_transaction_line.amount = amount_to_save
                    amount_to_save -= amount_to_save

                link_ticket_transaction_line.put()
            else:
                break

        received = True

    # Traitement de l'envoie d'email et de la facture
    if received:
        transaction_get = TransactionModel.get_by_id(int(parent_transaction.id()))
        detail_transaction = calcul_transaction(transaction_get)

        admin = False
        if request.args.get('admin'):
            admin = True

        #content = StringIO('contenu')
        content = render_template('/transaction/facture.html', **locals())
        output = StringIO()
        pisa.log.setLevel('DEBUG')
        pdf = pisa.CreatePDF(content, output, encoding='utf-8')
        pdf_data = pdf.dest.getvalue()
        output.close()
        name_pdf = str(parent_transaction.id())+"_received.pdf"

        from google.appengine.api import mail
        mail.send_mail(sender="no-reply@comantrans-online-2015.appspotmail.com",
                   to=user_get_id.email,
                   subject="Your received for transaction "+str(parent_transaction.id()),
                   body="Your message for your received",
                   attachments=[(name_pdf, pdf_data)])

        detail_transaction = calcul_transaction(transaction_get)

    return render_template('/transaction/transaction_foreign_user.html', **locals())


@app.route('/Payment_admin_local/<int:agency_id>', methods=["GET", "POST"])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Payment_admin_local(agency_id):

    agency_get_id = AgencyModel.get_by_id(agency_id)

    user_manager = UserModel.query(
        UserModel.agency == agency_get_id.key
    )

    transaction_admin_agency_query = TransactionModel.query(
        TransactionModel.agency == agency_get_id.key,
        TransactionModel.transaction_admin == True
    ).order(TransactionModel.transaction_date)

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    received = False
    if request.method == "POST" and agency_get_id.escrow_amount(True) < 0:
        amount = float(request.form['amount'])
        user_id = int(request.form['employe'])

        diff = agency_get_id.escrow_amount() - agency_get_id.escrow_amount(True)

        amount_diff = diff - amount
        if amount_diff >= 0:
            amount_to_save = amount
        else:
            amount_to_save = amount + amount_diff
            flash(u'Local Balance '+str(amount_diff*(-1))+u" "+str(agency_get_id.destination.get().currency.get().code)+u' has not saved', 'danger')

        #Traitement de la transaction parente

        parent_transaction = TransactionModel()
        parent_transaction.reason = "Agency Ticket Sale"
        parent_transaction.amount = amount_to_save
        parent_transaction.agency = agency_get_id.key
        parent_transaction.is_payment = True
        parent_transaction.transaction_admin = True
        parent_transaction.pre_amount = diff

        parent_transaction.destination = agency_get_id.destination
        parent_transaction.transaction_date = function.datetime_convert(date_auto_nows)

        user_current_id = UserModel.get_by_id(int(session.get('user_id')))
        parent_transaction.user = user_current_id.key


        user_employe_id = UserModel.get_by_id(int(user_id))
        parent_transaction.employe = user_employe_id.key

        parent_transaction = parent_transaction.put()

        received = True

    # Traitement de l'envoie d'email et de la facture
    if received:
        transaction_get = TransactionModel.get_by_id(int(parent_transaction.id()))
        detail_transaction = calcul_transaction(transaction_get)

        admin = False
        if request.args.get('admin'):
            admin = True

        #content = StringIO('contenu')
        content = render_template('/transaction/facture.html', **locals())
        output = StringIO()
        pisa.log.setLevel('DEBUG')
        pdf = pisa.CreatePDF(content, output, encoding='utf-8')
        pdf_data = pdf.dest.getvalue()
        output.close()
        name_pdf = str(parent_transaction.id())+"_received.pdf"

        from google.appengine.api import mail
        mail.send_mail(sender="no-reply@comantrans-online-2015.appspotmail.com",
                   to=user_employe_id.email,
                   subject="Your received for transaction "+str(parent_transaction.id()),
                   body="Your message for your received",
                   attachments=[(name_pdf, pdf_data)])

        detail_transaction = calcul_transaction(transaction_get)

    return render_template('/transaction/payment_local_admin.html', **locals())


@app.route('/Payment_admin_foreign/<int:agency_id>')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Payment_admin_foreign(agency_id):
    agency_get_id = AgencyModel.get_by_id(agency_id)
    return render_template('/transaction/payment_foreign_admin.html', **locals())


@app.route('/Payment_admin_foreign_single/<int:agency_id>', methods=["GET", "POST"])
@app.route('/Payment_admin_foreign_single/<int:agency_id>/<int:destination_id>', methods=["GET", "POST"])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Payment_admin_foreign_single(agency_id, destination_id=None):

    from ..destination.models_destination import DestinationModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")


    agency_get_id = AgencyModel.get_by_id(agency_id)
    destination_get_id = DestinationModel.get_by_id(destination_id)

    user_manager = UserModel.query(
        UserModel.agency == agency_get_id.key
    )


    transaction_destination_query = TransactionModel.query(
        TransactionModel.destination == destination_get_id.key,
        TransactionModel.agency == agency_get_id.key,
        TransactionModel.transaction_admin == True
    )

    transaction_destination_query_2 = TransactionModel.query(
        TransactionModel.destination == destination_get_id.key,
        TransactionModel.agency == agency_get_id.key
    )

    amount = 0
    amount_agency = 0
    for transaction in transaction_destination_query_2:

        entry_query_agency = TransactionModel.query(
            TransactionModel.is_payment == True,
            TransactionModel.agency == agency_get_id.key,
            TransactionModel.transaction_admin == False,
            TransactionModel.destination == transaction.destination
        )

        # SOMMES DES ENTRES
        entry_amount_agency = 0
        for entry in entry_query_agency:
            entry_amount_agency += entry.amount


        entry_query = TransactionModel.query(
            TransactionModel.is_payment == True,
            TransactionModel.agency == agency_get_id.key,
            TransactionModel.transaction_admin == True,
            TransactionModel.destination == transaction.destination
        )

        # SOMMES DES ENTRES
        entry_amount = 0
        for entry in entry_query:
            entry_amount += entry.amount

        expense_query = TransactionModel.query(
            TransactionModel.is_payment == False,
            TransactionModel.agency == agency_get_id.key,
            TransactionModel.transaction_admin == False,
            TransactionModel.destination == transaction.destination
        )

        # SOMMES DES SORTIES
        expense_amount = 0
        for expense in expense_query:
            expense_amount += expense.amount

        # TOTAL RETENU
        amount = entry_amount - expense_amount

        amount_agency = entry_amount_agency - expense_amount

    received = False
    if request.method == "POST":

        amount_local = 0
        for transaction in transaction_destination_query_2:
            entry_query = TransactionModel.query(
                TransactionModel.is_payment == True,
                TransactionModel.agency == agency_get_id.key,
                TransactionModel.transaction_admin == False,
                TransactionModel.destination == transaction.destination
            )

            # SOMMES DES ENTRES
            entry_amount = 0
            for entry in entry_query:
                entry_amount += entry.amount

            expense_query = TransactionModel.query(
                TransactionModel.is_payment == False,
                TransactionModel.agency == agency_get_id.key,
                TransactionModel.transaction_admin == False,
                TransactionModel.destination == transaction.destination
            )

            # SOMMES DES SORTIES
            expense_amount = 0
            for expense in expense_query:
                expense_amount += expense.amount

            # TOTAL RETENU CHEZ LE MANAGER
            amount_local = entry_amount - expense_amount

        amount_form = float(request.form['amount'])

        user_id = int(request.form['employe'])

        diff = amount_local - amount

        amount_diff = diff - amount_form
        if amount_diff > 0:
            amount_to_save = amount_form
        else:
            amount_to_save = amount_form + amount_diff
            flash(u'Foreign Balance '+str(amount_diff*-1)+u" "+str(destination_get_id.currency.get().code)+u' has not saved', 'danger')

        #Traitement de la transaction parente

        parent_transaction = TransactionModel()
        parent_transaction.reason = "Payment"
        parent_transaction.amount = amount_to_save
        parent_transaction.agency = agency_get_id.key
        parent_transaction.is_payment = True
        parent_transaction.transaction_admin = True
        parent_transaction.pre_amount = diff


        parent_transaction.destination = destination_get_id.key
        parent_transaction.transaction_date = function.datetime_convert(date_auto_nows)

        user_current_id = UserModel.get_by_id(int(session.get('user_id')))
        parent_transaction.user = user_current_id.key

        user_employe_id = UserModel.get_by_id(int(user_id))
        parent_transaction.user = user_employe_id.key
        parent_transaction = parent_transaction.put()

        received = True

    # Traitement de l'envoie d'email et de la facture
    if received:
        transaction_get = TransactionModel.get_by_id(int(parent_transaction.id()))
        detail_transaction = calcul_transaction(transaction_get)

        #content = StringIO('contenu')
        content = render_template('/transaction/facture.html', **locals())
        output = StringIO()
        pisa.log.setLevel('DEBUG')
        pdf = pisa.CreatePDF(content, output, encoding='utf-8')
        pdf_data = pdf.dest.getvalue()
        output.close()
        name_pdf = str(parent_transaction.id())+"_received.pdf"

        from google.appengine.api import mail
        mail.send_mail(sender="no-reply@comantrans-online-2015.appspotmail.com",
                   to=user_employe_id.email,
                   subject="Your received for transaction "+str(parent_transaction.id()),
                   body="Your message for your received",
                   attachments=[(name_pdf, pdf_data)])

        detail_transaction = calcul_transaction(transaction_get)

    return render_template('/transaction/payment_foreign_admin_single.html', **locals())