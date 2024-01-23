from typing import Dict, DefaultDict, NamedTuple, List
from enum import Enum

class StrEnum(str, Enum):
    pass

class ReviewStatus(StrEnum):
  ON_TIME = 'on_time'
  LATE = 'late'
  NO_RESPONSE = 'no_response'

class Review(NamedTuple):
  reviewer: str
  duration: str

