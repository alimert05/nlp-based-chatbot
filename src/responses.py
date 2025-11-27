from typing import Optional, List
import random
from collections import defaultdict
from storage import load_name, save_purchased_game
import config


class UserNameProxy:
    """Helper that always returns the best-known user name."""
    @property
    def value(self):
        return config.USER_NAME or load_name() or "user"

user_name = UserNameProxy()


# ===== BASIC RESPONSES =====
def ask_name() -> str:
    return "Bot: Welcome to the GAMES SHOP Before we start, could you please tell me your name so I can address you properly?"

def name_already_given() -> str:
    return f"Bot: You have already gave your name {user_name.value}. Would you like to change it?"

def greeting(name: Optional[str]) -> str:
    if name:
        return f"Bot: Hi {name}! Nice to meet you. How can I help you today?"
    return "Bot: I didn't quite catch your name. Please say something like 'I am John' or 'My name is John Smith'"

def greeting_again() -> str:
    return f"Bot: Welcome back to the GAMES SHOP {user_name.value}! How can I help you today?"

def no_name_change() -> str:
    return f"Bot: No problem, {user_name.value}. How can I help you today?"

def ask_new_name() -> str:
    return "Bot: Sure, what name would you like me to use for you?"

def name_already_known() -> str:
    return f"Bot: Yes, I remember your name, {user_name.value}. How can I help you today?"

def name_changed() -> str:
    return f"Bot: Great, I've successfully changed your name to {user_name.value}. How can I help you today?"

def recall_name(name: Optional[str]) -> str:
    if name:
        return f"Bot: Your name is {name}"
    return "Bot: Sorry, I don't know your name yet. Please introduce yourself."

def no_name_to_recall() -> str:
    return "Bot: Sorry, you haven't provided your name yet."
    
def ask_name_again() -> str:
    return "Bot: Would you like to tell me your name so I can address you properly?"

def name_refused() -> str:
    return "Bot: That's completely fine. How can I help you today?"
    
def greeting_back(user_input: str) -> str:
    user_input = user_input.capitalize()
    return f"Bot: {user_input}, {user_name.value}. How can I help you?"

def support_normal() -> str:
    return (
        f"Bot: I can do a few simple things, {user_name.value}:\n"
        "- I can remember your name if you share it with me.\n"
        "- We can have a bit of small talk.\n"
        "- You can ask me questions.\n"
        "- I can also help you browse and filter video games. If you like to do so, please type 'I want to buy some games'.\n\n"
        "What would you like to do?"
    )

def small_talk() -> str:
    return f"Bot: I'm doing great {user_name.value}, thanks for asking! How about you?"

def user_feeling_positive() -> str:
    return f"Bot: I am glad to hear that, {user_name.value}."

def user_feeling_negative() -> str:
    return f"Bot: I am sorry to hear that, {user_name.value}. I hope things get better soon."
    
def qa_answers(answer_list: List[str]) -> str:
    return f"Bot: {' '.join(answer_list)}"

def goodbye_saved_name() -> str:
    return f"Bot: I've saved your name for future sessions. Goodbye, {user_name.value} - hope to see you soon."

def goodbye_no_saved_name() -> str:
    return f"Bot: I've deleted your name. Goodbye, {user_name.value} -  hope to see you again."

def goodbye_only() -> str:
    return "Bot: Goodbye, I hope to see you again."

def ask_save_name() -> str:
    return f"Bot: Before you go, would you like me to save your name for next time? (yes/no)"

def prompt_again(matched_example) -> str:
    pretty_example = matched_example.replace('_', ' ')
    return f"Bot: {user_name.value}, I think you might trying to say: '{[pretty_example]}'.\n If that's not what you meant, you can type 'help' to see what I can do." 

def fallback() -> str:
    return f"Bot: I'm not sure I understand that, {user_name.value}. You can say something like 'what can you do?' to see your options."


# ===== GAME MODE RESPONSES =====
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
    return f"Bot: I found multiple games that could match what you asked for:\n{result}\nPlease reply with the number of the game you're interested in {user_name.value}."

def ask_platform_disambiguation(game_title: str, platforms: List[str], prices: Optional[List[float]] = None) -> str:
    if prices and len(prices) == len(platforms):
        lines = [f"{i+1}. {p} - £{price:.2f}" for i, (p, price) in enumerate(zip(platforms, prices))]
    else:
        lines = [f"{i+1}. {p}" for i, p in enumerate(platforms)]
    platforms_str = "\n".join(lines)
    return f"Bot: {game_title} is available on multiple platforms:\n{platforms_str}\nPlease reply with the number of the platform you want {user_name.value}."

def games_mode_on() -> str:
    return f"Bot: Sure thing {user_name.value}! Do you have specific game in your mind, or would you like to browse?"

