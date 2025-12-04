from typing import Optional
from joblib import dump, load
from config import (USERNAME_PATH, QA_PATH, 
                    GAMES_PATH, USERNAME_DECISION_PATH, 
                    PURCHASED_GAME_PATH)
from typing import Optional, Tuple, List
import pandas as pd
import sys


# User name storage
def save_name(name: str, path: str = USERNAME_PATH) -> None:
    """Save the name user's name to disk."""
    dump(name, path)

def load_name(path: str = USERNAME_PATH) -> Optional[str]:
    """
    Load the stored user name.
    Returns: str or None.
    """
    try:
        value = load(path)
        if isinstance(value, str):
            return value
    except Exception:
        pass
    return None

def reset_name(path: str = USERNAME_PATH) -> None:
    """Remove the currently saved name."""
    dump(None, path)

# User name saving decision (save name? yes or no)
def save_name_decision(decision: bool, path: str = USERNAME_DECISION_PATH) -> None:
    """Store whether the user wants their name to be saved."""
    dump(decision, path)

def load_name_decision(path: str = USERNAME_DECISION_PATH) -> Optional[bool]:
    """
    Load the user's name-saving preference.
    Returns: True, False, or None if not stored.
    """
    try:
        value = load(path)
        if isinstance(value, bool):
            return value
    except Exception:
        pass
    return None

# Purchased game
def save_purchased_game(game_title: str, game_platform: str, game_price: float,  path: str = PURCHASED_GAME_PATH) -> None:
    """Save the last purchased game details."""
    dump((game_title, game_platform, game_price), path)

def load_purchased_game(path: str = PURCHASED_GAME_PATH) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    """
    Load the last purchased game.
    Returns: (title, platform, price) or (None, None, None) if nothing stored.
    """
    try:
        value = load(path)         
        if isinstance(value, tuple) and len(value) == 3:
            return value
    except Exception:
        pass

    return None, None, None

def reset_purchased_game(path: str = PURCHASED_GAME_PATH) -> None:
    """Remove the currently purchased game."""
    dump(None, path)

# Load QA dataset
def load_qa_data(path: str = QA_PATH) -> Tuple[List[str], List[str]]:
    """
    Load the QA dataset from CSV.
    Returns: questions, answers, documents
    """
    try: 
        df = pd.read_csv(path)
    except FileNotFoundError:
        print("[ERROR] Could not find COMP3074-CW1-Dataset.csv")
        sys.exit(1)

    questions = df["Question"].astype(str).tolist()
    answers = df["Answer"].astype(str).tolist()
    documents = df["Document"].astype(str).tolist()

    return questions, answers, documents

# Loads games dataset
def load_games_data(path: str = GAMES_PATH) -> Tuple[List[str], List[str], List[str], List[str], List[str], List[float], List[str], List[float]]:
    """
    Load and return the full games dataset.
    Returns: titles, platforms, genres, publishers, developers,
        critic_scores, release_dates, prices
    """
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print("[ERROR] Could not find games_data.csv")

    titles = df["title"].astype(str).tolist()
    platforms = df["console"].astype(str).tolist()
    genre = df["genre"].astype(str).tolist()
    publisher = df["publisher"].astype(str).tolist()
    developer = df["developer"].astype(str).tolist()
    critic_score = df["critic_score"].astype(float).tolist()
    release_date = df["release_date"].astype(str).tolist()
    price = df["Price"].astype(float).tolist()

    return titles, platforms, genre, publisher, developer, critic_score, release_date, price
