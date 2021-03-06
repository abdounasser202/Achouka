__author__ = 'wilrona'


from ...modules import *

from ..customer.models_customer import CustomerModel
from ..ticket.models_ticket import (TicketPoly, TicketModel, TicketTypeNameModel,
                                    JourneyTypeModel, ClassTypeModel, AgencyModel, QuestionModel, TicketQuestion)

from ..customer.forms_customer import FormCustomerPOS


cache = Cache(app)


@app.route('/point-of-sale/<int:departure_id>', methods=['GET', 'POST'])
@app.route('/point-of-sale', methods=['GET', 'POST'])
@login_required
@roles_required(('employee_POS', 'super_admin'))
def Pos(departure_id=None):
    menu = 'pos'
    from ..ticket.models_ticket import TicketModel, AgencyModel, DepartureModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    today = function.datetime_convert(date_auto_nows)

    departure = DepartureModel.query(
        DepartureModel.departure_date >= datetime.date.today()
    ).order(
        DepartureModel.departure_date,
        DepartureModel.schedule,
        DepartureModel.time_delay
    )

    if not departure_id:
        current_departure = None
        if current_user.have_agency():
            agence_id = session.get('agence_id')
            user_agence = AgencyModel.get_by_id(int(agence_id))

            for dep in departure:
                departure_time = function.add_time(dep.schedule, dep.time_delay)
                departure_datetime = datetime.datetime(dep.departure_date.year, dep.departure_date.month, dep.departure_date.day, departure_time.hour, departure_time.minute, departure_time.second)
                if dep.destination.get().destination_start == user_agence.destination and departure_datetime > today:
                    current_departure = dep
                    break
        else:
            for dep in departure:
                departure_time = function.add_time(dep.schedule, dep.time_delay)
                departure_datetime = datetime.datetime(dep.departure_date.year, dep.departure_date.month, dep.departure_date.day, departure_time.hour, departure_time.minute, departure_time.second)
                if departure_datetime > today:
                    current_departure = dep
                    break

    else:
        current_departure = DepartureModel.get_by_id(departure_id)

    if current_departure:
        last_sale = TicketModel.query(
            TicketModel.departure == current_departure.key,
            TicketModel.selling == True,
            TicketModel.statusValid == True
        ).order(-TicketModel.date_reservation).fetch(limit=3)

    age = date_age
    return render_template('/index/pos.html', **locals())


@app.route('/reset_remaining_ticket')
def reset_remaining_ticket():

    if session.get('agence_id'):
        agency_user = AgencyModel.get_by_id(int(session.get('agence_id')))
        number = agency_user.TicketUnsold()
    else:
        number = 'No Ticket'

    return number+' Available'


@app.route('/ticket_sale_current/<int:departure_id>')
def ticket_sale_current(departure_id):

    from ..departure.models_departure import DepartureModel

    current_departure = DepartureModel.get_by_id(departure_id)
    last_sale = TicketModel.query(
            TicketModel.departure == current_departure.key,
            TicketModel.selling == True,
            TicketModel.statusValid == True
        ).order(-TicketModel.date_reservation)

    return render_template('/pos/ticket_sale_current.html', **locals())


@app.route('/search_customer_pos', methods=['GET', 'POST'])
@login_required
@roles_required(('employee_POS', 'super_admin'))
def search_customer_pos():
    from ..departure.models_departure import DepartureModel

    child = False
    if request.args.get('child'):
        child = True
        parent_ticket = request.args.get('parent_ticket')


    current_departure = None
    if request.form['current_departure']:
        current_departure = DepartureModel.get_by_id(int(request.form['current_departure']))

    birtday = request.form['birthday']
    full_name = request.form['full_name']

    customer = CustomerModel.query(
        CustomerModel.birthday == function.date_convert(birtday)
    )

    customer_count = CustomerModel.query(
        CustomerModel.birthday == function.date_convert(birtday)
    ).count()

    birth_and_full = False
    if full_name:
        birth_and_full = True
        list_customer_ids = []
        customer_count = 0
        for cust in customer:
            full_name_db = cust.last_name+" "+cust.first_name
            find_full_name = function.find(full_name_db, full_name)
            if find_full_name:
                list_customer_ids.append(cust.key.id())
                customer_count += 1

    return render_template('/pos/search_customer.html', **locals())


@app.route('/search_ticket_pos', methods=['GET', 'POST'])
@login_required
@roles_required(('employee_POS', 'super_admin'))
def search_ticket_pos():

    from ..departure.models_departure import DepartureModel
    number_ticket = request.form['number_ticket']

    number_ticket = ''.join(number_ticket.split('*'))

    departure_get = None
    departure_id = request.args.get('departure')
    if departure_id:
        departure_find = DepartureModel.get_by_id(int(departure_id))
        departure_get = departure_find.key

    if len(number_ticket) < 16:
        ticket_sold = TicketModel.query(
            TicketModel.selling == True
        )
        list_ticket_sold = []
        for ticket in ticket_sold:
            find_ticket_sold = function.find(str(ticket.key.id())+" ", str(number_ticket))
            if find_ticket_sold:
                list_ticket_sold.append(ticket.key.id())
        return render_template('/pos/search_ticket.html', **locals())
    else:
        ticket = TicketModel.get_by_id(int(number_ticket))
        return render_template('/pos/ticket_found.html', **locals())


