import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask

logger = logging.getLogger(__name__)

__version__ = "1.0.0-SNAPSHOT"
DEV_SECRET_KEY = "server-dev"
DEV_DATABASE = "server-dev.db"


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=DEV_SECRET_KEY,
        TOKEN_LIFESPAN_DAYS=30,
        STORAGE_PROVIDER_MODULE="shrikenet.adapters.sqlite",
        STORAGE_PROVIDER_CLASS="SQLite",
        STORAGE_PROVIDER_DB=DEV_DATABASE,
        TEXT_TRANSFORMER_MODULE="shrikenet.adapters.markdown",
        TEXT_TRANSFORMER_CLASS="Markdown",
        CRYPTO_PROVIDER_MODULE="shrikenet.adapters.werkzeug",
        CRYPTO_PROVIDER_CLASS="Werkzeug",
        LOGGING_FORMAT="%(asctime)s %(levelname)s %(name)s -> %(message)s",
        LOGGING_DATE_FORMAT="%Y-%m-%d %H:%M:%S",
        LOGGING_LEVEL="DEBUG",
        LOGGING_FILE=None,
        LOGGING_FILE_MAX_BYTES=102400,
        LOGGING_FILE_BACKUP_COUNT=5,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # setup logging
    logging_level = app.config["LOGGING_LEVEL"]
    level_number = logging.getLevelName(logging_level)
    logging.basicConfig(
        level=level_number,
        format=app.config["LOGGING_FORMAT"],
        datefmt=app.config["LOGGING_DATE_FORMAT"],
    )
    logging_file = app.config["LOGGING_FILE"]
    if logging_file is not None:
        handler = RotatingFileHandler(
            filename=app.config["LOGGING_FILE"],
            maxBytes=app.config["LOGGING_FILE_MAX_BYTES"],
            backupCount=app.config["LOGGING_FILE_BACKUP_COUNT"],
        )
        handler.setLevel(level_number)
        formatter = logging.Formatter(
            fmt=app.config["LOGGING_FORMAT"],
            datefmt=app.config["LOGGING_DATE_FORMAT"],
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.info(
        f"Logger initialized (level={logging_level}, "
        f"level_number={level_number}, "
        f"file={logging_file})."
    )

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import blog

    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    from shrikenet.api import hello_json, token_authority

    app.register_blueprint(hello_json.bp)
    app.register_blueprint(token_authority.bp)

    return app
