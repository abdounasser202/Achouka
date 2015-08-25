__author__ = 'Vercossa'

from ...modules import *

from ..customer.models_customer import CustomerModel
from ..ticket.models_ticket import (TicketPoly, TicketModel, TicketTypeNameModel, DepartureModel,
                                    JourneyTypeModel, ClassTypeModel, AgencyModel, QuestionModel, TicketQuestion)

from ..customer.forms_customer import FormCustomerPOS


cache = Cache(app)


@app.route('/create_customer_child_ticket/<int:ticket_id>', methods=['GET', 'POST'])
@app.route('/create_customer_child_ticket/<int:ticket_id>/<int:departure_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('employee_POS', 'super_admin'))
def create_customer_child_ticket(ticket_id=None, departure_id=None):

    departure_get = DepartureModel.get_by_id(departure_id)
    age = date_age
    return render_template('/pos_child/pos_modal.html', **locals())



@app.route('/test')
def test():
    from xhtml2pdf import pisa
    from cStringIO import StringIO

    content = StringIO('<h1>html goes here</h1>')
    output = StringIO()
    pisa.log.setLevel('DEBUG')
    pdf = pisa.CreatePDF(content, output, encoding='utf-8')
    pdf_data = pdf.dest.getvalue()
    output.close()

    response = make_response(pdf_data)
    response.headers["Content-Type"] = "application/pdf"
    return response