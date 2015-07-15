__author__ = 'wilrona'

from ...modules import *
from application import login_manager

from ..user.models_user import UserModel, RoleModel, UserRoleModel
from ..user.forms_user import FormLogin

cache = Cache(app)


@login_manager.user_loader
def load_user(userid):
    return UserModel.get_by_id(userid)


@app.route('/set_session')
def set_session():
    session.permanent = True
    return json.dumps({
        'statut': True
    })


@app.route('/', methods=['POST', 'GET'])
def Home():

    from ..activity.models_activity import ActivityModel
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    if 'user_id' in session:
        return redirect(url_for('Dashboard'))

    admin_role = RoleModel.query(
        RoleModel.name == 'super_admin'
    ).get()
    exist_super_admin = 0
    if admin_role:
        exist_super_admin = UserRoleModel.query(
            UserRoleModel.role_id == admin_role.key
        ).count()

    exist = False
    if exist_super_admin >= 1:
        exist = True

    url = None
    if request.args.get('url'):
        url = request.args.get('url')

    form = FormLogin()
    if form.validate_on_submit():
        try:
            password = hashlib.sha224(form.password.data).hexdigest()
        except UnicodeEncodeError:
            flash('Username or Password is invalid', 'danger')
            return redirect(url_for('Home'))

        user_login = UserModel.query(
            UserModel.email == form.email.data,
            UserModel.password == password
        ).get()

        if user_login is None:
            flash('Username or Password is invalid', 'danger')
        else:
            if not user_login.is_active():
                flash('Your account is disabled. Contact Administrator', 'danger')
                return redirect(url_for('Home', url=url))

            session['user_id'] = user_login.key.id()
            agency = 0
            if user_login.agency:
                agency = user_login.agency.get().key.id()

            #implementation de l'heure local
            time_zones = pytz.timezone('Africa/Douala')
            date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")


            session['agence_id'] = agency
            user_login.logged = True
            user_login.date_last_logged = function.datetime_convert(date_auto_nows)
            this_login = user_login.put()

            activity = ActivityModel()
            activity.object = "UserLogin"
            activity.time = function.datetime_convert(date_auto_nows)
            activity.identity = this_login.id()
            activity.nature = 1
            activity.put()

            if url:
                return redirect(url)

            return redirect(url_for('Dashboard'))

    return render_template('index/home.html', **locals())


@app.route('/logout_user')
def logout_user():
    if 'user_id' in session:
        user_id = session.get('user_id')
        UserLogout = UserModel.get_by_id(int(user_id))
        UserLogout.logged = False
        change = UserLogout.put()
        if change:
            session.pop('user_id')
            session.pop('agence_id')
    return redirect(url_for('Home'))