@app.route('/Ticket_found/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('employee_POS', 'super_admin'))
def Ticket_found(ticket_id):
    from ..departure.models_departure import DepartureModel

    ticket = TicketModel.get_by_id(ticket_id)

    departure_get = None
    departure_id = request.args.get('departure')
    if departure_id:
        departure_find = DepartureModel.get_by_id(int(departure_id))
        departure_get = departure_find.key

    return render_template('/pos/ticket_found.html', **locals())


@app.route('/find_parent_ticket_return/<int:ticket_id>/<int:departure_id>', methods=['POST'])
@app.route('/find_parent_ticket_return', methods=['POST'])
def find_parent_ticket_return(ticket_id=None, departure_id=None):
    from ..departure.models_departure import DepartureModel

    departure_get = DepartureModel.get_by_id(departure_id)

    number_ticket = request.form['number_tickets']

    upgrade = request.args.get('upgrade')

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    today = function.datetime_convert(date_auto_nows).date()

    number_ticket = ''.join(number_ticket.split('*'))

    ticket_sold = TicketModel.query(
        TicketModel.selling == True,
        TicketModel.departure == departure_get.key
    )

    list_ticket_sold = []
    for ticket in ticket_sold:
        find_ticket_sold = function.find(str(ticket.key.id())+" ", str(number_ticket))
        diff_year = today.year - function.date_convert(ticket.customer.get().birthday).year
        if find_ticket_sold and int(diff_year) > date_age['max']:
            list_ticket_sold. append(ticket.key.id())

    return render_template('/pos/search_ticket_parent.html', **locals())


@app.route('/select_parent_ticket/<int:ticket_id>/<int:departure_id>')
@app.route('/select_parent_ticket/<int:ticket_id>')
def select_parent_ticket(ticket_id, departure_id):

    upgrade = request.args.get('upgrade')
    return render_template('/pos/select_parent_ticket.html', **locals())

@app.route('/create_customer_and_ticket_return/<int:ticket_id>/<int:departure_id>', methods=['GET', 'POST'])
@app.route('/create_customer_and_ticket_return/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('employee_POS', 'super_admin'))
def create_customer_and_ticket_return(ticket_id, departure_id=None):

    from ..departure.models_departure import DepartureModel
    from ..user.models_user import UserModel

    Ticket_Return = TicketModel.get_by_id(ticket_id)

    #information de l'agence de l'utilisateur
    agency_current_user = AgencyModel.get_by_id(int(session.get('agence_id')))

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    number_list = global_dial_code_custom
    nationalList = global_nationality_contry

    #Verifier que les questions obligatoires ont ete selectionne
    question_request = None
    if request.method == 'POST':
        question_request = request.form.getlist('questions')

    #liste des questions
    questions = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True
    )

    #Traitement des questions obligatoires
    quest_obligated = []
    obligated = False
    number_obligated_question = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True,
        QuestionModel.is_obligate == True
    ).count()

    obligated_question = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True,
        QuestionModel.is_obligate == True
    )

    # s'il n'y a pas de question envoye et qu'il y'a des questions obligatoires definies
    if number_obligated_question >= 1 and question_request is None and request.method == 'POST':
        obligated = True
        quest_obligated = [question.key.id() for question in obligated_question]
    else:
        if question_request:
            count = 0

            #boucle la liste des questions envoyees et verifie si c'est dans la liste des questions obligatoires
            for quest in question_request:
                ks = QuestionModel.get_by_id(int(quest))
                if ks.is_obligate:
                    count += 1
                    quest_obligated.append(int(quest))

            # verifie que le quota de question obligatoire est atteint dans le questionnaire
            if count < number_obligated_question:
                obligated = True

    #information du client
    customer = CustomerModel.get_by_id(Ticket_Return.customer.get().key.id())
    form = FormCustomerPOS(obj=customer)
    if request.args.get('child'):
        form.child.data = 1

    # Envoie des informations par default sur la vue
    form.type_name.data = Ticket_Return.type_name.get().key.id()
    form.class_name.data = Ticket_Return.class_name.get().key.id()
    form.journey_name.data = Ticket_Return.journey_name.get().key.id()

    # information du depart courant
    departure_current = DepartureModel.get_by_id(departure_id)
    form.current_departure.data = str(departure_current.key.id())

    journey_ticket = JourneyTypeModel.query()
    class_ticket = ClassTypeModel.query()
    ticket_type_name = TicketTypeNameModel.query()

    #Traitement de l'affichage d'une attention sur la vente a effectuer
    today = function.datetime_convert(date_auto_nows)

    #liste des departs supperieur a la date du jour
    departure = DepartureModel.query(
        DepartureModel.departure_date >= datetime.date.today()
    ).order(
        DepartureModel.departure_date,
        DepartureModel.schedule,
        DepartureModel.time_delay
    )

    warning = False
    if current_user.have_agency():
            agence_id = session.get('agence_id')
            user_agence = AgencyModel.get_by_id(int(agence_id))
            current_departure = None
            for dep in departure:
                departure_time = function.add_time(dep.schedule, dep.time_delay)
                departure_datetime = datetime.datetime(dep.departure_date.year, dep.departure_date.month, dep.departure_date.day, departure_time.hour, departure_time.minute, departure_time.second)
                if dep.destination.get().destination_start == user_agence.destination and departure_datetime > today:
                    current_departure = dep
                    break
            if current_departure and current_departure.key.id() != departure_current.key.id():
                warning = True

    modal = 'false'
    ticket_update = None

    if form.validate_on_submit() and not obligated:

        if customer.first_name != form.first_name.data or\
            customer.last_name != form.last_name.data and customer.birthday != function.date_convert(form.birthday.data)\
            or customer.email != form.email.data or customer.nationality != form.nationality.data or\
            customer.dial_code != form.dial_code.data or customer.phone != form.phone.data or\
                        customer.profession != form.profession.data or customer.nic_number != form.nic_number.data or\
                customer.passport_number != form.passport_number.data:

            customer.first_name = form.first_name.data
            customer.last_name = form.last_name.data
            customer.birthday = function.date_convert(form.birthday.data)
            customer.email = form.email.data
            customer.nationality = form.nationality.data
            customer.dial_code = form.dial_code.data
            customer.phone = form.phone.data
            customer.profession = form.profession.data
            customer.nic_number = form.nic_number.data
            customer.passport_number = form.passport_number.data
            customer.is_new = False
            customer_save = customer.put()
        else:
            customer.is_new = False
            customer_save = customer.put()

        child_ticket = TicketModel.query(
            TicketModel.parent_return == Ticket_Return.key
        ).get()

        child_ticket.selling = True
        child_ticket.date_reservation = function.datetime_convert(date_auto_nows)
        child_ticket.travel_ticket = departure_current.destination

        user = UserModel.get_by_id(int(session.get('user_id')))
        child_ticket.ticket_seller = user.key

        #sauvegarde de l'agence de l'utilisateur courant
        child_ticket.agency = agency_current_user.key

        child_ticket.departure = departure_current.key

        if request.args.get("parent_ticket"):
            ticket_parent = TicketModel.get_by_id(int(request.args.get("parent_ticket")))
            child_ticket.parent_child = ticket_parent.key

        ticket_update = child_ticket.put()

        Ticket_Return.statusValid = False
        this_ticket = Ticket_Return.put()

        from ..activity.models_activity import ActivityModel

        time_zones = pytz.timezone('Africa/Douala')
        date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

        activity = ActivityModel()
        activity.user_modify = current_user.key
        activity.object = "TicketModel"
        activity.time = function.datetime_convert(date_auto_nows)
        activity.identity = this_ticket.id()
        activity.nature = 1
        activity.put()

        modal = 'true'

    return render_template('/pos/create_customer_and_ticket_return.html', **locals())


