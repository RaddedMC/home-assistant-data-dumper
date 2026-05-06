import enum
from functools import total_ordering

# Define log levels enum with comparison
@total_ordering
class LOG_LEVELS(enum.Enum):
    INSANE = 0
    NORMAL = 1
    SILENT = 2

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented