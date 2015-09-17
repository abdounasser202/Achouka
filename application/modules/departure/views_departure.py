__author__ = 'wilrona'


from ...modules import *

from models_departure import DepartureModel, VesselModel, TravelModel
from forms_departure import FormDeparture
# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/manage/journey')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Departure_Index():
    menu = 'recording'
    submenu = 'departure'

    from ..activity.models_activity import ActivityModel
    feed = ActivityModel.query(
        ActivityModel.object == 'DepartureModel',
    ).order(
        -ActivityModel.time
    )

    feed_tab = []
    count = 0
    for feed in feed:
        feed_list = {}
        feed_list['user'] = feed.user_modify
        vess = DepartureModel.get_by_id(feed.identity)
        feed_list['data'] = str(vess.departure_date)+" "+str(vess.schedule)+" for "+vess.destination.get().destination_start.get().name+" - "+vess.destination.get().destination_check.get().name
        feed_list['last_value'] = feed.last_value
        feed_list['time'] = feed.time
        feed_list['nature'] = feed.nature
        feed_tab.append(feed_list)
        count += 1
        if count > 5 and not request.args.get('modal'):
            count += 1
            break

    if request.args.get('modal'):
        return render_template('/departure/all_feed.html', **locals())

    if not current_user.has_roles(('admin', 'super_admin')) and current_user.has_roles('manager_agency'):
        from ..agency.models_agency import AgencyModel
        agency_user = AgencyModel.get_by_id(int(session.get('agence_id')))
        return redirect(url_for('Departure_manager_agency', agency_id=agency_user.key.id()))

    year = datetime.date.today().year

    day_today = datetime.date.today().day
    month_today = datetime.date.today().month
    date_day = datetime.date(year, month_today, day_today)

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    time_now = function.datetime_convert(date_auto_nows).time()

    departures = DepartureModel.query().order(
        DepartureModel.departure_date,
        DepartureModel.schedule,
        DepartureModel.time_delay
    )

    return render_template('/departure/index.html', **locals())


@app.route('/Departure_manager_agency/<int:agency_id>')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Departure_manager_agency(agency_id):
    menu = 'recording'
    submenu = 'departure'

    from ..activity.models_activity import ActivityModel
    feed = ActivityModel.query(
        ActivityModel.object == 'DepartureModel',
    ).order(
        -ActivityModel.time
    )

    feed_tab = []
    count = 0
    for feed in feed:
        feed_list = {}
        feed_list['user'] = feed.user_modify
        vess = DepartureModel.get_by_id(feed.identity)
        feed_list['data'] = str(vess.departure_date)+" "+str(vess.schedule)+" for "+vess.destination.get().destination_start.get().name+" - "+vess.destination.get().destination_check.get().name
        feed_list['last_value'] = feed.last_value
        feed_list['time'] = feed.time
        feed_list['nature'] = feed.nature
        feed_tab.append(feed_list)
        count += 1
        if count > 5 and not request.args.get('modal'):
            count += 1
            break

    if request.args.get('modal'):
        return render_template('/departure/all_feed.html', **locals())

    year = datetime.date.today().year

    day_today = datetime.date.today().day
    month_today = datetime.date.today().month
    date_day = datetime.date(year, month_today, day_today)

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    time_now = function.datetime_convert(date_auto_nows).time()

    from ..agency.models_agency import AgencyModel
    user_agency_id = AgencyModel.get_by_id(agency_id)

    departure_local_query = DepartureModel.query()

    departure_locals = []
    departure_in_commings = []
    foreign_departures = []
    for departure_local_loop in departure_local_query:
        if departure_local_loop.destination.get().destination_start == user_agency_id.destination:
            departure_locals.append(departure_local_loop)
        if departure_local_loop.destination.get().destination_check == user_agency_id.destination:
            departure_in_commings.append(departure_local_loop)
        if departure_local_loop.destination.get().destination_check != user_agency_id.destination and departure_local_loop.destination.get().destination_start != user_agency_id.destination:
            foreign_departures.append(departure_local_loop)

    return render_template('/departure/index_manager_agency.html', **locals())



