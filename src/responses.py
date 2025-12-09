from typing import Optional, List, Tuple
import random
from collections import defaultdict
from storage import load_name, save_purchased_game



class UserNameProxy:
    """Helper that always returns the best-known user name."""
    @property
    def value(self):
        return load_name() or "user"

user_name = UserNameProxy()

MAX_FILTER_RESULTS = 20

def _limit_filtered_lines(lines: List[str]) -> Tuple[List[str], int, bool]:
    total = len(lines)
    if total > MAX_FILTER_RESULTS:
        return random.sample(lines, MAX_FILTER_RESULTS), total, True
    return lines, total, False

def _filtered_notice(total: int, truncated: bool) -> str:
    if truncated:
        return f"{total} games found. Printing {MAX_FILTER_RESULTS} of them to keep the list readable.\n"
    return f"{total} games found.\n"

# ===== BASIC RESPONSES =====
# Name responses
def ask_name() -> str:
    return "Bot: Welcome to the GAMES SHOP Before we start, could you please tell me your name so I can address you properly?"

def name_already_given(new_username) -> str:
    return f"Bot: You have already gave your name as {user_name.value}. Would you like to change it to {new_username}?"

def confirm_name_change(new_name: str) -> str:
    return f"Bot: Do you confirm your new name: {new_name}? (yes/no)"

def back_from_name_change() -> str:
    return f"Bot: Okay {user_name.value}. How can I help you?"

def no_name_change_or_remove() -> str:
    return f"Bot: No problem, {user_name.value}. How can I help you today?"

def ask_new_name() -> str:
    return "Bot: Sure, what name would you like me to use for you?"

def name_known() -> str:
    return f"Bot: Yes, I remember your name, {user_name.value}. How can I help you today?"

def same_as_old_name() -> str:
    return f"Bot: It is same as your old name: {user_name.value}. Please provide a different name, or type 'back'."

def name_changed() -> str:
    return f"Bot: Great, I've successfully changed your name to {user_name.value}. How can I help you today?"

def recall_name() -> str:
    return f"Bot: Your name is {user_name.value}"

def ask_remove_name() -> str:
    return "Bot: Just to confirm — would you like me to remove your saved name?"

def name_removed() -> str:
    return "Bot: I've successfully removed your name."

def no_name_to_remove() -> str:
    return "Bot: I can't remove your name because you haven't provided one yet."

def no_name_to_change() -> str:
    return "Bot: You haven't provided your name yet. Would you like to tell me, so I can address you properly?"

def no_name_to_recall() -> str:
    return "Bot: Sorry, you haven't provided your name yet."

# Update this as error handler
def ask_name_again() -> str:
    return "Bot: Would you like to tell me your name so I can address you properly?"

def name_refused() -> str:
    return "Bot: That's completely fine. How can I help you today?"

def ask_save_name() -> str:
    return ("Bot: Before you go, would you like me to save your name for next time? "
            "(yes/no)\nIf you want to continue chatting instead, just type 'back'.")

def error_ask_save_name() -> str:
    return "Bot: Please answer with 'yes' or 'no', if you want to continue to chat you can type 'back'."

def error_name_change_confirmation() -> str:
    return f"Bot: Please answer with 'yes' if you'd like to change your name, or 'no' if you'd like to keep it, {user_name.value}."

def error_name_remove_confirmation() -> str:
    return f"Bot: Please answer with 'yes' if you'd like to remove your name, or 'no' if you'd like to keep it, {user_name.value}."
    
def greeting_back(user_input: str) -> str:
    user_input = user_input.capitalize()
    return f"Bot: {user_input}, {user_name.value}. How can I help you?"

def greeting(name: Optional[str]) -> str:
    if name:
        return f"Bot: Hi {name}! Nice to meet you. How can I help you today?"
    return "Bot: I didn't quite catch your name. Please say something like 'I am John' or 'My name is John Smith'"

def greeting_again() -> str:
    return f"Bot: Welcome back to the GAMES SHOP {user_name.value}! How can I help you today?"

