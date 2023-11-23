from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
DB_NAME = 'database.db'
migrate = Migrate()

#creates everything needed to run a Flask application
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'pending'
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    migrate.init_app(app, db)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/') # Blueprint allows you to create modular applications, thats why we are able to divide the functions into two models
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Exercise, Log

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    create_database(app)# creates the database

    return app

def create_database(app):# a debug code to see if the database is created and checks for the existing database
    db_path = path.join(app.root_path, 'webpages', DB_NAME)
    print(f'Database path: {db_path}')
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
        print('Created Database')