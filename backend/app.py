from flask import Flask
from api.routes import api_bp
from core import database

app = Flask(__name__, static_folder='../frontend', static_url_path='/')

# Register the API Blueprint with the /api prefix
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    # Ensure database is initialized
    database.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
