__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators

class FormTravel(wtf.Form):
    time = wtf.StringField(label='Travel line time')
    destination_start = wtf.StringField(label='Select your departure destination', validators=[validators.Required()])
    destination_check = wtf.StringField(label='Select your arrivals destination', validators=[validators.Required()])