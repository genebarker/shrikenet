import importlib

import click
from flask import current_app, g
from flask.cli import with_appcontext

from shrikenet.adapters.markdown import Markdown
from shrikenet.entities.services import Services


def get_services():
    if 'services' not in g:
        g.services = initialize_services()

    return g.services


def initialize_services():
    services = Services()
    services.storage_provider = get_storage_provider()
    services.text_transformer = get_text_transformer()
    services.crypto_provider = get_crypto_provider()
    return services


def get_storage_provider():
    storage_class = get_class_from_app_config('STORAGE_PROVIDER_MODULE',
                                              'STORAGE_PROVIDER_CLASS')
    db_config = {
        'db_name': current_app.config['DB_NAME'],
        'db_user': current_app.config['DB_USER'],
        'db_password': current_app.config['DB_PASSWORD'],
        'db_port': current_app.config['DB_PORT'],
    }
    storage_provider = storage_class(db_config)
    storage_provider.open()
    return storage_provider


def get_class_from_app_config(module_name, class_name):
    module = importlib.import_module(current_app.config[module_name])
    class_ = getattr(module, current_app.config[class_name])
    return class_


def get_text_transformer():
    transformer_class = get_class_from_app_config('TEXT_TRANSFORMER_MODULE',
                                                  'TEXT_TRANSFORMER_CLASS')
    text_transformer = transformer_class()
    return text_transformer


def get_crypto_provider():
    crypto_class = get_class_from_app_config('CRYPTO_PROVIDER_MODULE',
                                             'CRYPTO_PROVIDER_CLASS')
    crypto_provider = crypto_class()
    return crypto_provider


def close_services(e=None):
    services = g.pop('services', None)

    if services is not None:
        services.storage_provider.close()


def init_db():
    services = get_services()
    services.storage_provider.build_database_schema()
    services.storage_provider.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_services)
    app.cli.add_command(init_db_command)
