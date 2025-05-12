#!/usr/bin/env python3
"""
Utility functions for the CloneIA project.
"""
import os
import json
import platform
import subprocess
import logging
from typing import Dict, Optional, Any, List, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.getcwd(), 'cloneia.log'))
    ]
)
logger = logging.getLogger('cloneia')

# Project paths
PROJECT_ROOT = os.getcwd()
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
REFERENCE_DIR = os.path.join(PROJECT_ROOT, "reference")
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "resources")

# Ensure directories exist
for directory in [CONFIG_DIR, OUTPUT_DIR, REFERENCE_DIR, RESOURCES_DIR]:
    os.makedirs(directory, exist_ok=True)

# Default voice settings
DEFAULT_VOICE_SETTINGS = {
    "stability": 0.15,          # Slightly increased for better flow (was 0.05)
    "similarity_boost": 0.65,   # Reduced further for more natural speech and better flow (was 0.80)
    "style": 0.85,              # Slightly reduced to improve fluidity (was 1.0)
    "use_speaker_boost": True,  # Improve audio quality
    "model_id": "eleven_multilingual_v2"  # Advanced multilingual model for better accent
}

# Video constants
AVATAR_ID = "01cbe2535df5453a97f4a872ea532b33"
FOLDER_NAME = "augment"
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# Colors
BG_COLOR = (25, 25, 25)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (0, 123, 255)