@app.route('/manage/journey/edit', methods=['GET', 'POST'])
@app.route('/manage/journey/edit/<int:departure_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Departure_Edit(departure_id=None):
    menu = 'recording'
    submenu = 'departure'

    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    vessel = VesselModel.query()
    departravel = TravelModel.query()

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "DepartureModel"
    activity.time = function.datetime_convert(date_auto_nows)

    feed_tab = []

    if departure_id:
        departmod = DepartureModel.get_by_id(departure_id)
        form = FormDeparture(obj=departmod)

        form.destination.data = departmod.destination

        if departmod.reserved():
            flash('You update departure reserved', 'danger')
            return redirect(url_for('Departure_Index'))

        feed = ActivityModel.query(
            ActivityModel.object == 'DepartureModel',
            ActivityModel.identity == departmod.key.id()
        ).order(
            -ActivityModel.time
        )

        count = 0
        for feed in feed:
            feed_list = {}
            feed_list['user'] = feed.user_modify
            vess = DepartureModel.get_by_id(feed.identity)
            feed_list['data'] = str(vess.departure_date)+" "+str(vess.schedule)+" for "+vess.destination.get().destination_start.get().name+" - "+vess.destination.get().destination_check.get().name

            feed_list['last_value'] = feed.last_value
            feed_list['time'] = feed.time
            feed_list['nature'] = feed.nature
            feed_tab.append(feed_list)
            count += 1
            if count > 5:
                count += 1
                break

    else:
        departmod = DepartureModel()
        form = FormDeparture(request.form)

    if form.validate_on_submit():

        travel_destination = departmod.destination
        if not departure_id:
            travel_destination = TravelModel.get_by_id(int(form.destination.data))
            travel_destination = travel_destination.key

        vessel_departure = VesselModel.get_by_id(int(form.vessel.data))

        departure_exist = DepartureModel.query(
            DepartureModel.departure_date == function.date_convert(form.departure_date.data),
            DepartureModel.schedule == function.time_convert(form.schedule.data),
            DepartureModel.destination == travel_destination
        ).count()

        if departure_exist >= 1:

            if departmod.destination == travel_destination and departmod.departure_date == function.date_convert(form.departure_date.data) and departmod.schedule == function.time_convert(form.schedule.data):
                departmod.vessel = vessel_departure.key

                if departure_id:

                    last_vessel = str(departmod.vessel)
                    last_date = str(departmod.schedule)
                    last_hour = str(departmod.departure_date)

                    if form.vessel.data != last_vessel:
                        activity.identity = departmod.key.id()
                        activity.nature = 0
                        activity.last_value = last_vessel
                        activity.put()

                    if form.departure_date.data != last_date:
                        activity.identity = departmod.key.id()
                        activity.nature = 0
                        activity.last_value = last_date
                        activity.put()

                    if form.schedule.data != last_hour:
                        activity.identity = departmod.key.id()
                        activity.nature = 0
                        activity.last_value = last_hour
                        activity.put()

                    if form.vessel.data == last_vessel and form.departure_date.data == last_date and form.schedule.data == last_hour:
                        activity.identity = departmod.key.id()
                        activity.nature = 4
                        activity.put()

                flash(u' Journey Updated. ', 'success')
                return redirect(url_for('Departure_Index'))
            else:
                flash(u'This journey exist. ', 'danger')

        else:

            departmod.departure_date = function.date_convert(form.departure_date.data)
            departmod.schedule = function.time_convert(form.schedule.data)
            departmod.destination = travel_destination
            departmod.vessel = vessel_departure.key

            depart = departmod.put()

            activity.identity = depart.id()
            activity.nature = 1
            activity.put()

            if departure_id:
                flash(u' Journey Update. ', 'success')
            else:
                flash(u' Journey Saved. ', 'success')
            return redirect(url_for('Departure_Index'))

            #insertion et modification de la capacite restante pour les reservations
            # if not departure_id or (departmod.vessel != vessel_departure.key and departure_id):
            #
            #     if not departure_id:
            #         departmod.remaining_capacity = vessel_departure.capacity
            #
            #     else:
            #         reservation_number = departmod.vessel.get().capacity - departmod.remaining_capacity
            #         new_remaining_capacity = vessel_departure.capacity - reservation_number
            #         departmod.remaining_capacity = new_remaining_capacity

    return render_template('/departure/edit.html', **locals())


@app.route('/Time_Delay_Edit/<int:departure_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Time_Delay_Edit(departure_id):

    from ..activity.models_activity import ActivityModel
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    departmod = DepartureModel.get_by_id(departure_id)
    if request.method == 'POST':
        activity = ActivityModel()
        activity.user_modify = current_user.key
        activity.object = "DepartureModel"
        activity.time = function.datetime_convert(date_auto_nows)

        departmod.time_delay = function.time_convert(request.form['time_delay'])
        activity.identity = departmod.key.id()
        activity.nature = 4
        activity.last_value = "Add "+str(function.time_convert(request.form['time_delay']))+" to schedule time"
        activity.put()
        depart = departmod.put()
        flash(u' Delay added successfully. ', 'success')
        return redirect(url_for('Departure_Index'))
    return render_template('/departure/edit-delay.html', **locals())


@app.route('/manage/journey/details/<int:departure_id>')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Departure_details(departure_id):
    menu = 'recording'
    submenu = 'departure'


    from ..ticket.models_ticket import TicketModel
    departure_get = DepartureModel.get_by_id(departure_id)

    all_ticket = TicketModel.query(
        TicketModel.departure == departure_get.key
    )
    search = False
    printer = False
    if request.args.get('printer'):
        printer = True
        all_ticket = TicketModel.query(
            TicketModel.departure == departure_get.key,
            TicketModel.selling == True,
            TicketModel.generate_boarding == True,
            TicketModel.is_boarding == True
        )

    if request.args.get('reset'):
        return render_template('/departure/list_ticket_found_unboard.html', **locals())

    return render_template('/departure/details.html', **locals())


@app.route('/search_customer_to_board/<int:departure_id>', methods=['POST'])
@login_required
@roles_required(('super_admin', 'manager_agency'))
def search_customer_to_board(departure_id):
    from ..ticket.models_ticket import TicketPoly

    departure_get = DepartureModel.get_by_id(departure_id)

    number_ticket = str(request.form['number_ticket_generated'])
    number_ticket = ''.join(number_ticket.split('*'))

    ticket_sold = TicketPoly.query(
        TicketPoly.selling == True,
        TicketPoly.statusValid == False,
        TicketPoly.generate_boarding == True,
        TicketPoly.is_boarding == False,
        TicketPoly.departure == departure_get.key
    )
    search = True
    all_ticket = []
    for ticket in ticket_sold:
        find_ticket_sold = function.find(str(ticket.key.id())+" ", str(number_ticket))
        if find_ticket_sold:
            all_ticket.append(ticket)

    return render_template('/departure/list_ticket_found_unboard.html', **locals())


@app.route('/ticket_information/<int:ticket_id>/<int:departure_id>')
@app.route('/ticket_information/')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def ticket_information(ticket_id=None, departure_id=None):
    from ..ticket.models_ticket import TicketPoly

    ticket = TicketPoly.get_by_id(ticket_id)

    confirm = request.args.get('confirm')
    close = False
    if confirm:
        ticket.is_boarding = True
        ticket.put()
        close = True

    return render_template('/departure/ticket_information_validation.html', **locals())

@app.route('/reset_table_ticket/<int:departure_id>')
def reset_table_ticket(departure_id):
    from ..ticket.models_ticket import TicketPoly

    departure_get = DepartureModel.get_by_id(departure_id)

    all_ticket = TicketPoly.query(
        TicketPoly.departure == departure_get.key
    )

    search = False
    return render_template('/departure/list_ticket_found_unboard.html', **locals())