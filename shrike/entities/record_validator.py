class RecordValidator:

    @staticmethod
    def validate_fields(the_object):
        raise NotImplementedError

    @staticmethod
    def validate_references(the_object, storage_provider):
        raise NotImplementedError
