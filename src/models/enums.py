from enum import Enum, auto

class Event(Enum):
    ANNOUNCEMENT = auto()
    DEVELOPMENT = auto()

class SENTIMENT(Enum):
    POSITIVE = auto()
    NEGATIVE = auto()
    NEUTRAL = auto()