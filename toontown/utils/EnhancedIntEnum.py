from enum import IntEnum


class EnhancedIntEnum(IntEnum):
    """
    An abstraction over IntEnum to modify some default behaviour.

    - String values are parsed to an int when constructing
    - Only the enum name is returned when converting to a string.
    """

    @classmethod
    def _missing_(cls, value: object):
        """
        The default behaviour of IntEnum is to throw upon an invalid value being passed to the ctor.
        However, if the input value is a string we can try again if it converts to an int.
        If that fails or another type is provided, None is returned.
        """
        if not isinstance(value, str):
            return None

        try:
            return cls(int(value))
        except ValueError:
            return None

    def __str__(self) -> str:
        return self.name