def support() -> str:
    return (
        f"\nBot: Hi {user_name.value}! Here's a clear guide to everything you can do with me.\n"

        "\n════════════════════════════════════\n"
        "💬 1) General chat & course Q&A\n"
        "════════════════════════════════════\n"
        "- You can say hello, ask how I am, or just chat casually.\n"
        "- I can answer questions from my knowledge base (course Q&A).\n"
        "\nExamples:\n"
        "- \"hi\"\n"
        "- \"how are you\"\n"
        "- \"what is a process?\"\n"
        "- \"explain deadlock\"\n"
        "\nTip:\n"
        "- Type \"help\" anytime to see this menu again.\n"

        "\n════════════════════════════════════\n"
        "👤 2) Your name (optional)\n"
        "════════════════════════════════════\n"
        "- You can tell me your name if you want.\n"
        "- I can remember it for next time only if you agree.\n"
        "- You can also change or remove your name.\n"
        "\nExamples:\n"
        "- \"my name is Ali\"\n"
        "- \"what is my name?\"\n"
        "- \"I want to change my name\"\n"
        "- \"remove my name\"\n"

        "\n════════════════════════════════════\n"
        "🎮 3) Browsing and searching games\n"
        "════════════════════════════════════\n"
        "You can explore games in many ways:\n"
        "- Ask what games I have.\n"
        "- Search by name.\n"
        "- Filter by platform, genre, price, critic score, or release year.\n"
        "- Ask for extremes (cheapest, newest, highest rated, etc.).\n"
        "\nExamples:\n"
        "- \"what games do you have?\"\n"
        "- \"do you have Call of Duty?\"\n"
        "- \"show me games for PS5\"\n"
        "- \"show me action games\"\n"
        "- \"games under 20 pounds\"\n"
        "- \"games with rating above 8\"\n"
        "- \"games released after 2015\"\n"
        "- \"show me the cheapest games\"\n"
        "- \"show me the newest games\"\n"
        "\nYou can also list categories:\n"
        "- \"list all platforms\"\n"
        "- \"list all genres\"\n"

        "\n════════════════════════════════════\n"
        "🛒 4) Buying a game (step-by-step)\n"
        "════════════════════════════════════\n"
        "To start buying, say:\n"
        "- \"let me buy The Last of Us\"\n"
        "- \"I want to buy Call of Duty\"\n"
        "\nWhat I will do:\n"
        "1) If multiple games match, I show a numbered list.\n"
        "2) You choose a game by number.\n"
        "3) If the game has multiple platforms, I show platform + price options.\n"
        "4) You choose a platform by number.\n"
        "5) I ask you to confirm.\n"
        "\nAt confirmation, you can answer:\n"
        "- \"yes\" to buy\n"
        "- \"no\" to cancel\n"
        "- \"back\" to go one step up\n"

        "\n════════════════════════════════════\n"
        "🔁 5) Going back & changing your mind\n"
        "════════════════════════════════════\n"
        "- You can always type \"back\" to go one step back in multi-turn conversations.\n"
        "- \"I don't want games\" exits game transaction completely.\n"

        "\n════════════════════════════════════\n"
        "🧾 6) Purchase history\n"
        "════════════════════════════════════\n"
        "I store your recent purchases as a list.\n"
        "You can ask:\n"
        "- \"what did I buy?\"\n"
        "- \"show my purchase history\"\n"
        "\nYou can also clear it:\n"
        "- \"delete purchase history\"\n"

        "\n════════════════════════════════════\n"
        "⭐ 7) Personalised recommendations\n"
        "════════════════════════════════════\n"
        "After you buy games, you can ask for personalised suggestions.\n"
        "I will:\n"
        "- Look at your most recent purchased game.\n"
        "- Use its genre and platform.\n"
        "- Recommend up to 10 similar games.\n"
        "\nExample:\n"
        "- \"recommend a game\"\n"

        "\n════════════════════════════════════\n"
        "🕵️ 8) Search history\n"
        "════════════════════════════════════\n"
        "I can remember what you searched for (without duplicates).\n"
        "You can ask:\n"
        "- \"search history\"\n"
        "\nI will show a numbered list.\n"
        "You can:\n"
        "- Type a number to repeat that search.\n"
        "- Type \"back\" to exit the list.\n"
        "- Or type anything else to continue normally.\n"
        "\nTo clear it:\n"
        "- \"delete search history\"\n"

        "\n════════════════════════════════════\n"
        "🚪 9) Ending the chat\n"
        "════════════════════════════════════\n"
        "- You can say \"bye\" or \"quit\" to end the session.\n"
        "- If you gave me your name, I may ask whether you want me to save it.\n"

        "\nBot: That's everything! You can start with something simple like:\n"
        "- \"what games do you have?\"\n"
        "- \"recommend a game\"\n"
        "- \"show me action games\"\n"
        "- \"show me the best game\"\n"
        f"\nBot: I'm ready when you are, {user_name.value}.\n"
    )

