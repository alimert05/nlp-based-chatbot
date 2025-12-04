import config
from typing import Optional

from engines.name_engine import NameRecogniser
from engines.qa_engine import QaEngine
from engines.games_engine import GamesEngine
from engines.intent_engine import IntentEngine
from storage import (load_name, save_name, reset_name, 
        save_name_decision, load_name_decision, reset_purchased_game)
from responses import (
    recall_name, greeting, fallback, greeting_back, support, small_talk,
    user_feeling_positive, user_feeling_negative, qa_answers, prompt_again,
    ask_name_again, name_refused, no_name_to_recall, 
    ask_save_name, name_already_given,
    no_name_change_or_remove, name_changed, ask_new_name, name_known, 
    confirm_name_change, name_removed, no_name_to_change, no_name_to_remove, ask_remove_name,
    error_name_change_confirmation, error_name_remove_confirmation, back_from_goodbye, same_as_old_name,
    back_from_name_change, error_ask_save_name
)
from intent_handlers.game_intents_handler import GamesHandler

class IntentHandler:
    
    def __init__(self, intent_path: str = config.INTENTS_PATH) -> None:
    
        # Thresholds
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
        self.game_handler = GamesHandler()

        # State management
        self._init_state()

    # State Initialisation
    def _init_state(self):
        self.wait_user_input = False

        # Name handling
        self.name_refused = False
        self.change_name = False
        self.new_name_given = False
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
        self.goodbye_process = False
        self.goodbye_error = False
        self.greeting_process = False

    # Remove everything from the FIRST comma onward
    def _clean_user_input(self, text: str) -> str:
        return text.split(",", 1)[0].strip()

    # Main Dispatch
    def handle_intent(self, user_input: str) -> Optional[str]:
        """Main intent handling logic"""
        # Get intent match
        user_input = self._clean_user_input(user_input)
        label, intent_score, matched_example = self.intent_engine.match(user_input)

        # Get QA engine response
        answer, qa_score, document, best_idx = self.qa_engine.search(user_input)

        # Extract cleaned-up game query from template
        game_query = self.games_engine._extract_game_query_from_example(user_input, matched_example or "")

        # Game mode handling - Check if we're already in game mode
        if self.game_handler.is_game_intent(label):
            return self.game_handler.handle_game_intent(label, user_input, game_query)
            
        # QA engine queries (non-game mode only)
        if qa_score >= self.qa_threshold:
            if label is None or qa_score + self.qa_bonus > intent_score:
                return self._handle_qa_answer(answer, document, best_idx)
        
        # Purchase history
        if label == "purchase_history":
            return self.game_handler._handle_purchase_history()
        
        if label == "delete_purchase_history":
            return self.game_handler._handle_reset_purchase_history()

        # Game intents
        if self.game_handler.is_game_intent(label):
            return self.game_handler.handle_game_intent(label, user_input, game_query)
        
        # Non-game mode intents
        return self._handle_non_game_mode(label, user_input, matched_example, intent_score)
    
    # Non-game Intents
    def _handle_non_game_mode(self, label: str, user_input: str, matched_example: str, 
                             intent_score: float) -> str:
        """Handle all non-game mode intents"""

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
        
         # Name handling
        if self.waiting_name_confirmation:
            self.waiting_name_confirmation = False
            return self._explicit_name_change(label, user_input, None)
        
        if self.change_name:
            return self._handle_name_change(label, user_input)
        
        if self.waiting_name_remove_confirmation:
            self.waiting_name_remove_confirmation = False
            return self._handle_remove_name(label, user_input)
        
        if self.explicit_change_flow:
            if label == "introduce_self":
                self.explicit_change_flow = False
                self.waiting_name_confirmation = True
                return self._explicit_name_change(label, user_input, matched_example)
            return fallback()
        
        if not self.explicit_change_flow and label == "introduce_self":
            return self._handle_introduction(user_input, matched_example)

        if label == "change_name":
            if self.name_given is False:
                return no_name_to_change()
            self.explicit_change_flow = True
            return ask_new_name()
        
        if label == "back" and self.explicit_change_flow:
            return self._handle_back_name_flow()
        
        if label == "remove_name":
            self.waiting_name_remove_confirmation = True
            return ask_remove_name()

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
        
        # Low confidence handling
        if label is None or intent_score < self.low_confidence:
            return fallback()
        
        if self.low_confidence <= intent_score < self.high_confidence:
            return prompt_again(matched_example)
            
        self.wait_user_input = False
        return fallback()

    # Goodbye / End Session
    def _handle_goodbye_process(self, label: str) -> bool:
        """Mark that we are in the goodbye process if user wants to quit."""
        if label == "quit":
            self.goodbye_process = True
        return self.goodbye_process

    def _process_goodbye(self, label: str, user_input: str) -> str:
        """Handle goodbye name-saving decision."""
        if self.name_given:
            if label == "confirm_negative" or user_input.lower() == "no":
                save_name_decision(False)
                reset_name()
                reset_purchased_game()
                self.goodbye_process = False
                return "no_saved_name_and_end"

            if label == "confirm_positive" or user_input.lower() == "yes":
                save_name_decision(True)
                self.goodbye_process = False
                return "save_name_and_end"
            
            if self.goodbye_error:
                return error_ask_save_name()
            self.goodbye_error = True
            return ask_save_name()

        return "end"
    
    def _handle_back_goodbye_process(self) -> str:
        self.goodbye_process = False
        self.goodbye_error = False
        return back_from_goodbye()

    # Name Handling
    def _handle_introduction(self, user_input: str, matched_example: str) -> str:
        """Handle user introduction and name changing."""
        normalised_input = self.name_recogniser.normalise_intro(user_input, matched_example)
        extracted_name = self.name_recogniser.extract_name(normalised_input)
        
        if self.name_given is False:
            if extracted_name:
                self.name_given = True
                save_name(extracted_name)
                self.username = extracted_name
                return greeting(extracted_name)
            return ask_name_again()
        
        if extracted_name.lower() == str(self.username).lower():
            return name_known()
        self.change_name = True
        self.new_username = extracted_name
        return name_already_given(self.new_username)
    
    def _handle_name_change(self, label: str, user_input: str) -> str:
        """Name changing confirmation."""
        if user_input.lower() == "yes" or label == "confirm_positive":
            self.change_name = False
            self.name_given = True
            save_name(self.new_username)
            self.username = self.new_username
            return name_changed()
        if user_input.lower() == "no" or label == "confirm_negative":
            self.change_name = False
            self.new_name_given = False
            return no_name_change_or_remove()
        return error_name_change_confirmation()
    
    def _explicit_name_change(self, label: str, user_input: str, matched_example: Optional[str]) -> str:
        """Handle explicit name change logic."""
        if self.waiting_name_confirmation:
            normalised_input = self.name_recogniser.normalise_intro(user_input, matched_example)
            extracted_name = self.name_recogniser.extract_name(normalised_input)
            if extracted_name.lower() == str(self.username).lower():
                self.waiting_name_confirmation = False
                self.explicit_change_flow = True
                return same_as_old_name()
            self.pending_new_name = extracted_name
            return confirm_name_change(extracted_name)
        
        if user_input.lower() == "yes" or label == "confirm_positive":
            self.waiting_name_confirmation = False
            self.explicit_change_flow = False
            save_name(self.pending_new_name)
            self.username = self.pending_new_name
            return name_changed()
        
        if user_input.lower() == "no" or label == "confirm_negative":
            self.waiting_name_confirmation = False
            return no_name_change_or_remove()
        
        return error_name_change_confirmation()
    
    def _handle_back_name_flow(self) -> str:
        self.explicit_change_flow = False
        return back_from_name_change()
    
    def _handle_remove_name(self, label: str, user_input: str) -> str:
        """Handle user wants to remove their name."""
        # text = user_input.strip().lower()

        if self.name_given:
            if user_input.lower() == "yes" or label == "confirm_positive":
                self.name_given = False
                reset_name()
                return name_removed()
            if user_input.lower() == "no" or label == "confirm_negative":
                return no_name_change_or_remove()
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
    