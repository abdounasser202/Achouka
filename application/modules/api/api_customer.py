__author__ = 'Vercossa'

from api_function import *
from ..customer.models_customer import CustomerModel
from ..agency.models_agency import AgencyModel
# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/customer/get/<token>')
def get_customer_api(token):

    try:
        date = function.date_convert(request.args.get('last_update'))
    except:
        date = None

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    if date:
        get_customer = CustomerModel().query(
            CustomerModel.date_update >= date
        )
    else:
        get_customer = CustomerModel().query()

    data = {'status': 200, 'customer': []}
    for customer in get_customer:
        data['customer'].append(customer.make_to_dict())
    resp = jsonify(data)
    return resp


@app.route('/customer/put/<token>', methods=['POST'])
def put_customer_api(token):
    import unicodedata, ast

    # recuperation de nos valeurs envoye par POST
    customer = request.form.getlist('customer')
    # convertion du tableau en Unicode
    for customer in customer:
        unicodedata.normalize('NFKD', customer).encode('ascii', 'ignore')
    #transformation de notre unicode en dictionnaire
    customer = ast.literal_eval(customer)

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    save = None
    count = 0

    for data_get in customer:
        old_data = CustomerModel.get_by_id(int(data_get['customer_id']))
        if old_data:
            old_data.first_name = data_get['customer_first_name']
            old_data.last_name = data_get['customer_last_name']
            old_data.birthday = function.date_convert(data_get['customer_birthday'])
            old_data.passport_number = data_get['customer_passport_number']
            old_data.nic_number = data_get['customer_nic_number']
            old_data.profession = data_get['customer_profession']
            old_data.nationality = data_get['customer_nationality']
            old_data.phone = data_get['customer_phone']
            old_data.dial_code = data_get['customer_dial_code']
            old_data.email = data_get['customer_email']
            old_data.is_new = data_get['customer_is_new']
            old_data.status = data_get['customer_status']
            save = old_data.put()
        else:
            data_save = CustomerModel(id=int(data_get['customer_id']))
            data_save.first_name = data_get['customer_first_name']
            data_save.last_name = data_get['customer_last_name']
            data_save.birthday = function.date_convert(data_get['customer_birthday'])
            data_save.passport_number = data_get['customer_passport_number']
            data_save.nic_number = data_get['customer_nic_number']
            data_save.profession = data_get['customer_profession']
            data_save.nationality = data_get['customer_nationality']
            data_save.phone = data_get['customer_phone']
            data_save.dial_code = data_get['customer_dial_code']
            data_save.email = data_get['customer_email']
            data_save.is_new = data_get['customer_is_new']
            data_save.status = data_get['customer_status']
            save = data_save.put()
        count += 1

    if save:
        return not_found(error=200, message="You have send "+str(count)+" customer(s) in online apps")
    else:
        return not_found(error=404, message="You have send "+str(count)+" customer(s) in online apps")