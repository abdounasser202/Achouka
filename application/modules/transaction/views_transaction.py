__author__ = 'wilrona'

from ...modules import *

from ..transaction.models_transaction import TransactionModel, AgencyModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/recording/transaction')
def Transaction_Index():
    menu = 'recording'
    submenu = 'transaction'

    List_agency = AgencyModel.query()

    return render_template('/transaction/index.html', **locals())



@app.route('/recording/transaction/stat/<int:agency_id>')
def Transaction_Agency(agency_id):
    menu = 'recording'
    submenu = 'transaction'

    current_agency = AgencyModel.get_by_id(agency_id)

    transaction_agency_query = TransactionModel.query(
        TransactionModel.agency == current_agency.key
    )

    return render_template('/transaction/stat-views.html', **locals())