__author__ = 'bapetel'

"""
La nature d'une modification peut etre:
    creation ou enregistrement 1
    desactivation 2
    suppression 3
    modification 4
    activation 5
    is_default 6
    is_not_default 7
    is_special 8
    is_not_special 9
    ancienne_valeur 0
"""

from google.appengine.ext import ndb
from ..user.models_user import UserModel


class ActivityModel(ndb.Model):
    user_modify = ndb.KeyProperty(kind=UserModel) # utilisateur
    nature = ndb.IntegerProperty() # nature de la modification
    object = ndb.StringProperty() # type objet qui a ete modifie par exemple vessel
    identity = ndb.IntegerProperty() # id() de l'objet qui a ete modifie
    time = ndb.DateTimeProperty() # date de la modification