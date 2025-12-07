from flask import Blueprint
import os
from . import models

bp = Blueprint('techhub', __name__,
               template_folder='templates',
               static_folder='static',
               url_prefix='/techhub')

def init_app(app):
    """Configure the Flask app with necessary settings"""
    # Set secret key
    app.secret_key = 'dev-secret-key-change-in-production'

    # Configure upload folder
    upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'products')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

    # Initialize database
    models.init_db()

# Import routes after blueprint creation
from . import routes
