from flask import Blueprint

bp = Blueprint('auth', __name__)

from WebAppOptimizer.app.auth import routes