def confirm_order(selected_game: str, platform: str, price: float) -> str:
    return f"Bot: {selected_game} ({platform}) costs £{price:.2f}. Great choice, {user_name.value}! Would you like to confirm your order? (yes/no)"

def game_purchased(selected_game: str, platform: str, price: float) -> str:
    return f"Bot: Thank you for your purchase, {user_name.value}! You bought {selected_game} on {platform} for £{price:.2f}. Have a great day!"

def game_not_purchased() -> str:
    return f"Bot: No worries, {user_name.value}. If you'd like to look for another game, just ask!"

def support_game() -> str:
    return (
        f"Bot: In games mode, I can help you:\n"
        "- Search for games by name\n"
        "- Filter by platform, genre, price, critic score, or release year\n"
        "- Start a purchase process and remember what you’ve bought\n\n"
        f"What would you like to do, {user_name.value}?"
    )

def user_ends_game_mode() -> str:
    return f"Bot: That's fine, {user_name.value}. We can talk about something other than games. What would you like to do next?"

def purchase_history(title: str, platform: str, price: float) -> str:
    return f"Bot: {user_name.value}, you previously bought {title} ({platform}) for £{price:.2f}."

def back_from_game_selection() -> str:
    return f"Bot: Okay, we've gone back a step. How can I help you now, {user_name.value}?"

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
    for i, (title, platform, genre, publisher, developer, score, release, price) in enumerate(
        zip(titles, platforms, genres, publishers, developers, critic_scores, release_dates, prices), start=1
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
            f"{i}. {title} | Platform: {platform} | Genre: {genre} | Publisher: {publisher} | "
            f"Developer: {developer} | Critic Score: {score_str} | Release Date: {release_str} | Price: {price_str}\n"
        )

    result = "\n".join(lines)
    return f"Bot: {user_name.value}, here are the games I found that match your search:\n\n{result}"


# ======= PUBLISHER / DEVELOPER LISTING =======

def games_by_entity(entity_type: str, titles: List[str], entities: List[str]) -> str:
    if not titles or not entities:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games by that {entity_type.lower()}."

    merged = defaultdict(list)
    for title, entity in zip(titles, entities):
        merged[entity].append(title)

    lines = []
    for entity, title_list in merged.items():
        lines.append(f"{entity_type}: {entity}")
        for i, title in enumerate(sorted(title_list), start=1):
            lines.append(f"{i}. {title}")
        lines.append("")

    result = "\n".join(lines)
    return f"Bot: {user_name.value}, here are some games and their {entity_type.lower()}s:\n{result}"

def games_by_publisher(titles: List[str], publishers: List[str]) -> str:
    return games_by_entity("Publisher", titles, publishers)

def games_by_developer(titles: List[str], developers: List[str]) -> str:
    return games_by_entity("Developer", titles, developers)


# ======= PLATFORM / GENRE LISTING =======
def games_by_attribute(attr_name: str, attr_value: str, titles: List[str], attributes: List[str]) -> str:
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games for {attr_value}."

    merged = defaultdict(set)
    for title, attr in zip(titles, attributes):
        merged[title].add(attr)

    lines = []
    for i, (title, attr_set) in enumerate(merged.items(), start=1):
        attr_list = ", ".join(sorted(attr_set))
        lines.append(f"{i}. {title} — {attr_name}: {attr_list}")

    result = "\n".join(lines)
    return f"Bot: {user_name.value}, here are the games for {attr_value}:\n{result}"

def games_by_platform(platform: str, titles: List[str], platforms: List[str]) -> str:
    return games_by_attribute("Platforms", platform, titles, platforms)

def games_by_genre(genre: str, titles: List[str], genres: List[str]) -> str:
    return games_by_attribute("Genre", genre, titles, genres)


# ======== PRICE FILTER RESPONSES ========
def games_by_price_filter(mode: str, price1: float, price2: Optional[float], titles: List[str], prices: List[float], platforms: List[str]) -> str:
    
    mode_messages = {
        "before": f"under £{price1:.2f}",
        "after": f"over £{price1:.2f}",
        "exact": f"at price: £{price1:.2f}"
    }
    
    if mode == "between" and price2 is not None:
        mode_messages["between"] = f"priced between £{price1:.2f} and £{price2:.2f}"
    
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games {mode_messages.get(mode, 'for that price')}."
    
    merged = defaultdict(list)
    for title, p, platform in zip(titles, prices, platforms):
        merged[title].append((platform, float(p)))

    lines = []
    reverse_sort = mode == "after"
    for i, (title, offers) in enumerate(merged.items(), start=1):
        offers_str = ", ".join(
            f"{platform}: £{p:.2f}" for platform, p in sorted(offers, key=lambda x: x[1], reverse=reverse_sort)
        )
        lines.append(f"{i}. {title} - {offers_str}")

    result = "\n".join(lines)
    return f"Bot: {user_name.value}, here are the games {mode_messages[mode]}:\n{result}"

