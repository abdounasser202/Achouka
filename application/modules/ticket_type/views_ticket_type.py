__author__ = 'wilrona'

from ...modules import *

from models_ticket_type import TicketTypeModel, TicketTypeNameModel, ClassTypeModel, JourneyTypeModel, TravelModel
from ..agency.models_agency import AgencyModel, CurrencyModel
from forms_ticket_type import FormTicketType, FormJourneyType, FormClassType, FormTicketTypeName


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/tickettype')
def TicketType_Index():
    menu = 'settings'
    submenu = 'tickettype'

    tickettype = TicketTypeModel.query()

    return render_template('/tickettype/index.html', **locals())

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/tickettype/edit/<int:tickettype_id>', methods=['POST', 'GET'])
@app.route('/settings/tickettype/edit', methods=['POST', 'GET'])
def TicketType_Edit(tickettype_id=None):
    menu = 'settings'
    submenu = 'tickettype'

    #liste des voyages
    listTravel = TravelModel.query().order(TravelModel.destination_start)

    #liste des ticket type name
    listTicketType = TicketTypeNameModel.query().order(TicketTypeModel.name)

    #liste des classes de ticket
    listClassTicket = ClassTypeModel.query().order(ClassTypeModel.name)

    #liste des journey
    listJourneyTicket = JourneyTypeModel.query().order(JourneyTypeModel.name)

    if tickettype_id:
        tickettype = TicketTypeModel.get_by_id(tickettype_id)
        form = FormTicketType(obj=tickettype)

        form_currency = CurrencyModel.get_by_id(int(tickettype.currency.get().key.id()))
        form_currency = form_currency.code

        form_travel = tickettype.travel.get().key.id()
    else:
        tickettype = TicketTypeModel()
        form = FormTicketType(request.form)

        if form.currency.data:
            form_currency = CurrencyModel.get_by_id(int(form.currency.data))
            form_currency = form_currency.code

    if form.validate_on_submit():
        #recuperation des informations de selection
        currency = CurrencyModel.get_by_id(int(form.currency.data))
        type_name = TicketTypeNameModel.get_by_id(int(form.type_name.data))
        class_name = ClassTypeModel.get_by_id(int(form.class_name.data))
        journey_name = JourneyTypeModel.get_by_id(int(form.journey_name.data))
        travel = TravelModel.get_by_id(int(form.travel.data))

        tickettype.name = form.name.data
        tickettype.type_name = type_name.key
        tickettype.journey_name = journey_name.key
        tickettype.class_name = class_name.key
        tickettype.currency = currency.key
        tickettype.price = form.price.data
        tickettype.travel = travel.key

        try:
            tickettype.put()
            flash(u' Ticket  Type  Save. ', 'success')
            return redirect(url_for('TicketType_Index'))
        except CapabilityDisabledError:
            flash(u' Error data base. ', 'danger')
            return redirect(url_for('TicketType_Edit'))

    return render_template('/tickettype/edit.html', **locals())


@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/Active_tickettype/<int:tickettype_id>')
def Active_tickettype(tickettype_id):

    tickettype_active = TicketTypeModel.get_by_id(tickettype_id)

    tickettype_exit = TicketTypeModel.query(
        TicketTypeModel.type_name == tickettype_active.type_name,
        TicketTypeModel.class_name == tickettype_active.class_name,
        TicketTypeModel.journey_name == tickettype_active.journey_name,
        TicketTypeModel.travel == tickettype_active.travel,
        TicketTypeModel.active == True
    ).count()

    if tickettype_exit >= 1:
        if tickettype_active.active is False:
            flash(' Other ticket type have Class = '+str(tickettype_active.class_name)
                  +', Type  = '+str(tickettype_active.type_name)+' and Journey = '
                  +str(tickettype_active.journey_name)+'from '+str(tickettype_active.travel.get().destination_start.get().name)+" to "+str(tickettype_active.travel.get().destination_check.get().name)+" is activated", 'danger')
            return redirect(url_for('TicketType_Index'))
        else:
            if tickettype_active.active:
                tickettype_active.active = False
            else:
                tickettype_active.active = True

            tickettype_active.put()
            return redirect(url_for('TicketType_Index'))
    else:
        if tickettype_active.active:
            tickettype_active.active = False
        else:
            tickettype_active.active = True

        tickettype_active.put()
        return redirect(url_for('TicketType_Index'))

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/delete_tickettype/<int:tickettype_id>')
def delete_tickettype(tickettype_id):
    #recuperer la cle de la devise equivalence
    TicketType_delete = TicketTypeModel.get_by_id(tickettype_id)
    flash(u' Ticket Type deleted. ' + TicketType_delete.name, 'success')
    TicketType_delete.key.delete()
    return redirect(url_for('TicketType_Index'))