@app.route('/dashboard')
@login_required
def Dashboard():
    menu = 'dashboard'
    from ..ticket.models_ticket import AgencyModel, TicketModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    #TRAITEMENT DU TRAFIC GABON
    all_agency = AgencyModel.query()

    the_ticket_agency_gabon = []
    the_ticket_agency_cm_ngn = []

    time_minus_14days = datetime.datetime.now(time_zones) - datetime.timedelta(days=14)
    time_minus_14days = time_minus_14days.strftime("%Y-%m-%d %H:%M:%S")

    month_current = function.datetime_convert(date_auto_nows).month

    # TRAITEMENT DU DASHBOARD DU BOARDING
    if not current_user.has_roles(('admin', 'manager_agency', 'super_admin')) and current_user.has_roles('employee_Boarding'):
        return redirect(url_for('Boarding'))

    # TRAITEMENT DU DASHBOARD DE SELLER
    if not current_user.has_roles(('admin', 'manager_agency', 'super_admin')) and current_user.has_roles('employee_POS'):
        user_ticket = TicketModel.query(
            TicketModel.ticket_seller == current_user.key,
            TicketModel.selling == True
        ).order(-TicketModel.date_reservation)

        user_ticket_tab = []
        for ticket in user_ticket:
            tickets = {}
            tickets['travel'] = ticket.travel_ticket
            tickets['departure'] = ticket.departure
            tickets['number'] = 1
            user_ticket_tab.append(tickets)

        groupers = itemgetter("departure", "travel")

        the_ticket_sale = []
        for key, grp in groupby(sorted(user_ticket_tab, key=groupers), groupers):
            temp_dict = dict(zip(["departure", "travel"], key))
            temp_dict['number'] = 0
            for item in grp:
                temp_dict['number'] += item['number']
            the_ticket_sale.append(temp_dict)


        return render_template('/index/dashboard_pos.html', **locals())


    # TRAITEMENT DU DASHBOARD DU MANAGER
    if not current_user.has_roles(('admin','super_admin')) and current_user.has_roles('manager_agency'):

        user_agency = AgencyModel.get_by_id(int(session.get('agence_id')))

        ticket_agency = TicketModel.query(
            TicketModel.agency == user_agency.key,
            TicketModel.selling == True,
            TicketModel.date_reservation <= function.datetime_convert(date_auto_nows),
            TicketModel.date_reservation > function.datetime_convert(time_minus_14days)
        )
        the_ticket_agency_tab = []
        for ticket in ticket_agency:
            if ticket.travel_ticket.get().destination_start == user_agency.destination:
                tickets = {}
                tickets['date'] = function.format_date(ticket.departure.get().departure_date, "%Y-%m-%d")
                tickets['departure'] = ticket.departure
                tickets['departure_start'] = ticket.departure.get().destination.get().destination_start.get().name
                tickets['departure_check'] = ticket.departure.get().destination.get().destination_check.get().name
                tickets['heure'] = function.format_date(function.add_time(ticket.departure.get().schedule, ticket.departure.get().time_delay), "%H:%M:%S")
                tickets['price'] = ticket.sellprice
                tickets['currency'] = ticket.sellpriceCurrency.get().code
                the_ticket_agency_tab.append(tickets)
            else:
                tickets = {}
                tickets['date'] = function.format_date(datetime.datetime.now(), "%Y-%m-%d")
                tickets['departure'] = '11111111111'
                tickets['departure_start'] = "No destination start"
                tickets['departure_check'] = "No destination check"
                tickets['heure'] = function.format_date(datetime.datetime.now().time(), "%H:%M:%S")
                tickets['price'] = 0
                tickets['currency'] = user_agency.destination.get().currency.get().code
                the_ticket_agency_tab.append(tickets)

        grouper = itemgetter("date", "heure", "departure", "currency")

        the_ticket_agency = []
        for key, grp in groupby(sorted(the_ticket_agency_tab, key=grouper), grouper):
            temp_dict = dict(zip(["date", "heure", "departure", "currency"], key))
            temp_dict['price'] = 0
            for item in grp:
                temp_dict['departure_start'] = item['departure_start']
                temp_dict['departure_check'] = item['departure_check']
                temp_dict['price'] += item['price']
            the_ticket_agency.append(temp_dict)

        heure = function.datetime_convert(date_auto_nows).time()

        from ..departure.models_departure import DepartureModel

        departure = DepartureModel.query(
            DepartureModel.departure_date == datetime.date.today(),
            DepartureModel.schedule >= heure
        ).order(
            -DepartureModel.departure_date,
            DepartureModel.schedule,
            DepartureModel.time_delay
        )

        for dep in departure:
            if dep.destination.get().destination_start == user_agency.destination:
                current_departure = dep
                break

        for dep in departure:
            if dep.destination.get().destination_check == user_agency.destination:
                current_departure_check = dep
                break

        departure_current = DepartureModel.query(
            DepartureModel.departure_date == datetime.date.today(),
            DepartureModel.schedule < heure
        ).order(
            -DepartureModel.departure_date,
            DepartureModel.schedule,
            DepartureModel.time_delay
        )

        for dep in departure_current:
            interval = datetime.datetime.combine(datetime.date.today(), heure) - datetime.datetime.combine(dep.departure_date, function.add_time(dep.schedule, dep.time_delay))
            time_travel = function.time_convert(dep.destination.get().time)
            time_travel = datetime.timedelta(hours=time_travel.hour, minutes=time_travel.minute)
            if interval <= time_travel:
                current_departure_in_progress = dep
                break


        ticket_agency = TicketModel.query(
            TicketModel.agency == user_agency.key,
            TicketModel.selling == True
        )

        ticket_sale_local = {}
        ticket_sale_local['price'] = 0
        ticket_sale_local['number'] = 0
        for ticket in ticket_agency:
            if function.datetime_convert(ticket.date_reservation).month == month_current and ticket.travel_ticket.get().destination_start == user_agency.destination:
                ticket_sale_local['price'] += ticket.sellprice
                ticket_sale_local['number'] += 1
                ticket_sale_local['currency'] = ticket.sellpriceCurrency.get().code

        ticket_sale_foreign_tab = []
        for ticket in ticket_agency:
            if function.datetime_convert(ticket.date_reservation).month == month_current and ticket.travel_ticket.get().destination_start != user_agency.destination:
                ticket_sale_foreign = {}
                ticket_sale_foreign['travel'] = ticket.travel_ticket
                ticket_sale_foreign['price'] = ticket.sellprice
                ticket_sale_foreign['number'] = 1
                ticket_sale_foreign['currency'] = ticket.sellpriceCurrency.get().code
                ticket_sale_foreign_tab.append(ticket_sale_foreign)

        groupers = itemgetter("travel", "currency")

        the_ticket_sale_foreign = []
        for key, grp in groupby(sorted(ticket_sale_foreign_tab, key=groupers), groupers):
            temp_dict = dict(zip(["travel", "currency"], key))
            temp_dict['price'] = 0
            temp_dict['number'] = 0
            for item in grp:
                temp_dict['price'] += item['price']
                temp_dict['number'] += item['number']
            the_ticket_sale_foreign.append(temp_dict)

        return render_template('/index/dashboard_manager.html', **locals())


    # TRAITEMENT DU DASHBOARD DES ADMINISTRATEURS
    for agency in all_agency:
        ticket_agency = TicketModel.query(
            TicketModel.agency == agency.key,
            TicketModel.selling == True,
            TicketModel.date_reservation <= function.datetime_convert(date_auto_nows),
            TicketModel.date_reservation > function.datetime_convert(time_minus_14days)
        )

        for ticket in ticket_agency:
            if ticket.travel_ticket.get().destination_start == agency.destination and agency.country == 'GB':
                tickets = {}
                tickets['date'] = function.format_date(ticket.departure.get().departure_date, "%Y-%m-%d")
                tickets['departure'] = ticket.departure
                tickets['departure_start'] = ticket.departure.get().destination.get().destination_start.get().name
                tickets['departure_check'] = ticket.departure.get().destination.get().destination_check.get().name
                tickets['heure'] = function.format_date(function.add_time(ticket.departure.get().schedule, ticket.departure.get().time_delay), "%H:%M:%S")
                tickets['price'] = ticket.sellprice
                tickets['currency'] = ticket.sellpriceCurrency.get().code
                the_ticket_agency_gabon.append(tickets)
            else:
                tickets = {}
                tickets['date'] = function.format_date(datetime.datetime.now(), "%Y-%m-%d")
                tickets['departure'] = '11111111111'
                tickets['departure_start'] = "No destination start"
                tickets['departure_check'] = "No destination check"
                tickets['heure'] = function.format_date(datetime.datetime.now().time(), "%H:%M:%S")
                tickets['price'] = 0
                tickets['currency'] = agency.destination.get().currency.get().code
                the_ticket_agency_gabon.append(tickets)

        for ticket in ticket_agency:
            if ticket.travel_ticket.get().destination_start == agency.destination and (agency.country == 'CM' or agency.country == 'NGN'):
                tickets = {}
                tickets['date'] = function.format_date(ticket.departure.get().departure_date, "%Y-%m-%d")
                tickets['departure'] = ticket.departure
                tickets['departure_start'] = ticket.departure.get().destination.get().destination_start.get().name
                tickets['departure_check'] = ticket.departure.get().destination.get().destination_check.get().name
                tickets['heure'] = function.format_date(function.add_time(ticket.departure.get().schedule, ticket.departure.get().time_delay), "%H:%M:%S")
                tickets['price'] = ticket.sellprice
                tickets['currency'] = ticket.sellpriceCurrency.get().code
                the_ticket_agency_cm_ngn.append(tickets)
            else:
                tickets = {}
                tickets['date'] = function.format_date(datetime.datetime.now(), "%Y-%m-%d")
                tickets['departure'] = '11111111111'
                tickets['departure_start'] = "No destination start"
                tickets['departure_check'] = "No destination check"
                tickets['heure'] = function.format_date(datetime.datetime.now().time(), "%H:%M:%S")
                tickets['price'] = 0
                tickets['currency'] = agency.destination.get().currency.get().code
                the_ticket_agency_cm_ngn.append(tickets)


    grouper = itemgetter("date", "heure", "departure", "currency")

    ticket_sale_gabon = []
    for key, grp in groupby(sorted(the_ticket_agency_gabon, key=grouper), grouper):
        temp_dict = dict(zip(["date", "heure", "departure", "currency"], key))
        temp_dict['price'] = 0
        for item in grp:
            temp_dict['departure_start'] = item['departure_start']
            temp_dict['departure_check'] = item['departure_check']
            temp_dict['price'] += item['price']
        ticket_sale_gabon.append(temp_dict)

    ticket_sale_cm_ngn = []
    for key, grp in groupby(sorted(the_ticket_agency_cm_ngn, key=grouper), grouper):
        temp_dict = dict(zip(["date", "heure", "departure", "currency"], key))
        temp_dict['price'] = 0
        for item in grp:
            temp_dict['departure_start'] = item['departure_start']
            temp_dict['departure_check'] = item['departure_check']
            temp_dict['price'] += item['price']
        ticket_sale_cm_ngn.append(temp_dict)


    # TRAITEMENT DES STATISTIQUES DES VENTES PAR MOIR ET PAR PAYS
    ticket_sale_groupe_tab = []
    for agency in all_agency:
        ticket_agency = TicketModel.query(
            TicketModel.agency == agency.key,
            TicketModel.selling == True
        )
        for ticket in ticket_agency:
            if function.datetime_convert(ticket.date_reservation).month == month_current:
                tickets = {}
                tickets['country'] = agency.country
                tickets['price'] = ticket.sellprice
                tickets['number'] = 1
                tickets['currency'] = ticket.sellpriceCurrency.get().code
                ticket_sale_groupe_tab.append(tickets)

    groupers = itemgetter("country", "currency")
    ticket_sale_groupe = []
    for key, grp in groupby(sorted(ticket_sale_groupe_tab, key=groupers), groupers):
        temp_dict = dict(zip(["country", "currency"], key))
        temp_dict['price'] = 0
        temp_dict['number'] = 0
        for item in grp:
            temp_dict['price'] += item['price']
            temp_dict['number'] += item['number']
        ticket_sale_groupe.append(temp_dict)

    #TRAITEMENT DES STATISTIQUES DU NOMBRE DE CLIENT
    from ..customer.models_customer import CustomerModel
    all_customer = CustomerModel.query().count()
    old_customer = CustomerModel.query(
        CustomerModel.is_new == False
    ).count()
    new_customer = CustomerModel.query(
        CustomerModel.is_new == True
    ).count()

    #TRAITEMENT DES TICKETS VENDUS PAR CLASSE
    class_ticket_sold_tab = []
    for agency in all_agency:
        ticket_agency = TicketModel.query(
            TicketModel.agency == agency.key,
            TicketModel.selling == True
        )
        for ticket in ticket_agency:
            tickets = {}
            tickets['country'] = agency.country
            tickets['class'] = ticket.class_name.get().name
            tickets['number'] = 1
            class_ticket_sold_tab.append(tickets)

    groupers = itemgetter("country", "number")
    class_ticket_sold = []

    for key, grp in groupby(sorted(class_ticket_sold_tab, key=groupers), groupers):
        temp_dict = dict(zip(["country", "number"], key))
        temp_dict['class_query'] = []
        temp = {'numbers': 0}
        for item in grp:
            temp['numbers'] += 1
            temp['classes'] = item['class']
        temp_dict['class_query'].append(temp)
        class_ticket_sold.append(temp_dict)

    return render_template('/index/dashboard.html', **locals())


@app.route('/settings')
@login_required
@roles_required(('admin', 'super_admin'))
def Settings():

    menu = 'settings'
    return render_template('/index/settings.html', **locals())


@app.route('/recording')
@login_required
@roles_required(('manager_agency', 'super_admin'))
def Recording():

    menu = 'recording'
    return render_template('/index/recording.html', **locals())