from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from app.config import Config
import datetime
from flask_paranoid import Paranoid

import firebase_admin
from firebase_admin import credentials

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'danger'

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    paranoid = Paranoid(app)
    paranoid.redirect_view = 'users.login'
    login_manager.session_protection = None
    # with app.app_context():
    #     db.create_all()
    #     db.drop_all()
    from app.tasks.task import startSchedule
    @app.before_first_request
    def before__request():
        startSchedule()

    #with app.app_context():
    #    from app.models import User
    #    from app.models import init_db
    #    init_db()
    #    if User.query.filter_by(email=app.config['ADMIN_EMAIL']).first() == None:
    #        hashed_password = bcrypt.generate_password_hash(app.config['ADMIN_PASSWORD']).decode('utf-8')
    #        admin = User(firstName='Admin', lastName='User', email=app.config['ADMIN_EMAIL'], password=hashed_password, admin=True, registered_on=datetime.date.today(), confirmed=True, confirmed_on=datetime.date.today())
    #        db.session.add(admin)
    #        db.session.commit()

    # initialize FirebaseCloud Messaging
    cred = credentials.Certificate(app.config['GOOGLE_APPLICATION_CREDENTIALS'])
    firebase_admin.initialize_app(cred)

    from app.main.routes import main
    from app.notification.routes import notification
    from app.users.routes import users
    from app.errors.handlers import errors
    from app.users.utils import email
    app.register_blueprint(main)
    app.register_blueprint(notification)
    app.register_blueprint(users)
    app.register_blueprint(errors)
    app.register_blueprint(email)
    return app