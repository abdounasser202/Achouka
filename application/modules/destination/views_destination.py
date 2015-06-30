__author__ = 'wilrona'

from ...modules import *

from models_destination import DestinationModel, CurrencyModel
from forms_destination import FormDestination

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/destination')
def Destination_Index():
    menu = 'settings'
    submenu = 'destination'

    destinations = DestinationModel.query()

    return render_template('/destination/index.html', **locals())

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/destination/Edit/<int:destination_id>', methods=['GET', 'POST'])
@app.route('/settings/destination/Edit', methods=['GET', 'POST'])
def Destination_Edit(destination_id=None):
    menu = 'settings'
    submenu = 'destination'



    #liste des devises
    listcurency = CurrencyModel.query()

    if destination_id:
        # formulaire et information de la devise a editer
        destination = DestinationModel.get_by_id(destination_id)
        form = FormDestination(obj=destination)

        from ..agency.models_agency import AgencyModel
        from ..travel.models_travel import TravelModel
        from ..transaction.models_transaction import TransactionModel

        agency_destination_exist = AgencyModel.query(
            AgencyModel.destination == destination.key
        ).count()

        travel_destination_start_exist = TravelModel.query(
            TravelModel.destination_start == destination.key
        ).count()

        travel_destination_check_exist = TravelModel.query(
            TravelModel.destination_check == destination.key
        ).count()

        transaction_destination_exist = TransactionModel.query(
            TransactionModel.destination == destination.key
        ).count()

        currency_destination_id = destination.currency.get().key.id()

    else:
        form = FormDestination()
        destination = DestinationModel()

    if form.validate_on_submit():
        currency_dest = CurrencyModel.get_by_id(int(form.currency.data))
        dest_exit = DestinationModel.query(DestinationModel.code == form.code.data).count()
        if dest_exit >= 1:
            if destination.code == form.code.data: #Traitement pour la mise a jour
                destination.code = form.code.data
                destination.name = form.name.data
                destination.currency = currency_dest.key
                try:
                    destination.put()
                    flash(u' Destination Update. ', 'success')
                    return redirect(url_for('Destination_Index'))
                except CapabilityDisabledError:
                    flash(u' Error data base. ', 'danger')
                    return redirect(url_for('Destination_Edit'))
            else:
                form.code.errors.append('Other destination use this code '+form.code.data)
        else:
            destination.code = form.code.data
            destination.name = form.name.data
            destination.currency = currency_dest.key

            try:
                destination.put()
                flash(u' Destination Save. ', 'success')

                return redirect(url_for('Destination_Index'))
            except CapabilityDisabledError:
                flash(u' Error data base. ', 'danger')
                return redirect(url_for('Destination_Edit'))

    return render_template('/destination/edit.html', **locals())

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/destination/delete/', methods=['GET', 'POST'])
@app.route('/settings/destination/delete/<int:destination_id>', methods=['GET', 'POST'])
def Destination_Delete(destination_id=None):
    menu = 'settings'
    submenu = 'vessel'

    delete_destination = DestinationModel.get_by_id(int(destination_id))

    from ..agency.models_agency import AgencyModel
    from ..travel.models_travel import TravelModel
    from ..transaction.models_transaction import TransactionModel

    agency_destination_exist = AgencyModel.query(
        AgencyModel.destination == delete_destination.key
    ).count()

    travel_destination_start_exist = TravelModel.query(
        TravelModel.destination_start == delete_destination.key
    ).count()

    travel_destination_check_exist = TravelModel.query(
        TravelModel.destination_check == delete_destination.key
    ).count()

    transaction_destination_exist = TransactionModel.query(
        TransactionModel.destination == delete_destination.key
    ).count()

    if agency_destination_exist >= 1 or travel_destination_start_exist >= 1 or travel_destination_check_exist >= 1 or transaction_destination_exist >= 1:
        flash(u'You can\'t delete this destination', 'danger')
        return redirect(url_for("Destination_Index"))
    else:
        delete_destination.delete()
        flash(u'Destination has been deleted successfully', 'success')
        return  redirect(url_for("Destination_Index"))

    return render_template('/destination/index.html', **locals())

