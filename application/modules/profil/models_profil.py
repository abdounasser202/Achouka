__author__ = 'wilrona'

from google.appengine.ext import ndb


class ProfilModel(ndb.Model):
    name = ndb.StringProperty()
    standard = ndb.BooleanProperty(default=False)
    enable = ndb.BooleanProperty(default=True)

    def make_to_dict(self):
        from ..user.models_user import ProfilRoleModel
        to_dict = {}

        to_dict['id'] = self.key.id()
        to_dict['name'] = self.name
        to_dict['standard'] = self.standard
        to_dict['enable'] = self.enable

        profil_role = ProfilRoleModel.query(
            ProfilRoleModel.profil_id == self.key
        )

        roles = [role.role_id.id() for role in profil_role]
        to_dict['roles'] = roles

        return to_dict