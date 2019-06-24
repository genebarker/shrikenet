import importlib
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

from shrike.adapters.markdown_adapter import MarkdownAdapter
from shrike.entities.services import Services

def get_services():
    if 'services' not in g:
        g.services = initialize_services()

    return g.services

def initialize_services():
    storage_module = importlib.import_module(current_app.config['STORAGE_PROVIDER_MODULE'])
    storage_class = getattr(storage_module, current_app.config['STORAGE_PROVIDER_CLASS'])
    db_config = {
        'db_name': current_app.config['DB_NAME'],
        'db_user': current_app.config['DB_USER'],
        'db_password': current_app.config['DB_PASSWORD'],
    }
    storage_provider = storage_class(db_config)
    storage_provider.open()
    text_transformer = MarkdownAdapter()
    return Services(storage_provider, text_transformer)

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
