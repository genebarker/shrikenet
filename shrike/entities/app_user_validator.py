from .app_user import AppUser
from .field_validator import FieldValidator


class AppUserValidator:

    @staticmethod
    def validate_fields(app_user: AppUser):
        FieldValidator.validate_id(app_user.id)
        FieldValidator.validate_username(app_user.username)
        FieldValidator.validate_name(app_user.name)
