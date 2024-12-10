# Import necessary libraries and modules
import os
import sqlite3
from cs50 import SQL
from flask import Flask, request, redirect, session, url_for, jsonify, render_template, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from datetime import datetime, timedelta
from jinja2.exceptions import TemplateNotFound

# Import custom helper functions
from helpers import login_required, apology, calculate_score, get_best_location, apply_seasonal_adjustment, weights, get_current_season

# Initialize Flask application
app = Flask(__name__, static_folder='static')

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up SQLite database connection
db_path = os.path.join(os.path.dirname(__file__), "finalproject.db")
db = SQL(f"sqlite:///{db_path}")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Set secret key for session management
app.secret_key = '1227717712'

# Spotify API credentials
CLIENT_ID = "b7ca07268f1f4e06a9efc6fc352c58b6"
CLIENT_SECRET = "d9eda0bef18746a98384102397a4f072"
REDIRECT_URI = "https://musical-cod-g47qwxr4jw94cwg99-5000.app.github.dev/callback"

# Spotify API endpoints
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"

# OpenWeatherMap API Key
API_KEY = 'b6725bb82b4fd00cfeb5450908c9492c'

# Dictionary of locations with their characteristics
locations = {
    "Mumbai": ["busy", "tropical", "cultural", "vibrant", "spicy", "comfortable", "urban"],
    "Cape Town": ["scenic", "coastal", "adventurous", "outdoors", "varied", "neutral", "relaxed"],
    "Istanbul": ["historic", "cultural", "urban", "vibrant", "savory", "comfortable", "urban"],
    "Barcelona": ["warm", "artistic", "coastal", "lively", "varied", "comfortable", "relaxed"],
    "New York City": ["urban", "busy", "diverse", "entertainment", "varied", "comfortable", "urban"],
    "Rio De Janeiro": ["festive", "tropical", "beach", "vibrant", "varied", "comfortable", "relaxed"],
    "Los Angeles": ["sunny", "urban", "entertainment", "diverse", "varied", "neutral", "urban"],
    "Dubai": ["modern", "luxurious", "urban", "desert", "varied", "comfortable", "exclusive"],
    "Reykjavik": ["cold", "scenic", "quiet", "natural", "savory", "avoid", "relaxed"],
    "Tokyo": ["busy", "modern", "technological", "cultural", "varied", "comfortable", "urban"]
}

# Dictionary of location summaries
summaries = {
    "Barcelona": "Known for its Gaudí-inspired architecture, Mediterranean beaches, and vibrant Catalan culture, Barcelona is a hub for art, food, and nightlife.",
    "Cape Town": "Nestled between Table Mountain and stunning coastlines, Cape Town offers a mix of natural beauty, rich history, and a thriving cultural scene in South Africa.",
    "Dubai": "A futuristic city in the desert, Dubai dazzles with its skyscrapers, luxury shopping, and cultural blend of traditional and modern influences.",
    "Istanbul": "A city straddling two continents, Istanbul captivates with its fusion of Byzantine and Ottoman history, stunning mosques, and bustling bazaars.",
    "Los Angeles": "The entertainment capital of the world, LA offers Hollywood glamour, diverse neighborhoods, and sunny beaches alongside a thriving arts scene.",
    "Mumbai": "A bustling metropolis and India’s financial capital, Mumbai blends colonial architecture, Bollywood glamour, and vibrant street life with the serene beauty of the Arabian Sea.",
    "New York City": "The “City That Never Sleeps,” NYC is a global hub of finance, art, and diversity, with iconic landmarks like Times Square and Central Park.",
    "Reykjavik": "Iceland’s capital and cultural heart, Reykjavik enchants with its vibrant arts scene, geothermal spas, and proximity to stunning natural wonders like the Northern Lights.",
    "Rio De Janeiro": "Famous for its Carnival, samba rhythms, and the iconic Christ the Redeemer statue, Rio combines urban energy with breathtaking natural landscapes.",
    "Tokyo": "A seamless blend of ancient traditions and cutting-edge technology, Tokyo dazzles with its bustling streets, sushi culture, and tranquil temples.",
}


@app.route("/")
@login_required
def index():
    # Render the index page
    return render_template("index.html")


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Render quiz form
    if request.method == 'POST':
        return redirect(url_for('result'))
    return render_template('quiz.html')


@app.route('/result', methods=['POST'])
@login_required
def result():
    # Process quiz answers and determine best city
    # Get answers from form submission
    answers = {f"question_{i}": request.form.get(f"question_{i}") for i in range(1, 11)}

    # Ensure all questions are answered
    if None in answers.values():
        return apology("Please answer all questions.", 400)

    # Calculate scores based on answers
    score = calculate_score(answers, locations, weights)

    # Adjust scores based on current season
    current_season = get_current_season()
    adjusted_score = apply_seasonal_adjustment(score, locations, current_season)

    # Determine the best location
    best_location = get_best_location(adjusted_score)

    # Create name_of_city variable
    name_of_city = best_location.lower().replace(' ', '_')

    # Render result page with the best city and name_of_city
    return render_template('result.html', city_name=best_location, name_of_city=name_of_city)