@app.route('/Currency_Travel')
@app.route('/Currency_Travel/<int:travel_id>')
def Currency_Travel(travel_id=None):

    travel = None
    if travel_id:
        travel = TravelModel.get_by_id(travel_id)

    if travel:
        data = json.dumps({
            'statut': 'OK',
            'currency': travel.destination_start.get().currency.get().code,
            'id': travel.destination_start.get().currency.get().key.id(),
        }, sort_keys=True)
    else:
        data = json.dumps({
            'statut': 'error',
            'value': 'Choice travel'
        }, sort_keys=True)

    return data

#-------------------------------------------------------------------------------
#
# Class Type Controller
#
#-------------------------------------------------------------------------------
@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/tickettype/classtype', methods=['GET', 'POST'])
@app.route('/settings/tickettype/classtype/<int:class_type_id>', methods=['GET', 'POST'])
def ClassType_Index(class_type_id=None):
    menu = 'settings'
    submenu = 'tickettype'

    if class_type_id:
        class_type = ClassTypeModel.get_by_id(class_type_id)
        form = FormClassType(obj=class_type)
    else:
        class_type = ClassTypeModel()
        form = FormClassType(request.form)

    if form.validate_on_submit():
        class_exist = ClassTypeModel.query(ClassTypeModel.name == form.name.data).count()

        if class_exist >= 1:
            form.name.errors.append('This name '+str(form.name.data)+' exist')
        else:
            class_type.name = form.name.data
            class_type.put()
            if class_type_id:
                flash(u"Class Type Updated!", "success")
            else:
                flash(u"Class Type Saved!", "success")

            return redirect(url_for('ClassType_Index'))

    class_type_list = ClassTypeModel.query()

    return render_template("/tickettype/index-class-type.html", **locals())

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/ClassType_Default/<int:class_type_id>')
def ClassType_Default(class_type_id):

    class_type = ClassTypeModel.get_by_id(class_type_id)

    if not class_type.default:
        journey_default_exist = ClassTypeModel.query(
            ClassTypeModel.default == True,
            ClassTypeModel.key == class_type.key
        ).count()
        if journey_default_exist >= 1:
            flash(u"you can not define two class type as a criterion 'is default'!", "danger")
        else:
            class_type.default = True
    else:
        class_type.default = False
    class_type.put()

    flash(u"Journey Updated!", "success")
    return redirect(url_for('ClassType_Index'))

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/ClassType_Delete/<int:class_type_id>')
def ClassType_Delete(class_type_id):

    class_delete = ClassTypeModel.get_by_id(class_type_id)

    class_ticket_type_exist = TicketTypeModel.query(
        TicketTypeModel.class_name == class_delete.key
    ).count()

    from ..ticket.models_ticket import TicketModel
    class_ticket_exist = TicketModel.query(
        TicketModel.class_name == class_delete.key
    ).count()

    if class_ticket_type_exist >= 1 or class_ticket_exist >= 1:
        flash(u"You can't delete this class"+class_delete.name+u" it's used by ticket type and some ticket!", "danger")
        return redirect(url_for('ClassType_Index'))

    class_delete.key.delete()
    flash(u"Class Type has been deleted successfully!", "success")
    return redirect(url_for('ClassType_Index'))


