from typing import Optional, List
import random
from collections import defaultdict
from engines.games_engine import GamesEngine
from engines.games_detectors import (
    detect_platform, detect_genre, detect_price_critic_score, 
    detect_price_critic_between, detect_dates, detect_dates_between, 
    detect_selection
)
from storage import (save_purchased_game, reset_purchased_game, load_purchased_games)
from responses import (games, games_by_name, games_by_platform, games_by_genre, games_by_publisher,
    games_by_developer, games_by_low_price, games_by_high_price, games_by_exact_price,
    games_by_between_prices, games_by_between_scores, games_by_exact_score,
    games_by_high_score, games_by_low_score, games_by_date_before, games_by_date_after,
    games_by_date_exact, games_by_date_between, games_explore, game_purchased, 
    no_game_found, ask_platform_disambiguation, ask_game_disambiguation,
    confirm_order, game_not_purchased, user_ends_game_mode, back_from_game_selection, fallback,
    no_purchase_history, error_selection_invalid, error_confirm_oder, error_platform_not_detected, error_genre_not_detected,
    error_price_not_detected, error_price_range_not_detected, error_score_not_detected, error_score_range_not_detected,
    error_year_not_detected, error_year_range_not_detected, purchase_history_deleted, error_developer_not_detected, 
    error_publisher_not_detected, games_cheapest, games_most_expensive, games_lowest_score, games_highest_score, 
    games_oldest, games_newest, games_list_platforms, games_list_genres, purchase_history_list, no_games_to_recommend, recommend_games_personalised
)