def small_talk() -> str:
    return f"Bot: I'm doing great {user_name.value}, thanks for asking! How about you?"

def user_feeling_positive() -> str:
    return f"Bot: I am glad to hear that, {user_name.value}."

def user_feeling_negative() -> str:
    return f"Bot: I am sorry to hear that, {user_name.value}. I hope things get better soon."

# Some questions have multiple answers, so it returns random answers from answer list
def qa_answers(answer_list: List[str]) -> str:
    if not answer_list:
        return fallback()
    return f"Bot: {random.choice(answer_list)}"

def goodbye_saved_name() -> str:
    return f"Bot: I've saved your name for future sessions. Goodbye, {user_name.value} - hope to see you soon."

def goodbye_no_saved_name() -> str:
    return f"Bot: I've deleted your name. Goodbye {user_name.value}, hope to see you again."

def goodbye_only() -> str:
    return "Bot: Goodbye, I hope to see you again."

def back_from_goodbye() -> str:
    return f"Bot: Sure, how can I help you {user_name.value}?"

def prompt_again(matched_example: Optional[str]) -> str:
    pretty_example = matched_example.replace('_', ' ')
    return f"Bot: I think you might trying to say: '{pretty_example}'. If that's not what you meant, you can type 'help' to see what I can do." 

def unrelated_prompt() -> str:
    return "Bot: I think you are trying to do something else. How can I help you?"

def no_search_history() -> str:
    return "Bot: You don't have any search history yet."

def show_search_history(history: List[str]) -> str:
    lines = [f"{i+1}. {q}" for i, q in enumerate(history)]
    return (
        "Bot: Here is your search history:\n"
        + "\n".join(lines)
        + "\n\nBot: You can select the number from the list, or type back."
    )

def invalid_search_history_selection() -> str:
    return "Bot: Please select a valid number from the list, or type 'back'."

def back_from_search_history() -> str:
    return "Bot: Okay, back to normal mode."

def fallback() -> str:
    return f"Bot: I'm not sure I understand that, {user_name.value}. You can say something like 'what can you do?' to see your options."

# ===== GAME MODE RESPONSES =====
def recommend_games_personalised(bought_title: str, bought_platform: str, bought_genre: str, rec_titles: List[str]) -> str:
    lines = [f"- {t} ({bought_platform})" for t in rec_titles]

    return (
        f"Bot: You previously bought {bought_title} on {bought_platform}, "
        f"which is in the {bought_genre} genre.\n"
        f"Here are some {bought_genre} games you might like on {bought_platform}:\n"
        + "\n".join(lines)
    )

def no_games_to_recommend(bought_title: str, bought_platform: str, bought_genre: str) -> str:
    return (
                f"Bot: You previously bought {bought_title} on {bought_platform} "
                f"({bought_genre}). I couldn't find new recommendations that you haven't already purchased."
            )
    
def no_game_found():
    return f"Bot: Sorry {user_name.value}, I couldn't find any games that match that. Please try another name or a different filter."

def ask_game_disambiguation(candidates: List[dict]) -> str:
    if not candidates:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games matching that name."
    
    lines = []
    for i, c in enumerate(candidates):
        platform_list = ", ".join(c["platforms"])
        lines.append(f"{i+1}. {c['title']} - Platforms: {platform_list}")

    result = "\n".join(lines)
    return f"Bot: Okay {user_name.value}, I found multiple games that could match what you asked for:\n{result}\nPlease reply with the number of the game you're interested in, or type 'back' if you want to another game."

