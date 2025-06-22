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

# Import routes after app creation to avoid circular imports
try:
    from routes import *
    print("✅ App initialized successfully")
except ImportError as e:
    logging.error(f"Route import error: {e}")
    print("❌ App initialization failed - check dependencies")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)