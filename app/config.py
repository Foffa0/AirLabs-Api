import os

class Config:
    SECRET_KEY = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'#os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

    AIR_LABS_API_KEY = os.environ.get('AIR_LABS_API_KEY')