def ask_platform_disambiguation(game_title: str, platforms: List[str], prices: Optional[List[float]] = None) -> str:
    if prices and len(prices) == len(platforms):
        lines = [f"{i+1}. {p} - £{price:.2f}" for i, (p, price) in enumerate(zip(platforms, prices))]
    else:
        lines = [f"{i+1}. {p}" for i, p in enumerate(platforms)]
    platforms_str = "\n".join(lines)
    return f"Bot: Okay {user_name.value}, {game_title} is available on multiple platforms:\n{platforms_str}\nPlease reply with the number of the platform you want, or type 'back' if you want to reselect the game."

def back_from_game_selection() -> str:
    return f"Bot: Okay, we've gone back a step. How can I help you now, {user_name.value}?"

def error_selection_invalid(candidate_length: int) -> str:
    return f"Bot: Please reply with a number between 1 and {candidate_length}."

def games_explore() -> str:
    return f"Bot: Sure thing {user_name.value}! You can ask me to search by genre, platform, price, release year, or even look up a specific title."

def user_ends_game_mode() -> str:
    return f"Bot: That's fine, {user_name.value}. We can talk about something other than games. What would you like to do next?"

def confirm_order(selected_game: str, platform: str, price: float) -> str:
    return f"Bot: {selected_game} ({platform}) costs £{price:.2f}. Great choice, {user_name.value}! Would you like to confirm your order? (yes/no/back)"

def error_confirm_oder() -> str:
    return "Bot: Please answer with 'yes' or 'no' if you want to purchase this game, or type back if you want to change your selection."

def game_purchased(selected_game: str, platform: str, price: float) -> str:
    return f"Bot: Thank you for your purchase, {user_name.value}! You bought {selected_game} on {platform} for £{price:.2f}. Have a great day!"

def game_not_purchased() -> str:
    return f"Bot: No worries, {user_name.value}. If you'd like to look for another game, just ask!"

def purchase_history_list(history: List[Tuple[str, str, float]]) -> str:
    lines = []
    for i, (title, platform, price) in enumerate(reversed(history), start=1):
        lines.append(f"{i}. {title} ({platform}) - £{price:.2f}")
    return "Bot: Your recent purchases:\n" + "\n".join(lines)

def purchase_history_deleted() -> str:
    return "Bot: I've successfully deleted your purchase history."

def no_purchase_history() -> str:
    return "Bot: You haven't purchased any games yet."

# ===== GAME LISTING FUNCTIONS =====
def games(titles: List[str]) -> str:
    if not titles:
        return "Bot: I don't have any games in my list at the moment."
    
    k = min(len(titles), 10)
    titles = random.sample(titles, k)

    numbered_titles = [f"{i+1}. {title}" for i, title in enumerate(titles)]
    game_titles = "\n".join(numbered_titles)
    return f"Bot: Here are some games available in the store, {user_name.value}:\n{game_titles}"

def games_by_name(titles: List[str], platforms: List[str], genres: List[str], publishers: List[str], 
                  developers: List[str], critic_scores: List[float], release_dates: List[int], 
                  prices: List[float]) -> str:
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games matching that name."
    
    lines = []
    for title, platform, genre, publisher, developer, score, release, price in zip(
        titles, platforms, genres, publishers, developers, critic_scores, release_dates, prices
    ):
        try:
            price_val = float(price)
            price_str = f"£{price_val:.2f}"
        except (TypeError, ValueError):
            price_str = "N/A"

        genre = genre or "Unknown"
        publisher = publisher or "Unknown"
        developer = developer or "Unknown"
        score_str = f"{score:.1f}" if isinstance(score, (int, float)) else "N/A"
        release_str = str(release) if release else "Unknown"

        lines.append(
            f"{title} | Platform: {platform} | Genre: {genre} | Publisher: {publisher} | "
            f"Developer: {developer} | Critic Score: {score_str} | Release Date: {release_str} | Price: {price_str}"
        )

    shown, total, truncated = _limit_filtered_lines(lines)
    notice = _filtered_notice(total, truncated)
    numbered = [f"{i}. {line}" for i, line in enumerate(shown, start=1)]


    return (
        f"Bot: {user_name.value}, here are the games I found that match your search:\n"
        f"Bot: {notice}"
        + "\n".join(numbered)
    )

