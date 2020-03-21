class DuplicateIdentifierError(Exception):
    def __init__(self, identifier, is_overload):
        self.identifier = identifier
        self.is_overload = is_overload


class IdentifierNotFoundError(Exception):
    def __init__(self, location=None, requested_string=None):
        self.location = location
        self.requested_string = requested_string

class FunctionNotFoundError(Exception):
    pass

class TypeCheckingError(Exception):
    def __init__(self, location, error_string):
        self.location = location
        self.error_string = error_string
