__author__ = 'wilrona'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators


class FormTicket(wtf.Form):
    number = wtf.IntegerField(label='Number ticket generate', validators=[validators.Required()])