#-------------------------------------------------------------------------------
#
# Journey Type Controller
#
#-------------------------------------------------------------------------------
@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/tickettype/journettype', methods=['GET', 'POST'])
@app.route('/settings/tickettype/journettype/<int:journey_type_id>', methods=['GET', 'POST'])
def JourneyType_Index(journey_type_id=None):
    menu = 'settings'
    submenu = 'tickettype'

    if journey_type_id:
        journey_type = JourneyTypeModel.get_by_id(journey_type_id)
        form = FormJourneyType(obj=journey_type)
    else:
        journey_type = JourneyTypeModel()
        form = FormJourneyType(request.form)

    if form.validate_on_submit():
        journey_exist = JourneyTypeModel.query(JourneyTypeModel.name == form.name.data).count()

        if journey_exist >= 1:
            form.name.errors.append('This name '+str(form.name.data)+' exist')
        else:
            journey_type.name = form.name.data
            journey_type.put()
            if journey_type_id:
                flash(u"Journey Updated!", "success")
            else:
                flash(u"Journey Saved!", "success")

            return redirect(url_for('JourneyType_Index'))

    journey_type_list = JourneyTypeModel.query()

    return render_template("/tickettype/index-journey-type.html", **locals())

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/JourneyType_Default/<int:journey_type_id>')
def JourneyType_Default(journey_type_id):

    journey_type = JourneyTypeModel.get_by_id(journey_type_id)

    if not journey_type.default:
        journey_default_exist = JourneyTypeModel.query(
            JourneyTypeModel.default == True,
            JourneyTypeModel.key == journey_type.key
        ).count()
        if journey_default_exist >= 1:
            flash(u"you can not define two type of ticket as a criterion 'is default'!", "danger")
        else:
            journey_type.default = True
    else:
        journey_type.default = False
    journey_type.put()

    flash(u"Journey Updated!", "success")
    return redirect(url_for('JourneyType_Index'))

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/JourneyType_Delete/<int:journey_type_id>')
def JourneyType_Delete(journey_type_id):

    journey_delete = JourneyTypeModel.get_by_id(journey_type_id)

    journey_ticket_type_exist = TicketTypeModel.query(
        TicketTypeModel.journey_name == journey_delete.key
    ).count()

    from ..ticket.models_ticket import TicketModel
    journey_ticket_exist = TicketModel.query(
        TicketModel.journey_name == journey_delete.key
    ).count()

    if journey_ticket_exist >= 1 or journey_ticket_type_exist >= 1:
        flash(u"You can't delete this journey :"+journey_delete.name+u" it's used by ticket type and some ticket!!", "danger")
        return redirect(url_for('JourneyType_Index'))

    journey_delete.key.delete()
    flash(u"Journey Type has been deleted successfully!", "success")
    return redirect(url_for('JourneyType_Index'))


#-------------------------------------------------------------------------------
#
# Ticket Type Name Controller
#
#-------------------------------------------------------------------------------
@login_required
@roles_required(('admin', 'super_admin'))
@app.route("/settings/tickettype/tickettypename", methods=['GET', 'POST'])
@app.route('/settings/tickettype/tickettypename/<int:ticket_type_name_id>', methods=['GET', 'POST'])
def Ticket_Type_Name_Index(ticket_type_name_id=None):
    menu = 'settings'
    submenu = 'tickettype'

    if ticket_type_name_id:
        tickets = TicketTypeNameModel.get_by_id(ticket_type_name_id)
        form = FormTicketTypeName(obj=tickets)
    else:
        tickets = TicketTypeNameModel()
        form = FormTicketTypeName()


    if form.validate_on_submit():
        ticket_exist = TicketTypeNameModel.query(TicketTypeNameModel.name == form.name.data).count()

        if ticket_exist >= 1:
            form.name.errors.append('This name '+str(form.name.data)+' exist')
        else:
            tickets.name = form.name.data
            tickets.put()
            if ticket_type_name_id:
                flash(u"Ticket Type Name Updated!", "success")
            else:
                flash(u"Ticket Type Name Saved!", "success")
            return redirect(url_for('Ticket_Type_Name_Index'))


    ticket_list = TicketTypeNameModel.query()

    return render_template("/tickettype/index-ticket-type-name.html", **locals())