@app.route('/create_customer_and_ticket_pos', methods=['GET', 'POST'])
@app.route('/create_customer_and_ticket_pos/<int:customer_id>/<int:departure_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('employee_POS', 'super_admin'))
def create_customer_and_ticket_pos(customer_id=None, departure_id=None):
    from ..ticket_type.models_ticket_type import TicketTypeModel
    from ..departure.models_departure import DepartureModel
    from ..user.models_user import UserModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")


    number_list = global_dial_code_custom
    nationalList = global_nationality_contry

    #Verifier que les questions obligatoires ont ete selectionne
    question_request = None
    if request.method == 'POST':
        question_request = request.form.getlist('questions')

    #liste des questions
    questions = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True
    )

    # information du depart pour le ticket a afficher sur le template
    if departure_id:
        print_depature = DepartureModel.get_by_id(int(departure_id))
    else:
        if request.method == 'GET':
            print_depature = DepartureModel.get_by_id(int(request.args.get('current_departure')))
        else:
            print_depature = DepartureModel.get_by_id(int(request.form['current_departure']))


    #Traitement des questions obligatoires
    quest_obligated = []
    obligated = False
    number_obligated_question = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True,
        QuestionModel.is_obligate == True
    ).count()

    obligated_question = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True,
        QuestionModel.is_obligate == True
    )

    # s'il n'y a pas de question envoye et qu'il y'a des questions obligatoires definient
    if number_obligated_question >= 1 and question_request is None and request.method == 'POST':
        obligated = True
        quest_obligated = [question.key.id() for question in obligated_question]
    else:
        if question_request:
            count = 0
            #boucle la liste des questions envoyees et verifie si c'est dans la liste des questions obligatoires
            for quest in question_request:
                ks = QuestionModel.get_by_id(int(quest))
                if ks.is_obligate:
                    count += 1
                    quest_obligated.append(int(quest))

            # verifie que le quota de question obligatoire est atteint dans le questionnaire
            if count < number_obligated_question:
                obligated = True

    if customer_id:
        customer = CustomerModel.get_by_id(customer_id)
        form = FormCustomerPOS(obj=customer)
        if request.args.get('child'):
            form.child.data = 1
    else:
        customer = CustomerModel()
        # recuperation du formulaire en fonction de la methode
        if request.method == 'GET':
            form = FormCustomerPOS(request.args)
        else:
            form = FormCustomerPOS(request.form)

    if departure_id:
        form.current_departure.data = str(departure_id)

    class_ticket = ClassTypeModel.query()
    ticket_type_name = TicketTypeNameModel.query()

    child = request.args.get('child')
    parent_ticket = None
    if child:
        parent_ticket = int(request.args.get('parent_ticket'))
        parent = TicketModel.get_by_id(parent_ticket)
        class_ticket = ClassTypeModel.query(
            ClassTypeModel.key == parent.class_name
        )
        ticket_type_name = TicketTypeNameModel.query(
            TicketTypeNameModel.is_child == True
        )
    journey_ticket = JourneyTypeModel.query()


    #Traitement de l'affichage d'une attention sur la vente a effectuer
    today = function.datetime_convert(date_auto_nows)

    #liste des departs supperieur a la date du jour
    departure = DepartureModel.query(
        DepartureModel.departure_date >= datetime.date.today()
    ).order(
        DepartureModel.departure_date,
        DepartureModel.schedule,
        DepartureModel.time_delay
    )

    warning = False
    if current_user.have_agency():
            agence_id = session.get('agence_id')
            user_agence = AgencyModel.get_by_id(int(agence_id))
            current_departure = None
            for dep in departure:
                departure_time = function.add_time(dep.schedule, dep.time_delay)
                departure_datetime = datetime.datetime(dep.departure_date.year, dep.departure_date.month, dep.departure_date.day, departure_time.hour, departure_time.minute, departure_time.second)
                if dep.destination.get().destination_start == user_agence.destination and departure_datetime > today:
                    current_departure = dep
                    break
            if current_departure and current_departure.key.id() != print_depature.key.id():
                warning = True

    modal = 'false'
    ticket_update = None

    if form.validate_on_submit() and not obligated:

        if customer.first_name != form.first_name.data or\
            customer.last_name != form.last_name.data and customer.birthday != function.date_convert(form.birthday.data)\
            or customer.email != form.email.data or customer.nationality != form.nationality.data or\
            customer.dial_code != form.dial_code.data or customer.phone != form.phone.data or\
                        customer.profession != form.profession.data or customer.nic_number != form.nic_number.data or\
                customer.passport_number != form.passport_number.data:

            customer.first_name = form.first_name.data
            customer.last_name = form.last_name.data
            customer.birthday = function.date_convert(form.birthday.data)
            customer.email = form.email.data
            customer.nationality = form.nationality.data
            customer.dial_code = form.dial_code.data
            customer.phone = form.phone.data
            customer.profession = form.profession.data
            customer.nic_number = form.nic_number.data
            customer.passport_number = form.passport_number.data
            customer.date_create = function.datetime_convert(date_auto_nows)
            if customer_id:
                customer.is_new = False
            else:
                customer.is_new = True
            customer_save = customer.put()
        else:
            customer.is_new = False
            customer_save = customer.put()

        # caracteristique des tickets
        journey_ticket_car = JourneyTypeModel.get_by_id(int(form.journey_name.data))
        class_ticket_car = ClassTypeModel.get_by_id(int(form.class_name.data))
        ticket_type_name_car = TicketTypeNameModel.get_by_id(int(form.type_name.data))

        priceticket = TicketTypeModel.query(
            TicketTypeModel.type_name == ticket_type_name_car.key,
            TicketTypeModel.class_name == class_ticket_car.key,
            TicketTypeModel.journey_name == journey_ticket_car.key,
            TicketTypeModel.travel == print_depature.destination,
            TicketTypeModel.active == True
        ).get()
        agency_current_user = AgencyModel.get_by_id(int(session.get('agence_id')))

        Ticket_To_Sell = TicketModel.query(
            TicketModel.type_name == ticket_type_name_car.key,
            TicketModel.class_name == class_ticket_car.key,
            TicketModel.journey_name == journey_ticket_car.key,
            TicketModel.agency == agency_current_user.key,
            TicketModel.travel_ticket == print_depature.destination,
            TicketModel.selling == False
        ).order(TicketModel.datecreate).get()

        for kest in questions:
            Answers = TicketQuestion()
            Answers.ticket_id = Ticket_To_Sell.key
            Answers.question_id = kest.key
            if kest.is_obligate:
                Answers.response = True
            else:
                if str(kest.key.id()) in question_request:
                    Answers.response = True
                else:
                    Answers.response = False
            Answers.put()

        Ticket_To_Sell.selling = True
        Ticket_To_Sell.is_ticket = True
        Ticket_To_Sell.date_reservation = function.datetime_convert(date_auto_nows)
        Ticket_To_Sell.sellprice = priceticket.price
        Ticket_To_Sell.sellpriceCurrency = priceticket.currency

        if parent_ticket:
            Ticket_To_Sell.parent_child = parent.key

        if Ticket_To_Sell.is_return:
            duplicate_ticket = TicketModel()
            duplicate_ticket.type_name = Ticket_To_Sell.type_name
            duplicate_ticket.class_name = Ticket_To_Sell.class_name
            duplicate_ticket.is_ticket = True
            duplicate_ticket.is_count = False
            duplicate_ticket.datecreate = function.datetime_convert(date_auto_nows)

            customer_ticket = CustomerModel.get_by_id(customer_save.id())
            duplicate_ticket.customer = customer_ticket.key

            duplicate_ticket.parent_return = Ticket_To_Sell.key

            duplicate_ticket.put()

        customer_ticket = CustomerModel.get_by_id(customer_save.id())
        Ticket_To_Sell.customer = customer_ticket.key

        departure_ticket = DepartureModel.get_by_id(int(form.current_departure.data))
        Ticket_To_Sell.departure = departure_ticket.key

        user_ticket = UserModel.get_by_id(int(session.get('user_id')))
        Ticket_To_Sell.ticket_seller = user_ticket.key

        from ..transaction.models_transaction import TransactionModel, ExpensePaymentTransactionModel

        # Prise en compte des variations de prix des tickets avec les types de tickets
        last_transaction = None
        amount_different = 0
        if priceticket.price > Ticket_To_Sell.sellpriceAg:
            amount_different = priceticket.price - Ticket_To_Sell.sellpriceAg
            transaction = TransactionModel()
            transaction.agency = user_ticket.agency
            transaction.amount = amount_different
            transaction.destination = Ticket_To_Sell.travel_ticket.get().destination_start
            transaction.is_payment = False
            transaction.user = user_ticket.key
            transaction.transaction_date = function.datetime_convert(date_auto_nows)
            transaction.reason = " Additional cost to the ticket price difference"
            last_transaction = transaction.put()

            last_transaction = TransactionModel.get_by_id(last_transaction.id())

        if priceticket.price < Ticket_To_Sell.sellpriceAg:
            amount_different = Ticket_To_Sell.sellpriceAg - priceticket.price
            transaction = TransactionModel()
            transaction.agency = user_ticket.agency
            transaction.amount = amount_different
            transaction.destination = Ticket_To_Sell.travel_ticket.get().destination_start
            transaction.is_payment = True
            transaction.user = user_ticket.key
            transaction.transaction_date = function.datetime_convert(date_auto_nows)
            transaction.reason = " Additional cost to the ticket price difference"
            last_transaction = transaction.put()

            last_transaction = TransactionModel.get_by_id(last_transaction.id())

        if last_transaction:
            link_transaction = ExpensePaymentTransactionModel()
            link_transaction.amount = amount_different
            link_transaction = last_transaction.key
            link_transaction.ticket = Ticket_To_Sell.key
            link_transaction.is_difference = True
            link_transaction.put()

        ticket_update = Ticket_To_Sell.put()
        modal = 'true'

    return render_template('/pos/create_customer_and_ticket.html', **locals())


