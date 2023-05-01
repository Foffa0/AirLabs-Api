from itsdangerous import URLSafeTimedSerializer  as Serializer
from flask import current_app
from sqlalchemy.orm import backref
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(40), nullable=False)
    lastName = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    airports = db.relationship('Airport', backref='author', lazy=True)
    aircrafts = db.relationship('Aircraft', backref='author', lazy=True)
    devices = db.relationship('Notification', backref='user', lazy=True)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.id, salt=current_app.config['SECURITY_PASSWORD_SALT'])

    @staticmethod
    def verify_reset_token(token, expiration=18000):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
        except:
            return None
        return User.query.get(user_id)
    
    def get_activation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps(self.email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

    @staticmethod
    def verify_activation_token(token, expiration=18000):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_email = s.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
        except: 
            return None
        return user_email

    def __repr__(self):
        return f"User('{self.firstName}', '{self.lastName}', '{self.email}', '{self.admin}')"

class Airport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), nullable=False)
    icao = db.Column(db.String(4), nullable=False)
    iata = db.Column(db.String(3), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    aircrafts = db.relationship('Aircraft', backref='airport', lazy=True)

    def __repr__(self):
        return f"Airport('{self.name}', '{self.icao}', '{self.iata}')"

class Aircraft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), nullable=False)
    icao = db.Column(db.String(4), nullable=False)
    url = db.Column(db.String(150), nullable=True)
    airport_id = db.Column(db.Integer, db.ForeignKey('airport.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Aircraft('{self.name}', '{self.icao}')"
    
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Device('{self.token}', '{self.user_id}')"
    
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flightnumber = db.Column(db.String(40), nullable=True)
    aircraft_icao = db.Column(db.String(4), nullable=False)
    aircraft = db.Column(db.String(80), nullable=True)
    #time = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    arrival = db.Column(db.Boolean, nullable=False)
    airport_icao = db.Column(db.String(4), nullable=False)
    airport_name = db.Column(db.String(80), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Device('{self.flightnumber}', '{self.aircraft}'), '{self.time}'), '{self.arrival}')"

def init_db():
    db.create_all()

if __name__ == '__main__':
    init_db()