@login_required
@roles_required(('admin', 'super_admin'))
@app.route("/Ticket_Type_Name_Child/<int:ticket_type_name_id>", methods=["GET", "POST"])
def Ticket_Type_Name_Child(ticket_type_name_id):
    ticket = TicketTypeNameModel.get_by_id(ticket_type_name_id)

    if not ticket.is_child:
        is_child_exist = TicketTypeNameModel.query(
            TicketTypeNameModel.is_child == True,
            TicketTypeNameModel.key != ticket.key
        ).count()
        if is_child_exist >= 1:
            flash(u"you can not define two type of ticket as a criterion 'is child'!", "danger")
        else:
            ticket.is_child = True
    else:
        ticket.is_child = False
    ticket.put()

    return redirect(url_for("Ticket_Type_Name_Index"))


@login_required
@roles_required(('admin', 'super_admin'))
@app.route("/Ticket_Type_Name_Default/<int:ticket_type_name_id>")
def Ticket_Type_Name_Default(ticket_type_name_id):

    ticket = TicketTypeNameModel.get_by_id(ticket_type_name_id)

    if not ticket.default:
        is_default_exist = TicketTypeNameModel.query(
            TicketTypeNameModel.default == True,
            TicketTypeNameModel.key != ticket.key
        ).count()
        if is_default_exist >= 1:
            flash(u"you can not define two type of ticket as a criterion 'is default'!", "danger")
        else:
            ticket.default = True
    else:
        ticket.default = False

    ticket.put()
    flash(u"Ticket Type Name Updated!", "success")
    return redirect(url_for("Ticket_Type_Name_Index"))

@login_required
@roles_required(('admin', 'super_admin'))
@app.route("/Ticket_Type_Name_Special/<int:ticket_type_name_id>")
def Ticket_Type_Name_Special(ticket_type_name_id):

    ticket = TicketTypeNameModel.get_by_id(ticket_type_name_id)

    if ticket.special == False:
        ticket.special = True
    else:
        ticket.special = False
    ticket.put()

    flash(u"Ticket Type Name Updated!", "success")
    return redirect(url_for("Ticket_Type_Name_Index"))

@login_required
@roles_required(('admin', 'super_admin'))
@app.route("/Delete_Ticket_Type_Name/<int:ticket_type_name_id>")
def Delete_Ticket_Type_Name(ticket_type_name_id):
    delete_ticket = TicketTypeNameModel.get_by_id(ticket_type_name_id)
    # On verifiera si le TicketTypeName est utilisee

    ticket_type_name_ticket_type_exist = TicketTypeModel.query(
        TicketTypeModel.type_name == delete_ticket.key
    ).count()

    from ..ticket.models_ticket import TicketModel
    ticket_type_name_ticket_exist = TicketModel.query(
        TicketModel.type_name == delete_ticket.key
    ).count()

    if ticket_type_name_ticket_exist >= 1 or ticket_type_name_ticket_type_exist >= 1:
        flash(u"You can't delete this ticket type name :"+delete_ticket.name+u" it's used by ticket type and some ticket!!", "danger")
        return redirect(url_for("Ticket_Type_Name_Index"))

    # Si oui il ne sera pas supprime
    delete_ticket.key.delete()
    flash(u"Ticket Type name has been deleted successfully!", "success")
    return redirect(url_for("Ticket_Type_Name_Index"))
