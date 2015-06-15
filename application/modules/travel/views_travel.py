__author__ = 'wilrona'

from ...modules import *

from models_travel import TravelModel, DestinationModel

from forms_travel import FormTravel
# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/recording/travel')
def Travel_Index():
    menu = 'recording'
    submenu = 'travel'

    travels = TravelModel.query()

    return render_template('/travel/index.html', **locals())


@app.route('/recording/travel/edit', methods=['GET', 'POST'])
@app.route('/recording/travel/edit/<int:travel_id>', methods=['GET', 'POST'])
def Travel_Edit(travel_id=None):
    menu = 'recording'
    submenu = 'travel'

    destitravel = DestinationModel.query()
    if travel_id:
        travelmod = TravelModel.get_by_id(travel_id)
        travelmod2 = TravelModel.query(
            TravelModel.destination_check == travelmod.destination_start,
            TravelModel.destination_start == travelmod.destination_check
        ).get()
        form = FormTravel(obj=travelmod)
    else:
        travelmod = TravelModel()
        travelmod2 = TravelModel()
        form = FormTravel(request.form)

    if form.validate_on_submit():
        start_destitravel = DestinationModel.get_by_id(int(form.destination_start.data))
        check_destitravel = DestinationModel.get_by_id(int(form.destination_check.data))

        # on compte le nombre de travel ayant la meme destination depart et arrive
        count_dest_travel = TravelModel.query(
            TravelModel.destination_start == start_destitravel.key,
            TravelModel.destination_check == check_destitravel.key
        ).count()

        if count_dest_travel >= 1:
            if travelmod.destination_start == start_destitravel.key and travelmod.destination_check == check_destitravel.key:

                travelmod.time = function.time_convert(form.time.data)
                travelmod2.time = function.time_convert(form.time.data)
                try:
                    travelmod.put()
                    travelmod2.put()
                    flash(u' Travel Save. ', 'success')
                    return redirect(url_for("Travel_Index"))
                except CapabilityDisabledError:
                    flash(u' Error data base. ', 'danger')
                    return redirect(url_for('Travel_Index'))
            else:
                flash(u"This travel exist!", "danger")
        elif start_destitravel == check_destitravel:
            flash(u"This travel kind  does'nt exist!", "danger")
        else:
            travelmod.time = function.time_convert(form.time.data)
            travelmod.destination_start = start_destitravel.key
            travelmod.destination_check = check_destitravel.key
            travelmod.datecreate = function.datetime_convert(date_auto_now)

            travelmod2.time = function.time_convert(form.time.data)
            travelmod2.destination_start = check_destitravel.key
            travelmod2.destination_check = start_destitravel.key
            travelmod2.datecreate = function.datetime_convert(date_auto_now)

            try:
                travelmod.put()
                travelmod2.put()
                flash(u' Travel Save. ', 'success')
                return redirect(url_for("Travel_Index"))
            except CapabilityDisabledError:
                flash(u' Error data base. ', 'danger')
                return redirect(url_for('Travel_Index'))

    return render_template('/travel/edit.html', **locals())