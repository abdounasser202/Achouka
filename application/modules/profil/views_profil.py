__author__ = 'wilrona'

from ...modules import *

from models_profil import ProfilModel
from forms_profil import FormProfil

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


@app.route('/settings/profil')
def Profil_Index():
    menu = 'settings'
    submenu = 'profil'

    profil_lists = ProfilModel.query()
    return render_template('/profil/index.html', **locals())



@app.route('/settings/profil/view/<int:profil_id>', methods=['GET', 'POST'])
def Profil_View(profil_id):
    menu = 'settings'
    submenu = 'profil'
    from ..user.models_user import ProfilRoleModel

    profil = ProfilModel.get_by_id(profil_id)
    form = FormProfil(obj=profil)
    profilRole = ProfilRoleModel.query(ProfilRoleModel.profil_id == profil.key)

    view = True

    return render_template('/profil/edit.html', **locals())



@app.route('/settings/profil/edit', methods=['GET', 'POST'])
@app.route('/settings/profil/edit/<int:profil_id>', methods=['GET', 'POST'])
def Profil_Edit(profil_id=None):
    menu = 'settings'
    submenu = 'profil'
    from ..user.models_user import ProfilRoleModel

    if profil_id:
        profil = ProfilModel.get_by_id(profil_id)
        form = FormProfil(obj=profil)
        profilRole = ProfilRoleModel.query(ProfilRoleModel.profil_id == profil.key)
    else:
        profil = ProfilModel()
        form = FormProfil(request.form)

    if form.validate_on_submit():
        profil_exist = ProfilModel.query(ProfilModel.name == form.name.data).count()
        if profil_exist >= 1:
            if profil.name == form.name.data:

                profil.name = form.name.data
                if form.standard.data:
                    if int(form.standard.data) == 2:
                        profil.standard = False
                    else:
                        profil.standard = True
                else:
                    profil.standard = False

                try:
                    profil.put()
                    flash(u' Profil Save. '+str(form.standard.data), 'success')
                    return redirect(url_for('Profil_Index'))
                except CapabilityDisabledError:
                    flash(u' Error data base. ', 'danger')
                    return redirect(url_for('Profil_Index'))
            else:
                form.name.errors.append('This name profil '+ str(form.name.data) + 'is already exist')
        else:
            profil.name = form.name.data

            if form.standard.data:
                if int(form.standard.data) == 2:
                    profil.standard = False
                else:
                    profil.standard = True
            else:
                profil.standard = False

            try:
                profil.put()
                flash(u' Profil Save. ', 'success')
                return redirect(url_for('Profil_Index'))
            except CapabilityDisabledError:
                flash(u' Error data base. ', 'danger')
                return redirect(url_for('Agency_Index'))

    return render_template('/profil/edit.html', **locals())



@app.route('/AddRoleProfil/<int:profil_id>', methods=['GET', 'POST'])
def Add_Role_Profil(profil_id):
    from ..user.models_user import ProfilRoleModel, RoleModel

    profil_update = ProfilModel.get_by_id(profil_id)

    profilrole = ProfilRoleModel.query(ProfilRoleModel.profil_id == profil_update.key).fetch()

    if current_user.has_roles('super_admin'):
        roles = RoleModel.query()
    else:
        roles = RoleModel.query(
            RoleModel.visible == True
        )

    if request.method == "POST":
        post_role = request.form.getlist('roles')
        nombre = 0
        for role in post_role:
            slc_role = RoleModel.get_by_id(int(role))
            if slc_role:
                profilRole = ProfilRoleModel()
                profilRole.role_id = slc_role.key
                profilRole.profil_id = profil_update.key
                profilRole.put()

            nombre += 1

        if nombre > 0:
            flash('you have add '+str(nombre)+' Role for this profil', 'success')
        else:
            flash('you have add '+str(nombre)+' Role for this profil', 'danger')
        return redirect(url_for('Profil_Edit', profil_id=profil_id))

    return render_template('/profil/list_role.html', **locals())


@roles_required(('super_admin', 'admin'))
@app.route('/DeleteRoleProfil/<int:profilrole_id>/<int:profil_id>')
def Delete_Role_Profil(profilrole_id, profil_id):
    from ..user.models_user import ProfilRoleModel

    profilrole = ProfilRoleModel.get_by_id(profilrole_id)
    profil = ProfilModel.get_by_id(profil_id)

    if profilrole:
        profilrole.key.delete()
        flash('Role Deleted', 'success')
    else:
        flash('Data not found', 'danger')

    return redirect(url_for('Profil_Edit', profil_id=profil.key.id()))


@app.route('/settings/profil/delete', methods=['GET', 'POST'])
@app.route('/settings/profil/delete/<int:profil_id>', methods=['GET', 'POST'])
def Profil_Delete(profil_id=None):
    from ..user.models_user import ProfilRoleModel

    """ Suppression des profils """
    menu = 'settings'
    submenu = 'profil'

    delete_profil = ProfilModel.get_by_id(profil_id)

    role_profil_exist = ProfilRoleModel.query(ProfilRoleModel.profil_id==delete_profil.key).count()

    if role_profil_exist  >= 1:
        flash(u'You can\'t delete this profil', 'danger')
        return redirect(url_for("Profil_Index"))
    else:
        delete_profil.key.delete()
        flash(u'Profil has been deleted successfully', 'success')
        return  redirect(url_for("Profil_Index"))

    return render_template('/profil/index.html', **locals())