__author__ = 'wilrona'

from ...modules import *

from ..transaction.models_transaction import TransactionModel, AgencyModel, UserModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/recording/transaction')
def Transaction_Index():
    menu = 'recording'
    submenu = 'transaction'

    if not current_user.has_roles(('admin','super_admin')) and current_user.has_roles('manager_agency'):
        agency_user = AgencyModel.get_by_id(int(session.get('agence_id')))
        return redirect(url_for('Transaction_Agency', agency_id=agency_user.key.id()))

    List_agency = AgencyModel.query()

    return render_template('/transaction/index.html', **locals())



@app.route('/recording/transaction/stat/<int:agency_id>')
def Transaction_Agency(agency_id):
    menu = 'recording'
    submenu = 'transaction'

    current_agency = AgencyModel.get_by_id(agency_id)

    destination_transaction_query = TransactionModel.query(
        TransactionModel.agency == current_agency.key,
        TransactionModel.destination != current_agency.destination,
        projection=[TransactionModel.destination],
        distinct=True
    )

    transaction_agency_query = TransactionModel.query(
        TransactionModel.agency == current_agency.key
    )

    # Liste des utilisateurs de l'agence
    user_agency = UserModel.query(
        UserModel.agency == current_agency.key
    )

    return render_template('/transaction/stat-views.html', **locals())