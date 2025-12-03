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
    # PlayStation Family
    "PS":      ["ps", "playstation"],
    "PS2":     ["ps2", "playstation 2", "ps 2"],
    "PS3":     ["ps3", "playstation 3", "ps 3"],
    "PS4":     ["ps4", "playstation 4", "ps 4"],
    "PS5":     ["ps5", "playstation 5", "ps 5"],
    "PSP":     ["psp", "playstation portable"],
    "PSV":     ["vita", "psvita", "ps vita", "playstation vita"],
    
    # Xbox Family
    "XBOX":    ["xbox"],
    "X360":    ["xbox 360", "x360", "x 360"],
    "XOne":    ["xbox one", "xone", "x one"],
    "XS":      ["xbox series x", "xbox series s", "series x", "series s", "xsx", "xss"],

    # Nintendo Family
    "NES":     ["nes", "nintendo entertainment system"],
    "SNES":    ["snes", "super nintendo"],
    "N64":     ["n64", "nintendo 64"],
    "GC":      ["gamecube", "gc"],
    "Wii":     ["wii"],
    "WiiU":    ["wiiu", "wii u"],
    "GB":      ["gameboy", "game boy"],
    "GBC":     ["gameboy color", "game boy color"],
    "GBA":     ["gba", "gameboy advance", "game boy advance"],
    "DS":      ["ds", "nintendo ds"],
    "DSiW":    ["dsi", "dsiware"],
    "3DS":     ["3ds", "nintendo 3ds"],
    "NS":      ["switch", "nintendo switch"],

    # Sega
    "GEN":     ["genesis", "mega drive"],
    "DC":      ["dreamcast", "dc"],
    
    # PC / Computer
    "PC":      ["pc", "computer", "windows"],
    "Linux":   ["linux"],

    # Handheld / Mobile / Special Platforms
    "NGage":   ["ngage", "n-gage"],
    "AJ":      ["aj"],
    "All":     ["all platforms", "multi platform"]
}

GENRE_ALIASES = {
    "Action":          ["action", "action-adventure", "hack and slash"],
    "Adventure":       ["adventure", "story", "narrative"],
    "Arcade":          ["arcade"],
    "Board Game":      ["board", "board game"],
    "Education":       ["educational", "learning"],
    "Fighting":        ["fighting", "fighter", "beat 'em up"],
    "MMO":             ["mmo", "massively multiplayer"],
    "Misc":            ["misc", "other", "various"],
    "Music":           ["music", "rhythm"],
    "Party":           ["party", "mini games"],
    "Platform":        ["platformer", "platform"],
    "Puzzle":          ["puzzle", "brain", "logic"],
    "Racing":          ["racing", "driving", "car game"],
    "Role-Playing":    ["rpg", "role-playing", "role playing", "jrpg"],
    "Sandbox":         ["sandbox", "open world"],
    "Shooter":         ["shooter", "fps", "tps", "first person shooter", "third person shooter"],
    "Simulation":      ["simulation", "sim", "simulator"],
    "Sports":          ["sports", "sport", "football", "soccer", "basketball", "tennis"],
    "Strategy":        ["strategy", "tactics", "rts", "turn-based", "turn based"],
    "Visual Novel":    ["visual novel", "vn", "story game"],
}



