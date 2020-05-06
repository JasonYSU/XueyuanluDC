from flask import Blueprint

api = Blueprint('user', __name__)

from . import views, verify
