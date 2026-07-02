from src.database import express_interest, get_my_matches, get_user_by_id


def handle_interest(from_user_id: int, activity_id: int, activity_owner_id: int) -> bool:
    """
    Called when a user clicks 'Interested' on an activity.
    Returns True if this created a match, False otherwise.
    """
    return express_interest(from_user_id, activity_id, activity_owner_id)


def get_matches_with_details(user_id: int) -> list:
    """
    Returns all matches for a user, enriched with the other person's details.
    """
    matches = get_my_matches(user_id)
    result = []

    for match in matches:
        # figure out who the OTHER person is
        if match["user1_id"] == user_id:
            other_id = match["user2_id"]
            other_name = match["user2_name"]
        else:
            other_id = match["user1_id"]
            other_name = match["user1_name"]

        other_user = get_user_by_id(other_id)

        result.append({
            "match_id": match["id"],
            "other_user_id": other_id,
            "other_name": other_name,
            "other_age": other_user["age"] if other_user else "?",
            "other_city": other_user["city"] if other_user else "?",
            "other_bio": other_user["bio"] if other_user else "",
            "activity_title": match["activity_title"],
            "activity_category": match["activity_category"],
            "matched_at": match["created_at"],
        })

    return result


# activity category emoji map — used across the app
CATEGORY_EMOJI = {
    "Coffee": "☕",
    "Dining Out": "🍽️",
    "Cooking Class": "🍳",
    "Movies": "🎬",
    "Live Music / Events": "🎵",
    "Pickleball": "🏓",
    "Badminton": "🏸",
    "Tennis": "🎾",
    "Running / Jogging": "🏃",
    "Cycling": "🚴",
    "Yoga / Gym": "🧘",
    "Rock Climbing": "🧗",
    "Swimming": "🏊",
    "Hiking": "🥾",
    "Camping": "🏕️",
    "Road Trip": "🚗",
    "Bucket List Adventure": "🪂",
    "Book Club": "📚",
    "Wine Tasting": "🍷",
    "Trivia Night": "🎯",
    "Gaming": "🎮",
    "Study / Career Buddy": "💼",
    "Language Exchange": "🌍",
    "Other": "✨",
}

CATEGORIES = list(CATEGORY_EMOJI.keys())