import os
import logging
from flask import Flask
from flask_session import Session

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)

# Configure session
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-triton-2025")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

# Initialize session
Session(app)

# Import routes after app creation to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
