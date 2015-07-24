__author__ = 'Vercossa'

from ...modules import *

def not_found(error=None, message=None):

    if not message:
        message = 'Not Found: ' + request.url
    if not error:
        error = 404

    messages = {
            'status': error,
            'message': message,
    }
    resp = jsonify(messages)
    return resp