# ======= PUBLISHER / DEVELOPER LISTING =======

def games_by_entity(entity_type: str, titles: List[str], entities: List[str]) -> str:
    if not titles or not entities:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games by that {entity_type.lower()}."

    merged = defaultdict(set)
    for title, entity in zip(titles, entities):
        if title and entity:
            merged[entity].add(title)

    lines = []
    for entity, title_set in merged.items():
        lines.append(f"{entity_type}: {entity}")
        for title in sorted(title_set):
            lines.append(title)

    shown, total, truncated = _limit_filtered_lines(lines)
    notice = _filtered_notice(total, truncated)

    # If you want numbering AFTER sampling
    numbered = [f"{i}. {line}" for i, line in enumerate(shown, start=1)]

    return (
        f"Bot: {user_name.value}, here are some games and their {entity_type.lower()}s:\n"
        f"Bot: {notice}"
        + "\n".join(numbered)
    )

def games_by_publisher(titles: List[str], publishers: List[str]) -> str:
    return games_by_entity("Publisher", titles, publishers)

def games_by_developer(titles: List[str], developers: List[str]) -> str:
    return games_by_entity("Developer", titles, developers)

def error_publisher_not_detected() -> str:
    return "Bot: I couldn't recognise that publisher. Try something like 'games by Nintendo' or 'Ubisoft games'."

def error_developer_not_detected() -> str:
    return "Bot: I couldn't recognise that developer. Try something like 'games made by Naughty Dog'."

# ======= PLATFORM / GENRE LISTING =======
def games_list_platforms(platforms: List[str]) -> str:
    if not platforms:
        return f"Bot: I couldn't find any platforms in my catalogue right now, {user_name.value}."
    
    # sort and make a nice bullet list
    unique_sorted = sorted(set(p for p in platforms if p))
    lines = [f"- {p}" for p in unique_sorted]
    listing = "\n".join(lines)
    return (
        f"Bot: {user_name.value}, here are the platforms you can browse games for:\n"
        f"{listing}"
    )

def games_list_genres(genres: List[str]) -> str:
    if not genres:
        return f"Bot: I couldn't find any genres in my catalogue right now, {user_name.value}."
    
    unique_sorted = sorted(set(g for g in genres if g))
    lines = [f"- {g}" for g in unique_sorted]
    listing = "\n".join(lines)
    return (
        f"Bot: {user_name.value}, here are the game genres you can search:\n"
        f"{listing}"
    )
    
def games_by_attribute(attr_name: str, attr_value: str, titles: List[str], attributes: List[str]) -> str:
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games for {attr_value}."

    merged = defaultdict(set)
    for title, attr in zip(titles, attributes):
        merged[title].add(attr)

    lines = []
    for title, attr_set in merged.items():
        attr_list = ", ".join(sorted(attr_set))
        lines.append(f"{title} — {attr_name}: {attr_list}")

    shown, total, truncated = _limit_filtered_lines(lines)
    notice = _filtered_notice(total, truncated)
    numbered = [f"{i}. {line}" for i, line in enumerate(shown, start=1)]

    return (
        f"Bot: {user_name.value}, here are the games for {attr_value}:\n"
        f"Bot: {notice}"
        + "\n".join(numbered)
    )

def games_by_platform(platform: str, titles: List[str], platforms: List[str]) -> str:
    return games_by_attribute("Platforms", platform, titles, platforms)

def games_by_genre(genre: str, titles: List[str], genres: List[str]) -> str:
    return games_by_attribute("Genre", genre, titles, genres)

def error_platform_not_detected() -> str:
    return f"Bot: I didn't catch which platform you meant, {user_name.value}. Try saying 'games for PS4' or 'PC games'."

def error_genre_not_detected() -> str:
    return f"Bot: I didn't catch which genre you meant, {user_name.value}. Try another genre or type 'help'."

