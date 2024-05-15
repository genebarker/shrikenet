# Flask
# SECRET_KEY = 'server-dev'
# TOKEN_LIFESPAN_DAYS = 30
SECRET_KEY = "changeThisLMAO"

# StorageProvider
# STORAGE_PROVIDER_MODULE = 'shrikenet.adapters.sqlite'
# STORAGE_PROVIDER_CLASS = 'SQLiteAdapter'
# STORAGE_PROVIDER_DB = "server-dev.db"

# TextTransformer (Markup)
# TEXT_TRANSFORMER_MODULE = 'shrikenet.adapters.markdown'
# TEXT_TRANSFORMER_CLASS = 'Markdown'

# CryptoProvider
# CRYPTO_PROVIDER_MODULE = "shrikenet.adapters.werkzeug"
# CRYPTO_PROVIDER_CLASS = "Werkzeug"
# shrikenet.adapters.swapcase / Swapcase is available
# (insecure, used to ease hand entry of app_user records for testing)

# PasswordChecker
# PASSWORD_CHECKER_MODULE = "shrikenet.adapters.zxcvbn"
# PASSWORD_CHECKER_CLASS = "zxcvbnAdapter"
# PASSWORD_MIN_STRENGTH = 2
# (0 to 4 - where 0 is too guessable and 4 is very unguessable)

# Logging
# LOGGING_FORMAT = '%(asctime)s %(levelname)s %(name)s -> %(message)s'
# LOGGING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
# LOGGING_LEVEL = 'DEBUG'
# LOGGING_FILE = None
LOGGING_FILE = "instance/server-dev.log"
# LOGGING_FILE_MAX_BYTES = 102400
# LOGGING_FILE_BACKUP_COUNT = 5
