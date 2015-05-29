__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from models_user import UserModel


class FormLogin(wtf.Form):
    email = wtf.StringField('Email', validators=[validators.Required()])
    password = wtf.PasswordField('Password', [validators.Required("Password is required.")])
    remember_me = wtf.BooleanField(label='Remember me')
    submit = wtf.SubmitField("Sign In")


def unique_email_validator(form, field):
    """ email must be unique"""
    user_manager =  UserModel.query(
        UserModel.email == field.data
    ).count()
    if user_manager >= 1:
        raise wtf.ValidationError('This Email is already in use. Please try another one.')


def password_validator(form, field):
        """ Password must have one lowercase letter, one uppercase letter and one digit."""
        # Convert string to list of characters
        password = list(field.data)
        password_length = len(password)

        # Count lowercase, uppercase and numbers
        lowers = uppers = digits = 0
        for ch in password:
            if ch.islower(): lowers+=1
            if ch.isupper(): uppers+=1
            if ch.isdigit(): digits+=1

        # Password must have one lowercase letter, one uppercase letter and one digit
        is_valid = password_length>=6 and lowers and uppers and digits
        if not is_valid:
            raise wtf.ValidationError('Password must have at least 6 characters with one lowercase letter, one uppercase letter and one number')


def first_name_validator(form, field):
    """ Username must cont at least 3 alphanumeric characters long"""
    first_name = field.data
    if len(first_name) < 3:
        raise wtf.ValidationError('Username must be at least 3 characters long')
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._'
    chars = list(first_name)
    for char in chars:
        if char not in valid_chars:
            raise wtf.ValidationError("Username may only contain letters, numbers, '-', '.' and '_'.")

def last_name_validator(form, field):
    """ Username must cont at least 3 alphanumeric characters long"""
    last_name = field.data
    if len(last_name) < 3:
        raise wtf.ValidationError('Username must be at least 3 characters long')
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._'
    chars = list(last_name)
    for char in chars:
        if char not in valid_chars:
            raise wtf.ValidationError("Username may only contain letters, numbers, '-', '.' and '_'.")

class FormRegisterUserAdmin(wtf.Form):
    first_name = wtf.StringField(label='First Name', validators=[validators.Required(), first_name_validator])
    last_name = wtf.StringField(label='Last Name', validators=[validators.Required(), last_name_validator])
    email = wtf.StringField(label='Email Adresse', validators=[validators.Email('Email not valid'), validators.Required(), unique_email_validator])
    phone = wtf.StringField(label='Phone Number')
    password = wtf.PasswordField(label='Password', validators=[validators.Required('Password is required'), password_validator])
    retype_password = wtf.PasswordField(label='Retype Password', validators=[validators.EqualTo('password', message='Password and Retype Password did not match')])
    currency = wtf.StringField(validators=[validators.Required()])
    agency = wtf.StringField()
    submit = wtf.SubmitField("Register")


class FormEditUserAdmin(wtf.Form):
    first_name = wtf.StringField(label='First Name', validators=[validators.Required(), first_name_validator])
    last_name = wtf.StringField(label='Last Name', validators=[validators.Required(), last_name_validator])
    phone = wtf.StringField(label='Phone Number')
    currency = wtf.StringField(validators=[validators.Required()])
    agency = wtf.StringField()


class FormRegisterUser(wtf.Form):
    first_name = wtf.StringField(label='First Name', validators=[validators.Required(), first_name_validator])
    last_name = wtf.StringField(label='Last Name', validators=[validators.Required(), last_name_validator])
    email = wtf.StringField(label='Email Adresse', validators=[validators.Email('Email not valid'), validators.Required(), unique_email_validator])
    phone = wtf.StringField(label='Phone Number')
    password = wtf.PasswordField(label='Password', validators=[validators.Required('Password is required'), password_validator])
    retype_password = wtf.PasswordField(label='Retype Password', validators=[validators.EqualTo('password', message='Password and Retype Password did not match')])
    profil = wtf.StringField(validators=[validators.Required()])
    agency = wtf.StringField()
    submit = wtf.SubmitField("Register")


class FormEditUser(wtf.Form):
    first_name = wtf.StringField(label='First Name', validators=[validators.Required(), first_name_validator])
    last_name = wtf.StringField(label='Last Name', validators=[validators.Required(), last_name_validator])
    phone = wtf.StringField(label='Phone Number', validators=[validators.Required()])
    profil = wtf.StringField(validators=[validators.Required()])
    agency = wtf.StringField()