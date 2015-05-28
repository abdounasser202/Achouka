__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators


class FormTicketType(wtf.Form):
    name = wtf.StringField(label='Ticket Type Name', validators=[validators.Required()])
    class_name = wtf.StringField(label=' Select Class ', validators=[validators.Required()])
    type_name = wtf.StringField(label=' Select Type', validators=[validators.Required()])
    journey_name = wtf.StringField(label=' Select Journey', validators=[validators.Required()])
    price = wtf.FloatField(label=' Price', validators=[validators.Required()])
    currency = wtf.StringField(validators=[validators.Required()])
    active = wtf.BooleanField(default=False)


class FormTicketTypeName(wtf.Form):
    name = wtf.StringField(label="Ticket Type Name", validators=[validators.Required()])
    is_child = wtf.BooleanField(default=False)
    default = wtf.BooleanField(default=False)


class FormJourneyType(wtf.Form):
    name = wtf.StringField(label='Journey Type Name', validators=[validators.Required()])
    default = wtf.BooleanField(default=False)


class FormClassType(wtf.Form):
    name = wtf.StringField(label='Class Type Name', validators=[validators.Required()])
    default = wtf.BooleanField(default=False)


class FormSelectTicketType(wtf.Form):
    type_name = wtf.StringField(label=' Select Type',validators=[validators.Required()])
    class_name = wtf.StringField(label=' Select Class ', validators=[validators.Required()])
    journey_name = wtf.StringField(label=' Select Journey', validators=[validators.Required()])