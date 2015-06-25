__author__ = 'wilrona'


from ...modules import *

from ..customer.models_customer import CustomerModel
from ..ticket.models_ticket import TicketModel, TicketTypeNameModel, JourneyTypeModel, ClassTypeModel, AgencyModel, QuestionModel, TicketQuestion

from ..customer.forms_customer import FormCustomerPOS


cache = Cache(app)


@app.route('/search_customer_pos', methods=['GET', 'POST'])
def search_customer_pos():
    from ..departure.models_departure import DepartureModel

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
def search_ticket_pos():
    number_ticket = request.form['number_ticket']

    number_ticket = ''.join(number_ticket.split('*'))

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
def Ticket_found(ticket_id):
    ticket = TicketModel.get_by_id(ticket_id)
    return render_template('/pos/ticket_found.html', **locals())



@app.route('/create_customer_and_ticket_pos', methods=['GET', 'POST'])
@app.route('/create_customer_and_ticket_pos/<int:customer_id>/<int:departure_id>', methods=['GET', 'POST'])
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

    # information du depart pour le ticket
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

    # # s'il n'y a pas de question envoye et qu'il y'a des questions obligatoires definient
    # if number_obligated_question >= 1 and not question_request and request.method == 'POST':
    #     obligated = True
    #     quest_obligated = [question.key.id() for question in obligated_question]
    # else:
    #     if question_request:
    #         count = 0
    #
    #         #boucle la liste des questions envoyees et verifie si c'est dans la liste des questions obligatoires
    #         for quest in question_request:
    #             if quest in [question.key.id() for question in obligated_question]:
    #                 count += 1
    #                 quest_obligated.append(quest)
    #
    #         # verifie que le quota de question obligatoire est atteint dans le questionnaire
    #         if count <= number_obligated_question:
    #             obligated = True


    if customer_id:
        customer = CustomerModel.get_by_id(customer_id)
        form = FormCustomerPOS(obj=customer)
    else:
        customer = CustomerModel()
        # recuperation du formulaire en fonction de la methode
        if request.method == 'GET':
            form = FormCustomerPOS(request.args)
        else:
            form = FormCustomerPOS(request.form)

    if departure_id:
        form.current_departure.data = str(departure_id)

    journey_ticket = JourneyTypeModel.query()
    class_ticket = ClassTypeModel.query()
    ticket_type_name = TicketTypeNameModel.query()



    modal = 'false'
    ticket_update = None

    if form.validate_on_submit() and not obligated:

        customer.first_name = form.first_name.data
        customer.last_name = form.last_name.data
        customer.birthday = function.date_convert(form.birthday.data)
        customer.email = form.email.data
        customer.nationality = form.nationality.data
        customer.dial_code = form.dial_code.data
        customer.phone = form.phone.data
        customer.profession = form.profession.data
        customer_save = customer.put()

        # caracteristique des tickets
        journey_ticket_car = JourneyTypeModel.get_by_id(int(form.journey_name.data))
        class_ticket_car = ClassTypeModel.get_by_id(int(form.class_name.data))
        ticket_type_name_car = TicketTypeNameModel.get_by_id(int(form.type_name.data))

        priceticket = TicketTypeModel.query(
            TicketTypeModel.type_name == ticket_type_name_car.key,
            TicketTypeModel.class_name == class_ticket_car.key,
            TicketTypeModel.journey_name == journey_ticket_car.key,
            TicketTypeModel.active == True
        ).get()
        agency_current_user = AgencyModel.get_by_id(int(session.get('agence_id')))

        Ticket_To_Sell = TicketModel.query(
            TicketModel.type_name == ticket_type_name_car.key,
            TicketModel.class_name == class_ticket_car.key,
            TicketModel.journey_name == journey_ticket_car.key,
            TicketModel.agency == agency_current_user.key,
            TicketModel.selling == False
        ).order(TicketModel.datecreate).get()

        for question in question_request:
            Answers = TicketQuestion()
            quest = QuestionModel.get_by_id(int(question))
            Answers.ticket_id = Ticket_To_Sell.key
            Answers.question_id = quest.key
            Answers.put()

        Ticket_To_Sell.selling = True
        Ticket_To_Sell.is_ticket = True
        Ticket_To_Sell.date_reservation = function.datetime_convert(date_auto_nows)
        Ticket_To_Sell.sellprice = priceticket.price
        Ticket_To_Sell.sellpriceCurrency = priceticket.currency

        customer_ticket = CustomerModel.get_by_id(customer_save.id())
        Ticket_To_Sell.customer = customer_ticket.key

        departure_ticket = DepartureModel.get_by_id(int(form.current_departure.data))
        Ticket_To_Sell.departure = departure_ticket.key

        user_ticket = UserModel.get_by_id(int(session.get('user_id')))
        Ticket_To_Sell.ticket_seller = user_ticket.key

        ticket_update = Ticket_To_Sell.put()
        modal = 'true'

    return render_template('/pos/create_customer_and_ticket.html', **locals())



@app.route('/modal_generate_pdf_ticket')
@app.route('/modal_generate_pdf_ticket/<int:ticket_id>')
def modal_generate_pdf_ticket(ticket_id=None):

    return render_template('/pos/view-pdf.html', **locals())




@app.route('/generate_pdf_ticket/<int:ticket_id>')
def generate_pdf_ticket(ticket_id):

    Ticket_print = TicketModel.get_by_id(ticket_id)

    import cStringIO
    output = cStringIO.StringIO()

    style = getSampleStyleSheet()
    width, height = 595.27, 280.63
    p = canvas.Canvas(output, pagesize=(595.27, 280.63))

    code = str(Ticket_print.key.id())
    barcode = code39.Standard39(code, barHeight=20, stop=1)
    barcode.humanReadable = 1

    # from application import APP_STATIC

    # f = open(os.path.join(APP_STATIC, 'fonts/Lato-Bold.ttf'))
    # font = f.read()

    #font = r"Lato-Bold.ttf"
    #pdfmetrics.registerFont("Lato-Bold.ttf")
    string = '<font name="Times-Roman" size="14">%s</font>'

    econo = string % Ticket_print.class_name.get().name+" - "+string % Ticket_print.type_name.get().name+" - "+string % Ticket_print.journey_name.get().name
    name = string % Ticket_print.customer.get().first_name+" "+string % Ticket_print.customer.get().last_name
    froms = string % Ticket_print.departure.get().destination.get().destination_start.get().name
    destination = string % Ticket_print.departure.get().destination.get().destination_check.get().name
    date = string % str(function.format_date(Ticket_print.departure.get().departure_date, '%d-%m-%Y'))
    time = string % str(function.format_date(function.add_time(Ticket_print.departure.get().schedule, Ticket_print.departure.get().time_delay), "%H:%M"))
    lieu = string % Ticket_print.agency.get().name
    agent = string % str(Ticket_print.ticket_seller.get().key.id())

    p.drawImage(url_for('static', filename='TICKET-ONLY.jpg', _external=True), 0, 0, width=21*cm, height=9.9*cm, preserveAspectRatio=True)

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
            TicketModel.selling == False
        ).count()


    have_ticket = 'false'
    if Agency_ticket >= 1:
        have_ticket = 'true'

    if priceticket:
        data = json.dumps({
            'statut': 'OK',
            'price': priceticket.price,
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
def remaining_ticket():
    number = current_user.remaining_ticket()
    data = json.dumps({
        'ticket': number
    }, sort_keys=True)

    return data


@app.route('/Calendrier')
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