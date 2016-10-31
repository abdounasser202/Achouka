__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators

class FormAgency(wtf.Form):
    name = wtf.StringField(label='Agency name', validators=[validators.Required()])
    country = wtf.StringField(label='Country', validators=[validators.Required()])
    phone = wtf.StringField(label='Phone')
    fax = wtf.StringField(label='Fax')
    address = wtf.StringField(label='Adress')
    reduction = wtf.FloatField(label='Discount', default=0)
    destination = wtf.StringField(label='Select town', validators=[validators.Required()])
    status = wtf.BooleanField(default=False)