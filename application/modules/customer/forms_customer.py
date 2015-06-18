__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators


def unique_email_validator(form, field):
    if not field.data:
        field.errors[:] = []
        raise validators.StopValidation()


class FormCustomer(wtf.Form):
    first_name = wtf.StringField(label='Fist name', validators=[validators.Required()])
    last_name = wtf.StringField(label='Last name', validators=[validators.Required()])
    birthday = wtf.DateField(label='Birthday', validators=[validators.Required()], format="%d/%m/%Y")
    profession = wtf.StringField(label='Profession')
    nationality = wtf.StringField(label='Select Nationality')
    email = wtf.StringField(label='Email Adress', validators=[unique_email_validator, validators.Email()])
    dial_code = wtf.StringField(label='Code')
    phone = wtf.StringField(label='Phone Number')


class FormCustomerSearch(wtf.Form):
    first_name = wtf.StringField(label='Fist name', validators=[validators.Required()])
    last_name = wtf.StringField(label='Last name', validators=[validators.Required()])
    birthday = wtf.DateField(label='Birthday', validators=[validators.Required()], format="%d/%m/%Y")


class FormCustomerPOS(wtf.Form):
    first_name = wtf.StringField(label='Fist name', validators=[validators.Required()])
    last_name = wtf.StringField(label='Last name', validators=[validators.Required()])
    birthday = wtf.DateField(label='Birthday', validators=[validators.Required()], format="%d/%m/%Y")
    profession = wtf.StringField(label='Profession')
    nationality = wtf.StringField(label='Select Nationality')
    email = wtf.StringField(label='Email Adress', validators=[unique_email_validator, validators.Email()])
    phone = wtf.StringField(label='Phone Number')
    dial_code = wtf.StringField(label='Code')
    type_name = wtf.StringField(validators=[validators.Required()])
    class_name = wtf.StringField(validators=[validators.Required()])
    journey_name = wtf.StringField(validators=[validators.Required()])
    current_departure = wtf.HiddenField()