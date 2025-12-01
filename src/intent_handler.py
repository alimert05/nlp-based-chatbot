import config
from typing import Optional
from collections import defaultdict

from engines.name_engine import NameRecogniser
from engines.qa_engine import QaEngine
from engines.games_engine import GamesEngine
from engines.intent_engine import IntentEngine
from engines.games_detectors import (
    detect_platform, detect_genre, detect_price_critic_score, 
    detect_price_critic_between, detect_dates, detect_dates_between, 
    detect_selection
)
from storage import (load_name, save_name, reset_name, 
        save_name_decision, load_name_decision, 
        load_purchased_game, save_purchased_game, reset_purchased_game)
from responses import (
    recall_name, greeting, fallback, greeting_back, support_normal, small_talk,
    user_feeling_positive, user_feeling_negative, qa_answers, prompt_again, games,
    games_by_name, games_by_platform, games_by_genre, games_by_publisher,
    games_by_developer, games_by_low_price, games_by_high_price, games_by_exact_price,
    games_by_between_prices, games_by_between_scores, games_by_exact_score,
    games_by_high_score, games_by_low_score, games_by_date_before, games_by_date_after,
    games_by_date_exact, games_by_date_between, games_mode_on, game_purchased,
    support_game, no_game_found, ask_platform_disambiguation, ask_game_disambiguation,
    confirm_order, game_not_purchased, ask_name_again, name_refused, no_name_to_recall, 
    ask_save_name, purchase_history, user_ends_game_mode, back_from_game_selection, name_already_given,
    no_name_change_or_remove, name_changed, ask_new_name, name_already_known, confirm_name_change, name_removed, 
    no_name_to_change, no_name_to_remove, ask_remove_name
)

