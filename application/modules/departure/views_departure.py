__author__ = 'wilrona'


from ...modules import *

from models_departure import DepartureModel, VesselModel, TravelModel
from forms_departure import FormDeparture
# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/recording/departure')
@login_required
@roles_required(('super_admin', 'manager_agency'))
def Departure_Index():
    menu = 'recording'
    submenu = 'departure'

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



@app.route('/recording/departure/edit', methods=['GET', 'POST'])
@app.route('/recording/departure/edit/<int:departure_id>', methods=['GET', 'POST'])
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

    if departure_id:
        departmod = DepartureModel.get_by_id(departure_id)
        form = FormDeparture(obj=departmod)

        form.destination.data = departmod.destination.get().key.id()

        last_vessel = str(departmod.vessel.get().key.id())
        last_date = str(departmod.departure_date)
        last_hour = str(departmod.schedule)

        if departmod.reserved():
            flash('You update departure reserved', 'danger')
            return redirect(url_for('Departure_Index'))

    else:
        departmod = DepartureModel()
        form = FormDeparture(request.form)

    if form.validate_on_submit():
        travel_destination = TravelModel.get_by_id(int(form.destination.data))
        vessel_departure = VesselModel.get_by_id(int(form.vessel.data))

        departure_exist = DepartureModel.query(
            DepartureModel.departure_date == function.date_convert(form.departure_date.data),
            DepartureModel.schedule == function.time_convert(form.schedule.data),
            DepartureModel.destination == travel_destination.key
        ).count()

        if departure_exist >= 1:

            if departmod.destination == travel_destination.key and departmod.departure_date == function.date_convert(form.departure_date.data) and departmod.schedule == function.time_convert(form.schedule.data):
                departmod.vessel = vessel_departure.key
                departmod.departure_date = function.date_convert(form.departure_date.data)
                departmod.schedule = function.time_convert(form.schedule.data)
                depart = departmod.put()

                if form.vessel.data != last_vessel:
                    activity.identity = depart.id()
                    activity.nature = 0
                    activity.last_value = last_vessel
                    activity.put()

                if function.date_convert(form.departure_date.data) != function.date_convert(last_date):
                    activity.identity = depart.id()
                    activity.nature = 0
                    activity.last_value = last_date
                    activity.put()

                if function.time_convert(form.schedule.data) != function.time_convert(last_hour):
                    activity.identity = depart.id()
                    activity.nature = 0
                    activity.last_value = last_hour
                    activity.put()

                if form.vessel.data == last_vessel and form.departure_date.data == last_date and form.schedule.data == last_hour:
                    activity.identity = departmod.key.id()
                    activity.nature = 4
                    activity.put()

                flash(u' Departure Updated. ', 'success')
                return redirect(url_for('Departure_Index'))
            else:
                flash(u'This departure exist. ', 'danger')

        else:

            departmod.departure_date = function.date_convert(form.departure_date.data)
            departmod.schedule = function.time_convert(form.schedule.data)
            departmod.destination = travel_destination.key
            departmod.vessel = vessel_departure.key

            depart = departmod.put()

            if departure_id:
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

                flash(u' Departure Updated. ', 'success')

            else:
                activity.identity = depart.id()
                activity.nature = 1
                activity.put()
                flash(u' Departure Saved. ', 'success')

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

    activity = ActivityModel()
    activity.user_modify = current_user.key
    activity.object = "DepartureModel"
    activity.time = function.datetime_convert(date_auto_nows)

    departmod = DepartureModel.get_by_id(departure_id)
    last_time = departmod.time_delay

    if request.method == 'POST':
        departmod.time_delay = function.time_convert(request.form['time_delay'])
        depart = departmod.put()

        activity.identity = depart.id()
        activity.nature = 0
        activity.last_value = str(last_time)
        activity.put()

        flash(u' Delay add successfully. ', 'success')
        return redirect(url_for('Departure_Index'))
    return render_template('/departure/edit-delay.html', **locals())