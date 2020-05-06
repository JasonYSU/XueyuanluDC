from flask import Blueprint

api = Blueprint('population_api', __name__)

from . import views
