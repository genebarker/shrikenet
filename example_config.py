# Flask
SECRET_KEY = 'poorSecret'

# StorageProvider
STORAGE_PROVIDER_MODULE = 'shrikenet.adapters.postgresql'
STORAGE_PROVIDER_CLASS = 'PostgreSQL'
DB_NAME = 'shrike20'
DB_USER = 'mrshrike'
DB_PASSWORD = 'poorPassword'
DB_PORT = 5432

# TextTransformer (Markup)
TEXT_TRANSFORMER_MODULE = 'shrikenet.adapters.markdown'
TEXT_TRANSFORMER_CLASS = 'Markdown'

# CryptoProvider
CRYPTO_PROVIDER_MODULE = 'shrikenet.adapters.werkzeug'
CRYPTO_PROVIDER_CLASS = 'Werkzeug'

# Logging
# LOGGING_FORMAT = '%(asctime)s %(levelname)s %(name)s -> %(message)s'
# LOGGING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
# LOGGING_LEVEL = 'DEBUG'
# LOGGING_FILE = None
LOGGING_FILE = 'instance/shrikenet.log'
# LOGGING_FILE_MAX_BYTES = 102400
# LOGGING_FILE_BACKUP_COUNT = 5
