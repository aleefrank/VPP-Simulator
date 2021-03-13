from flask import Blueprint

bp = Blueprint('errors', __name__)

from WebAppOptimizer.app.errors import handlers