class GamesHandler:
    def __init__(self):
        self.games_engine = GamesEngine()

        # Game mode & purchased flow state flags
        self.only_one_platform = False # True if selected game has exactly one platform
        self.only_one_game = False # True if search result has exactly one game
        self.choose_game_name_mode = False # True when user is choosing a game from a numbered list
        self.choose_platform_mode = False # True when user is choosing a platform from a numbered list
        self.buying_process = False # True when use is in any step of the buying flow
        
        # Current selections / context
        self.selected_game_title: Optional[str] = None
        self.current_platform_choice: Optional[str] = None
        self.current_price_choice: Optional[float] = None
        self.game_query: Optional[str] = None
        self.buy_candidates: list[dict] = [] # List of candidate games 
        self.current_platforms: list[str] = [] # Platforms for currently selected game
        self.current_prices: list[float] = [] # Prices aligned with current_platforms

    def is_game_intent(self, label: str) -> bool:
            """Return True if this intent should be handled inside game mode."""            
            if label == "quit":
                return False
            
            game_intents = {
                "dont_want_games",
                "games_list",
                "games_list_by_name",
                "start_buying_process",
                "games_search_by_platform",
                "games_search_by_genre",
                "games_by_publisher",
                "games_by_developer",
                "games_search_by_price_low",
                "games_search_by_price_high",
                "games_search_by_price_exact",
                "games_search_by_price_between",
                "games_search_by_critic_low",
                "games_search_by_critic_high",
                "games_search_by_critic_exact",
                "games_search_by_critic_between",
                "games_search_by_release_before",
                "games_search_by_release_after",
                "games_search_by_release_exact",
                "games_search_by_release_between",
                "games_search_cheapest",
                "games_search_most_expensive",
                "games_search_lowest_critic",
                "games_search_highest_critic",
                "games_search_oldest",
                "games_search_newest",
                "explore_platforms",
                "explore_genres",
                "explore_games",
                "recommend_game"
            }

            # While in a multi-step buy process, always treat as game intent
            if self.buying_process or self.choose_game_name_mode or self.choose_platform_mode:
                return True

            return label in game_intents      

    def handle_game_intent(self, label: str, user_input: str, game_query: str) -> str:
        """Handle all game mode intents - called when already in game mode"""
        self.game_query = game_query

        # ---- PLATFORM DETECTION OVERRIDE ----
        detected_platform = detect_platform(user_input)
        if detected_platform is not None:
            label = "games_search_by_platform"

        # ---- GENRE DETECTION OVERRIDE ----
        detected_genre = detect_genre(user_input)
        if detected_genre is not None:
            label = "games_search_by_genre"
        
        # 0. Games exploration intent (user wants to explore/browse games)
        if label == "explore_games":
            return games_explore()
        
        # 0.1 Game recommendation
        if label == "recommend_game":
            return self._handle_recommend_game()
        
        # 0.2 List all platforms
        if label == "explore_platforms":
            return games_list_platforms(self.games_engine.platforms)

        # 0.3 List all genres
        if label == "explore_genres":
            return games_list_genres(self.games_engine.genre)

        # 1. User wants to leave entirely from buying process
        if label == "dont_want_games":
            self._reset_buying_state()
            return user_ends_game_mode()

        # 2. User wants to go back within the buying process
        if label == "back" and self.buying_process:
            return self._handle_back_in_buy_process()
        
        # 3. Selection steps (game/platform choice)
        if self.choose_game_name_mode or self.choose_platform_mode:
            return self._handle_selection_process(user_input)
        
        # 4. Filtering (platform/genre/price/score/date)
        filter_response = self._handle_filters(label, user_input)
        if filter_response:
            return filter_response
        
        # 5. Starting buy process
        if label == "start_buying_process" and not self.buying_process:
            (titles, platforms, _, _, _, _, _, prices) = self.games_engine.search_by_title(game_query)
            return self._handle_buy_process(titles, platforms, prices)
        
        # 6. Game listing (10 random games)
        if label == "games_list":
            return games(self.games_engine.titles)
        
        # 7. Game listing by name
        if label == "games_list_by_name":
            (titles, platforms, genres, publishers, developers,
             scores, dates, prices) = self.games_engine.search_by_title(game_query)
            return games_by_name(titles, platforms, genres, publishers, developers,
                                scores, dates, prices)
        
        # 8. Confirmation step
        if self.buying_process:
            return self._handle_buy_confirmation(label, user_input)

        # Fallback if nothing else matches
        return fallback()

    # Resets all flags related to buying process
    def _reset_buying_state(self):
        """Reset all game-purchase-related state."""
        self.buying_process = False
        self.choose_game_name_mode = False
        self.choose_platform_mode = False
        self.current_platforms = []
        self.current_prices = []
        self.selected_game_title = None
        self.current_platform_choice = None
        self.current_price_choice = None
        self.only_one_platform = False
        self.only_one_game = False

    # Purchase History Handling
    def _handle_purchase_history(self) -> str:
        """
        Returns the user's purchase history if it exists,
        otherwise respond that there is no purchase history.
        """
        history = load_purchased_games()
        if not history:
            return no_purchase_history()
        return purchase_history_list(history)
    
    # Resets purchase history
    def _handle_reset_purchase_history(self) -> str:
        reset_purchased_game()
        return purchase_history_deleted()

    # Buy Flow: Selection (game / platform)
    def _handle_selection_process(self, user_input: str) -> str:
        """
        Handle game and platform selection by number during the buy process.
        - If choose_game_mode: map selection to a candidate game.
        - If choose_platform_mode: map selection to a platform/price for the chosen game.
        """
        selected_id = detect_selection(user_input)

        # Choose game by number
        if self.choose_game_name_mode:
            if selected_id is None or not (1 <= selected_id <= len(self.buy_candidates)):
                return error_selection_invalid(len(self.buy_candidates))

            selected = self.buy_candidates[selected_id - 1]
            title = selected["title"]
            platforms = selected["platforms"]
            prices = selected["prices"]

            # Move from game selection to platform selection stage
            self.choose_game_name_mode = False
            self.current_platforms = platforms
            self.current_prices = prices
            self.selected_game_title = title
            
            # If only one platform is available for chosen game, return confirmation
            if len(platforms) == 1:
                self.only_one_platform = True
                self.choose_platform_mode = False
                self.current_platform_choice = self.current_platforms[0]
                self.current_price_choice = self.current_prices[0]
                return confirm_order(self.selected_game_title, self.current_platforms[0], self.current_prices[0])
            
            # Else ask user to choose platform
            self.choose_platform_mode = True
            return ask_platform_disambiguation(title, platforms, prices)

        # Choose platform by number
        if self.choose_platform_mode:
            if selected_id is None or not (1 <= selected_id <= len(self.current_platforms)):
                return error_selection_invalid(len(self.current_platforms))

            platform = self.current_platforms[selected_id - 1]
            price = self.current_prices[selected_id - 1]
            title = self.selected_game_title or "that game"

            # Move to confirmation stage
            self.choose_platform_mode = False
            self.current_platform_choice = platform
            self.current_price_choice = price

            return confirm_order(title, platform, price)
        
    def _handle_back_in_buy_process(self):
        """
        Handle 'back' during the buy process.
        Depending on where the user is:
        - From game selection stage -> exit buy flow
        - From platform selection stage -> go back to game selection list
        - From confirmation stage -> go back to platform selection list
        """
        # 1. At game selection stage
        if self.choose_game_name_mode:
            self._reset_buying_state()
            return back_from_game_selection()

        # 2. At platform selection stage
        if self.choose_platform_mode:
            self.choose_platform_mode = False
            self.choose_game_name_mode = True
            self.selected_game_title = None
            self.current_platforms = []
            self.current_prices = []
            self.current_platform_choice = None
            self.current_price_choice = None
            return ask_game_disambiguation(self.buy_candidates)
    
        # 3. At confirmation stage with a single game + single platform
        if self.only_one_game and self.only_one_platform:
            self._reset_buying_state()
            return back_from_game_selection()

        # 4. At confirmation stage with single platform but multiple games
        if self.only_one_platform:
            self.choose_game_name_mode = True
            self.selected_game_title = None
            self.current_platform_choice = None
            self.current_price_choice = None
            return ask_game_disambiguation(self.buy_candidates)

        # 5. At confirmation stage with multiple platforms
        self.choose_platform_mode = True
        self.current_platform_choice = None
        self.current_price_choice = None
        return ask_platform_disambiguation(
            self.selected_game_title,
            self.current_platforms,
            self.current_prices,
        )

    # Filter Handling
    def _handle_filters(self, label: str, user_input: str) -> Optional[str]:
        """
        Handle all game filtering operations (platform, genre, price, score, date).
        Returns a response string if filter handled, otherwise None.
        """
        if label == "games_search_by_platform":
            platform = detect_platform(user_input)
            if platform is None:
                return error_platform_not_detected()
            titles, platforms = self.games_engine.filter_by_platform(platform)
            return games_by_platform(platform, titles, platforms)
        
        if label == "games_search_by_genre":
            genre = detect_genre(user_input)
            if genre is None:
                return error_genre_not_detected()
            titles, genres = self.games_engine.filter_by_genre(genre)
            return games_by_genre(genre, titles, genres)
        
        if label == "games_by_publisher":
            titles, publishers = self.games_engine.search_by_publisher(user_input)
            if not titles:
                return error_publisher_not_detected()
            return games_by_publisher(titles, publishers)

        if label == "games_by_developer":
            titles, developers = self.games_engine.search_by_developers(user_input)
            if not titles:
                return error_developer_not_detected()
            return games_by_developer(titles, developers)

        price_response = self._handle_price_filters(label, user_input)
        if price_response:
            return price_response

        score_response = self._handle_score_filters(label, user_input)
        if score_response:
            return score_response

        date_response = self._handle_date_filters(label, user_input)
        if date_response:
            return date_response

        return None

    def _handle_price_filters(self, label: str, user_input: str) -> Optional[str]:
        """Handle price filtering"""
        if label == "games_search_cheapest":
            extreme, titles, prices, platforms = self.games_engine.get_extreme_price_games("cheapest")
            if not titles:
                return no_game_found()
            return games_cheapest(extreme, titles, prices, platforms)

        if label == "games_search_most_expensive":
            extreme, titles, prices, platforms = self.games_engine.get_extreme_price_games("most_expensive")
            if not titles:
                return no_game_found()
            return games_most_expensive(extreme, titles, prices, platforms)
        
        if label == "games_search_by_price_low":
            price = detect_price_critic_score(user_input)
            if price is None:
                return error_price_not_detected()
            titles, prices, platforms = self.games_engine.filter_prices("before", price)
            return games_by_low_price(price, titles, prices, platforms)

        if label == "games_search_by_price_high":
            price = detect_price_critic_score(user_input)
            if price is None:
                return error_price_not_detected()
            titles, prices, platforms = self.games_engine.filter_prices("after", price)
            return games_by_high_price(price, titles, prices, platforms)
        
        if label == "games_search_by_price_exact":
            price = detect_price_critic_score(user_input)
            if price is None:
                return error_price_not_detected()
            titles, prices, platforms = self.games_engine.filter_prices("exact", price)
            return games_by_exact_price(price, titles, prices, platforms)
        
        if label == "games_search_by_price_between":
            low_price, high_price = detect_price_critic_between(user_input)
            if low_price is None or high_price is None:
                return error_price_range_not_detected()
            titles, prices, platforms = self.games_engine.filter_prices("between", low_price, high_price)
            return games_by_between_prices(low_price, high_price, titles, prices, platforms)

        return None

    def _handle_score_filters(self, label: str, user_input: str) -> Optional[str]:
        """Handle critic score filtering"""
        if label == "games_search_lowest_critic":
            extreme, titles, scores, platforms = self.games_engine.get_extreme_score_games("lowest")
            if not titles:
                return no_game_found()
            return games_lowest_score(extreme, titles, scores, platforms)

        if label == "games_search_highest_critic":
            extreme, titles, scores, platforms = self.games_engine.get_extreme_score_games("highest")
            if not titles:
                return no_game_found()
            return games_highest_score(extreme, titles, scores, platforms)
        
        if label == "games_search_by_critic_low":
            score = detect_price_critic_score(user_input)
            if score is None:
                return error_score_not_detected()
            titles, scores, platforms = self.games_engine.filter_scores("below", score)
            return games_by_low_score(score, titles, scores, platforms)

        if label == "games_search_by_critic_high":
            score = detect_price_critic_score(user_input)
            if score is None:
                return error_score_not_detected()
            titles, scores, platforms = self.games_engine.filter_scores("above", score)
            return games_by_high_score(score, titles, scores, platforms)

        if label == "games_search_by_critic_exact":
            score = detect_price_critic_score(user_input)
            if score is None:
                return error_score_not_detected()
            titles, scores, platforms = self.games_engine.filter_scores("exact", score)
            return games_by_exact_score(score, titles, scores, platforms)

        if label == "games_search_by_critic_between":
            low_score, high_score = detect_price_critic_between(user_input)
            if low_score is None or high_score is None:
                return error_score_range_not_detected()
            titles, scores, platforms = self.games_engine.filter_scores("between", low_score, high_score)
            return games_by_between_scores(low_score, high_score, titles, scores, platforms)

        return None

    def _handle_date_filters(self, label: str, user_input: str) -> Optional[str]:
        """Handle release date filtering"""
        if label == "games_search_oldest":
            extreme, titles, years, platforms = self.games_engine.get_extreme_release_dates("oldest")
            if not titles:
                return no_game_found()
            return games_oldest(extreme, titles, years, platforms)

        if label == "games_search_newest":
            extreme, titles, years, platforms = self.games_engine.get_extreme_release_dates("newest")
            if not titles:
                return no_game_found()
            return games_newest(extreme, titles, years, platforms)
        
        if label == "games_search_by_release_before":
            date = detect_dates(user_input)
            if date is None:
                return error_year_not_detected()
            titles, dates, platforms = self.games_engine.filter_date("before", date)
            return games_by_date_before(date, titles, dates, platforms)
        
        if label == "games_search_by_release_after":
            date = detect_dates(user_input)
            if date is None:
                return error_year_not_detected()
            titles, dates, platforms = self.games_engine.filter_date("after", date)
            return games_by_date_after(date, titles, dates, platforms)
        
        if label == "games_search_by_release_exact":
            date = detect_dates(user_input)
            if date is None:
                return error_year_not_detected()
            titles, dates, platforms = self.games_engine.filter_date("exact", date)
            return games_by_date_exact(date, titles, dates, platforms)
        
        if label == "games_search_by_release_between":
            min_year, max_year = detect_dates_between(user_input)
            if min_year is None or max_year is None:
                return error_year_range_not_detected()
            titles, dates, platforms = self.games_engine.filter_date("between", min_year, max_year)
            return games_by_date_between(min_year, max_year, titles, dates, platforms)

        return None

    # Buy Flow: Candidates & Confirmation
    def _handle_buy_process(self, titles, platforms, prices) -> str:
        """
        Start the buy process:
        - Merge rows by title (collect platforms + prices per title)
        - Decide whether to:
            - confirm directly (1 game, 1 platform)
            - ask platform (1 game, multiple platforms)
            - or ask which game (multiple titles)
        """
        self.buying_process = True

        if not titles:
            return no_game_found()

        merged_games = defaultdict(list)
        for title, platform, price_val in zip(titles, platforms, prices):
            merged_games[title].append({
                "platform": platform,
                "price": float(price_val)
            })

        candidates = []
        for t, offers in merged_games.items():
            platforms_list = [o["platform"] for o in offers]
            prices_list = [o["price"] for o in offers]
            candidates.append({
                "title": t,
                "platforms": platforms_list,
                "prices": prices_list
            })

        # If there are no candidates check if there are multiple platform or not
        if len(candidates) == 1:
            self.only_one_game = True
            selected = candidates[0]
            title = selected["title"]
            platforms_list = selected["platforms"]
            prices_list = selected["prices"]

            self.current_platforms = platforms_list
            self.current_prices = prices_list
            self.selected_game_title = title

            # If there is one platform then return confirmation
            if len(platforms_list) == 1:
                self.only_one_platform = True
                self.current_platform_choice = self.current_platforms[0]
                self.current_price_choice = self.current_prices[0]
                return confirm_order(self.selected_game_title, self.current_platforms[0], self.current_prices[0])
            else:
                self.choose_platform_mode = True
                return ask_platform_disambiguation(title, platforms_list, prices_list)

        # Else ask to select game
        self.choose_game_name_mode = True
        self.buy_candidates = candidates
        return ask_game_disambiguation(candidates)

    def _handle_buy_confirmation(self, label: str, user_input: str) -> str:
        """
        Handle final purchase confirmation:
        - yes / confirm_positive -> purchase completed and saved to history
        - no / confirm_negative -> cancel purchase
        """
        if user_input.lower() == "no" or label == "confirm_negative":
            self._reset_buying_state()
            return game_not_purchased()
        
        if user_input.lower() == "yes" or label == "confirm_positive":
            platform = self.current_platform_choice
            price = self.current_price_choice
            title = self.selected_game_title 
            save_purchased_game(title, platform, price)
            self._reset_buying_state()
            return game_purchased(title, platform, price)
        
        return error_confirm_oder()
    
    def _handle_recommend_game(self) -> str:
        """
        Personalised recommendation:
        - Use most recent purchased game.
        - Get its genre using search_by_title.
        - Recommend games that match BOTH the same genre + same platform.
        """

        history = load_purchased_games()
        # If no history list random 10 games
        if not history:
            return games(self.games_engine.titles)

        # Most recent purchase
        bought_title, bought_platform, _ = history[-1]

        # Get genre of purchased title (no helper method needed)
        (_, _, genres, _, _, _, _, _) = self.games_engine.search_by_title(bought_title)

        bought_genre = str(genres[0]) if genres else None

        if not bought_genre:
            return games(self.games_engine.titles)

        # Get titles that match genre
        genre_titles, _ = self.games_engine.filter_by_genre(bought_genre)
        if not genre_titles:
            return no_game_found()

        # Get titles that match platform
        platform_titles, _ = self.games_engine.filter_by_platform(bought_platform)
        if not platform_titles:
            return no_game_found()

        # Intersection of titles (case-insensitive)
        genre_set = {t.lower() for t in genre_titles}
        platform_set = {t.lower() for t in platform_titles}

        matched_titles = [t for t in platform_titles if t.lower() in genre_set.intersection(platform_set)]

        # Remove already purchased titles
        purchased_titles = {t.lower() for (t, _, _) in history}
        matched_titles = [t for t in matched_titles if t.lower() not in purchased_titles]

        if not matched_titles:
            return no_games_to_recommend(bought_title, bought_platform, bought_genre)

        # Pick up to 10
        if len(matched_titles) > 10:
            rec_titles = random.sample(matched_titles, 10)
        else:
            rec_titles = matched_titles[:10]

        return recommend_games_personalised(
            bought_title=bought_title,
            bought_platform=bought_platform,
            bought_genre=bought_genre,
            rec_titles=rec_titles
        )    