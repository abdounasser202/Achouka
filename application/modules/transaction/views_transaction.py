__author__ = 'wilrona'

from ...modules import *

from ..agency.models_agency import AgencyModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/recording/transaction')
def Transaction_Index():
    menu = 'recording'
    submenu = 'transaction'

    return render_template('/transaction/index.html', **locals())