def init_bucketlist_table():
    with sqlite3.connect('finalproject.db') as conn:
        cursor = conn.cursor()

        # Execute the SQL query to create the 'bucketlist' table if it doesn't already exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bucketlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                city_name TEXT NOT NULL,
                summary TEXT DEFAULT "Summary not available",
                UNIQUE(username, city_name)
            )
        ''')
        conn.commit()


# Call the function to initialize the bucketlist table
init_bucketlist_table()


def add_summary_column():
    # Add a summary column to the bucketlist table if it doesn't exist
    with sqlite3.connect('finalproject.db') as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(bucketlist);")
        columns = [col[1] for col in cursor.fetchall()]
        if 'summary' not in columns:
            cursor.execute('''
                ALTER TABLE bucketlist ADD COLUMN summary TEXT DEFAULT "Summary not available"
            ''')
            print("Added 'summary' column to bucketlist table.")


add_summary_column()


def populate_summary():

    with sqlite3.connect('finalproject.db') as conn:
        cursor = conn.cursor()
        for city, summary in summaries.items():
            cursor.execute('''
                UPDATE bucketlist
                SET summary = ?
                WHERE city_name = ?
            ''', (summary, city))
        conn.commit()


populate_summary()


@app.route('/add_to_bucketlist', methods=['POST'])
@login_required
def add_to_bucketlist():
    data = request.get_json()

    # Validate input
    city_name = data.get('city_name')
    username = session.get('username')

    # Check if city_name is valid (non-empty string), else return error message
    if not city_name or not isinstance(city_name, str):
        return jsonify({'success': False, 'error': 'Valid city name is required'}), 400

    # If no username exists in the session, return error (user not logged in)
    if not username:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401

    # Fetch the city summary
    summary = summaries.get(city_name)
    if summary == "Summary not available":
        print(f"Summary for {city_name} not found.")

    try:
        # Insert into the database
        with sqlite3.connect('finalproject.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO bucketlist (username, city_name, summary) VALUES (?, ?, ?)',
                (username, city_name, summary)
            )
            conn.commit()
        return jsonify({'success': True})

    # Catch any database-related errors (e.g., issues with the query or connection)
    except sqlite3.DatabaseError as db_error:
        return jsonify({'success': False, 'error': f'Database error: {str(db_error)}'}), 500

    # Catch any general exceptions that might occur
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/remove_from_bucketlist', methods=['POST'])
@login_required
def remove_from_bucketlist():
    # Extract the JSON data from the incoming request
    data = request.get_json()
    city_name = data.get('city_name')
    username = session.get('username')

    # Check if both city name and username are provided; if not, return an error response
    if not city_name or not username:
        return jsonify({'success': False, 'error': 'City name and username are required'}), 400

    try:
        # Connect to the SQLite database to execute the removal operation
        with sqlite3.connect('finalproject.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM bucketlist WHERE username = ? AND city_name = ?', (username, city_name)
            )
            conn.commit()
        # Return a success response once the item is removed
        return jsonify({'success': True})
    except Exception as e:
        # If an error occurs, return a failure response
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/bucketlist')
@login_required
def bucketlist():
    # Retrieve the username from the session to query the bucketlist for that specific user
    username = session.get('username')
    try:
        # Establish a connection to the SQLite database
        with sqlite3.connect('finalproject.db') as conn:
            cursor = conn.cursor()
            # Query the bucketlist table to get city names and summaries for the logged-in user
            cursor.execute(
                'SELECT city_name, summary FROM bucketlist WHERE username = ?', (username,)
            )
            # Fetch all matching bucketlist items
            bucketlist_items = cursor.fetchall()

        # Render the 'bucketlist.html' template, passing the city names and summaries for display
        return render_template('bucketlist.html', bucketlist_items=[{'city_name': item[0], 'summary': item[1]} for item in bucketlist_items])
    except Exception as e:
        # Return a server error if an exception occurs during database interaction
        return f"Error: {e}", 500


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]  # Store username in session

        # Make the session persistent by setting a custom expiration time
        session.permanent = True  # This makes the session persistent across browser sessions
        # Set the session timeout (e.g., 30 days)
        app.permanent_session_lifetime = timedelta(days=30)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    # egister user and forget any user_id
    session.clear()

    if request.method == "POST":
        # Validate form inputs
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must confirm your password", 400)

        # Check if username already exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) == 1:
            return apology("username already exists", 400)

        # Check if passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("You inputted two different passwords", 400)

        # Insert new user into database
        username = request.form.get("username")
        password = request.form.get("password")
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                   username, generate_password_hash(password))

        # Log in the new user
        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)
        session["user_id"] = user_id[0]["id"]

        flash("Registration successful!", "success")

        # Redirect user to home page
        return render_template("login.html")

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route('/explore/<city_name>/<subpage>')
def explore(city_name, subpage):
    # Render city exploration pages
    cityname = city_name.lower().replace(' ', '_')
    template_path = f"{cityname}/{subpage}.html"
    try:
        return render_template(template_path, city_name=city_name)
    except TemplateNotFound:
        return f"Template {template_path} not found.", 404


if __name__ == '__main__':
    app.run(debug=True)
