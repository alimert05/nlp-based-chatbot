"""
Utility functions for extracting structured information from user input:

- Platform detection (e.g. PS5, PC)
- Genre detection (e.g. Action, RPG)
- Price / critic score detection
- Release year detection (single year / range)
- Numeric selection
"""
import re
from typing import Optional, Tuple
from config import PLATFORM_ALIASES, GENRE_ALIASES


def _detect_from_aliases(user_input: str, alias_map: dict[str, list[str]]) -> Optional[str]:
    """
    Given a user input and an alias dictionary, return the canonical key whose alias best matches the text.
    """
    text = user_input.lower()

    for canonical, aliases in alias_map.items():
        # Checks longer aliases first to avoid partial overlaps
        for alias in sorted(aliases, key=len, reverse=True): 
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, text):
                return canonical
    return None

# Platform Detection
def detect_platform(user_input: str) -> Optional[str]:
    """
    Detect the canonical platform name from user input.

    Returns:
        - "PS4", "PS5", "PC", ... if detected
        - None if no platform is recognised 
    """
    return _detect_from_aliases(user_input, PLATFORM_ALIASES)

# Genre Detection
def detect_genre(user_input: str) -> Optional[str]:
    """
    Detect the canonical genre label form user input.

    Returns: 
        - e.g. "Action", "RPG", ...
        - None if no genre is recognised
    """
    return _detect_from_aliases(user_input, GENRE_ALIASES)
    
# Price and Critic Score Detection
def detect_price_critic_score(user_input: str) -> Optional[float]:
    """
    Extract single numeric value from the user input, used for either price or critic score queries.

    Examples: 
        "games under 20" -> 20.0
        "score above 85.5" -> 85.5
    """
    match = re.search(r'[+-]?\d*\.?\d+', user_input)
    if not match:
        return None
    return float(match.group())

def detect_price_critic_between(user_input: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract a pair of numeric values (low, high) from user input.

    Returns: 
        - (low, high) if two numbers are found
        - (None, None) if fewer than two number are found
    """
    numbers = re.findall(r'[+-]?\d*\.?\d+', user_input)
    if len(numbers) < 2:
        return (None, None)
    
    low, high = map(float, numbers[:2])
    if low > high:
        low, high = high, low
    return low, high


# Dates Detection
def detect_dates(user_input: str) -> Optional[int]:
    """
    Detect a single year.

    Returns: year as int, or None if no valid year is found
    """
    match = re.search(r"\b(19[5-9]\d|20[0-4]\d|2050)\b", user_input)
    if not match:
        return None
    return int(match.group())

def detect_dates_between(user_input: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Detect a pair of years.

    Returns:
        - (min_year, max_year) if two valid years are found
        - (None, None) if fewer than two are found
    """
    years = re.findall(r"\b(19[5-9]\d|20[0-4]\d|2050)\b", user_input)
    if len(years) < 2:
        return (None, None)
    
    min, max = map(int, years[:2])
    if min > max:
        min, max = max, min
    return min, max

# Numeric selection Detection
def detect_selection(user_input: str) -> Optional[int]:
    """
    Detect a numeric selection from user input.

    Example: 
        - "I choose 3" -> 3
        - "option 2" -> 2
        - "number 10" -> 10
    
    Returns: int value if a number is found, else None.
    """
    match = re.search(r'\b(\d+)\b', user_input)
    if not match:
        return None
    return int(match.group(1))