# ======== PRICE FILTER RESPONSES ========
def games_cheapest(price: float,
                   titles: List[str],
                   prices: List[float],
                   platforms: List[str]) -> str:
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games right now."

    merged = defaultdict(list)
    for title, p, platform in zip(titles, prices, platforms):
        merged[title].append((platform, float(p)))

    lines = []
    for i, (title, offers) in enumerate(merged.items(), start=1):
        offers_str = ", ".join(f"{platform}: £{p:.2f}" for platform, p in offers)
        lines.append(f"{i}. {title} - {offers_str}")

    result = "\n".join(lines)
    return (
        f"Bot: {user_name.value}, here are the cheapest games at £{price:.2f}:\n"
        f"{result}"
    )

def games_most_expensive(price: float,
                         titles: List[str],
                         prices: List[float],
                         platforms: List[str]) -> str:
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games right now."

    merged = defaultdict(list)
    for title, p, platform in zip(titles, prices, platforms):
        merged[title].append((platform, float(p)))

    lines = []
    for i, (title, offers) in enumerate(merged.items(), start=1):
        offers_str = ", ".join(f"{platform}: £{p:.2f}" for platform, p in offers)
        lines.append(f"{i}. {title} - {offers_str}")

    result = "\n".join(lines)
    return (
        f"Bot: {user_name.value}, here are the most expensive games at £{price:.2f}:\n"
        f"{result}"
    )

def games_by_price_filter(mode: str, price1: float, price2: Optional[float], titles: List[str], prices: List[float], platforms: List[str]) -> str:
    
    mode_messages = {
        "before": f"under £{price1:.2f}",
        "after": f"over £{price1:.2f}",
        "exact": f"at price: £{price1:.2f}",
    }

    if mode == "between" and price2 is not None:
        mode_messages["between"] = f"priced between £{price1:.2f} and £{price2:.2f}"

    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games {mode_messages.get(mode, 'for that price')}."

    merged = defaultdict(list)
    for title, p, platform in zip(titles, prices, platforms):
        merged[title].append((platform, float(p)))

    reverse_sort = (mode == "after")

    items = []
    for title, offers in merged.items():
        offers_sorted = sorted(offers, key=lambda x: x[1])
        key_price = offers_sorted[-1][1] if reverse_sort else offers_sorted[0][1]
        items.append((title, offers_sorted, key_price))

    items_sorted = sorted(items, key=lambda x: x[2], reverse=reverse_sort)

    lines = []
    for title, offers_sorted, _ in items_sorted:
        offers_str = ", ".join(f"{platform}: £{p:.2f}" for platform, p in offers_sorted)
        lines.append(f"{title} - {offers_str}")

    shown, total, truncated = _limit_filtered_lines(lines)
    notice = _filtered_notice(total, truncated)
    numbered = [f"{i}. {line}" for i, line in enumerate(shown, start=1)]

    return (
        f"Bot: {user_name.value}, here are the games {mode_messages[mode]}:\n"
        f"Bot: {notice}"
        + "\n".join(numbered)
    )
def games_by_low_price(price: float, titles: List[str], prices: List[float], platforms: List[str]) -> str:
    return games_by_price_filter("before", price, None, titles, prices, platforms)

def games_by_high_price(price: float, titles: List[str], prices: List[float], platforms: List[str]) -> str:
    return games_by_price_filter("after", price, None, titles, prices, platforms)

def games_by_exact_price(price: float, titles: List[str], prices: List[float], platforms: List[str]) -> str:
    return games_by_price_filter("exact", price, None, titles, prices, platforms)

def games_by_between_prices(low: float, high: float, titles: List[str], prices: List[float], platforms: List[str]) -> str:
    return games_by_price_filter("between", low, high, titles, prices, platforms)

def error_price_not_detected() -> str:
    return f"Bot: I couldn't find a price value in your request, {user_name.value}. Try something like 'games under 20 pounds', or 'games over 20 pounds', or 'games that cost 20 pounds'."

def error_price_range_not_detected() -> str:
    return f"Bot: I couldn't find two price values in your request, {user_name.value}. Try something like 'games between 20 and 40 pounds'."

