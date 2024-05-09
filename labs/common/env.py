import os
import random

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
GENAI_API_KEYS = os.getenv("GENAI_API_KEYS")

GENAI_API_KEYS_LIST = GENAI_API_KEYS.split(",") if GENAI_API_KEYS else []

def get_gemini_key():
    if GENAI_API_KEYS:
        # randomly select a key
        key = random.choice(GENAI_API_KEYS_LIST)
        
        if key and key != "":
            return key
        
    return GENAI_API_KEY