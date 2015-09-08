__author__ = 'Vercossa'

from api_function import *
from ..agency.models_agency import AgencyModel
from ..transaction.models_transaction import TransactionModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/transaction/get/<token>')
def get_transaction_api(token):

    try:
       date = datetime.datetime.combine(request.args.get('last_update'), datetime.datetime.min.time())
    except:
        date = None

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    if date:
        get_transaction = TransactionModel.query(
            TransactionModel.transaction_date <= date,
            TransactionModel.agency == get_agency.key
        )
    else:
        get_transaction = TransactionModel.query(
            TransactionModel.agency == get_agency.key
        )
    data = {'status': 200, 'transactions': []}
    for transactions in get_transaction:
        data['transactions'].append(transactions.make_to_dict())
    resp = jsonify(data)
    return resp