# ======= SCORE FILTER RESPONSES =======
def games_lowest_score(score: float,
                   titles: List[str],
                   scores: List[float],
                   platforms: List[str]) -> str:
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games right now."

    merged = defaultdict(list)
    for title, cs, platform in zip(titles, scores, platforms):
        merged[title].append((platform, float(cs)))

    lines = []
    for i, (title, offers) in enumerate(merged.items(), start=1):
        offers_str = ", ".join(f"{platform}: {s:.2f}" for platform, s in offers)
        lines.append(f"{i}. {title} - {offers_str}")

    result = "\n".join(lines)
    return (
        f"Bot: {user_name.value}, here are the games with lowest score {score:.2f}:\n"
        f"{result}"
    )

def games_highest_score(score: float,
                         titles: List[str],
                         scores: List[float],
                         platforms: List[str]) -> str:
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games right now."

    merged = defaultdict(list)
    for title, cs, platform in zip(titles, scores, platforms):
        merged[title].append((platform, float(cs)))

    lines = []
    for i, (title, offers) in enumerate(merged.items(), start=1):
        offers_str = ", ".join(f"{platform}: {s:.2f}" for platform, s in offers)
        lines.append(f"{i}. {title} - {offers_str}")

    result = "\n".join(lines)
    return (
        f"Bot: {user_name.value}, here are the games with highest score {score:.2f}:\n"
        f"{result}"
    )

def games_by_score_filter(mode: str, score1: float, score2: Optional[float], titles: List[str], scores: List[float], platforms: List[str]) -> str:

    mode_messages = {
        "below": f"under {score1:.1f}",
        "above": f"over {score1:.1f}",
        "exact": f"with critic score {score1:.1f}",
    }

    if mode == "between" and score2 is not None:
        mode_messages["between"] = f"between {score1:.1f} and {score2:.1f}"

    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games {mode_messages.get(mode, 'matching that score filter')}."

    merged = defaultdict(list)
    for title, s, platform in zip(titles, scores, platforms):
        merged[title].append((platform, float(s)))

    reverse_sort = (mode == "above") 

    items = []
    for title, offers in merged.items():
        offers_sorted = sorted(offers, key=lambda x: x[1])
        key_score = offers_sorted[-1][1] if reverse_sort else offers_sorted[0][1]
        items.append((title, offers_sorted, key_score))

    # sort games by score
    items_sorted = sorted(items, key=lambda x: x[2], reverse=reverse_sort)

    lines = []
    for title, offers_sorted, _ in items_sorted:
        offers_str = ", ".join(f"{platform}: {s:.1f}" for platform, s in offers_sorted)
        lines.append(f"{title} — {offers_str}")

    shown, total, truncated = _limit_filtered_lines(lines)
    notice = _filtered_notice(total, truncated)
    numbered = [f"{i}. {line}" for i, line in enumerate(shown, start=1)]

    return (
        f"Bot: {user_name.value}, here are games {mode_messages[mode]}:\n"
        f"Bot: {notice}"
        + "\n".join(numbered)
    )

def games_by_low_score(score: float, titles: List[str], scores: List[float], platforms: List[str]) -> str:
    return games_by_score_filter("below", score, None, titles, scores, platforms)

def games_by_high_score(score: float, titles: List[str], scores: List[float], platforms: List[str]) -> str:
    return games_by_score_filter("above", score, None, titles, scores, platforms)

def games_by_exact_score(score: float, titles: List[str], scores: List[float], platforms: List[str]) -> str:
    return games_by_score_filter("exact", score, None, titles, scores, platforms)

def games_by_between_scores(low: float, high: float, titles: List[str], scores: List[float], platforms: List[str]) -> str:
    return games_by_score_filter("between", low, high, titles, scores, platforms)

def error_score_not_detected() -> str:
    return f"Bot: I couldn't find a critic score value in your request, {user_name.value}. Try something like 'games with rating lower than 8', or 'games with rating higher than 8', or 'games that have rating 8'."

def error_score_range_not_detected() -> str:
    return f"Bot: I couldn't find two critic scores in your request, {user_name.value}. Try something like 'games with rating between 7 and 8'."