@app.route('/modal_generate_pdf_ticket')
@app.route('/modal_generate_pdf_ticket/<int:ticket_id>')
@login_required
@roles_required(('employee_POS', 'super_admin'))
def modal_generate_pdf_ticket(ticket_id=None):
    return render_template('/pos/view-pdf.html', **locals())


@app.route('/generate_pdf_ticket/<int:ticket_id>')
@login_required
@roles_required(('employee_POS', 'super_admin'))
def generate_pdf_ticket(ticket_id):

    Ticket_print = TicketPoly.get_by_id(ticket_id)

    import cStringIO
    output = cStringIO.StringIO()

    style = getSampleStyleSheet()
    width, height = 595.27, 280.63
    p = canvas.Canvas(output, pagesize=(595.27, 280.63))

    code = str(Ticket_print.key.id())
    barcode = code39.Standard39(code, barHeight=20, stop=1)
    barcode.humanReadable = 1

    string = '<font name="Times-Roman" size="14">%s</font>'

    journey = string % 'Return Ticket'
    if Ticket_print.journey_name:
        journey = string % Ticket_print.journey_name.get().name

    econo = string % Ticket_print.class_name.get().name+" - "+string % Ticket_print.type_name.get().name+" - "+journey
    name = string % Ticket_print.customer.get().first_name+" "+string % Ticket_print.customer.get().last_name
    froms = string % Ticket_print.departure.get().destination.get().destination_start.get().name
    destination = string % Ticket_print.departure.get().destination.get().destination_check.get().name
    date = string % str(function.format_date(Ticket_print.departure.get().departure_date, '%d-%m-%Y'))
    time = string % str(function.format_date(function.add_time(Ticket_print.departure.get().schedule, Ticket_print.departure.get().time_delay), "%H:%M"))
    lieu = string % Ticket_print.agency.get().name
    agent = string % str(Ticket_print.ticket_seller.get().key.id())

    p.drawImage(url_for('static', filename='TICKET-ONLY-2.jpg', _external=True), 0, 0, width=21*cm, height=9.9*cm, preserveAspectRatio=True)

    c = Paragraph(econo, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 7.3*cm, 7.9*cm)

    c = Paragraph(name, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 2.97*cm, 6.42*cm)

    c = Paragraph(froms, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 2.97*cm, 4.9*cm)

    c = Paragraph(destination, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 8.56*cm, 4.9*cm)

    c = Paragraph(date, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 2.97*cm, 3.42*cm)

    c = Paragraph(time, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 8.56*cm, 3.42*cm)

    c = Paragraph(lieu, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 2.97*cm, 1.9*cm)

    c = Paragraph(agent, style=style['Normal'])
    c.wrapOn(p, width, height)
    c.drawOn(p, 8.56*cm, 1.9*cm)


    p.saveState()
    p.translate(2*cm, 13.9*cm)
    p.setFillColorRGB(255, 255, 255)
    p.setStrokeColorRGB(255, 255, 255)
    p.rect(-1.1*cm, -12.5*cm, 1.2*cm, 5.5*cm, fill=1)
    p.rotate(-90)
    p.setFillColorRGB(0, 0, 0)
    barcode.drawOn(p, 6.6*cm, -0.80*cm)
    p.restoreState()


    p.showPage()
    p.save()

    pdf_out = output.getvalue()
    output.close()

    response = make_response(pdf_out)
    response.headers["Content-Type"] = "application/pdf"

    return response


