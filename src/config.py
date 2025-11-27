"""
Configuration module for paths and shared constants used across the project.

This file centralises:
- File system paths
- Alias dictionaries for platform and genre detection
- Shared runtime variables
"""
from pathlib import Path
from typing import Final

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# User-related local storage

# Stores the user's chosen name (string or None)
USERNAME_PATH = PROJECT_ROOT / "data" / "joblib" / "user_name.joblib"

# Stores a boolean flag indicating whether the user allowed name saving
USERNAME_DECISION_PATH = PROJECT_ROOT / "data" / "joblib" / "user_name_decision.joblib"

# Stores details about the last purchased game (title, platform, price)
PURCHASED_GAME_PATH = PROJECT_ROOT / "data" / "joblib" /  "purchased_game.joblib"

# Dataset paths
# QA dataset (CSV)
QA_PATH = PROJECT_ROOT / "data" / "QA_data" / "COMP3074-CW1-Dataset.csv"

# Games csv (CSV)
GAMES_PATH = PROJECT_ROOT / "data" / "games_data" / "games_data.csv"

# Intent definition JSON 
INTENTS_PATH  = PROJECT_ROOT / "data" / "intents" / "intents.json"

# Platform and Genre Aliases 
PLATFORM_ALIASES = {
    "PS3": ["playstation 3", "playstation3", "ps3", "ps 3"],
    "PS4": ["playstation 4", "playstation4", "ps4", "ps 4"],
    "PS5": ["playstation 5", "playstation5", "ps5", "ps 5"],
    "PC":  ["pc", "computer", "windows"],
    "X360": ["xbox 360", "xbox360", "x360", "x 360"],
    "XOne": ["xbox one", "xboxone", "xone", "x one"],
}

GENRE_ALIASES = {
    "Action": ["action", "action-adventure"],
    "Adventure": ["adventure", "story"],
    "RPG": ["rpg", "role-playing", "role playing"],
    "Shooter": ["shooter", "fps", "first person shooter"],
    "Sports": ["sports", "sport", "football", "soccer", "basketball"],
    "Racing": ["racing", "driving"],
    "Simulation": ["simulation", "simulator", "sim"],
    "Strategy": ["strategy", "tactics"],
    "Puzzle": ["puzzle", "brain", "logic"]
}

# Global runtime variable
USER_NAME: str = None