def games_by_low_price(price: float, titles: List[str], prices: List[float], platforms: List[str]) -> str:
    return games_by_price_filter("before", price, None, titles, prices, platforms)

def games_by_high_price(price: float, titles: List[str], prices: List[float], platforms: List[str]) -> str:
    return games_by_price_filter("after", price, None, titles, prices, platforms)

def games_by_exact_price(price: float, titles: List[str], prices: List[float], platforms: List[str]) -> str:
    return games_by_price_filter("exact", price, None, titles, prices, platforms)

def games_by_between_prices(low: float, high: float, titles: List[str], prices: List[float], platforms: List[str]) -> str:
    return games_by_price_filter("between", low, high, titles, prices, platforms)


# ======= SCORE FILTER RESPONSES =======
def games_by_score_filter(mode: str, score1: float, score2: Optional[float], titles: List[str], scores: List[float], platforms: List[str]) -> str:

    mode_messages = {
        "below": f"under {score1:.1f}",
        "above": f"over {score1:.1f}",
        "exact": f"with critic score {score1:.1f}"
    }
    
    if mode == "between" and score2 is not None:
        mode_messages["between"] = f"between {score1:.1f} and {score2:.1f}"
    
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games {mode_messages.get(mode, 'matching that score filter')}."

    merged = defaultdict(list)
    for title, s, platform in zip(titles, scores, platforms):
        merged[title].append((platform, s))

    lines = []
    reverse_sort = (mode == "above")
    for i, (title, offers) in enumerate(merged.items(), start=1):
        offers_str = ", ".join(
            f"{platform}: {s:.1f}" for platform, s in sorted(offers, key=lambda x: x[1], reverse=reverse_sort)
        )
        lines.append(f"{i}. {title} — {offers_str}")

    result = "\n".join(lines)
    return f"Bot: {user_name.value}, here are games with critic score {mode_messages[mode]}:\n{result}"

def games_by_low_score(score: float, titles: List[str], scores: List[float], platforms: List[str]) -> str:
    return games_by_score_filter("below", score, None, titles, scores, platforms)

def games_by_high_score(score: float, titles: List[str], scores: List[float], platforms: List[str]) -> str:
    return games_by_score_filter("above", score, None, titles, scores, platforms)

def games_by_exact_score(score: float, titles: List[str], scores: List[float], platforms: List[str]) -> str:
    return games_by_score_filter("exact", score, None, titles, scores, platforms)

def games_by_between_scores(low: float, high: float, titles: List[str], scores: List[float], platforms: List[str]) -> str:
    return games_by_score_filter("between", low, high, titles, scores, platforms)


# ======= DATE FILTER RESPONSES =======
def games_by_date_filter(mode: str, year1: int, year2: Optional[int], titles: List[str], years: List[int], platforms: List[str]) -> str:

    mode_messages = {
        "before": f"before {year1}",
        "after": f"after {year1}",
        "exact": f"in {year1}"
    }
    
    if mode == "between" and year2 is not None:
        mode_messages["between"] = f"between {year1} and {year2}"
    
    if not titles:
        return f"Bot: Sorry {user_name.value}, I couldn't find any games released {mode_messages.get(mode, 'matching that date filter')}."

    merged = defaultdict(list)
    for title, y, platform in zip(titles, years, platforms):
        merged[title].append((platform, y))

    lines = []
    for i, (title, offers) in enumerate(merged.items(), start=1):
        offers_str = ", ".join(
            f"{platform}: {y}" for platform, y in sorted(offers, key=lambda x: x[1])
        )
        lines.append(f"{i}. {title} — {offers_str}")

    result = "\n".join(lines)
    return f"Bot: {user_name.value}, here are games released {mode_messages[mode]}:\n{result}"

def games_by_date_before(year: int, titles: List[str], years: List[int], platforms: List[str]) -> str:
    return games_by_date_filter("before", year, None, titles, years, platforms)

def games_by_date_after(year: int, titles: List[str], years: List[int], platforms: List[str]) -> str:
    return games_by_date_filter("after", year, None, titles, years, platforms)

def games_by_date_exact(year: int, titles: List[str], years: List[int], platforms: List[str]) -> str:
    return games_by_date_filter("exact", year, None, titles, years, platforms)

def games_by_date_between(min_year: int, max_year: int, titles: List[str], years: List[int], platforms: List[str]) -> str:
    return games_by_date_filter("between", min_year, max_year, titles, years, platforms)