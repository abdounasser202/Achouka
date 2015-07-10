__author__ = 'wilrona'

from ...modules import *
from forms_vessel import FormVessel
from models_vessel import VesselModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/settings/vessel')
@login_required
@roles_required(('admin', 'super_admin'))
def Vessel_Index():
    menu = 'settings'
    submenu = 'vessel'

    vessels = VesselModel.query()

    return render_template('/vessel/index.html', **locals())


@app.route('/settings/vessel/edit/', methods=['GET', 'POST'])
@app.route('/settings/vessel/edit/<int:vessel_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Vessel_Edit(vessel_id=None):
    menu = 'settings'
    submenu = 'vessel'

    from ..activity.models_activity import ActivityModel
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    if vessel_id:
        vessel = VesselModel.get_by_id(vessel_id)
        form = FormVessel(obj=vessel)
    else:
        form = FormVessel()
        vessel = VesselModel()

    if form.validate_on_submit():

        Vessel_exist = VesselModel.query(
                VesselModel.name == form.name.data
        ).count()

        if Vessel_exist >= 1:
            if vessel.name == form.name.data and vessel_id:
                vessel.name = form.name.data
                vessel.capacity = form.capacity.data
                vessel.immatricul = form.immatricul.data

                this_vessel_modifier = vessel.put()

                # enregistrement de l'activite de modification
                activity = ActivityModel()
                activity.object = "VesselModel"
                activity.nature = 4
                activity.user_modify = current_user.key
                activity.identity = this_vessel_modifier.id()
                activity.time = function.datetime_convert(date_auto_nows)
                activity.put()

                flash(u' Vessel Update. ', 'success')
                return redirect(url_for('Vessel_Index'))
            else:
              form.name.errors.append('Other Vessel use this name')
        else:
            vessel.name = form.name.data
            vessel.capacity = form.capacity.data
            vessel.immatricul = form.immatricul.data
            this_vessel_creator = vessel.put()

            # enregistrement de l'activite de creation
            activity = ActivityModel()
            activity.time = function.datetime_convert(date_auto_nows)
            activity.identity = this_vessel_creator.id()
            activity.object = "VesselModel"
            activity.user_modify = current_user.key


            if vessel_id:
                 activity.nature = 4
                 flash(u' Vessel Update. ', 'success')

            else:
                activity.nature = 1
                flash(u' Vessel Save. ', 'success')

            activity.put()
            return redirect(url_for('Vessel_Index'))

    return render_template('/vessel/edit.html', **locals())


@app.route('/settings/vessel/delete/', methods=['GET', 'POST'])
@app.route('/settings/vessel/delete/<int:vessel_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Vessel_Delete(vessel_id=None):
    menu = 'settings'
    submenu = 'vessel'

    from ..departure.models_departure import DepartureModel
    from ..activity.models_activity import ActivityModel

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    delete_vessel = VesselModel.get_by_id(int(vessel_id))

    departure_vessel_exist = DepartureModel.query(DepartureModel.vessel == delete_vessel.key).count()

    if departure_vessel_exist >= 1:
        flash(u'You can\'t delete this vessel', 'danger')
        return redirect(url_for("Vessel_Index"))
    else:
        # enregistrement de l'activite de suppression
        activity = ActivityModel()
        activity.user_modify = current_user.key
        activity.object = "VesselModel"
        activity.nature = 3
        activity.identity = delete_vessel.key.id()
        activity.time = function.datetime_convert(date_auto_nows)
        activity.put()

        delete_vessel.key.delete()
        flash(u'Vessel has been deleted successfully', 'success')
        return redirect(url_for("Vessel_Index"))

    return render_template('/vessel/index.html', **locals())

