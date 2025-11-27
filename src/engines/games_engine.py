from storage import load_games_data
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from nltk import word_tokenize
from typing import List, Tuple, Optional

class GamesEngine:
    """
    A search and filtering engine for game data.

    This component handles:
        - title similarity search
        - filtering by platform, genre, price, critic score, and release year
        - publisher-based and developer-based search
    """
    def __init__(self):
        # Load games data from CSV via storage.py
        (self.titles, 
         self.platforms, 
         self.genre, 
         self.publisher, 
         self.developer, 
         self.critic_score, 
         self.release_date, 
         self.price) = load_games_data()
        
        
        # Title similarity TF-IDF
        self.name_vectoriser = TfidfVectorizer()
        self.q_matrix = self.name_vectoriser.fit_transform(self.titles)

        # Publisher similarity TF-IDF
        self.publisher_vectoriser = TfidfVectorizer()
        self.publisher_matrix = self.publisher_vectoriser.fit_transform(self.publisher)

        # Developer similarity TF-IDF
        self.developer_vectoriser = TfidfVectorizer()
        self.developer_matrix = self.developer_vectoriser.fit_transform(self.developer)

    # Title Search
    def search_by_title(self, user_input: str, min_score: float = 0.4) -> Tuple[List[str], List[str], List[str], List[str], List[str], List[float], List[str], List[float], List[float]]:
        """
        Search for games based on title similarity.
        Returns all matching attributes for matched titles.
        """

        query_vec = self.name_vectoriser.transform([user_input])
        similarity = cosine_similarity(query_vec, self.q_matrix)[0]

        # Sort descending by similarity
        sorted_idx = np.argsort(similarity)[::-1]

        # Collect indices above threshold
        selected_idx = [
            i for i in sorted_idx
            if similarity[i] >= min_score
            ]

        if not selected_idx:
            return [], [], [], [], [], [], [], []

        return (
            [self.titles[i] for i in selected_idx],
            [self.platforms[i] for i in selected_idx],
            [self.genre[i] for i in selected_idx],
            [self.publisher[i] for i in selected_idx],
            [self.developer[i] for i in selected_idx],
            [self.critic_score[i] for i in selected_idx],
            [self.release_date[i] for i in selected_idx],
            [self.price[i] for i in selected_idx]
        )
        
    # Publisher Search
    def search_by_publisher(self, user_input: str, min_score: float = 0.4 ) -> Tuple[List[str], List[str]]:
        """
        Return all games published by the most similar publisher match.
        """

        query_vec = self.publisher_vectoriser.transform([user_input])
        similarity = cosine_similarity(query_vec, self.publisher_matrix)[0]

        best_idx = int(np.argmax(similarity))
        best_score = float(similarity[best_idx])

        if best_score < min_score:
            return [], []

        best_publisher = str(self.publisher[best_idx])

        matched_titles: List[str] = []
        matched_publishers: List[str] = []

        for title, pub in zip(self.titles, self.publisher):
            if str(pub) == best_publisher:
                matched_titles.append(title)
                matched_publishers.append(pub)

        return matched_titles, matched_publishers
    
    # Developer Search
    def search_by_developers(self, user_input: str, min_score: float = 0.4 ) -> Tuple[List[str], List[str]]:
        """
        Return all games created by the most similar developer.
        """

        query_vec = self.developer_vectoriser.transform([user_input])
        similarity = cosine_similarity(query_vec, self.developer_matrix)[0]
 
        best_idx = int(np.argmax(similarity))
        best_score = float(similarity[best_idx])

        if best_score < min_score:
            return [], []

        best_developer = str(self.developer[best_idx])

        matched_titles: List[str] = []
        matched_developers: List[str] = []

        for title, dev in zip(self.titles, self.developer):
            if str(dev) == best_developer:
                matched_titles.append(title)
                matched_developers.append(dev)
                
        return matched_titles, matched_developers
    
    # Platform / Genre Filters
    def filter_by_platform(self, platform: str):
        """
        Return all titles where canonical platform name appears in the platform field.
        """
        matched_titles = []
        matched_platforms = []

        for title, plat in zip(self.titles, self.platforms):
            if platform.lower() in plat.lower():
                matched_titles.append(title)
                matched_platforms.append(plat)

        return matched_titles, matched_platforms
    
    def filter_by_genre(self, genre: str):
        """
        Return all titles where canonical genre appears in the genre field.
        """
        matched_titles = []
        matched_genres = []

        for title, gen in zip(self.titles, self.genre):
            if genre.lower() in gen.lower():
                matched_titles.append(title)
                matched_genres.append(gen)

        return matched_titles, matched_genres
    
    # Price Filters
    def filter_prices(self, mode: str, price1: float, price2: Optional[float] = None):
        """
        Filtering modes:
            before -> price < p1
            after -> price > p1
            exact -> price == p1
            between -> p1 <= price <= p2
        """

        titles, prices, platforms = [], [], []

        if price2 is not None and price1 > price2:
            price1, price2 = price2, price1

        for title, price_obj, platform in zip(self.titles, self.price, self.platforms):
            if isinstance(price_obj, list):
                if not price_obj:
                    continue
                value = price_obj[0]
            else:
                value = price_obj

            try:
                value = float(value)
            except (TypeError, ValueError):
                continue


            if (
                (mode == "before" and round(value) < price1)
                or (mode == "after" and round(value) > price1)
                or (mode == "exact" and round(value) == price1)
                or (mode == "between" and price2 is not None and price1 <= round(value) <= price2)
            ):
                titles.append(title)
                prices.append(value)
                platforms.append(platform)

        return titles, prices, platforms 
    
    # score filtering  
    def filter_scores(self, mode: str, score1: float, score2: Optional[float] = None):
        """
        Same modes as price filtering.
        """
        titles, critic_scores, platforms = [], [], []

        if score2 is not None and score1 > score2:
            score1, score2 = score2, score1

        for title, score_obj, platform in zip(self.titles, self.critic_score, self.platforms):
            if isinstance(score_obj, list):
                if not score_obj:
                    continue
                value = score_obj[0]
            else:
                value = score_obj

            try:
                value = float(value)
            except (TypeError, ValueError):
                continue

            if (
                (mode == "below" and value < score1)
                or (mode == "above" and value > score1)
                or (mode == "exact" and value == score1)
                or (mode == "between" and score2 is not None and score1 <= value <= score2)
            ):
                titles.append(title)
                critic_scores.append(value)
                platforms.append(platform)

        return titles, critic_scores, platforms 
    
    # Date Filters
    @staticmethod
    def _extract_year(date_str: str) -> int:
        """
        Extract the year (first 4 digits) from a YYYY-MM-DD style string.
        """ 
        try: 
            return int(date_str[:4])
        except Exception:
            return None

    def filter_date(self, mode: str, year1: float, year2: Optional[float] = None):
        """
        Same modes: before, after, exact, between
        """
        titles, years, platforms = [], [], []

        if year2 is not None and year1 > year2:
            year1, year2 = year2, year1

        for title, date_obj, platform in zip(self.titles, self.release_date, self.platforms):
            year = self._extract_year(str(date_obj))
            if year is None:
                continue

            if (
                (mode == "before" and year < year1)
                or (mode == "after" and year > year1)
                or (mode == "exact" and year == year1)
                or (mode == "between" and year2 is not None and year1 <= year <= year2)
            ):
                titles.append(title)
                years.append(year)
                platforms.append(platform)

        return titles, years, platforms 
    
    # Game Query Extraction
    @staticmethod
    def _extract_game_query_from_example(user_input: str, matched_example: str) -> str:
        """
        Use the matched intent example as a template and return
        the remaining words as the 'game-ish' query.

        Example:
            user_input    = "do you have fifa 23 on ps5"
            matched_example = "do you have"
            -> "fifa 23 on ps5"
        """

        if not matched_example:
            return user_input

        ui_tokens = word_tokenize(user_input.lower())
        ex_tokens = word_tokenize(matched_example.lower())

        # 1) strip common prefix
        i = 0
        while i < len(ui_tokens) and i < len(ex_tokens) and ui_tokens[i] == ex_tokens[i]:
            i += 1

        remainder = ui_tokens[i:]

        # 2) optional: light cleanup – drop very generic trailing words
        # e.g. if last token is literally "games"
        if remainder and remainder[-1] in {"game", "games"}:
            remainder = remainder[:-1]

        # 3) rebuild string or fall back
        query = " ".join(remainder).strip()
        return query if query else user_input
    

        