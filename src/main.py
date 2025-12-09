from intent_handlers.non_game_intents_handler import IntentHandler
from responses import (fallback, goodbye_saved_name, 
                       goodbye_no_saved_name, ask_name, 
                       greeting_again, goodbye_only)
from storage import load_name_decision, load_name

class UserNameProxy:
    """Helper that always returns the best-known user name."""
    @property
    def value(self):
        return load_name() or "You"

user_name = UserNameProxy()


def main() -> None:
    """
    Entry point for the chatbot.

    Responsibilities:
        - Initialise the intent handler.
        - Decide the initial greeting based on whether the user allowed their name to be saved previously.
        - Run the main input/output loop:
            - read user input,
            - call IntentHandler.handle_intent.
            - handle special control tokens for ending the conversation,
            - print bot responses.
    """
    
    intent_handler = IntentHandler()

    # Decide initial greeting based on stored name decision
    decision = load_name_decision()
    if decision is True:
        print(greeting_again())
    else:
        print(ask_name())

    while True:
        # Decides which name to show in the prompt:
        # 1) saved name from storage
        # 2) fallback to generic "You"
        display_name =  user_name.value
        
        user_input = input(f"{display_name}: ").strip()
        response = intent_handler.handle_intent(user_input)
        
        # Special control tokens returned by IntentHandler when user quits

        # Name is not saved and session ends
        if response == "no_saved_name_and_end":
            print(goodbye_no_saved_name())
            break
        # Name is saved and session ends
        if response == "save_name_and_end":
            print(goodbye_saved_name())
            break
        
        # No name to save just ends session
        if response == "end":
            print(goodbye_only())
            break
        
        # Normal bot responses
        if response:
            print(response)
        else:
            # Fallback if nothing was returned
            print(fallback())


if __name__ == "__main__":
    main()