@app.route('/Search_Ticket_Type', methods=['GET','POST'])
@login_required
@roles_required(('employee_POS', 'super_admin'))
def Search_Ticket_Type():

    from ..ticket_type.models_ticket_type import TicketTypeModel
    from ..departure.models_departure import DepartureModel

    type_name = request.json['type_name']
    class_name = request.json['class_name']
    journey_name = request.json['journey_name']
    current_departure = request.json['current_departure']

    typeticket = TicketTypeNameModel.get_by_id(int(type_name))
    journeyticket = JourneyTypeModel.get_by_id(int(journey_name))
    classticket = ClassTypeModel.get_by_id(int(class_name))

    departure = DepartureModel.get_by_id(int(current_departure))


    priceticket = TicketTypeModel.query(
        TicketTypeModel.type_name == typeticket.key,
        TicketTypeModel.class_name == classticket.key,
        TicketTypeModel.journey_name == journeyticket.key,
        TicketTypeModel.travel == departure.destination.get().key,
        TicketTypeModel.active == True
    ).get()

    Agency_ticket = 0
    if session.get('agence_id'):
        agency_user = AgencyModel.get_by_id(int(session.get('agence_id')))
        Agency_ticket = TicketModel.query(
            TicketModel.class_name == classticket.key,
            TicketModel.type_name == typeticket.key,
            TicketModel.journey_name == journeyticket.key,
            TicketModel.agency == agency_user.key,
            TicketModel.travel_ticket == departure.destination.get().key,
            TicketModel.selling == False
        ).count()


    have_ticket = 'false'
    if Agency_ticket >= 1:
        have_ticket = 'true'

    if priceticket:
        data = json.dumps({
            'statut': 'OK',
            'price': function.format_price(priceticket.price),
            'currency': priceticket.currency.get().code,
            'type_name' : typeticket.name,
            'class_name': classticket.name,
            'journey_name': journeyticket.name,
            'haveticket': have_ticket
        }, sort_keys=True)
    else:
        data = json.dumps({
            'statut': 'error',
            'value': 'Undefined',
            'type_name' : typeticket.name,
            'class_name': classticket.name,
            'journey_name': journeyticket.name,
            'haveticket': have_ticket
        }, sort_keys=True)

    return data


