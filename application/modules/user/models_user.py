__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..currency.models_currency import CurrencyModel
from ..agency.models_agency import AgencyModel
from ..profil.models_profil import ProfilModel


class UserModel(ndb.Model):

    password = ndb.StringProperty()
    reset_password_token = ndb.StringProperty()

    email = ndb.StringProperty()
    confirmed_at = ndb.DateTimeProperty()
    date_create = ndb.DateTimeProperty(auto_now_add=True)

    is_enabled = ndb.BooleanProperty(default=True)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    phone = ndb.StringProperty()
    logged = ndb.BooleanProperty(default=False)
    date_last_logged = ndb.DateTimeProperty()

    agency = ndb.KeyProperty(kind=AgencyModel)
    currency = ndb.KeyProperty(kind=CurrencyModel)
    profil = ndb.KeyProperty(kind=ProfilModel)

    def is_active(self):
        return self.is_enabled

    def is_authenticated(self):
        return self.logged

    def is_anonymous(self):
        return False

    def full_name(self):
        full_name = ''+str(self.last_name)+' '+str(self.first_name)+''
        return full_name

    def agencys(self):
        agency = None
        if self.agency:
            agency_data = AgencyModel.get_by_id(self.agency.id())
            agency = agency_data.name
        else:
            agency = 'Super Agency'
        return agency

    def have_agency(self): #verifie que l'utilisateur courant a une agence pour faire des ventes
        if self.agency:
            return True
        return False

    def have_credit(self): #verifie que l'agence de l'utilisateur courant a des tickets a vendre
        from ..ticket.models_ticket import TicketModel
        user_agence = AgencyModel.get_by_id(self.agency.id())

        user_ticket = TicketModel.query(
            TicketModel.agency == user_agence.key
        ).count()

        if user_ticket >= 1:
            return True

        return False

    def has_roles(self, *requirements):

        user_role = UserRoleModel.query(
            UserRoleModel.user_id == self.key
        )

        user_roles = [role.role_id.get().name for role in user_role]

        # has_role() accepts a list of requirements
        for requirement in requirements:
            if isinstance(requirement, (list, tuple)):
                # this is a tuple_of_role_names requirement
                tuple_of_role_names = requirement
                authorized = False
                for role_name in tuple_of_role_names:
                    if role_name in user_roles:
                        # tuple_of_role_names requirement was met: break out of loop
                        authorized = True
                        break
                if not authorized:
                    return False                    # tuple_of_role_names requirement failed: return False
            else:
                # this is a role_name requirement
                role_name = requirement
                # the user must have this role
                if not role_name in user_roles:
                    return False                    # role_name requirement failed: return False

        # All requirements have been met: return True
        return True

    def remaining_ticket(self):
        if self.agency:
            agency_user = AgencyModel.get_by_id(self.agency.id())
            number = agency_user.TicketUnsold()
        else:
            number = 'No Ticket'
        return number+' Available'



class RoleModel(ndb.Model):
    name = ndb.StringProperty()
    visible = ndb.BooleanProperty(default=True)


class UserRoleModel(ndb.Model):
    user_id = ndb.KeyProperty(kind=UserModel)
    role_id = ndb.KeyProperty(kind=RoleModel)


class ProfilRoleModel(ndb.Model):
    profil_id = ndb.KeyProperty(kind=ProfilModel)
    role_id = ndb.KeyProperty(kind=RoleModel)