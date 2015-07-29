__author__ = 'wilrona'

from google.appengine.ext import ndb


class ProfilModel(ndb.Model):
    name = ndb.StringProperty()
    standard = ndb.BooleanProperty(default=False)
    enable = ndb.BooleanProperty(default=True)

    def make_to_dict(self):
        from ..user.models_user import ProfilRoleModel
        to_dict = {}

        to_dict['profil_id'] = self.key.id()
        to_dict['profil_name'] = self.name
        to_dict['profil_standard'] = self.standard
        to_dict['profil_enable'] = self.enable

        profil_role = ProfilRoleModel.query(
            ProfilRoleModel.profil_id == self.key
        )

        roles = [{
            'role_id': role.role_id.id(),
            'role_name': role.role_id.get().name,
            'role_visible': role.role_id.get().visible
        } for role in profil_role]
        to_dict['profil_roles'] = roles

        return to_dict