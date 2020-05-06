from flask import Blueprint

api = Blueprint('community', __name__)

from . import views
