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

    from ..activity.models_activity import ActivityModel
    feed = ActivityModel.query(
        ActivityModel.object == 'VesselModel',
    ).order(
        -ActivityModel.time
    )

    feed_tab = []
    count = 0
    for feed in feed:
        feed_list = {}
        feed_list['user'] = feed.user_modify
        vess = VesselModel.get_by_id(feed.identity)
        if vess:
            feed_list['data'] = vess.name+" ("+str(vess.capacity)+")"
        else:
            feed_list['data'] = feed.last_value
        feed_list['time'] = feed.time
        feed_list['nature'] = feed.nature
        feed_list['id'] = feed.identity
        feed_tab.append(feed_list)
        count += 1
        if count > 5:
            count += 1
            break

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

    feed_tab = []

    if vessel_id:
        vessel = VesselModel.get_by_id(vessel_id)
        form = FormVessel(obj=vessel)

        feed = ActivityModel.query(
            ActivityModel.object == 'VesselModel',
            ActivityModel.identity == vessel.key.id()
        ).order(
            -ActivityModel.time
        )
        count = 0
        for feed in feed:
            feed_list = {}
            feed_list['user'] = feed.user_modify
            vess = VesselModel.get_by_id(feed.identity)
            feed_list['data'] = feed.last_value
            if vess:
                feed_list['data'] = vess.name+" ("+str(vess.capacity)+")"
            feed_list['time'] = feed.time
            feed_list['nature'] = feed.nature
            feed_list['id'] = feed.identity
            feed_tab.append(feed_list)
            count += 1
            if count > 5:
                count += 1
                break
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

        del_activity = ActivityModel.query(
            ActivityModel.object == "VesselModel",
            ActivityModel.identity == delete_vessel.key.id()
        )

        for del_act in del_activity:
            del_act.key.delete()

        # enregistrement de l'activite de suppression
        activity = ActivityModel()
        activity.user_modify = current_user.key
        activity.object = "VesselModel"
        activity.nature = 3
        activity.identity = delete_vessel.key.id()
        activity.time = function.datetime_convert(date_auto_nows)
        activity.last_value = delete_vessel.name+" ("+str(delete_vessel.capacity)+")"
        activity.put()

        #SUPPRESSION DE TOUTES LES ACTIVITES DE L'ENREGISTREMENT A SUPPRIMER


        delete_vessel.key.delete()
        flash(u'Vessel has been deleted successfully', 'success')
        return redirect(url_for("Vessel_Index"))

    return render_template('/vessel/index.html', **locals())

