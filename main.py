from app import app
import routes  # Ensure routes are imported

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=5000, debug=True)
