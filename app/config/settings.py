import os
from typing import Dict, List

class Config:
    MODEL_NAME = "all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    MAX_DESCRIPTIONS = int(os.getenv("MAX_AUDIO_DESCRIPTIONS", "100"))
    
    DEBUG_MODE = False
    PORT = int(os.getenv("PORT", "8000"))
    
    NO_MATCH_RESPONSE = "none"
    ERROR_RESPONSE = "error"