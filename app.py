import os
import logging
from flask import Flask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "triton-concrete-coating-secret-key-2025")

# Print startup message
print("\n🏗️ Spankks Construction")
print("🏝️ Professional construction and home improvements across O'ahu")
print("📞 Contact: (808) 778-9132")
print("🌐 Licensed & Insured")
print("\nBuilt with ❤️ for the local community\n")

# Register template helpers
try:
    from template_helpers import register_template_helpers
    register_template_helpers(app)
    logging.info("Template helpers registered successfully")
except ImportError as e:
    logging.warning(f"Could not register template helpers: {e}")

# Import routes after app creation to avoid circular imports
try:
    from routes import *
    # Only log to file, not to console on public pages
    logging.info("App initialized successfully")
except ImportError as e:
    logging.error(f"Route import error: {e}")
    logging.error("App initialization failed - check dependencies")