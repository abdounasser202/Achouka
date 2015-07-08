__author__ = 'wilrona'

from ...modules import *

from models_agency import AgencyModel, DestinationModel, CurrencyModel

from forms_agency import FormAgency

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@roles_required(('admin', 'super_admin'))
@app.route('/settings/agency')
@login_required
def Agency_Index():
    menu = 'settings'
    submenu = 'agency'

    agencytype = global_agencytype

    agency = AgencyModel.query()
    destagency = DestinationModel.query()

    return render_template('agency/index.html', **locals())



@app.route('/settings/agency/edit', methods=['GET', 'POST'])
@app.route('/settings/agency/edit/<int:agency_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Agency_Edit(agency_id=None):
    menu = 'settings'
    submenu = 'agency'

    destagency = DestinationModel.query()
    currency = CurrencyModel.query()
    country_agency = global_current_country

    if agency_id:
        agencymod = AgencyModel.get_by_id(agency_id)
        form = FormAgency(obj=agencymod)

        form.country.data = agencymod.country
        form.destination.data = agencymod.destination
    else:
        agencymod = AgencyModel()
        form = FormAgency()

    if form.validate_on_submit():

        if not agency_id:
            destsave = DestinationModel.get_by_id(int(form.destination.data))

        agency_exist = AgencyModel.query(
                AgencyModel.name == form.name.data,
                AgencyModel.is_achouka == True
        ).count()


        if agency_exist >= 1:
            if agency_id and form.name.data == agencymod.name:
                agencymod.name = form.name.data
                agencymod.country = form.country.data
                agencymod.phone = form.phone.data
                agencymod.fax = form.fax.data
                agencymod.address = form.address.data
                agencymod.reduction = form.reduction.data
                if not agency_id:
                    agencymod.destination = destsave.key
                agencymod.put()
                flash(u' Agency Update. ', 'success')
                return redirect(url_for('Agency_Index'))
            else:
                form.name.errors.append('Other Agency use this name')
        else:
            agencymod.name = form.name.data
            agencymod.country = form.country.data
            agencymod.phone = form.phone.data
            agencymod.fax = form.fax.data
            agencymod.address = form.address.data
            agencymod.reduction = form.reduction.data
            agencymod.is_achouka = True
            if not agency_id:
                agencymod.destination = destsave.key

            agencymod.put()
            if agency_id:
                flash(u' Agency Update. ', 'success')
            else:
                flash(u' Agency Save. ', 'success')

            return redirect(url_for('Agency_Index'))

    return render_template('agency/edit.html', **locals())


@roles_required(('admin', 'super_admin'))
@app.route("/settings/agency/activate/<int:agency_id>")
@login_required
def Active_Agency(agency_id):
    agencymod = AgencyModel.get_by_id(agency_id)

    if not agencymod.status:
        agency_exist = AgencyModel.query(
            AgencyModel.is_achouka == agencymod.is_achouka,
            AgencyModel.status == True,
            AgencyModel.destination == agencymod.destination
        ).count()

        if agency_exist >= 1:
            flash(u'you can activate agency with the same destination : '+agencymod.destination.get().name, 'danger')
        else:
            agencymod.status = True
    else:
        agencymod.status = False

    flash(u' Agency Update. ', 'success')
    agencymod.put()
    return redirect(url_for('Agency_Index'))