class IntentHandler:
    
    def __init__(self, intent_path: str = config.INTENTS_PATH) -> None:
    
        # Thresholds
        self.threshold = 0.55
        self.qa_threshold = 0.45
        self.qa_bonus = 0.05
        self.games_threshold = 0.40
        self.high_confidence = 0.70
        self.low_confidence = 0.45

        # Engines
        self.name_recogniser = NameRecogniser()
        self.qa_engine = QaEngine()
        self.games_engine = GamesEngine()
        self.intent_engine = IntentEngine(
            intent_path=intent_path,
            threshold=0.55,
            high_confidence_intents={"greet", "discover", "small_talk"},
        )

        # State management
        self._init_state()

    # State Initialisation
    def _init_state(self):
        self.wait_user_input = False

        # Game mode & purchased flow
        self.game_mode = False
        self.choose_game_name_mode = False # choosing which game
        self.choose_platform_mode = False # choosing which platform
        self.buying_process = False
        self.goodbye_process = False
        self.only_one_platform = False
        self.only_one_game = False

        self.selected_game_title : Optional[str] = None
        self.current_platform_choice : Optional[str] = None
        self.current_price_choice : Optional[float] = None
        self.game_query : Optional[str] = None
        self.buy_candidates : list[dict] = []
        self.current_platforms : list[str] = []
        self.current_prices : list[float] = []

        # Name handling
        self.change_name = False # asking user if they want to change name
        self.new_name_given = False # expecting a new name text
        self.normalised_name = Optional[str]
        self.extracted_name = Optional[str]

        # Explicit name-change flow
        self.explicit_change_flow = False
        self.pending_new_name: Optional[str] = None 
        self.waiting_name_confirmation = False  

        self.waiting_name_remove_confirmation = False

        # Name decision handling (persistent)
        self.decision = load_name_decision()
        self.username = load_name()
        self.new_username = None
        self.name_given = True if self.decision is True else False

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
        

    # Main Dispatch
    def handle_intent(self, user_input: str) -> Optional[str]:
        """Main intent handling logic"""
        # Get intent match
        label, intent_score, matched_example = self.intent_engine.match(user_input)
        
        # Hand-crafter override for "I don't want games" style messages
        text = user_input.lower()
        if "don't" in text or "dont" in text:
            # Only override if intent is related to buying games or listing games
            if "game" in text or "buy" in text:
                label = "dont_want_games"

        # Get QA engine response
        answer, qa_score, document, best_idx = self.qa_engine.search(user_input)
        
        # Get raw games search results
        (games_titles, games_platforms, games_genre, games_publisher, games_developer,
         games_critic_score, games_release_date, games_price) = self.games_engine.search_by_title(user_input)
        
        # Extract cleaned-up game query from template
        self.game_query = self.games_engine._extract_game_query_from_example(user_input, matched_example or "")
        
        # Name handling
        if self.waiting_name_confirmation:
            self.waiting_name_confirmation = False
            return self._explicit_name_change(user_input, None)
        
        if self.change_name:
            self.change_name = False
            return self._handle_name_change(user_input)
        
        if label == "introduce_self" and not self.explicit_change_flow:
            return self._handle_introduction(user_input, matched_example)

        if label == "change_name":
            if self.name_given is False:
                return no_name_to_change()
            self.explicit_change_flow = True
            return ask_new_name()
        
        if label == "introduce_self" and self.explicit_change_flow:
            self.explicit_change_flow = False
            self.waiting_name_confirmation = True
            return self._explicit_name_change(user_input, matched_example)
        
        if label == "remove_name":
            self.waiting_name_remove_confirmation = True
            return ask_remove_name()
        
        if self.waiting_name_remove_confirmation:
            self.waiting_name_remove_confirmation = False
            return self._handle_remove_name(user_input)
        
        # Goodbye flow
        if self._handle_goodbye_process(label):
            return self._process_goodbye(user_input)
            
        # QA engine queries (non-game mode only)
        if not self.game_mode and qa_score >= self.qa_threshold:
            if label is None or qa_score + self.qa_bonus > intent_score:
                return self._handle_qa_answer(answer, document, best_idx)
        
        # Purchase history
        if label == "purchase_history":
            return self._handle_purchase_history()
            
        # Game mode activation
        if self._should_activate_game_mode(label):
            if not self._can_use_game_features():
                return ask_name_again()
            return self._activate_game_mode(label, games_titles, games_platforms, games_genre, 
                                           games_publisher, games_developer, games_critic_score, 
                                           games_release_date, games_price)
        
        # Game mode handling
        if self.game_mode:
            return self._handle_game_mode(label, user_input, games_titles, games_platforms, 
                                         games_genre, games_publisher, games_developer, 
                                         games_critic_score, games_release_date, games_price)
        
        # Non-game mode handling
        return self._handle_non_game_mode(label, user_input, matched_example, intent_score)

    # Goodbye / End Session
    def _handle_goodbye_process(self, label: str) -> bool:
        """Mark that we are in the goodbye process if user wants to quit."""
        if label == "quit":
            self.goodbye_process = True
        return self.goodbye_process

    def _process_goodbye(self, user_input: str) -> str:
        """Handle goodbye name-saving decision."""
        if self.name_given:
            if user_input == "no":
                save_name_decision(False)
                reset_name()
                reset_purchased_game()
                self.goodbye_process = False
                return "no_saved_name_and_end"
            
            if user_input == "yes":
                save_name_decision(True)
                self.goodbye_process = False
                return "save_name_and_end"
            
            return ask_save_name()
        return "end"

    # Name Handling
    def _handle_introduction(self, user_input: str, matched_example: str) -> str:
        """Handle user introduction and name changing."""
        normalised_input = self.name_recogniser.normalise_intro(user_input, matched_example)
        extracted_name = self.name_recogniser.extract_name(normalised_input)
        
        # Case 1: user has not given a name yet (or is giving a new one)
        if self.name_given is False:
            if extracted_name:
                self.name_given = True
                save_name(extracted_name)
                self.username = extracted_name
                return greeting(extracted_name)
            return ask_name_again()
        
        # Case 2: name already known previously
        if extracted_name.lower() == str(self.username).lower():
            return name_already_known()
        self.change_name = True
        self.new_username = extracted_name
        return name_already_given(self.new_username)
    
    def _handle_name_change(self, user_input: str) -> str:
        """Name changing confirmation."""
        text = user_input.strip().lower()

        if text == "yes":
            self.name_given = True
            save_name(self.new_username)
            self.username = self.new_username
            return name_changed()
        if text == "no":
            self.change_name = False
            self.new_name_given = False
            return no_name_change_or_remove()
        return "Bot: Please answer with 'yes' if you'd like to change your name, or 'no' if you'd like to keep it as it is."
    
    def _explicit_name_change(self, user_input: str, matched_example: Optional[str]) -> str:
        """Handle explicit name change logic."""
        if self.waiting_name_confirmation:
            normalised_input = self.name_recogniser.normalise_intro(user_input, matched_example)
            extracted_name = self.name_recogniser.extract_name(normalised_input)
            self.pending_new_name = extracted_name
            return confirm_name_change(extracted_name)
        
        text = user_input.strip().lower()
        if text == "yes":
            self.waiting_name_confirmation = False
            self.explicit_change_flow = False
            save_name(self.pending_new_name)
            self.username = self.pending_new_name
            return name_changed()

        if text == "no":
            self.waiting_name_confirmation = False
            return no_name_change_or_remove()
        
        return "Bot: Please answer with 'yes' if you'd like to change your name, or 'no' if you'd like to keep it as it is."
    
    def _handle_remove_name(self, user_input) -> str:
        """Handle user wants to remove their name."""
        text = user_input.strip().lower()

        if self.name_given:
            if text == "yes":
                self.name_given = False
                reset_name()
                return name_removed()
            if text == "no":
                return no_name_change_or_remove()
            return "Bot: Please answer with 'yes' if you'd like to change your name, or 'no' if you'd like to keep it as it is."
        return no_name_to_remove()

        
    
    # QA flow handling
    def _handle_qa_answer(self, answer: list, document: list, best_idx: int) -> str:
        """Handle QA engine answers and group consecutive rows from same document."""
        if not document or not answer:
            return fallback()

        best_idx = max(0, min(best_idx, len(document) - 1))
        target_doc = document[best_idx]

        start = best_idx
        while start > 0 and document[start - 1] == target_doc:
            start -= 1

        end = best_idx + 1
        while end < len(document) and document[end] == target_doc:
            end += 1

        return qa_answers(answer[start:end])

    # Purchase History Handling
    def _handle_purchase_history(self) -> str:
        """Handle purchase history request"""
        title, platform, price = load_purchased_game()
        if not title or not platform or not price:
            return "Bot: You haven't purchased any games yet."
        return purchase_history(title, platform, price)

    # Game Mode Entry / Checks
    def _can_use_game_features(self) -> bool:
        """Check if user can use game features (name given or explicitly refused)."""
        return self.name_given

    def _should_activate_game_mode(self, label: str) -> bool:
        """Check if we should activate game mode"""
        return label in {"games_mode_on", "games_list", "games_list_by_name"}

    def _activate_game_mode(self, label: str, titles, platforms, genres, publishers, 
                           developers, scores, dates, prices) -> str:
        """Activate game mode based on label"""
        self.game_mode = True
        
        if label == "games_mode_on":
            return games_mode_on()
        elif label == "games_list":
            return games(self.games_engine.titles)
        elif label == "games_list_by_name":
            (titles, platforms, genres, publishers, developers,
            scores, dates, prices) = self.games_engine.search_by_title(self.game_query )
            return games_by_name(titles, platforms, genres, publishers, developers,
                                scores, dates, prices)

    # Game Mode Main Handler
    def _handle_game_mode(self, label: str, user_input: str, titles, platforms, genres, 
                         publishers, developers, scores, dates, prices) -> str:
        """Handle all game mode intents"""

        # 1. User wants to leave game mode
        if label == "dont_want_games":
            self.game_mode = False
            self._reset_buying_state()
            return user_ends_game_mode()

        # 2. User wants to go back within the buying process
        if label == "back" and self.buying_process:
            return self._handle_back_in_buy_process()
        
        # 3. Selection steps (game/platform choice)
        if self.choose_game_name_mode or self.choose_platform_mode:
            return self._handle_selection_process(user_input)
        
        # Help within game mode
        if label == "discover":
            return support_game()
        
        # 5. Filtering (platform/genre/price/score/date)
        filter_response = self._handle_filters(label, user_input)
        if filter_response:
            return filter_response
        
        # 6. Starting buy process
        if label == "start_buying_process" and not self.buying_process:
            (titles, platforms, _, _, _,
            _, _, prices) = self.games_engine.search_by_title(self.game_query)
            return self._handle_buy_process(titles, platforms, prices)
        
        # 7. Confirmation step
        if self.buying_process:
            return self._handle_buy_confirmation(user_input)
    
        return fallback()

    # Buy Flow: Selection
    def _handle_selection_process(self, user_input: str) -> str:
        """Handle game and platform selection"""
        selected_id = detect_selection(user_input)

        # Choose game by number
        if self.choose_game_name_mode:
            if selected_id is None or not (1 <= selected_id <= len(self.buy_candidates)):
                return f"Bot: Please reply with a number between 1 and {len(self.buy_candidates)}."

            selected = self.buy_candidates[selected_id - 1]
            title = selected["title"]
            platforms = selected["platforms"]
            prices = selected["prices"]
            self.choose_game_name_mode = False
            self.current_platforms = platforms
            self.current_prices = prices
            self.selected_game_title = title

            if len(platforms) == 1:
                self.only_one_platform = True
                self.choose_platform_mode = False
                self.current_platform_choice = self.current_platforms[0]
                self.current_price_choice = self.current_prices[0]
                return confirm_order(self.selected_game_title, self.current_platforms[0], self.current_prices[0])
            
            self.choose_platform_mode = True
            return ask_platform_disambiguation(title, platforms, prices)

        # Choose platform by number
        if self.choose_platform_mode:
            if selected_id is None or not (1 <= selected_id <= len(self.current_platforms)):
                return f"Bot: Please reply with a number between 1 and {len(self.current_platforms)}."

            platform = self.current_platforms[selected_id - 1]
            price = self.current_prices[selected_id - 1]
            title = self.selected_game_title or "that game"

            self.choose_platform_mode = False

            self.current_platform_choice = platform
            self.current_price_choice = price
            # self.current_platforms = []
            # self.current_prices = []
            # self.selected_game_title = None

            return confirm_order(title, platform, price)
        
    def _handle_back_in_buy_process(self):
        """Handle 'back' command at different stages of the buy process."""
        # 1. At game selection stage
        if self.choose_game_name_mode:
            self._reset_buying_state()
            return back_from_game_selection()

        # 2. At platform selection stage
        if self.choose_platform_mode:
            # Go back to choosing the game
            self.choose_platform_mode = False
            self.choose_game_name_mode = True

            self.selected_game_title = None
            self.current_platforms = []
            self.current_prices = []
            self.current_platform_choice = None
            self.current_price_choice = None

            return ask_game_disambiguation(self.buy_candidates)

    
        # 3. At confirmation stage
        # Case: only one game & only one platform → just cancel
        if self.only_one_game and self.only_one_platform:
            self._reset_buying_state()
            return back_from_game_selection()

        # Case: only one platform (but multiple games) → go back to game list
        if self.only_one_platform:
            self.choose_game_name_mode = True
            self.selected_game_title = None
            self.current_platform_choice = None
            self.current_price_choice = None
            return ask_game_disambiguation(self.buy_candidates)

        # Case: multiple platforms for the selected game
        # (either single game with many platforms OR multi game + multi platform
        # but we're already on a selected game here)
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
        """Handle all game filtering operations"""
        # Platform filter
        if label == "games_search_by_platform":
            platform = detect_platform(user_input)
            if platform is None:
                return "Bot: I didn't catch which platform you meant. Try saying 'games for PS4' or 'PC games'."
            titles, platforms = self.games_engine.filter_by_platform(platform)
            return games_by_platform(platform, titles, platforms)
        
        # Genre filter
        if label == "games_search_by_genre":
            genre = detect_genre(user_input)
            if genre is None:
                return "Bot: I didn't catch which genre you meant. Try another genre or type 'help'."
            titles, genres = self.games_engine.filter_by_genre(genre)
            return games_by_genre(genre, titles, genres)
        
        # Publisher filter
        if label == "games_by_publisher":
            titles, publishers = self.games_engine.search_by_publisher(user_input)
            return games_by_publisher(titles, publishers)

        # Developer filter
        if label == "games_by_developer":
            titles, developers = self.games_engine.search_by_developers(user_input)
            return games_by_developer(titles, developers)

        # Price filters
        price_response = self._handle_price_filters(label, user_input)
        if price_response:
            return price_response

        # Score filters
        score_response = self._handle_score_filters(label, user_input)
        if score_response:
            return score_response

        # Date filters
        date_response = self._handle_date_filters(label, user_input)
        if date_response:
            return date_response

        return None

    def _handle_price_filters(self, label: str, user_input: str) -> Optional[str]:
        """Handle price filtering"""
        if label == "games_search_by_price_low":
            price = detect_price_critic_score(user_input)
            if price is None:
                return "Bot: I couldn't find any games matches this price filter. Try something like 'games under 20 pounds'."
            titles, prices, platforms = self.games_engine.filter_prices("before", price)
            return games_by_low_price(price, titles, prices, platforms)

        if label == "games_search_by_price_high":
            price = detect_price_critic_score(user_input)
            if price is None:
                return "Bot: I couldn't find any games matches this price filter. Try something like 'games over 20 pounds'."
            titles, prices, platforms = self.games_engine.filter_prices("after", price)
            return games_by_high_price(price, titles, prices, platforms)
        
        if label == "games_search_by_price_exact":
            price = detect_price_critic_score(user_input)
            if price is None:
                return "Bot: I couldn't find any games matches this price. Try something like 'games that cost 20 pounds'."
            titles, prices, platforms = self.games_engine.filter_prices("exact", price)
            return games_by_exact_price(price, titles, prices, platforms)
        
        if label == "games_search_by_price_between":
            low_price, high_price = detect_price_critic_between(user_input)
            if low_price is None or high_price is None:
                return "Bot: I couldn't find any games matches this price. Try something like 'between 20 and 40 pounds'."
            titles, prices, platforms = self.games_engine.filter_prices("between", low_price, high_price)
            return games_by_between_prices(low_price, high_price, titles, prices, platforms)

        return None

    def _handle_score_filters(self, label: str, user_input: str) -> Optional[str]:
        """Handle critic score filtering"""
        if label == "games_search_by_critic_low":
            score = detect_price_critic_score(user_input)
            if score is None:
                return "Bot: I couldn't find a critic score value in your request. Try something like 'games with rating lower than 8'."
            titles, scores, platforms = self.games_engine.filter_scores("below", score)
            return games_by_low_score(score, titles, scores, platforms)

        if label == "games_search_by_critic_high":
            score = detect_price_critic_score(user_input)
            if score is None:
                return "Bot: I couldn't find a critic score value in your request. Try something like 'games with rating higher than 8'."
            titles, scores, platforms = self.games_engine.filter_scores("above", score)
            return games_by_high_score(score, titles, scores, platforms)

        if label == "games_search_by_critic_exact":
            score = detect_price_critic_score(user_input)
            if score is None:
                return "Bot: I couldn't find a critic score value in your request. Try something like 'games that have rating 8'."
            titles, scores, platforms = self.games_engine.filter_scores("exact", score)
            return games_by_exact_score(score, titles, scores, platforms)

        if label == "games_search_by_critic_between":
            low_score, high_score = detect_price_critic_between(user_input)
            if low_score is None or high_score is None:
                return "Bot: I couldn't find two critic scores in your request. Try something like 'games with rating between 7 and 8'."
            titles, scores, platforms = self.games_engine.filter_scores("between", low_score, high_score)
            return games_by_between_scores(low_score, high_score, titles, scores, platforms)

        return None

    def _handle_date_filters(self, label: str, user_input: str) -> Optional[str]:
        """Handle release date filtering"""
        if label == "games_search_by_release_before":
            date = detect_dates(user_input)
            if date is None:
                return "Bot: I couldn't see any year in your request. Try something like 'games before 2015'."
            titles, dates, platforms = self.games_engine.filter_date("before", date)
            return games_by_date_before(date, titles, dates, platforms)
        
        if label == "games_search_by_release_after":
            date = detect_dates(user_input)
            if date is None:
                return "Bot: I couldn't see any year in your request. Try something like 'games after 2015'."
            titles, dates, platforms = self.games_engine.filter_date("after", date)
            return games_by_date_after(date, titles, dates, platforms)
        
        if label == "games_search_by_release_exact":
            date = detect_dates(user_input)
            if date is None:
                return "Bot: I couldn't see any year in your request. Try something like 'games released in 2015'."
            titles, dates, platforms = self.games_engine.filter_date("exact", date)
            return games_by_date_exact(date, titles, dates, platforms)
        
        if label == "games_search_by_release_between":
            min_year, max_year = detect_dates_between(user_input)
            if min_year is None or max_year is None:
                return "Bot: I couldn't see any games between these years. Try something like 'games released between 2010 and 2015'."
            titles, dates, platforms = self.games_engine.filter_date("between", min_year, max_year)
            return games_by_date_between(min_year, max_year, titles, dates, platforms)

        return None

    # Buy Flow: Candidates & Confirmation
    def _handle_buy_process(self, titles, platforms, prices) -> str:
        """Handle buy process initiation: build candidates and decide next step"""
        self.buying_process = True

        if not titles:
            return no_game_found()

        # Merge games by title, collecting platform+price pairs
        merged_games = defaultdict(list)
        for title, platform, price_val in zip(titles, platforms, prices):
            merged_games[title].append({
                "platform": platform,
                "price": float(price_val)
            })

        # Build candidates list
        candidates = []
        for t, offers in merged_games.items():
            # keep platform-price alignment
            platforms_list = [o["platform"] for o in offers]
            prices_list = [o["price"] for o in offers]
            candidates.append({
                "title": t,
                "platforms": platforms_list,
                "prices": prices_list
            })

        # Single game found
        if len(candidates) == 1:
            self.only_one_game = True
            selected = candidates[0]
            title = selected["title"]
            platforms_list = selected["platforms"]
            prices_list = selected["prices"]

            self.current_platforms = platforms_list
            self.current_prices = prices_list      # store prices for later
            self.selected_game_title = title

            if len(platforms_list) == 1:
                self.only_one_platform = True
                return confirm_order(self.selected_game_title, self.current_platforms[0], self.current_prices[0])
            else:
                self.choose_platform_mode = True
                return ask_platform_disambiguation(title, platforms_list, prices_list)

        # Multiple games found
        self.choose_game_name_mode = True
        self.choose_platform_mode = True
        self.buy_candidates = candidates
        return ask_game_disambiguation(candidates)

    def _handle_buy_confirmation(self, user_input: str) -> Optional[str]:
        """Handle buy confirmation (yes/no)"""
        if user_input == "no":
            self.buying_process = False
            self.current_platforms = []
            self.current_prices = []
            self.selected_game_title = None
            self.only_one_platform = False
            # reset_purchased_game()
            return game_not_purchased()
        
        if user_input == "yes":
            self.buying_process = False
            self.game_mode = False
            platform = self.current_platform_choice
            price = self.current_price_choice
            title = self.selected_game_title 

            # Reset (can use defined function)
            self.only_one_platform = False
            self.current_platforms = []
            self.current_prices = []
            self.selected_game_title = None
            self.current_price_choice = None
            self.current_platform_choice = None
            save_purchased_game(title, platform, price)
            return game_purchased(title, platform, price)
        
        self.current_platforms = []
        self.current_prices = []
        self.selected_game_title = None
        
        return None

    # Non-game Intents
    def _handle_non_game_mode(self, label: str, user_input: str, matched_example: str, 
                             intent_score: float) -> str:
        """Handle all non-game mode intents"""

        # User refuses to give name
        if label == "name_refuse":
            self.name_given = False
            return name_refused()

        # Discover capabilities
        if label == "discover":
            return support_normal()
        
        # Simple greeting
        if label == "greet":
            return greeting_back(matched_example)

        # Check if name is required for features
        if not self._can_use_game_features():
            return ask_name_again()

        # Recall name
        if label == "recall_name":
            if self.name_given:
                return recall_name()
            else:
                return no_name_to_recall()
        
        # Small talk
        if label == "small_talk":
            self.wait_user_input = True
            return small_talk()
        
        if label == "user_feeling_positive":
            if self.wait_user_input:
                self.wait_user_input = False
                return user_feeling_positive()
            return fallback()
        
        if label == "user_feeling_negative":
            if self.wait_user_input:
                self.wait_user_input = False
                return user_feeling_negative()
            return fallback()
        
        # Low confidence handling
        if label is None or intent_score < self.low_confidence:
            return fallback()
        
        if self.low_confidence <= intent_score < self.high_confidence:
            return prompt_again(matched_example)
            
        self.wait_user_input = False
        return fallback()
