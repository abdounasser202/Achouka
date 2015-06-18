__author__ = 'wilrona'

from ...modules import *

from models_customer import CustomerModel
from forms_customer import FormCustomer

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/recording/customer')
def Customer_Index():
    menu = 'recording'
    submenu = 'customer'

    from lib.phonenumbers import phonenumber
    from lib.phonenumbers import geocoder

    number = phonenumbers.parse("+23776370738", None)
    national_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL)
    country_name = repr(geocoder.description_for_number(number, "en"))

    customers = CustomerModel.query()

    return render_template('customer/index.html', **locals())


@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/recording/customer/edit', methods=['GET', 'POST'])
@app.route('/recording/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
def Customer_Edit(customer_id=None):
    menu = 'recording'
    submenu = 'customer'
    nationalList = global_nationality_contry

    if customer_id:
        customer = CustomerModel.get_by_id(customer_id)
        form = FormCustomer(obj=customer)

    else:
        customer = CustomerModel()
        form = FormCustomer(request.form)

    customer_count = 0
    if form.validate_on_submit():

        customer_exist = CustomerModel.query(
            CustomerModel.first_name == form.first_name.data,
            CustomerModel.last_name == form.last_name.data,
            CustomerModel.birthday == function.date_convert(form.birthday.data)
        )
        customer_count = customer_exist.count()

        if customer_count >= 1 and not customer_id:
            customer_view = customer_exist.get()
            flash(u' This customer exist. ', 'danger')
        else:
            customer.first_name = form.first_name.data
            customer.last_name = form.last_name.data
            customer.birthday = function.date_convert(form.birthday.data)
            customer.profession = form.profession.data
            customer.email = form.email.data
            customer.nationality = form.nationality.data
            customer.phone = form.phone.data

            custom = customer.put()
            flash(u' Customer save. ', 'success')
            return redirect(url_for('Customer_Index'))

    return render_template('customer/edit.html', **locals())


@login_required
@roles_required(('super_admin', 'manager_agency'))
@app.route('/Active_Customer/<int:customer_id>')
def Active_Customer(customer_id):
    custom = CustomerModel.get_by_id(customer_id)
    if custom.status is False:
        custom.status = True

    else:
        custom.status = False

    custom.put()

    flash(u' Customer Updated. ', 'success')
    return redirect(url_for("Customer_Index"))