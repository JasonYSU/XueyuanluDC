from flask import jsonify, request, current_app
from sqlalchemy.sql import func
from app import db

from app.population import api
from app.models import Population
from app.utils.response_code import RET

from datetime import datetime

