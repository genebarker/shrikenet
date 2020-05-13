import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        STORAGE_PROVIDER_MODULE='shrikenet.adapters.memory',
        STORAGE_PROVIDER_CLASS='Memory',
        DB_NAME='unused',
        DB_USER='unused',
        DB_PASSWORD='unused',
        TEXT_TRANSFORMER_MODULE='shrikenet.adapters.markdown',
        TEXT_TRANSFORMER_CLASS='Markdown',
        CRYPTO_PROVIDER_MODULE='shrikenet.adapters.swapcase',
        CRYPTO_PROVIDER_CLASS='Swapcase',
        LOGGING_FORMAT='%(asctime)s %(levelname)s %(name)s -> %(message)s',
        LOGGING_DATE_FORMAT='%Y-%m-%d %H:%M:%S',
        LOGGING_LEVEL='DEBUG',
        LOGGING_FILE=None,
        LOGGING_FILE_MAX_BYTES=102400,
        LOGGING_FILE_BACKUP_COUNT=5,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # setup logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOGGING_LEVEL']),
        format=app.config['LOGGING_FORMAT'],
        datefmt=app.config['LOGGING_DATE_FORMAT'],
    )
    if app.config['LOGGING_FILE'] is not None:
        handler = RotatingFileHandler(
            filename=app.config['LOGGING_FILE'],
            maxBytes=app.config['LOGGING_FILE_MAX_BYTES'],
            backupCount=app.config['LOGGING_FILE_BACKUP_COUNT'],
        )
        formatter = logging.Formatter(
            fmt=app.config['LOGGING_FORMAT'],
            datefmt=app.config['LOGGING_DATE_FORMAT'],
        )
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(handler)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
