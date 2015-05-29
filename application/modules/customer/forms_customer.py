__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators


class FormCustomer(wtf.Form):
    first_name = wtf.StringField(label='Fist name', validators=[validators.Required()])
    last_name = wtf.StringField(label='Last name', validators=[validators.Required()])
    birthday = wtf.DateField(label='Birthday', validators=[validators.Required()], format="%d/%m/%Y")
    profession = wtf.StringField(label='Profession')
    nationality = wtf.StringField(label='Select Nationality')
    email = wtf.StringField(label='Email Adress', validators=[validators.Email()])
    phone = wtf.StringField(label='Phone Number')



class FormCustomerSearch(wtf.Form):
    first_name = wtf.StringField(label='Fist name', validators=[validators.Required()])
    last_name = wtf.StringField(label='Last name', validators=[validators.Required()])
    birthday = wtf.DateField(label='Birthday', validators=[validators.Required()], format="%d/%m/%Y")