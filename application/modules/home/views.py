__author__ = 'wilrona'

from ...modules import *
from application import login_manager

from ..user.models_user import UserModel, RoleModel, UserRoleModel
from ..user.forms_user import FormLogin

cache = Cache(app)


@login_manager.user_loader
def load_user(userid):
    return UserModel.get_by_id(userid)


@app.route('/set_session')
def set_session():
    session.permanent = True
    return json.dumps({
        'statut': True
    })


@app.route('/', methods=['POST', 'GET'])
def Home():

    if 'user_id' in session:
        return redirect(url_for('Dashboard'))

    admin_role = RoleModel.query(
        RoleModel.name == 'super_admin'
    ).get()
    exist_super_admin = 0
    if admin_role:
        exist_super_admin = UserRoleModel.query(
            UserRoleModel.role_id == admin_role.key
        ).count()

    exist = False
    if exist_super_admin >= 1:
        exist = True

    url = None
    if request.args.get('url'):
        url = request.args.get('url')

    form = FormLogin()
    if form.validate_on_submit():
        try:
            password = hashlib.sha224(form.password.data).hexdigest()
        except UnicodeEncodeError:
            flash('Username or Password is invalid', 'danger')
            return redirect(url_for('Home'))

        user_login = UserModel.query(
            UserModel.email == form.email.data,
            UserModel.password == password
        ).get()

        if user_login is None:
            flash('Username or Password is invalid', 'danger')
        else:
            if not user_login.is_active():
                flash('Your account is disabled. Contact Administrator', 'danger')
                return redirect(url_for('Home', url=url))

            session['user_id'] = user_login.key.id()
            agency = 0
            if user_login.agency:
                agency = user_login.agency.get().key.id()

            session['agence_id'] = agency
            user_login.logged = True
            user_login.put()

            if url:
                return redirect(url)

            if not user_login.has_roles(('admin', 'manager_agency', 'super_admin')) and user_login.has_roles('employee_POS'):
                return redirect(url_for('Pos'))

            if not user_login.has_roles(('admin', 'manager_agency', 'super_admin')) and user_login.has_roles('employee_Boarding'):
                return redirect(url_for('Boarding'))

            return redirect(url_for('Dashboard'))

    return render_template('index/home.html', **locals())


@app.route('/logout_user')
def logout_user():
    if 'user_id' in session:
        user_id = session.get('user_id')
        UserLogout = UserModel.get_by_id(int(user_id))
        UserLogout.logged = False
        change = UserLogout.put()
        if change:
            session.pop('user_id')
            session.pop('agence_id')
    return redirect(url_for('Home'))


@app.route('/dashboard')
@login_required
def Dashboard():
    menu = 'dashboard'

    return render_template('/index/dashboard.html', **locals())


@app.route('/settings')
@login_required
@roles_required(('admin', 'super_admin'))
def Settings():

    menu = 'settings'
    return render_template('/index/settings.html', **locals())


@app.route('/recording')
@login_required
@roles_required(('manager_agency', 'super_admin'))
def Recording():

    menu = 'recording'
    return render_template('/index/recording.html', **locals())