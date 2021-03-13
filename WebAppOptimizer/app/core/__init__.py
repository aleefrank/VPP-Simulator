from flask import Blueprint

bp = Blueprint('core', __name__)

from WebAppOptimizer.app.core import routes
