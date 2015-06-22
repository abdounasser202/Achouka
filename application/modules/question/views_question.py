__author__ = 'wilrona'

from ...modules import *

from models_question import QuestionModel
from forms_question import FormQuestion

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/questions')
def Question_Index():
    menu="settings"
    submenu="question"

    items = QuestionModel.query()
    return render_template("question/index.html", **locals())

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/settings/questions/edit', methods=['GET', 'POST'])
@app.route('/settings/questions/edit/<int:question_id>', methods=['GET', 'POST'])
def Question_Edit(question_id=None):
    menu="settings"
    submenu="question"

    if question_id:
        items = QuestionModel.get_by_id(question_id)
        form = FormQuestion(obj=items)

    else:
        items = QuestionModel()
        form = FormQuestion()

    if form.validate_on_submit():
        items.question = form.question.data

        if int(form.is_obligate.data) == 1:
            items.is_obligate = True
        else:
            items.is_obligate = False

        if int(form.is_pos.data) == 1:
            items.is_pos = True
        else:
            items.is_pos = False

        items.put()

        flash(u"Question has been saved!", "success")
        return redirect(url_for("Question_Index"))
    return render_template('question/edit.html', **locals())

@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/questions/delete', methods=['GET', 'POST'])
@app.route('/questions/delete/<int:question_id>', methods=['GET', 'POST'])
def Question_Delete(question_id=None):
    items = QuestionModel.get_by_id(int(question_id))
    items.key.delete()

    flash(u"Question has been deleted!", "success")
    return redirect(url_for("Question_Index"))


@login_required
@roles_required(('admin', 'super_admin'))
@app.route('/questions/active/<int:question_id>')
def Question_Active(question_id):
    items = QuestionModel.get_by_id(int(question_id))

    if items.active:
        items.active = False
        flash(u"Question has been disabled!", "success")
    else:
        items.active = True
        flash(u"Question has been activated!", "success")
    items.put()
    return redirect(url_for("Question_Index"))

