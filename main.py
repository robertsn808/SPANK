
from config.app import app

# Import all routes after app initialization
try:
    import routes
    import routes_public
    import routes_admin  # Add admin routes
    print("All routes imported successfully")
except ImportError as e:
    print(f"Route import error: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
