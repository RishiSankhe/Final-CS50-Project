import requests
from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", bottom=message), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def calculate_score(answers, locations, weights):
    # Initialize score dictionary with 0 for each location
    score = {location: 0 for location in locations}

    # Calculate score based on answers and traits
    for question, answer in answers.items():
        for location, traits in locations.items():
            if answer in traits:
                score[location] += weights.get(question, 1)
            elif answer in ["varied", "neutral"]:
                score[location] += weights.get(question, 1) * 0.5

    return score


def get_best_location(score):
    # Return the location with the highest score
    return max(score, key=score.get)


def apply_seasonal_adjustment(score, locations, season):
    # Define seasonal factors for adjusting scores
    seasonal_factors = {
        "summer": {"tropical": 1.2, "cold": 0.8},
        "winter": {"cold": 1.2, "tropical": 0.8},
        "spring": {"warm": 1.1, "scenic": 1.1},
        "fall": {"urban": 1.1, "cultural": 1.1}
    }

    # Apply seasonal adjustments to scores
    for location in score:
        for trait, factor in seasonal_factors.get(season, {}).items():
            if trait in locations[location]:
                score[location] *= factor

    return score


def get_current_season():
    # Determine the current season based on the month
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "fall"


# Define weights for each question
weights = {
    "question_1": 2.0,
    "question_2": 1.2,
    "question_3": 1.2,
    "question_4": 1.0,
    "question_5": 1.3,
    "question_6": 0.8,
    "question_7": 0.9,
    "question_8": 0.7,
    "question_9": 0.6,
    "question_10": 1.1
}
