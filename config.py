import os
import urlparse


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ['SECRET_KEY']

    PORT = int(os.environ.get('PORT', 5000))

    # Mail config
    MAIL_SERVER = 'smtp.mandrillapp.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    ADMIN_EMAIL = os.environ['ADMIN_EMAIL']
    DEFAULT_MAIL_SENDER = ADMIN_EMAIL

    # Database config
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ['DATABASE_URL'])

    DATABASE = {
        'engine': 'peewee.PostgresqlDatabase',
        'name': url.path[1:],
        'user': url.username,
        'password': url.password,
        'host': url.hostname,
        'port': url.port,
    }


class LocalConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass
