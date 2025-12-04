# intent_engine.py
import json
from typing import Optional, Tuple, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import config


class IntentEngine:
    """
    Responsible only for:
      - loading intent examples from JSON
      - vectorising examples
      - computing cosine similarity
      - returning (label, score, matched_example)
    """

    def __init__(self, intent_path: str = config.INTENTS_PATH, ngram_range=(1, 2), threshold: float = 0.55, high_confidence_intents: Optional[set[str]] = None) -> None:
        
        self.intent_path = intent_path
        self.threshold = threshold
        self.high_confidence_intents = (
            high_confidence_intents
            if high_confidence_intents is not None
            else {"greet", "small_talk"}
        )

        # Load intents JSON
        with open(self.intent_path, "r", encoding="utf8") as f:
            data = json.load(f)
        self.intents = data["intents"]

        # Prepare training examples
        self.example_texts: List[str] = []
        self.example_labels: List[str] = []

        for intent in self.intents:
            tag = intent["tag"]
            for example in intent["examples"]:
                self.example_texts.append(example.lower())
                self.example_labels.append(tag)

        # Vectoriser + matrix of examples
        self.vectoriser = TfidfVectorizer(ngram_range=ngram_range)
        self.example_matrix = self.vectoriser.fit_transform(self.example_texts)

    def match(self, user_input: str) -> Tuple[Optional[str], float, Optional[str]]:
        """
        Return:
          (best_label, best_score, best_example_text)

        If confidence is below threshold, best_label is None.
        """
        user_input = user_input.strip().lower()

        if not user_input:
            return None, 0.0, None

        user_vec = self.vectoriser.transform([user_input])
        similarity = cosine_similarity(user_vec, self.example_matrix)[0]

        # Penalise some intents for longer utterances if needed
        word_count = len(user_input.split())
        if word_count > 1:
            for idx, label in enumerate(self.example_labels):
                if label in self.high_confidence_intents:
                    similarity[idx] *= 0.9

        best_idx = int(np.argmax(similarity))
        best_score = float(similarity[best_idx])
        best_label = self.example_labels[best_idx]
        best_example = self.example_texts[best_idx]

        if best_score < self.threshold:
            return None, best_score, None

        return best_label, best_score, best_example