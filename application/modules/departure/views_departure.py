__author__ = 'wilrona'


from ...modules import *

from models_departure import DepartureModel, VesselModel, TravelModel
from forms_departure import FormDeparture
# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/recording/departure')
def Departure_Index():
    menu = 'recording'
    submenu = 'departure'

    departures = DepartureModel.query()
    return render_template('/departure/index.html', **locals())

@app.route('/recording/departure/edit', methods=['GET', 'POST'])
@app.route('/recording/departure/edit/<int:departure_id>', methods=['GET', 'POST'])
def Departure_Edit(departure_id=None):
    menu = 'recording'
    submenu = 'departure'

    vessel = VesselModel.query()
    departravel = TravelModel.query()

    if departure_id:
        departmod = DepartureModel.get_by_id(departure_id)
        form = FormDeparture(obj=departmod)

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

        if departure_exist == 0:
            #insertion et modification de la capacite restante pour les reservations
            if not departure_id or (departmod.vessel != vessel_departure.key and departure_id):

                if not departure_id:
                    departmod.remaining_capacity = vessel_departure.capacity

                else:
                    reservation_number = departmod.vessel.get().capacity - departmod.remaining_capacity
                    new_remaining_capacity = vessel_departure.capacity - reservation_number
                    departmod.remaining_capacity = new_remaining_capacity

            departmod.departure_date = function.date_convert(form.departure_date.data)
            departmod.schedule = function.time_convert(form.schedule.data)
            departmod.destination = travel_destination.key
            departmod.vessel = vessel_departure.key

            depart = departmod.put()
            flash(u' Departure Saved. ', 'success')
            return redirect(url_for('Departure_Index'))
        else:
             flash(u'This departure exist. ', 'danger')

    return render_template('/departure/edit.html', **locals())


@app.route('/Time_Delay_Edit/<int:departure_id>', methods=['GET', 'POST'])
def Time_Delay_Edit(departure_id):
    departmod = DepartureModel.get_by_id(departure_id)
    if request.method == 'POST':
        departmod.time_delay = function.time_convert(request.form['time_delay'])
        depart = departmod.put()
        flash(u' Delay add successfully. ', 'success')
        return redirect(url_for('Departure_Index'))
    return render_template('/departure/edit-delay.html', **locals())