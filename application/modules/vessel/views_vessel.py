__author__ = 'wilrona'

from ...modules import *
from forms_vessel import FormVessel
from models_vessel import VesselModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/vessel')
def Vessel_Index():
    menu = 'settings'
    submenu = 'vessel'

    vessels = VesselModel.query()

    return render_template('/vessel/index.html', **locals())

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/vessel/edit/', methods=['GET', 'POST'])
@app.route('/settings/vessel/edit/<int:vessel_id>', methods=['GET', 'POST'])
def Vessel_Edit(vessel_id=None):
    menu = 'settings'
    submenu = 'vessel'

    if vessel_id:
        vessel = VesselModel.get_by_id(vessel_id)
        form = FormVessel(obj=vessel)
    else:
        form = FormVessel()
        vessel = VesselModel()

    if form.validate_on_submit():

        Vessel_exist = VesselModel.query(VesselModel.name == form.name.data).count()

        if Vessel_exist >= 1:
            if vessel.name == form.name.data:
                vessel.name = form.name.data
                vessel.capacity = form.capacity.data
                vessel.immatricul = form.immatricul.data
                try:
                    vessel.put()
                    flash(u' Vessel Update. ', 'success')
                    return redirect(url_for('Vessel_Index'))
                except CapabilityDisabledError:
                    flash(u' Error data base. ', 'danger')
                    return redirect(url_for('Vessel_Edit'))
            else:
                form.name.errors.append('Other Vessel use this name')

        else:
            vessel.name = form.name.data
            vessel.capacity = form.capacity.data
            vessel.immatricul = form.immatricul.data
            try:
                vessel.put()
                flash(u' Vessel Save. ', 'success')
                return redirect(url_for('Vessel_Index'))
            except CapabilityDisabledError:
                flash(u' Error data base. ', 'danger')
                return redirect(url_for('Vessel_Edit'))

    return render_template('/vessel/edit.html', **locals())

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/vessel/delete/', methods=['GET', 'POST'])
@app.route('/settings/vessel/delete/<int:vessel_id>', methods=['GET', 'POST'])
def Vessel_Delete(vessel_id=None):
    menu = 'settings'
    submenu = 'vessel'
    from ..departure.models_departure import DepartureModel

    delete_vessel = VesselModel.get_by_id(int(vessel_id))

    departure_vessel_exist = DepartureModel.query(DepartureModel.vessel == delete_vessel.key).count()

    if departure_vessel_exist >= 1:
        flash(u'You can\'t delete this vessel', 'danger')
        return redirect(url_for("Vessel_Index"))
    else:
        delete_vessel.key.delete()
        flash(u'Vessel has been deleted successfully', 'success')
        return redirect(url_for("Vessel_Index"))

    return render_template('/vessel/index.html', **locals())

