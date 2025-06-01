from enum import Enum
from typing import Literal

class MatchingMethod(str, Enum):
    """Enum for different matching methods"""
    INDIVIDUAL = "individual"
    COMBINED = "combined"
    HYBRID = "hybrid"
    MAX = "max"

class ResponseStatus(str, Enum):
    """Enum for response status"""
    SUCCESS = "success"
    NO_MATCH = "no_match"
    ERROR = "error"

MatchingMethodType = Literal["individual", "combined", "hybrid", "max"]
ConfidenceScore = float  #0.0 to 1.0
AudioFileName = str