@app.route('/remaining_ticket')
@login_required
@roles_required(('employee_POS', 'super_admin'))
def remaining_ticket():
    from ..departure.models_departure import DepartureModel
    number = current_user.remaining_ticket()
    departure_id = DepartureModel.get_by_id(int(request.args.get('departure')))

    last_sale = TicketModel.query(
                TicketModel.departure == departure_id.key,
                TicketModel.selling == True,
                TicketModel.statusValid == True
            ).order(-TicketModel.date_reservation).fetch(limit=3)

    tickets = []
    for ticket in last_sale:
        last = {}
        last['id'] = str(ticket.key.id())
        last['customer'] = ticket.customer.get().last_name+" "+ticket.customer.get().first_name
        tickets.append(last)

    data = json.dumps({
        'ticket': number,
        'ticket_sale': tickets
    }, sort_keys=True)

    return data


@app.route('/Calendrier')
@login_required
@roles_required(('employee_POS', 'super_admin'))
def Calendrier(current_month_active=None, current_day_active=None):

    cal = calendar.Calendar(0)

    year = datetime.date.today().year

    if not current_month_active:
        current_month_active = datetime.date.today().month

    if not current_day_active:
        current_day_active = datetime.date.today().day

    cal_list = [cal.monthdatescalendar(year, i+1) for i in xrange(12)]

    return render_template('/pos/calendrier.html', **locals())


@app.route('/List_All_Departure/<int:current_month_active>/<int:current_day_active>')
@app.route('/List_All_Departure')
@login_required
@roles_required(('employee_POS', 'super_admin'))
def List_All_Departure(current_month_active=None, current_day_active=None):
    from ..departure.models_departure import DepartureModel

    year = datetime.date.today().year

    if not current_month_active:
        current_month_active = datetime.date.today().month

    if not current_day_active:
        current_day_active = datetime.date.today().day

    date = datetime.date(year, current_month_active, current_day_active)
    departure_list = DepartureModel.query(
        DepartureModel.departure_date == date
    ).order(
        DepartureModel.schedule,
        DepartureModel.time_delay
    )

    day_today = datetime.date.today().day
    month_today = datetime.date.today().month
    date_day = datetime.date(year, month_today, day_today)

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    time_now = function.datetime_convert(date_auto_nows).time()

    return render_template('/pos/list_all_departure.html', **locals())


