from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flasgger import Swagger
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
swagger = Swagger()

def create_app(config_name):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    # This line is critical. It tells your backend to accept API requests
    # from your frontend server.
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}) 

    # Swagger configuration
    app.config['SWAGGER'] = {
        'title': 'Justice Link Kenya API',
        'uiversion': 3,
        "specs_route": "/apidocs/"
    }
    swagger.init_app(app)

    # Import and register blueprints
    from .routes import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

    return app