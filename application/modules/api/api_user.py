__author__ = 'Vercossa'


from api_function import *
from ..user.models_user import UserModel, AgencyModel, UserRoleModel
from ..profil.models_profil import ProfilModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/login_user_api/<password>/<email>/<token>')
def login_user_api(password, email, token):

    user_login = UserModel.query(
        UserModel.email == email,
        UserModel.password == password
    ).get()

    if not user_login:
        return not_found()
    else:

        data = {}
        data['user'] = user_login.make_to_dict()

        if not user_login.profil:
            #prendre le super admin
            role_user = UserRoleModel.query(
                UserRoleModel.user_id == user_login.key
            ).get()
            data['role'] = role_user.make_to_dict()
            resp = jsonify(data)
            return resp


        if user_login.profil and user_login.agency and user_login.agency.get().Key() == token:
            #prendre les utilisateurs de l'agence en cours
            user_profil = ProfilModel.get_by_id(user_login.make_to_dict()['profil'].id())
            data['profil'] = user_profil.make_to_dict()
            resp = jsonify(data)
            return resp

        return not_found(error=403, message="Forbidden. you have not permission to access")