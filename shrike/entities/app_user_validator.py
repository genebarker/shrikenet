from .app_user import AppUser
from .validator import Validator


class AppUserValidator:

    @staticmethod
    def validate_fields(app_user: AppUser):
        Validator.validate_username(app_user.username)
        Validator.validate_name(app_user.name)
