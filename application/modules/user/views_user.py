__author__ = 'wilrona'

from ...modules import *
from google.appengine.ext import ndb

from models_user import UserModel, RoleModel, UserRoleModel, CurrencyModel
from forms_user import FormRegisterUserAdmin

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/creationsuperadmin', methods=['GET', 'POST'])
def Super_Admin_Create():

    form = FormRegisterUserAdmin(request.form)

    if form.validate_on_submit():
        User = UserModel()

        role = RoleModel.query(RoleModel.name == 'super_admin').get()
        if not role:
            role = RoleModel()
            role.name = 'super_admin'
            role.visible = False

            role = role.put()
            role = RoleModel.get_by_id(role.id())

        UserRole = UserRoleModel()

        currency = CurrencyModel.query(
            CurrencyModel.code == form.currency.data
        ).get()

        if not currency:
            CurrencyCreate = CurrencyModel()
            CurrencyCreate.code = form.currency.data
            CurrencyCreate.name = 'Franc CFA'
            currencyCreate = CurrencyCreate.put()
        else:
            currencyCreate = currency

        if role:
            if currencyCreate:
                currency = CurrencyModel.get_by_id(currencyCreate.id())
            else:
                currency = CurrencyModel.get_by_id(currencyCreate.key.id())

            User.first_name = form.first_name.data
            User.last_name = form.last_name.data
            User.email = form.email.data
            User.phone = form.phone.data
            User.currency = currency.key

            password = hashlib.sha224(form.password.data).hexdigest()
            User.password = password

            UserCreate = User.put()
            UserCreate = UserModel.get_by_id(UserCreate.id())

            UserRole.role_id = role.key
            UserRole.user_id = UserCreate.key

            UserRole.put()
        return redirect(url_for('Home'))

    return render_template('user/edit-super-admin.html', **locals())
