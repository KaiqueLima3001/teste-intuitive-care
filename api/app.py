from flask import Flask
from flask_cors import CORS
from flask.json import jsonify
from api.config import Config
from api.routes.operadoras import operadoras_bp
from api.routes.estatisticas import estatisticas_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app) 
    
    app.register_blueprint(operadoras_bp, url_prefix='/api/operadoras')
    app.register_blueprint(estatisticas_bp, url_prefix='/api/estatisticas')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
