import random
import re
import json

from flask import current_app, jsonify, request, make_response, g
from flask_httpauth import HTTPBasicAuth

from app import redis_conn
from app.models import User
from app.utils.response_code import RET,error_map
from app.utils.email import send_mail
from . import api

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):
    if request.path == '/login':
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.verify_password(password):
            return False
    else:
        user = User.verify_user_token(email_or_token)
        if not user:
            return False

    g.user = user
    return True

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)