@app.route('/point-of-sale/ticket-available')
@login_required
@roles_required(('employee_POS', 'super_admin'))
def Ticket_POS():
    menu = "ticket_available"
    from ..ticket_type.models_ticket_type import TicketTypeModel

    #information de l'agence de l'utilisateur
    current_agency = AgencyModel.get_by_id(int(session.get('agence_id')))

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

    return render_template('/pos/ticket-available.html', **locals())


@app.route('/create_customer_and_ticket_upgrade/<int:ticket_id>/<int:departure_id>')
@app.route('/create_customer_and_ticket_upgrade/<int:ticket_id>')
def create_customer_and_ticket_upgrade(ticket_id, departure_id=None):
    from ..ticket_type.models_ticket_type import TicketTypeModel
    from ..departure.models_departure import DepartureModel

    ticket_get = TicketModel.get_by_id(ticket_id)

    departure_get = DepartureModel.get_by_id(departure_id)
    upgrade = request.args.get('upgrade')
    parent_ticket = request.args.get("parent_ticket")

    ticket_type_query = TicketTypeModel.query(
        TicketTypeModel.journey_name != ticket_get.journey_name,
        TicketTypeModel.class_name == ticket_get.class_name,
        TicketTypeModel.type_name == ticket_get.type_name,
        TicketTypeModel.active == True,
        TicketTypeModel.travel == departure_get.destination
    )

    return render_template('/pos/create_customer_and_ticket_upgrade.html', **locals())


@app.route('/create_customer_and_ticket_upgrade_2/<int:departure_id>/<int:ticket_id>')
@app.route('/create_customer_and_ticket_upgrade_2/<int:departure_id>/<int:ticket_id>/<int:ticket_type_id>')
def create_customer_and_ticket_upgrade_2(departure_id, ticket_id, ticket_type_id=None):
    from ..ticket_type.models_ticket_type import TicketTypeModel
    from ..departure.models_departure import DepartureModel

    departure_get = DepartureModel.get_by_id(departure_id)
    upgrade = request.args.get('upgrade')

    ticket_type_get = TicketTypeModel.get_by_id(ticket_type_id)

    ticket_to_upgrade = TicketTypeModel.query(
        TicketTypeModel.class_name != ticket_type_get.class_name,
        TicketTypeModel.type_name == ticket_type_get.type_name,
        TicketTypeModel.journey_name == ticket_type_get.journey_name,
        TicketTypeModel.active == True,
        TicketTypeModel.travel == departure_get.destination
    )

    return render_template('/pos/create_customer_and_ticket_upgrade_2.html', **locals())


