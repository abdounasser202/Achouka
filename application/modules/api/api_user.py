__author__ = 'Vercossa'


from api_function import *
from ..user.models_user import UserModel, AgencyModel, UserRoleModel
from ..profil.models_profil import ProfilModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/login_user/get/<password>/<email>/<token>')
def login_user_api(password, email, token):

    user_login = UserModel.query(
        UserModel.email == email,
        UserModel.password == password
    ).get()

    if not user_login:
        return not_found()
    else:
        data = {}
        verified_token = request.args.get('exist')
        tokens = None
        agency_exist = AgencyModel.get_by_key(token)
        if verified_token == '1' and agency_exist:
            tokens = agency_exist.Key()
            data['current_agency'] = agency_exist.make_to_dict()
            from ..destination.models_destination import DestinationModel
            destination_agency = DestinationModel.get_by_id(agency_exist.destination.id())
            data['current_agency']['agency_destination'] = destination_agency.make_to_dict()


        data['user'] = user_login.make_to_dict()
        data['status'] = 200

        #super_admin
        if not user_login.profil and tokens:
            #prendre le super admin
            role_user = UserRoleModel.query(
                UserRoleModel.user_id == user_login.key
            ).get()
            data['profil_user'] = None
            data['role_user'] = role_user.make_to_dict()
            resp = jsonify(data)
            return resp

        #Admin
        if user_login.profil and tokens and not user_login.agency and user_login.is_active(token):
            #prendre les utilisateurs de l'agence en cours
            user_profil = ProfilModel.get_by_id(user_login.profil.id())
            data['profil_user'] = user_profil.make_to_dict()
            resp = jsonify(data)
            return resp

        if tokens:
            return not_found(error=403, message="Forbidden. you have not permission to access/<token>")
        else:
            return not_found(error=400, message="Bad Request. your token's agency is not correct/<token>")
            
@app.route("/user/get/<token>")
def get_user_api(token):

    get_agency = AgencyModel.get_by_key(token)
    if not get_agency:
        return not_found(message="Your token is not correct")

    get_user = UserModel().query()
    data = {}
    data['status'] = 200
    data['user'] = []
    for user in get_user:
        user.make_to_dict()['profil_id'] = user.profil.id()
        data['user'].append(user.make_to_dict())
    resp = jsonify(data)
    return resp
