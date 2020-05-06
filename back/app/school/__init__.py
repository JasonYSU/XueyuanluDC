from flask import Blueprint

api = Blueprint('school_api', __name__)

from . import views