def load_api_key(key_name: str = "ELEVENLABS_API_KEY") -> Optional[str]:
    """
    Load an API key from environment or .env file.

    Args:
        key_name: Name of the environment variable containing the API key

    Returns:
        Optional[str]: The API key or None if not found
    """
    # Try to get from environment
    api_key = os.getenv(key_name)

    if not api_key:
        # Try to load directly from .env file
        env_path = os.path.join(PROJECT_ROOT, ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith(f"{key_name}="):
                            api_key = line.strip().split("=")[1].strip('"').strip("'")
                            break
            except Exception as e:
                logger.error(f"Error reading .env file: {e}")

    if not api_key:
        logger.warning(f"{key_name} not found")
    else:
        logger.info(f"{key_name} found: {api_key[:4]}...{api_key[-4:]}")

    return api_key

def load_elevenlabs_api_key() -> Optional[str]:
    """
    Load the ElevenLabs API key from environment or .env file.

    Returns:
        Optional[str]: The API key or None if not found
    """
    return load_api_key("ELEVENLABS_API_KEY")

def load_heygen_api_key() -> Optional[str]:
    """
    Load the HeyGen API key from environment or .env file.

    Returns:
        Optional[str]: The API key or None if not found
    """
    return load_api_key("HEYGEN_API_KEY")

def load_voice_config(profile_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Load voice configuration from file.

    Args:
        profile_name: Name of the voice profile to load

    Returns:
        Optional[Dict[str, Any]]: Voice configuration or None if not found
    """
    # Determine the configuration file path
    if profile_name:
        if profile_name.lower() == "flukakusamplefree":
            config_path = os.path.join(CONFIG_DIR, "voice_config.json")
        elif profile_name.lower() == "flukakuia":
            config_path = os.path.join(CONFIG_DIR, "voice_config_flukakuia.json")
        elif profile_name.lower() in ["mix", "flukakumix"]:
            config_path = os.path.join(CONFIG_DIR, "voice_config_mix.json")
        else:
            config_path = os.path.join(CONFIG_DIR, f"voice_config_{profile_name}.json")
    else:
        config_path = os.path.join(CONFIG_DIR, "voice_config.json")

    # Load the configuration
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"Loaded voice configuration from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading voice configuration: {e}")
    else:
        logger.warning(f"Voice configuration file not found: {config_path}")

    return None

def save_voice_config(config: Dict[str, Any], profile_name: Optional[str] = None) -> bool:
    """
    Save voice configuration to file.

    Args:
        config: Voice configuration to save
        profile_name: Name of the voice profile to save

    Returns:
        bool: True if successful, False otherwise
    """
    # Determine the configuration file path
    if profile_name:
        if profile_name.lower() in ["mix", "flukakumix"]:
            config_path = os.path.join(CONFIG_DIR, "voice_config_mix.json")
        else:
            config_path = os.path.join(CONFIG_DIR, f"voice_config_{profile_name}.json")
    else:
        config_path = os.path.join(CONFIG_DIR, "voice_config.json")

    # Save the configuration
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved voice configuration to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving voice configuration: {e}")
        return False

def open_audio_file(file_path: str) -> bool:
    """
    Open an audio file with the system's default player.

    Args:
        file_path: Path to the audio file

    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"Audio file not found: {file_path}")
        return False

    try:
        system = platform.system()

        if system == "Darwin":  # macOS
            subprocess.call(["open", file_path])
        elif system == "Windows":
            subprocess.call(["start", file_path], shell=True)
        else:  # Linux and others
            subprocess.call(["xdg-open", file_path])

        logger.info(f"Opened audio file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error opening audio file: {e}")
        return False

def optimize_text(text: str) -> str:
    """
    Optimize text for natural speech.

    This function applies various optimizations to make the text sound more natural
    when converted to speech, including:
    - Replacing the introduction for maximum energy
    - Removing excessive punctuation that causes pauses
    - Replacing terms for better pronunciation
    - Using uppercase for emphasis on keywords

    Args:
        text: Original text

    Returns:
        str: Optimized text
    """
    if not text:
        return text

    # Replace introduction for maximum energy
    if text.lower().startswith("e aí cambada"):
        text = "EAÍCAMBADA" + text[len("e aí cambada"):]
    elif text.lower().startswith("fala cambada"):
        text = "FALACAMBADA" + text[len("fala cambada"):]

    # Remove excessive punctuation that causes pauses
    for char in [',', '.', '!', '?', '...', ';', ':']:
        text = text.replace(char, '')

    # Replace terms for better pronunciation
    replacements = {
        "Bitcoin": "Bitcoim",
        "Ethereum": "Etherium",
        "Cardano": "Cardâno",
        "Solana": "Solâna",
        "Polkadot": "Polcadot",
        "Binance": "Bináns",
        "Coinbase": "Cóinbeis",
        "NFT": "ÊnÊfeTê",
        "DeFi": "DêFai",
        "staking": "stêiking",
        "blockchain": "blókcheim",
        "wallet": "wólet",
        "token": "tôken",
        "altcoin": "ôltcoin",
        "mining": "máining",
        "miner": "máiner"
    }

    for original, replacement in replacements.items():
        text = text.replace(original, replacement)

    # Use uppercase for emphasis on keywords
    emphasis_words = [
        "bombando", "muito", "super", "mega", "alta", "subindo",
        "disparou", "explodiu", "recorde", "máxima", "forte",
        "incrível", "enorme", "gigante", "absurdo", "impressionante",
        "surpreendente", "extraordinário", "fenomenal", "espetacular"
    ]

    for word in emphasis_words:
        if word in text.lower():
            text = text.replace(word, word.upper())
            text = text.replace(word.capitalize(), word.upper())

    logger.debug(f"Optimized text: {text[:50]}...")
    return text

def get_available_profiles() -> List[Dict[str, str]]:
    """
    Get a list of available voice profiles.

    Returns:
        List[Dict[str, str]]: List of profile information
    """
    profiles = []

    for filename in os.listdir(CONFIG_DIR):
        if filename.startswith("voice_config") and filename.endswith(".json"):
            try:
                config_path = os.path.join(CONFIG_DIR, filename)
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                profile_name = filename.replace("voice_config_", "").replace(".json", "")
                if profile_name == "voice_config":
                    profile_name = "default"

                profiles.append({
                    "name": profile_name,
                    "file": filename,
                    "voice_name": config.get("voice_name", "Unknown"),
                    "voice_id": config.get("voice_id", "Unknown")
                })
            except Exception as e:
                logger.error(f"Error loading profile {filename}: {e}")

    return profiles

def ensure_directory(path: str) -> bool:
    """
    Ensure a directory exists.

    Args:
        path: Directory path

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False

def get_timestamp_filename(prefix: str, extension: str) -> str:
    """
    Generate a filename with a timestamp.

    Args:
        prefix: Filename prefix
        extension: File extension (without dot)

    Returns:
        str: Generated filename
    """
    import time
    from datetime import datetime

    timestamp = int(time.time())
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{prefix}_{date_str}.{extension}"
