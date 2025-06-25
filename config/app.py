import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Base(DeclarativeBase):
    pass

# Initialize Flask app with absolute template and static folder paths
import os
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.environ.get("SESSION_SECRET", "triton-concrete-coating-secret-key-2025")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Print startup message only for admin routes
import os
if os.environ.get('FLASK_ENV') == 'development' or '/admin' in os.environ.get('REQUEST_URI', ''):
    print("\n🏗️ Spankks Construction")
    print("🏝️ Professional construction and home improvements across O'ahu") 
    print("📞 Contact: (808) 778-9132")
    print("🌐 Licensed & Insured")
    print("\nBuilt with ❤️ for the local community\n")

# Register template helpers
try:
    from utils.template_helpers import register_template_helpers
    register_template_helpers(app)
    logging.info("Template helpers registered successfully")
except ImportError as e:
    logging.warning(f"Could not register template helpers: {e}")

# Create database tables
with app.app_context():
    # Import models to create tables
    import models.models_db  # noqa: F401
    db.create_all()

# Routes will be imported in main.py to avoid circular imports
logging.info("App initialized successfully")