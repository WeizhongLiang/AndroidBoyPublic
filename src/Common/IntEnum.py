from enum import Enum


class IntEnum(Enum):
    def __int__(self):
        return self.value

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value
