import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this_should_be_a_secret_key'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/infraguard'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