@app.route('/create_upgrade_ticket/<int:departure_id>/<int:ticket_id>/<int:ticket_type_same_id>/<int:ticket_type_id>', methods=['GET','POST'])
@app.route('/create_upgrade_ticket/<int:departure_id>/<int:ticket_id>/<int:ticket_type_same_id>', methods=['GET','POST'])
def create_upgrade_ticket(departure_id, ticket_id, ticket_type_same_id, ticket_type_id=None):

    from ..ticket_type.models_ticket_type import TicketTypeModel
    from ..departure.models_departure import DepartureModel
    from ..user.models_user import UserModel
    from ..transaction.models_transaction import TransactionModel, ExpensePaymentTransactionModel

    Ticket_Return = TicketModel.get_by_id(ticket_id)

    #information de l'agence de l'utilisateur
    agency_current_user = AgencyModel.get_by_id(int(session.get('agence_id')))

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    number_list = global_dial_code_custom
    nationalList = global_nationality_contry

    #Verifier que les questions obligatoires ont ete selectionne
    question_request = None
    if request.method == 'POST':
        question_request = request.form.getlist('questions')

    #liste des questions
    questions = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True
    )

    #Traitement des questions obligatoires
    quest_obligated = []
    obligated = False
    number_obligated_question = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True,
        QuestionModel.is_obligate == True
    ).count()

    obligated_question = QuestionModel.query(
        QuestionModel.is_pos == True,
        QuestionModel.active == True,
        QuestionModel.is_obligate == True
    )

    # s'il n'y a pas de question envoye et qu'il y'a des questions obligatoires definies
    if number_obligated_question >= 1 and question_request is None and request.method == 'POST':
        obligated = True
        quest_obligated = [question.key.id() for question in obligated_question]
    else:
        if question_request:
            count = 0

            #boucle la liste des questions envoyees et verifie si c'est dans la liste des questions obligatoires
            for quest in question_request:
                ks = QuestionModel.get_by_id(int(quest))
                if ks.is_obligate:
                    count += 1
                    quest_obligated.append(int(quest))

            # verifie que le quota de question obligatoire est atteint dans le questionnaire
            if count < number_obligated_question:
                obligated = True

    #information du client
    customer = CustomerModel.get_by_id(Ticket_Return.customer.get().key.id())
    form = FormCustomerPOS(obj=customer)
    if request.args.get('child'):
        form.child.data = 1

    ticket_type_choice_get = TicketTypeModel.get_by_id(ticket_type_id)
    ticket_type_same_get = TicketTypeModel.get_by_id(ticket_type_same_id)

    Amount = ticket_type_choice_get.price - ticket_type_same_get.price

    form.type_name.data = ticket_type_choice_get.type_name.get().key.id()
    form.class_name.data = ticket_type_choice_get.class_name.get().key.id()
    form.journey_name.data = ticket_type_choice_get.journey_name.get().key.id()

    departure_current = DepartureModel.get_by_id(departure_id)
    form.current_departure.data = str(departure_current.key.id())

    journey_ticket = JourneyTypeModel.query()
    class_ticket = ClassTypeModel.query()
    ticket_type_name = TicketTypeNameModel.query()

    #Traitement de l'affichage d'une attention sur la vente a effectuer
    today = function.datetime_convert(date_auto_nows)

    #liste des departs supperieur a la date du jour
    departure = DepartureModel.query(
        DepartureModel.departure_date >= datetime.date.today()
    ).order(
        DepartureModel.departure_date,
        DepartureModel.schedule,
        DepartureModel.time_delay
    )

    warning = False
    if current_user.have_agency():
        agence_id = session.get('agence_id')
        user_agence = AgencyModel.get_by_id(int(agence_id))
        current_departure = None
        for dep in departure:
            departure_time = function.add_time(dep.schedule, dep.time_delay)
            departure_datetime = datetime.datetime(dep.departure_date.year, dep.departure_date.month, dep.departure_date.day, departure_time.hour, departure_time.minute, departure_time.second)
            if dep.destination.get().destination_start == user_agence.destination and departure_datetime > today:
                current_departure = dep
                break
        if current_departure and current_departure.key.id() != departure_current.key.id():
            warning = True

    modal = 'false'
    ticket_update = None

    if form.validate_on_submit() and not obligated:

        if customer.first_name != form.first_name.data or\
            customer.last_name != form.last_name.data and customer.birthday != function.date_convert(form.birthday.data)\
            or customer.email != form.email.data or customer.nationality != form.nationality.data or\
            customer.dial_code != form.dial_code.data or customer.phone != form.phone.data or\
                        customer.profession != form.profession.data or customer.nic_number != form.nic_number.data or\
                customer.passport_number != form.passport_number.data:

            customer.first_name = form.first_name.data
            customer.last_name = form.last_name.data
            customer.birthday = function.date_convert(form.birthday.data)
            customer.email = form.email.data
            customer.nationality = form.nationality.data
            customer.dial_code = form.dial_code.data
            customer.phone = form.phone.data
            customer.profession = form.profession.data
            customer.nic_number = form.nic_number.data
            customer.passport_number = form.passport_number.data
            customer.is_new = False
            customer_save = customer.put()
        else:
            customer.is_new = False
            customer_save = customer.put()

        child_ticket = TicketModel.query(
            TicketModel.parent_return == Ticket_Return.key
        ).get()

        child_ticket.type_name = ticket_type_choice_get.type_name
        child_ticket.class_name = ticket_type_choice_get.class_name
        child_ticket.journey_name = ticket_type_choice_get.journey_name

        child_ticket.selling = True
        child_ticket.is_count = True
        child_ticket.date_reservation = function.datetime_convert(date_auto_nows)
        child_ticket.sellprice = Amount
        child_ticket.sellpriceAg = Amount

        child_ticket.sellpriceCurrency = ticket_type_choice_get.currency
        child_ticket.sellpriceAgCurrency = ticket_type_choice_get.currency

        child_ticket.travel_ticket = ticket_type_choice_get.travel

        user = UserModel.get_by_id(int(session.get('user_id')))
        child_ticket.ticket_seller = user.key
        child_ticket.agency = user.agency

        child_ticket.upgrade_parent = Ticket_Return.key
        child_ticket.is_upgrade = True
        child_ticket.departure = departure_current.key

        child_ticket.parent_return = None

        if request.args.get("parent_ticket"):
            ticket_parent = TicketModel.get_by_id(int(request.args.get("parent_ticket")))
            child_ticket.parent_child = ticket_parent.key

        # Modification du ticket enfant
        ticket_update = child_ticket.put()

        Ticket_Return.statusValid = False
        this_ticket = Ticket_Return.put()

        transaction = TransactionModel()
        transaction.reason = "Upgrade ticket"
        transaction.amount = Amount
        transaction.is_payment = False
        transaction.agency = user.agency
        transaction.destination = ticket_type_choice_get.travel.get().destination_start
        transaction.transaction_date = function.datetime_convert(date_auto_nows)
        transaction.user = user.key

        transaction_id = transaction.put()

        link_transaction = ExpensePaymentTransactionModel()
        link_transaction.transaction = transaction_id
        link_transaction.ticket = ticket_update
        link_transaction.amount = Amount
        link_transaction.put()

        modal = 'true'

    return render_template('/pos/create_upgrade_ticket.html', **locals())
