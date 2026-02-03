import os
from datetime import timedelta

class Config:
    # Utiliser variable d'environnement ou générer une clé sécurisée
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    TESTING = False
    # Configuration session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in dev

class ProdConfig(Config):
    DEBUG = False
    TESTING = False

class TestConfig(Config):
    TESTING = True
    DEBUG = False
