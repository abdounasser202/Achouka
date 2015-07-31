# -*- coding: utf-8 -*-

__author__ = "Vercossa"

from api_function import *
from ..question.models_question import QuestionModel

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route("/get_question_api")
def get_question_api():
    
    get_question = QuestionModel().query()
    data = {}
    for question in get_question:
        data[question.key.id()] = question.make_to_dict()
    resp = jsonify(data)
    return resp
