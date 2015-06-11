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
@app.route('/create_customer_and_ticket_pos/<int:customer_id>/<int:departure_id>', methods=['GET', 'POST'])
def create_customer_and_ticket_pos(customer_id=None, departure_id=None):
    from ..ticket_type.models_ticket_type import TicketTypeModel
    from ..departure.models_departure import DepartureModel
    from ..user.models_user import UserModel

    nationalList = global_nationality_contry

    #Verifier que les questions obligatoires ont ete selectionne
    question_request = request.form.getlist('questions')

    if customer_id:
        customer = CustomerModel.get_by_id(customer_id)
        form = FormCustomerPOS(obj=customer)
    else:
        customer = CustomerModel()
        if request.method == 'GET':
            form = FormCustomerPOS(request.args)
        else:
            form = FormCustomerPOS(request.form)

    if departure_id:
        form.current_departure.data = str(departure_id)

    journey_ticket = JourneyTypeModel.query()
    class_ticket = ClassTypeModel.query()
    ticket_type_name = TicketTypeNameModel.query()

    questions = QuestionModel.query(
        QuestionModel.is_pos == True
    )

    modal = 'false'
    ticket_update = None

    if form.validate_on_submit():

        customer.first_name = form.first_name.data
        customer.last_name = form.last_name.data
        customer.birthday = function.date_convert(form.birthday.data)
        customer.email = form.email.data
        customer.nationality = form.nationality.data
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
        Ticket_To_Sell.date_reservation = datetime.datetime.now()
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
    #(595.27, 280.63)
    p = canvas.Canvas(output, pagesize=(595.27, 280.63))

    code = str(Ticket_print.key.id())
    # barcode = createBarcodeDrawing('Standard39', value=code, barHeight=20, humanReadable=True)
    barcode = code39.Standard39(code, barHeight=20, stop=1)
    barcode.humanReadable = 1


    econo = Ticket_print.class_name.get().name
    name = Ticket_print.customer.get().first_name+" "+Ticket_print.customer.get().last_name
    froms = Ticket_print.departure.get().destination.get().destination_start.get().name
    destination = Ticket_print.departure.get().destination.get().destination_check.get().name
    date = str(function.format_date(Ticket_print.departure.get().departure_date, '%d-%m-%Y'))
    time = str(function.format_date(function.add_time(Ticket_print.departure.get().schedule, Ticket_print.departure.get().time_delay), "%H:%M"))
    lieu = Ticket_print.agency.get().name
    agent = str(Ticket_print.ticket_seller.get().key.id())

    p.drawImage(url_for('static', filename='TICKET-ONLY.jpg', _external=True), 0, 0, width=21*cm, height=9.9*cm, preserveAspectRatio=True)
    p.drawString(11.3*cm, 7.9*cm, econo)
    p.drawString(2.97*cm, 6.22*cm, name)
    p.drawString(2.97*cm, 4.7*cm, froms)
    p.drawString(8.56*cm, 4.7*cm, destination)
    p.drawString(2.97*cm, 3.22*cm, date)
    p.drawString(8.56*cm, 3.22*cm, time)
    p.drawString(2.97*cm, 1.7*cm, lieu)
    p.drawString(8.56*cm, 1.7*cm, agent)


    p.saveState()
    p.translate(2*cm, 13.9*cm)
    p.rotate(-90)
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

    have_ticket = 'false'
    if Agency_ticket >= 1:
        have_ticket = 'true'

    if priceticket:
        data = json.dumps({
            'statut': 'OK',
            'price': priceticket.price,
            'currency': priceticket.currency.get().code,
            'haveticket': have_ticket
        }, sort_keys=True)
    else:
        data = json.dumps({
            'statut': 'error',
            'value': 'Undefined',
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