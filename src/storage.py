from pathlib import Path
from typing import Any, Optional, Tuple, List
from joblib import dump, load
from config import (USERNAME_PATH, QA_PATH, 
                    GAMES_PATH, USERNAME_DECISION_PATH, 
                    PURCHASED_GAME_PATH, SEARCH_HISTORY_PATH)
import pandas as pd
import sys

PurchasedGame = Tuple[str, str, float]

def _dump(value: Any, path: Path) -> None:
    """Write a value with joblib, creating the parent directory if it does not exist yet."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    dump(value, path)

# User name storage
def save_name(name: str, path: Path = USERNAME_PATH) -> None:
    """Save the user's name to disk."""
    _dump(name, path)

def load_name(path: Path = USERNAME_PATH) -> Optional[str]:
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

def reset_name(path: Path = USERNAME_PATH) -> None:
    """Remove the currently saved name."""
    _dump(None, path)

# User name saving decision (save name? yes or no)
def save_name_decision(decision: bool, path: Path = USERNAME_DECISION_PATH) -> None:
    """Store whether the user wants their name to be saved."""
    _dump(decision, path)

def load_name_decision(path: Path = USERNAME_DECISION_PATH) -> Optional[bool]:
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

# Purchased games history
def load_purchased_games(path: Path = PURCHASED_GAME_PATH) -> List[PurchasedGame]:
    """
    Load purchase history.
    Returns a list of (title, platform, price).
    Backward-compatible with old single-tuple storage.
    """
    try:
        value = load(path)

        # NEW format: list of tuples
        if isinstance(value, list):
            cleaned: List[PurchasedGame] = []
            for item in value:
                if isinstance(item, tuple) and len(item) == 3:
                    title, platform, price = item
                    if isinstance(title, str) and isinstance(platform, str):
                        try:
                            cleaned.append((title, platform, float(price)))
                        except Exception:
                            pass
            return cleaned

        # OLD format: single tuple
        if isinstance(value, tuple) and len(value) == 3:
            title, platform, price = value
            if isinstance(title, str) and isinstance(platform, str):
                try:
                    return [(title, platform, float(price))]
                except Exception:
                    return []

    except Exception:
        pass

    return []

def save_purchased_game(game_title: str, game_platform: str, game_price: float, path: Path = PURCHASED_GAME_PATH, max_history: int = 10) -> None:
    """
    Save purchase into history list.
    Keeps only the last `max_history` purchases.
    """
    history = load_purchased_games(path)
    history.append((game_title, game_platform, float(game_price)))

    if max_history and max_history > 0:
        history = history[-max_history:]

    _dump(history, path)

def reset_purchased_games(path: Path = PURCHASED_GAME_PATH) -> None:
    """Remove purchase history."""
    _dump([], path)

# Load QA dataset
def load_qa_data(path: Path = QA_PATH) -> Tuple[List[str], List[str], List[str]]:
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
def load_games_data(path: Path = GAMES_PATH) -> Tuple[List[str], List[str], List[str], List[str], List[str], List[float], List[str], List[float]]:
    """
    Load and return the full games dataset.
    Returns: titles, platforms, genres, publishers, developers,
        critic_scores, release_dates, prices
    """
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print("[ERROR] Could not find games_data.csv")
        sys.exit(1)

    titles = df["title"].astype(str).tolist()
    platforms = df["console"].astype(str).tolist()
    genre = df["genre"].astype(str).tolist()
    publisher = df["publisher"].astype(str).tolist()
    developer = df["developer"].astype(str).tolist()
    critic_score = df["critic_score"].astype(float).tolist()
    release_date = df["release_date"].astype(str).tolist()
    price = df["Price"].astype(float).tolist()

    return titles, platforms, genre, publisher, developer, critic_score, release_date, price

# Search history
def load_search_history(path: Path = SEARCH_HISTORY_PATH) -> List[str]:
    """Load search history list."""
    try:
        value = load(path)
        if isinstance(value, list):
            # keep only strings
            return [str(v) for v in value if isinstance(v, str) and v.strip()]
    except Exception:
        pass
    return []


def save_search_query(query: str, path: Path = SEARCH_HISTORY_PATH, max_history: int = 20) -> None:
    """
    Append a query to search history ONLY if it's not already present.
    If it exists, don't add a duplicate.

    Optional improvement included:
    - Moves existing query to the end (most recent),
      while keeping the list unique.
    """
    query = str(query).strip()
    if not query:
        return

    history = load_search_history(path)

    # Case-insensitive uniqueness
    lowered = query.lower()
    history = [h for h in history if h.strip() and h.lower() != lowered]

    # Add once (now unique)
    history.append(query)

    if max_history and max_history > 0:
        history = history[-max_history:]

    _dump(history, path)


def reset_search_history(path: Path = SEARCH_HISTORY_PATH) -> None:
    """Clear search history."""
    _dump([], path)