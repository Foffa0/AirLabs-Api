import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

    AIR_LABS_API_KEY = os.environ.get('AIR_LABS_API_KEY')

    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    OAUTH2_TOKEN = os.environ.get('OAUTH2_TOKEN')

    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')

    AEROAPI_KEY = os.environ.get('AEROAPI_KEY')