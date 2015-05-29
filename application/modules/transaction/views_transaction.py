__author__ = 'wilrona'

from ...modules import *

from ..agency.models_agency import AgencyModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/recording/transaction')
def Transaction_Index():
    menu = 'recording'
    submenu = 'transaction'

    return render_template('/transaction/index.html', **locals())