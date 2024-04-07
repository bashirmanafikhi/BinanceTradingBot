# config.py
import os

class Config:
    ENVIRONMENT = 'development'
    SERVER_URL = 'http://localhost:5000/'
    SECRET_KEY = 'secret-key-goes-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'

class ProductionConfig(Config):
    ENVIRONMENT = 'production'
    SERVER_URL = 'https://www.langora.online/'

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return ProductionConfig if env == 'production' else Config