# ======= DATE FILTER RESPONSES =======
def games_oldest(year: int,
                   titles: List[str],
                   years: List[int],
                   platforms: List[str]) -> str:
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games right now."

    merged = defaultdict(list)
    for title, yrs, platform in zip(titles, years, platforms):
        merged[title].append((platform, int(yrs)))

    lines = []
    for i, (title, offers) in enumerate(merged.items(), start=1):
        offers_str = ", ".join(f"{platform}: {y}" for platform, y in offers)
        lines.append(f"{i}. {title} - {offers_str}")

    result = "\n".join(lines)
    return (
        f"Bot: {user_name.value}, here are the oldest games {year}:\n"
        f"{result}"
    )

def games_newest(year: int,
                         titles: List[str],
                         years: List[int],
                         platforms: List[str]) -> str:
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games right now."

    merged = defaultdict(list)
    for title, yrs, platform in zip(titles, years, platforms):
        merged[title].append((platform, int(yrs)))

    lines = []
    for i, (title, offers) in enumerate(merged.items(), start=1):
        offers_str = ", ".join(f"{platform}: {y}" for platform, y in offers)
        lines.append(f"{i}. {title} - {offers_str}")

    result = "\n".join(lines)
    return (
        f"Bot: {user_name.value}, here are the newest {year}:\n"
        f"{result}"
    )

def games_by_date_filter(mode: str, year1: int, year2: Optional[int], titles: List[str], years: List[int], platforms: List[str]) -> str:

    mode_messages = {
        "before": f"before {year1}",
        "after": f"after {year1}",
        "exact": f"in {year1}",
    }

    if mode == "between" and year2 is not None:
        mode_messages["between"] = f"between {year1} and {year2}"

    if not titles:
        return (
            f"Bot: Sorry {user_name.value}, I couldn't find any games released "
            f"{mode_messages.get(mode, 'matching that date filter')}."
        )

    # Group offers by title
    merged = defaultdict(list)
    for title, y, platform in zip(titles, years, platforms):
        merged[title].append((platform, int(y)))

    # For 'after' we want newest first, otherwise oldest first
    reverse_sort = (mode == "after")

    items = []
    for title, offers in merged.items():
        # sort offers within the title
        offers_sorted = sorted(offers, key=lambda x: x[1])
        # pick key year for sorting titles
        key_year = offers_sorted[-1][1] if reverse_sort else offers_sorted[0][1]
        items.append((title, offers_sorted, key_year))

    # sort titles by key_year
    items_sorted = sorted(items, key=lambda x: x[2], reverse=reverse_sort)

    lines = []
    for title, offers_sorted, _ in items_sorted:
        offers_str = ", ".join(f"{platform}: {y}" for platform, y in offers_sorted)
        lines.append(f"{title} — {offers_str}")

    shown, total, truncated = _limit_filtered_lines(lines)
    notice = _filtered_notice(total, truncated)
    numbered = [f"{i}. {line}" for i, line in enumerate(shown, start=1)]

    return (
        f"Bot: {user_name.value}, here are games released {mode_messages[mode]}:\n"
        f"Bot: {notice}"
        + "\n".join(numbered)
    )

def games_by_date_before(year: int, titles: List[str], years: List[int], platforms: List[str]) -> str:
    return games_by_date_filter("before", year, None, titles, years, platforms)

def games_by_date_after(year: int, titles: List[str], years: List[int], platforms: List[str]) -> str:
    return games_by_date_filter("after", year, None, titles, years, platforms)

def games_by_date_exact(year: int, titles: List[str], years: List[int], platforms: List[str]) -> str:
    return games_by_date_filter("exact", year, None, titles, years, platforms)

def games_by_date_between(min_year: int, max_year: int, titles: List[str], years: List[int], platforms: List[str]) -> str:
    return games_by_date_filter("between", min_year, max_year, titles, years, platforms)

def error_year_not_detected() -> str:
    return f"Bot: I couldn't see any year in your request, {user_name.value}. Try something like 'games before 2015', or 'games after 2015', or 'games released in 2015'."

def error_year_range_not_detected() -> str:
    return f"Bot: I couldn't see two years in your request, {user_name.value}. Try something like 'games released between 2010 and 2015'."

