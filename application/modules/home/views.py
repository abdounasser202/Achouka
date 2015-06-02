__author__ = 'wilrona'

from ...modules import *
from application import login_manager

from ..user.models_user import UserModel, RoleModel, UserRoleModel
from ..user.forms_user import FormLogin


cache = Cache(app)


@login_manager.user_loader
def load_user(userid):
    return UserModel.get_by_id(userid)



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

    form = FormLogin()
    if form.validate_on_submit():
        password = hashlib.sha224(form.password.data).hexdigest()
        user_login = UserModel.query(
            UserModel.email == form.email.data,
            UserModel.password == password
        ).get()
        if user_login is None:
            flash('Username or Password is invalid', 'danger')
        else:
            session['user_id'] = user_login.key.id()
            agency = 0
            if user_login.agency:
                agency = user_login.agency.get().key.id()

            session['agence_id'] = agency
            user_login.logged = True
            user_login.put()

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
    return redirect(url_for('Home'))


@app.route('/dashboard')
@login_required
def Dashboard():
    menu = 'dashboard'
    return render_template('/index/dashboard.html', **locals())


@app.route('/point-of-sell/', methods=['GET', 'POST'])
def Pos(year=None, current_month_active=None, current_day_active=None):
    menu = 'pos'
    from ..agency.models_agency import AgencyModel
    from ..departure.models_departure import DepartureModel

    departure = DepartureModel.query(
        DepartureModel.departure_date == datetime.date.today(),
        DepartureModel.schedule >= datetime.datetime.today().time()
    ).order(
        DepartureModel.schedule,
        DepartureModel.time_delay
    )

    if current_user.have_agency():
        user_agence = AgencyModel.get_by_id(int(session.get('agence_id')))

        for dep in departure:
            if dep.destination.get().destination_start == user_agence.destination:
                current_departure = dep
                break
    else:
        current_departure = departure.get()

    return render_template('/index/pos.html', **locals())




@app.route('/settings')
def Settings():

    menu = 'settings'
    return render_template('/index/settings.html', **locals())


@app.route('/recording')
def Recording():

    menu = 'recording'
    return render_template('/index/recording.html', **locals())