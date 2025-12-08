import config
from typing import Optional

from engines.name_engine import NameRecogniser
from engines.qa_engine import QaEngine
from engines.games_engine import GamesEngine
from engines.intent_engine import IntentEngine
from storage import (load_name, save_name, reset_name, 
        save_name_decision, load_name_decision, reset_purchased_game, load_search_history, 
        save_search_query, reset_search_history)
from responses import (
    recall_name, greeting, fallback, greeting_back, support, small_talk,
    user_feeling_positive, user_feeling_negative, qa_answers, prompt_again,
    ask_name_again, name_refused, no_name_to_recall, 
    ask_save_name, name_already_given,
    no_name_change_or_remove, name_changed, ask_new_name, name_known, 
    confirm_name_change, name_removed, no_name_to_change, no_name_to_remove, ask_remove_name,
    error_name_change_confirmation, error_name_remove_confirmation, back_from_goodbye, same_as_old_name,
    back_from_name_change, error_ask_save_name, unrelated_prompt, show_search_history, no_search_history, 
    invalid_search_history_selection, back_from_search_history
)
from intent_handlers.game_intents_handler import GamesHandler

class IntentHandler:
    """
    Top-level intent router / state machine.

    Responsibilities:
    - Route user input between:
        * game flow (GamesHandler)
        * QA flow (course Q&A)
        * name handling (introduce / change / remove)
        * small talk and emotional follow-ups
        * goodbye / end-session flow
    - Maintain cross-turn state such as:
        * whether the user gave their name
        * explicit name change flow
        * goodbye flow (save name or not)
        * small-talk follow-up (positive/negative)
    """
    
    def __init__(self, intent_path: str = config.INTENTS_PATH) -> None:
    
        # Confidence thresholds
        self.high_confidence = 0.70
        self.low_confidence = 0.40

        # Engines
        self.name_recogniser = NameRecogniser()
        self.qa_engine = QaEngine()
        self.games_engine = GamesEngine()
        self.intent_engine = IntentEngine(
            intent_path=intent_path,
            threshold=0.50,
            high_confidence_intents={"greet", "discover", "small_talk"},
        )
        self.game_handler = GamesHandler()

        # State management
        self._init_state()

    # State Initialisation
    def _init_state(self):
        """Initialise all per-session state variables"""
        # Unrelated intent check
        self.count = False

        # Search history flow
        self.waiting_search_history_selection = False
        self._replay_mode = False

        # For small-talk follow-up (positive/negative feelings)
        self.wait_user_input = False

        # Name handling (implicit flow)
        self.name_refused = False # True if user refused to give name earlier
        self.change_name = False # True if user is in simple yes/no name change confirmation
        self.normalised_name = Optional[str] 
        self.extracted_name = Optional[str]

        # Explicit name-change flow
        self.explicit_change_flow = False
        self.pending_new_name: Optional[str] = None 
        self.waiting_name_confirmation = False  
        self.waiting_name_remove_confirmation = False

        # Name decision handling (persistent)
        self.decision = load_name_decision() # True / False / None
        self.username = load_name() # Stored username if any
        self.new_username = None # For simple name-change flow
        self.name_given = True if self.decision is True else False

        # Goodbye / greeting flow
        self.goodbye_process = False
        self.goodbye_error = False
        self.greeting_process = False

    # Remove everything from the FIRST comma onward
    def _clean_user_input(self, text: str) -> str:
        return text.split(",", 1)[0].strip()

    # Main Dispatch
    def handle_intent(self, user_input: str) -> Optional[str]:
        """
        Main intent handling logic

        Steps:
        1. Clean input and detect top-level intent
        2. Run QA engine for potential knowledge-based answers
        3. Route to:
            - games handler,
            - purchase history,
            - or non-game intent handler.
        """
        
        user_input = self._clean_user_input(user_input)

        # If user is selecting from search history (OPTIONAL mode)
        if self.waiting_search_history_selection:
            # User explicitly cancels
            if user_input.lower() == "back":
                self.waiting_search_history_selection = False
                return back_from_search_history()

            # User chose an index
            if user_input.isdigit():
                history = load_search_history()
                idx = int(user_input) - 1

                if 0 <= idx < len(history):
                    self.waiting_search_history_selection = False

                    # prevent double-logging when replaying
                    self._replay_mode = True
                    try:
                        return self.handle_intent(history[idx])
                    finally:
                        self._replay_mode = False

                # Only error case you want
                return invalid_search_history_selection()

            # Anything else: exit mode and continue normally
            self.waiting_search_history_selection = False
            
        # Get intent match
        label, intent_score, matched_example = self.intent_engine.match(user_input)

        # Now log if appropriate
        if not self._replay_mode and self._should_log_search(label, user_input):
            save_search_query(user_input)

        # Get QA engine response
        answer, qa_score, document, best_idx = self.qa_engine.search(user_input)

        # Extract cleaned-up game query from template
        game_query = self.games_engine._extract_game_query_from_example(user_input, matched_example or "")

        # Game mode handling - Check if we're already in game mode
        if self.game_handler.is_game_intent(label):
            return self.game_handler.handle_game_intent(label, user_input, game_query)
            
        # QA engine queries (non-game mode only)
        if qa_score > intent_score:
            return self._handle_qa_answer(answer, document, best_idx)
        
        # Purchase history
        if label == "purchase_history":
            return self.game_handler._handle_purchase_history()
        
        if label == "delete_purchase_history":
            return self.game_handler._handle_reset_purchase_history()

        # Game intents
        if self.game_handler.is_game_intent(label):
            return self.game_handler.handle_game_intent(label, user_input, game_query)
        
        if self.low_confidence <= intent_score < self.high_confidence:
            # Ask user to rephrase
            return prompt_again(matched_example)
        
        # Low confidence handling
        if label is None:
            return fallback()
        
        # Non-game mode intents
        return self._handle_non_game_mode(label, user_input, matched_example)
    
    # Non-game Intents
    def _handle_non_game_mode(self, label: str, user_input: str, matched_example: str) -> str:
        """
        handle all non-game intents:
        - greeting / discover / small talk
        - name introduction / recall / change / remove 
        - goodbye flow and name-saving decision
        - low-confidence fallback
        """

        # User refuses to give name
        if self.name_given is False and self.name_refused is False:
            if label == "name_refuse":
                self.greeting_process = False
                self.name_refused = True
                return name_refused()
            else:
                self.greeting_process = False
                self.name_refused = True
        
        # Goodbye flow
        if label == "back" and self.goodbye_process:
            return self._handle_back_goodbye_process() 
        
        if self._handle_goodbye_process(label):
            return self._process_goodbye(label, user_input)
        
        # --- Explicit name-change flow ---
        # Step 0: user starts the flow
        if label == "change_name":
            if not self.name_given:
                return no_name_to_change()
            # We are now in the explicit change-name flow
            self.explicit_change_flow = True
            self.waiting_name_confirmation = False
            self.pending_new_name = None
            return ask_new_name()  # "Tell me your new name or type 'back'."

        # Step 1 & 2: we are already in the explicit change-name flow
        if self.explicit_change_flow:
            # User wants to cancel at any point
            if label == "back":
                return self._handle_back_name_flow()

            # If we are currently waiting for YES/NO confirmation
            if self.waiting_name_confirmation:
                # Let _explicit_name_change handle yes/no/invalid
                return self._explicit_name_change(label, user_input, None)

            # Otherwise, we are waiting for the NEW NAME itself
            if label == "introduce_self":
                # User is giving their new name sentence
                return self._explicit_name_change(label, user_input, matched_example)

            if self.count:
                self.count = False
                self.explicit_change_flow = False
                return unrelated_prompt()
            
            # Anything else here means: user didn't give a name,
            # so remind them what to do.
            self.count = True
            return ask_new_name()
        
        # Simple name-change flow (not explicit multi-step)
        if self.change_name:
            return self._handle_name_change(label, user_input)
        
        # Remove-name confirmation flow
        if self.waiting_name_remove_confirmation:
            return self._handle_remove_name(label, user_input)
        
        # Normal introduction (when user not in explicit change flow)
        if not self.explicit_change_flow and label == "introduce_self":
            return self._handle_introduction(user_input, matched_example)
        
        # Back from explicit-change flow 
        if label == "back" and self.explicit_change_flow:
            return self._handle_back_name_flow()
        
        # Start remove-name confirmation flow
        if label == "remove_name":
            self.waiting_name_remove_confirmation = True
            return ask_remove_name()
        
        # Search history
        if label == "search_history":
            history = load_search_history()
            if not history:
                return no_search_history()

            self.waiting_search_history_selection = True
            return show_search_history(history)

        if label == "delete_search_history":
            reset_search_history()
            self.waiting_search_history_selection = False
            return "Bot: I've cleared your search history."

        # Discover capabilities
        if label == "discover":
            return support()
        
        # Simple greeting
        if label == "greet":
            return greeting_back(matched_example)

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
        
        # No specific handler above -> generic fallback
        self.wait_user_input = False
        # return fallback()

    # Goodbye / End Session
    def _handle_goodbye_process(self, label: str) -> bool:
        """
        Mark that we are in the goodbye process if user wants to quit
         - Resets any active game buying state so that the session can end cleanly.
        """
        if label == "quit":
            self.goodbye_process = True
            self.game_handler._reset_buying_state()
        return self.goodbye_process

    def _process_goodbye(self, label: str, user_input: str) -> str:
        """
        Handle goodbye flow where the bot asks:
        - whether to save the user's name for next time.

        Returns: 
        - "save_name_and_end" or "no_saved_name_and_end" control tokens
        - or "end" if no name is known
        """
        if self.name_given:
             
            if label == "confirm_negative" or user_input.lower() == "no":
                save_name_decision(False)
                reset_name()
                reset_purchased_game()
                self.goodbye_process = False
                return "no_saved_name_and_end"

            if label == "confirm_positive":
                save_name_decision(True)
                self.goodbye_process = False
                return "save_name_and_end"
            
            # If no clear response 
            if self.goodbye_error:
                return error_ask_save_name()
            
            if self.count:
                self.count = False
                self.goodbye_process = False
                self.goodbye_error = False
                return unrelated_prompt()
            
            self.count = True
            self.goodbye_error = True
            return ask_save_name()

        # If there is no name stored, just end the conversation
        return "end"
    
    def _handle_back_goodbye_process(self) -> str:
        """
        Handle 'back' inside the goodbye flow:
        - Cancel goodbye and go back to normal mode.
        """
        self.goodbye_process = False
        self.goodbye_error = False
        return back_from_goodbye()

    # Name Handling
    def _handle_introduction(self, user_input: str, matched_example: str) -> str:
        """
        Handle user introduction and name changing in the simple flow:
        - If no name known -> store new name.
        - If same as stored name -> respond with 'I already know your name'.
        - If different -> ask user if they want to change to the new name.
        """
        normalised_input = self.name_recogniser.normalise_intro(user_input, matched_example)
        extracted_name = self.name_recogniser.extract_name(normalised_input)
        
        # First time giving name
        if self.name_given is False:
            if extracted_name:
                self.name_given = True
                save_name(extracted_name)
                self.username = extracted_name
                return greeting(extracted_name)
            return ask_name_again()
        
        # Name already known and user repeats the same
        if extracted_name.lower() == str(self.username).lower():
            return name_known()
        
        # Different name -> enter simple confirmation flow
        self.change_name = True
        self.new_username = extracted_name
        return name_already_given(self.new_username)
    
    def _handle_name_change(self, label: str, user_input: str) -> str:
        """
        Simple name-change confirmation:
        - 'yes' / confirmation positive -> save new username
        - 'no' / confirmation_negative -> keep old name
        """
        if label == "confirm_positive":
            self.change_name = False
            self.name_given = True
            save_name(self.new_username)
            self.username = self.new_username
            return name_changed()
        
        if label == "confirm_negative":
            self.change_name = False
            return no_name_change_or_remove()
        
        if self.count:
            self.count = False
            self.change_name = False
            return unrelated_prompt()
        
        self.count = True
        return error_name_change_confirmation()
    
    def _explicit_name_change(self, label: str, user_input: str, matched_example: Optional[str]) -> str:
        """Handle explicit name change logic.

        Two phases:
        1) Not waiting_name_confirmation -> expecting the NEW NAME.
        2) waiting_name_confirmation -> expecting YES/NO to confirm the new name.
        """
        # self.count = False

        # --- PHASE 1: expecting the NEW NAME ---
        if not self.waiting_name_confirmation:
            normalised_input = self.name_recogniser.normalise_intro(user_input, matched_example)
            extracted_name = self.name_recogniser.extract_name(normalised_input)
            self.count = False
            
            # No name detected -> ask again
            if not extracted_name:
                self.count = True
                # Message should tell user: "Please tell me your new name or type 'back'."
                return ask_new_name()

            # If the new name is the same as old one
            if self.username and extracted_name.lower() == str(self.username).lower():
                # Stay in the explicit_change_flow but do NOT move to confirmation
                return same_as_old_name()

            # Store new name and move to confirmation phase
            self.pending_new_name = extracted_name
            self.waiting_name_confirmation = True
            return confirm_name_change(extracted_name)

        # --- PHASE 2: expecting YES / NO confirmation ---
        if label == "confirm_positive":
            # User confirmed the new name
            self.waiting_name_confirmation = False
            self.explicit_change_flow = False
            if self.pending_new_name:
                save_name(self.pending_new_name)
                self.username = self.pending_new_name
            self.count = False
            return name_changed()

        if label == "confirm_negative":
            # User rejected the change -> do nothing and exit flow
            self.waiting_name_confirmation = False
            self.explicit_change_flow = False
            self.pending_new_name = None
            self.count = False
            return no_name_change_or_remove()

        # If user types "back" here, we handle it outside via _handle_back_name_flow,
        # so reaching here means: not yes / not no / not back.
        # Ask them again to confirm or type back.
        if self.count:
            self.count = False
            self.waiting_name_confirmation = False
            self.explicit_change_flow = False
            self.pending_new_name = None
            return unrelated_prompt()
        
        self.count = True
        return error_name_change_confirmation()  # e.g. "Please say yes, no, or 'back' to cancel."
    
    def _handle_back_name_flow(self) -> str:
        """Cancel the explicit name-change flow and go back to normal.
        Resets explicit_change_flow and pending_new_name so user can start over
        """
        self.explicit_change_flow = False
        self.waiting_name_confirmation = False
        self.pending_new_name = None
        return back_from_name_change()
    
    def _handle_remove_name(self, label: str, user_input: str) -> str:
        """
        Handle user confirmation when they want to remove their stored name:
        - 'yes' / confirm_positive -> remove name and clear decision
        - 'no' / confirm_negative  -> keep name
        """
        if self.name_given:
            if self.count:
                self.count = False
                self.waiting_name_remove_confirmation = False
                return unrelated_prompt()
            if label == "confirm_positive":
                self.waiting_name_remove_confirmation = False
                self.name_given = False
                save_name_decision(False)
                reset_name()
                return name_removed()
            if label == "confirm_negative":
                self.waiting_name_remove_confirmation = False
                return no_name_change_or_remove()
            self.count = True
            return error_name_remove_confirmation()
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
    
    def _should_log_search(self, label: Optional[str], user_input: str) -> bool:
        text = user_input.strip().lower()

        if not text or text.isdigit():
            return False

        if label in {"small_talk", "greet", "discover"}:
            return False
        
        if label in {
            "search_history", "delete_search_history",
            "quit", "back",
            "confirm_positive", "confirm_negative"
        }:
            return False

        return True
    