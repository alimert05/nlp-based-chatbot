import re
from typing import Optional
from nltk import word_tokenize
from responses import fallback

# A single "word" in a name, including accents and internal hyphens/apostrophes
NAME_WORD = r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[-'][A-Za-zÀ-ÖØ-öø-ÿ]+)?"

# A name phrase: 1-5 words
NAME_PHRASE = rf"{NAME_WORD}(?:\s+{NAME_WORD}){{0,4}}"

# All intro phrases from introduce_self + introduce_new_name
INTRO_PHRASES = (
    # New-name specific
    r"my new name is|"
    r"i want to change it to|"
    r"change my name to|"
    r"change it to|"
    r"please use the name|"
    r"use the name|"

    # Generic name-intro phrases
    r"my name is|"
    r"hi, my name is|"
    r"let's say my name is|"

    r"i am|i'm|im|"
    r"this is|"

    r"call me|"
    r"you can call me|"
    r"you can just call me|"
    r"you may call me|"
    r"people call me|"
    r"i go by|"
    r"i prefer to be called|"

    # Variants of "it is"
    r"it is|it's|its"
)

# Pattern: full sentence with an intro phrase, then a name, stopping at punctuation/comma
PATTERN = re.compile(
    rf"^(?:\s*(?:hi|hello|hey)\s*,?\s*)?"        # optional greeting
    rf"(?:{INTRO_PHRASES})\s+"                   # one of the intro phrases
    rf"({NAME_PHRASE})"                          # the actual name
    r"(?=\s*(?:[,.!?;:]|$))",                    # stop before comma/punctuation or end
    re.IGNORECASE,
)

class NameRecogniser:
    """
    Extract a person's name from short, natural language introductions.
    """
    def __init__(self) -> None:
        self.user_input: Optional[str] = None
        self.name: Optional[str] = None

    def extract_name(self, user_input: str) -> Optional[str]:
        """
        Try to extract a name from the user input.
        """
        self.user_input = user_input.strip()
        
        # Try to match an intro-style pattern
        m = PATTERN.search(self.user_input)
        if m:
            self.name = " ".join(w.capitalize() for w in m.group(1).split())
            return self.name

        # No name recognised
        return None
    
    # Name Normalisation
    def normalise_intro(self, user_input: str, matched_example: Optional[str]) -> Optional[str]:
        """
        Try to align the user's introduction to the matched template.
        Handles typos in introduction "my naem is" -> "my name is".
        """
        if not matched_example:
            return user_input
        
        ui_tokens = word_tokenize(user_input.lower())
        ex_tokens = word_tokenize(matched_example.lower())
        name_tokens: list[str] = []

        # Strategy 1: take everything after the last word in the example
        last_word = ex_tokens[-1]
        if last_word in ui_tokens:
            idx = ui_tokens.index(last_word)
            if idx < len(ui_tokens) - 1:
                name_tokens = ui_tokens[idx + 1:]

        # Strategy 2: strip common prefix
        if not name_tokens:
            i = 0
            while (i < len(ui_tokens) and 
                   i < len(ex_tokens) and 
                   ui_tokens[i] == ex_tokens[i]):
                i += 1
            if i < len(ui_tokens):
                name_tokens = ui_tokens[i:]
        
        name_tokens = [t for t in name_tokens if t.isalpha()]

        if name_tokens:
            return matched_example + " " + " ".join(name_tokens)
        else:
            # Fall back, do not crash
            return fallback()