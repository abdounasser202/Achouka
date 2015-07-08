__author__ = 'wilrona'

from ...modules import *

from models_currency import CurrencyModel, EquivalenceModel
from ..ticket_type.models_ticket_type import TicketTypeModel
from ..agency.models_agency import AgencyModel

from forms_currency import FormCurrency


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@roles_required(('admin', 'super_admin'))
@app.route('/settings/currency')
@login_required
def Currency_Index():
    menu = 'settings'
    submenu = 'currency'

    currencys = CurrencyModel.query()

    return render_template('/currency/index.html', **locals())


@app.route('/settings/currency/edit', methods=['POST', 'GET'])
@app.route('/settings/currency/edit/<int:currency_id>', methods=['POST', 'GET'])
@login_required
@roles_required(('admin', 'super_admin'))
def Currency_Edit(currency_id=None):
    menu = 'settings'
    submenu = 'currency'

    from ..activity.models_activity import ActivityModel
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    if currency_id:
        # formulaire et information de la devise a editer
        currency = CurrencyModel.get_by_id(currency_id)
        form = FormCurrency(obj=currency)

        # liste des devises sauf celle en cours
        listCurrency = CurrencyModel.query(CurrencyModel.key != currency.key)

        #liste des equivalences de la devise en cours
        Equivalences = EquivalenceModel.query(EquivalenceModel.currencyRate == currency.key)

    else:
        form = FormCurrency(request.form)
        currency = CurrencyModel()

    if form.validate_on_submit():
        code_exist = CurrencyModel.query(CurrencyModel.code == form.code.data).count()

        if code_exist >= 1: # si le code existe on peut modifier la devise

            if currency.code == form.code.data:
                currency.code = form.code.data
                currency.name = form.name.data

                try:
                    devise = currency.put()

                    # enregistrement de l'activite de modification du currency
                    currency_activity_modification = ActivityModel()
                    currency_activity_modification.user_modify = current_user.key
                    currency_activity_modification.identity = devise.id()
                    currency_activity_modification.nature = 4
                    currency_activity_modification.object = "currency"
                    currency_activity_modification.time = function.datetime_convert(date_auto_nows)
                    currency_activity_modification.put()

                    flash(u' Currency Save. ', 'success')
                    return redirect(url_for('Currency_Index'))

                except CapabilityDisabledError:
                    flash(u' Error data base. ', 'danger')
                    return redirect(url_for('Currency_Edit'))
            else:
                form.code.errors.append('Other Currency use this code '+form.code.data)

        else: # Si le code n'existe pas on cree la devise correspondant a ce code si cette devise existe
            currency.code = form.code.data
            currency.name = form.name.data

            try:
                devise = currency.put()

                # enregistrement de l'activite de creation du currency
                currency_activity_creation = ActivityModel()
                currency_activity_creation.user_modify = current_user.key
                currency_activity_creation.identity = devise.id()
                currency_activity_creation.nature = 1
                currency_activity_creation.object = "currency"
                currency_activity_creation.time = function.datetime_convert(date_auto_nows)
                currency_activity_creation.put()

                flash(u' Currency Save. ', 'success')
                return redirect(url_for('Currency_Index'))

            except CapabilityDisabledError:
                flash(u' Error data base. ', 'danger')
                return redirect(url_for('Currency_Edit'))

    return render_template('/currency/edit.html', **locals())


@roles_required(('admin', 'super_admin'))
@app.route("/settings/currency/equiv", methods=["POST", "GET"])
@login_required
def Currency_Equiv():
    currency = CurrencyModel().query()
    currency_equi = CurrencyModel().query()
    for cur in currency:

        for equi in currency_equi:

            if cur.key != equi.key:
                url = "http://jsonrates.com/get/?from="+str(cur.code)+"&to="+str(equi.code)+"&apiKey=jr-084b62a28886145a8da8b93d3220794c"
                result = urlfetch.fetch(url).content
                rate = json.loads(result) # rate est un objet de type <dict>
                error = False

                for k,v in rate.items():

                    if k == "error":
                        error = True

                    elif k == "rate":
                        valeur = v

                if error:
                    flash(u'Conversion between ' + cur.code + u' - ' + equi.code + u'does not exist!', 'danger')

                else:
                    equi_exist = EquivalenceModel().query(
                        EquivalenceModel.currencyRate == cur.key,
                        EquivalenceModel.currencyEqui == equi.key).count()

                    if equi_exist >= 1: # si l'equivalence existe on peut la mettre a jour
                        equi_update = EquivalenceModel().query(
                            EquivalenceModel.currencyRate == cur.key,
                            EquivalenceModel.currencyEqui == equi.key).get()
                        equi_update.value = float(valeur)
                        converter = equi_update.put()


                    else: # si l'equivalence n'existe pas on cree une nouvelle equivalence
                        equivalence = EquivalenceModel()
                        equivalence.currencyRate = cur.key
                        equivalence.value = float(valeur)
                        equivalence.currencyEqui = equi.key
                        recording = equivalence.put()

    flash('Conversion successfully completed', 'success')
    return redirect(url_for("Currency_Index"))


@app.route('/settings/currency/delete/', methods=['GET', 'POST'])
@app.route('/settings/currency/delete/<int:currency_id>', methods=['GET', 'POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def Currency_Delete(currency_id=None):

    from ..ticket.models_ticket import TicketModel, UserModel
    from ..transaction.models_transaction import TransactionModel

    delete_currency = CurrencyModel.get_by_id(int(currency_id))

    equi_currency_exist = EquivalenceModel.query(
        EquivalenceModel.currencyRate == delete_currency.key
    ).count()

    ticket_type_currency_exist = TicketTypeModel.query(
        TicketTypeModel.currency == delete_currency.key
    ).count()

    ticket_currency_exist = TicketModel.query(
        TicketModel.sellpriceAgCurrency == delete_currency.key
    ).count()

    agency_currency_exist = AgencyModel.query(
        AgencyModel.currency == delete_currency.key
    ).count()

    transaction_currency_exist = TransactionModel.query(
        TransactionModel.currency==delete_currency.key
    ).count()

    user_currency_admin = UserModel.query(
        UserModel.currency == delete_currency.key
    ).count()

    if equi_currency_exist >= 1 or ticket_type_currency_exist >= 1 or ticket_currency_exist >= 1 or agency_currency_exist >= 1 or transaction_currency_exist >= 1 or user_currency_admin >=  1:
        flash(u'You can\'t delete this currency', 'danger')
        return redirect(url_for("Currency_Index"))

    else:
        # enregistrement de l'activite de suppression du currency
        currency_activity_deletion = ActivityModel()
        currency_activity_deletion.user_modify = current_user.key
        currency_activity_deletion.identity = delete_currency
        currency_activity_deletion.nature = 3
        currency_activity_deletion.object = "currency"
        currency_activity_deletion.time = function.datetime_convert(date_auto_nows)
        currency_activity_deletion.put()

        delete_currency.key.delete()
        flash(u'Currency has been deleted successfully', 'success')
        return redirect(url_for("Currency_Index"))


@app.route('/delete_currency_equivalence/<int:equivalence_id>', methods=['POST'])
@login_required
@roles_required(('admin', 'super_admin'))
def delete_currency_equivalence(equivalence_id):

    Equivalence = EquivalenceModel.get_by_id(equivalence_id)

    Equivalence.key.delete()
    flash('Equivalence has been deleted successfully', 'success')
    return redirect(url_for('Currency_Index'))
