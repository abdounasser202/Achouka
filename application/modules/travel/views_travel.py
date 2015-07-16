__author__ = 'wilrona'

from ...modules import *

from models_travel import TravelModel, DestinationModel

from forms_travel import FormTravel
# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/recording/travel')
@login_required
@roles_required(('super_admin', 'admin'))
def Travel_Index():
    menu = 'recording'
    submenu = 'travel'

    travels = TravelModel.query()

    return render_template('/travel/index.html', **locals())


@app.route('/recording/travel/edit', methods=['GET', 'POST'])
@app.route('/recording/travel/edit/<int:travel_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('super_admin', 'admin'))
def Travel_Edit(travel_id=None):
    menu = 'recording'
    submenu = 'travel'

    from ..activity.models_activity import ActivityModel

    #implementation de l'heure local
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    destitravel = DestinationModel.query()
    if travel_id:
        travelmod = TravelModel.get_by_id(travel_id)
        form = FormTravel(obj=travelmod)

        form.destination_start.data = travelmod.destination_start.get().key.id()
        form.destination_check.data = travelmod.destination_check.get().key.id()
    else:
        travelmod = TravelModel()
        form = FormTravel(request.form)

    if form.validate_on_submit():
        start_destitravel = DestinationModel.get_by_id(int(form.destination_start.data))
        check_destitravel = DestinationModel.get_by_id(int(form.destination_check.data))

        # on compte le nombre de travel ayant la meme destination depart et arrive
        count_dest_travel = TravelModel.query(
            TravelModel.destination_start == start_destitravel.key,
            TravelModel.destination_check == check_destitravel.key
        ).count()

        activity = ActivityModel()
        activity.user_modify = current_user.key
        activity.object = "TravelModel"
        activity.time = function.datetime_convert(date_auto_nows)

        if count_dest_travel >= 1:
            if travelmod.destination_start == start_destitravel.key and travelmod.destination_check == check_destitravel.key:
                travelmod.time = function.time_convert(form.time.data)

                this_travel = travelmod.put()
                activity.identity = this_travel.id()
                activity.nature = 4
                activity.put()

                flash(u' Travel Updated! ', 'success')
                return redirect(url_for("Travel_Index"))

            else:
                flash(u"This travel exist!", "danger")

        elif start_destitravel == check_destitravel:
            flash(u"This travel kind  does'nt exist!", "danger")

        else:
            if form.time.data:
                travelmod.time = function.time_convert(form.time.data)
            travelmod.destination_start = start_destitravel.key
            travelmod.destination_check = check_destitravel.key

            if not travel_id:
                travelmod.datecreate = function.datetime_convert(date_auto_nows)

            if not travel_id:
                travelmod2 = TravelModel()
                if form.time.data:
                    travelmod2.time = function.time_convert(form.time.data)
                travelmod2.destination_start = check_destitravel.key
                travelmod2.destination_check = start_destitravel.key
                travelmod2.datecreate = function.datetime_convert(date_auto_nows)
                this_travel = travelmod2.put()

                activity.identity = this_travel.id()
                activity.nature = 1
                activity.put()

            this_travel = travelmod.put()

            activity.identity = this_travel.id()
            activity.nature = 1
            activity.put()
            flash(u' Travel Saved! ', 'success')
            return redirect(url_for("Travel_Index"))

    return render_template('/travel/edit.html', **locals())