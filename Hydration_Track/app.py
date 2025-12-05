# Flask web app for a workout-based hydration tracker.
# This file defines:
# - App configuration + database setup
# - Login/auth (register/login/logout)
# - Hydration calculation endpoint
# - Dashboard + history pages
# - A simple daily water “bottle” API

from flask import Flask, render_template, request, redirect, jsonify, url_for
from datetime import datetime, timedelta
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re

# SQLAlchemy models + your hydration algorithm
from models import db, User, WorkoutSession, DailyWater
from hydration_engine import hydration_engine


# ---------------------------------------------------------
# APP + CONFIG
# ---------------------------------------------------------

# Create the Flask app instance
app = Flask(__name__)

# Secret key is used for session signing (login sessions, CSRF protection if you add it, etc.)
# NOTE: For production, store this in an environment variable, not in source code.
app.secret_key = "supersecretkey123"

# Database connection string. Using local SQLite DB file named hydration.db.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hydration.db"

# Disables a SQLAlchemy feature that tracks object changes (saves some overhead)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Attach SQLAlchemy to this Flask app
db.init_app(app)

# Create tables if they don't exist yet (simple class-project startup behavior)
with app.app_context():
    db.create_all()


# ---------------------------------------------------------
# RATE LIMITER
# ---------------------------------------------------------

# Rate limiting helps protect endpoints (especially login/register) from brute force and abuse.
# It uses the client's IP address to count requests.
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],  # global defaults for all routes unless overridden
)


# ---------------------------------------------------------
# LOGIN MANAGER
# ---------------------------------------------------------

# Flask-Login manages user sessions (who is logged in).
login_manager = LoginManager()
login_manager.init_app(app)

# If a user hits a @login_required route, redirect them here.
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login callback:
    Given a user_id stored in the session cookie, load the User from the database.
    """
    # Legacy warning is fine for this class project (User.query.get is deprecated in newer SQLAlchemy styles)
    return User.query.get(int(user_id))


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

# Username rule: 3–20 chars, letters/numbers underscore only
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")


def valid_username(username: str) -> bool:
    """
    Validate the username format.
    Returns True only if username matches USERNAME_RE.
    """
    if not isinstance(username, str):
        return False
    username = username.strip()
    return bool(USERNAME_RE.fullmatch(username))


def valid_password(password: str) -> bool:
    """
    Validate password (simple rule): length from 6 to 64.
    Note: This is *not* strong password validation; it's just a basic constraint.
    """
    if not isinstance(password, str):
        return False
    length = len(password)
    return 6 <= length <= 64


def validate_number(value, min_val, max_val):
    """
    Defensive numeric validation:
    - convert input to float if possible
    - enforce allowed range [min_val, max_val]
    Returns float(value) if valid, else None.
    """
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v < min_val or v > max_val:
        return None
    return v


def get_today_str():
    """
    Return today's date in UTC as YYYY-MM-DD.
    This is used as the daily key for DailyWater entries.
    """
    return datetime.utcnow().strftime("%Y-%m-%d")


def ensure_daily_water_state(user):
    """
    Ensure a DailyWater row exists for the current UTC date.
    If it doesn't exist yet, create it with 0 oz.
    """
    today = get_today_str()

    # Look for today's daily water record
    record = DailyWater.query.filter_by(user_id=user.id, date=today).first()

    # If no record exists for today, create one
    if not record:
        record = DailyWater(user_id=user.id, date=today, water_oz=0.0)
        db.session.add(record)
        db.session.commit()


# ---------------------------------------------------------
# Drink Suggestions
# ---------------------------------------------------------

# Simple built-in "catalog" of drink options with electrolyte content (per serving).
# Values are approximate placeholders; you can swap in your own data.
REFUEL_DRINKS = [
    {"name": "Plain water", "serving_oz": 16, "sodium_mg": 0, "potassium_mg": 0, "magnesium_mg": 0},
    {"name": "Sports drink (moderate sodium)", "serving_oz": 20, "sodium_mg": 250, "potassium_mg": 80, "magnesium_mg": 0},
    {"name": "Electrolyte mix (high sodium)", "serving_oz": 16, "sodium_mg": 1000, "potassium_mg": 200, "magnesium_mg": 60},
    {"name": "Oral rehydration solution (balanced)", "serving_oz": 12, "sodium_mg": 370, "potassium_mg": 280, "magnesium_mg": 0},
    {"name": "Coconut water + pinch of salt", "serving_oz": 12, "sodium_mg": 250, "potassium_mg": 600, "magnesium_mg": 60},
]


def recommend_drinks(target_sodium_mg, target_potassium_mg, target_magnesium_mg, max_results=3):
    """
    Recommend drinks by scoring how well each option covers the target electrolytes.

    Scoring approach:
    - Convert targets to non-negative floats.
    - If all targets are 0, recommend plain water.
    - For each electrolyte, compute a capped ratio: delivered/target capped at 1.0
    - Weighted score: sodium weighted higher (common focus for sweat refueling)
    """
    ts = max(float(target_sodium_mg or 0), 0.0)
    tk = max(float(target_potassium_mg or 0), 0.0)
    tm = max(float(target_magnesium_mg or 0), 0.0)

    # If no electrolyte replenishment is needed, keep it simple.
    if ts == 0 and tk == 0 and tm == 0:
        return [REFUEL_DRINKS[0]]

    def ratio(delivered, target):
        """
        Returns a number between 0 and 1.
        If target is 0, treat it as already satisfied.
        """
        if target <= 0:
            return 1.0
        return min(delivered / target, 1.0)

    scored = []
    for d in REFUEL_DRINKS:
        s = ratio(d["sodium_mg"], ts)
        k = ratio(d["potassium_mg"], tk)
        m = ratio(d["magnesium_mg"], tm)

        # Sodium weighted heavier for sweat refuel
        score = 0.55 * s + 0.30 * k + 0.15 * m
        scored.append((score, d))

    # Highest score first; return the top N drinks
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:max_results]]


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

@app.route("/")
@login_required
def home():
    """
    Main dashboard route.

    Responsibilities:
    - Require profile setup (weight + sex) before showing dashboard
    - Ensure today's DailyWater row exists
    - Query workouts, compute summary stats
    - Compute hydration goal (either user-set or dynamic)
    - Build data structures for charts + dashboard cards
    - Render index.html
    """
    # If user hasn't completed setup, send them to /setup
    if current_user.weight_kg is None or current_user.sex is None:
        return redirect("/setup")

    # Make sure today's water record is initialized
    ensure_daily_water_state(current_user)

    # Base query for all workouts by this user
    base_query = WorkoutSession.query.filter_by(user_id=current_user.id)

    # All sessions newest first
    sessions = base_query.order_by(WorkoutSession.timestamp.desc()).all()
    last_session = sessions[0] if sessions else None

    # Time windows in UTC
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)  # midnight today (UTC)
    seven_days_ago = now - timedelta(days=7)

    # Count workouts performed today
    todays_count = base_query.filter(WorkoutSession.timestamp >= today_start).count()

    # Pull today's sessions for totals
    todays_sessions = base_query.filter(WorkoutSession.timestamp >= today_start).all()

    # Sum today's saved per-workout values (already stored at time of calculation)
    total_water_ml_today = sum((s.water_needed_ml or 0) for s in todays_sessions)
    total_water_oz_today = total_water_ml_today / 29.5735

    total_sodium_mg_today = sum((s.sodium_mg or 0) for s in todays_sessions)
    total_potassium_mg_today = sum((s.potassium_mg or 0) for s in todays_sessions)
    total_magnesium_mg_today = sum((s.magnesium_mg or 0) for s in todays_sessions)

    # Today's total refuel needs (used for drink recommendations + stats)
    today_refuel = {
        "water_oz": total_water_oz_today,
        "sodium_mg": total_sodium_mg_today,
        "potassium_mg": total_potassium_mg_today,
        "magnesium_mg": total_magnesium_mg_today,
    }

    # Most recent workout refuel (used by a "last workout" card)
    if last_session:
        last_refuel = {
            "water_oz": float(last_session.water_needed_ml or 0) / 29.5735,
            "sodium_mg": float(last_session.sodium_mg or 0),
            "potassium_mg": float(last_session.potassium_mg or 0),
            "magnesium_mg": float(last_session.magnesium_mg or 0),
            "sweat_rate": float(last_session.sweat_rate or 0),
        }
    else:
        last_refuel = None

    # Drink suggestions based on TODAY total electrolyte needs
    today_drink_recs = recommend_drinks(
        today_refuel["sodium_mg"],
        today_refuel["potassium_mg"],
        today_refuel["magnesium_mg"],
        max_results=3,
    )

    # Pull last 7 days of sessions for averages/trends
    last_7d = base_query.filter(WorkoutSession.timestamp >= seven_days_ago).all()

    if last_7d:
        # Average sweat rate across last 7 days
        avg_sweat_rate = sum(s.sweat_rate for s in last_7d) / len(last_7d)

        # Total water needed across last 7 days
        total_water_ml_7d = sum(s.water_needed_ml for s in last_7d)
        total_water_oz_7d = total_water_ml_7d / 29.5735

        # Max temp in last 7 days converted to °F (if temps exist)
        temps_c = [s.temperature_c for s in last_7d if s.temperature_c is not None]
        max_temp_f = (max(temps_c) * 9/5 + 32) if temps_c else None
    else:
        avg_sweat_rate = None
        total_water_oz_7d = None
        max_temp_f = None

    # ----------------------------
    # DAILY HYDRATION GOAL (Dynamic)
    # ----------------------------
    # Priority:
    # 1) If user manually has daily_goal_oz set -> use it
    # 2) Else if they have enough workout history -> compute dynamic goal
    # 3) Else fallback to 64 oz

    # 1. Weight from most recent session if available, otherwise None
    if sessions and sessions[0].weight_kg is not None:
        weight_lbs = sessions[0].weight_kg * 2.205
    else:
        weight_lbs = None

    # 3. Avg temp last 7 days (°F), used for heat adjustment
    if last_7d:
        temps_f = [(s.temperature_c * 9/5 + 32) for s in last_7d]
        avg_temp_f = sum(temps_f) / len(temps_f)
    else:
        avg_temp_f = None

    # 4. Heat adjustment: add ounces based on temperature bands
    temp_adjust = 0
    if avg_temp_f is not None:
        if avg_temp_f >= 85:
            temp_adjust = 24
        elif avg_temp_f >= 75:
            temp_adjust = 12

    # 5. Determine final goal
    if current_user.daily_goal_oz is not None:
        hydration_goal_oz = current_user.daily_goal_oz
    elif weight_lbs and avg_sweat_rate is not None:
        # Baseline: 0.5 oz per lb + sweat component + heat adjustment
        baseline = weight_lbs * 0.5
        sweat_component = avg_sweat_rate * 22
        hydration_goal_oz = baseline + sweat_component + temp_adjust
    else:
        hydration_goal_oz = 64.0

    # ----------------------------
    # Today's water intake
    # ----------------------------
    # NOTE: This pulls from current_user, but your bottle API uses DailyWater.
    # If you want a single source of truth, use DailyWater everywhere.
    water_today_oz = current_user.water_today_oz or 0.0

    # ----------------------------
    # CHART DATA
    # ----------------------------
    # Build arrays used for chart rendering on the frontend.
    chart_data = {
        "dates": [s.timestamp.strftime("%m/%d") for s in sessions],
        "sweat_rate": [s.sweat_rate for s in sessions],
        "water_oz": [round(s.water_needed_ml / 29.5735, 1) for s in sessions],
        # Only include temps if temperature exists
        "temp_f": [
            round((s.temperature_c * 9/5 + 32), 1)
            for s in sessions if s.temperature_c is not None
        ],
        # Scatter plot pairs: temperature (x) vs sweat_rate (y)
        "temp_vs_sweat": [
            {"x": round((s.temperature_c * 9/5 + 32), 1), "y": s.sweat_rate}
            for s in sessions if s.temperature_c is not None
        ],
    }

    # Package all dashboard stats into one dict for template use
    stats = {
        "today_workouts": todays_count,
        "lifetime_workouts": base_query.count(),
        "avg_sweat_rate": avg_sweat_rate,
        "total_water_oz_7d": total_water_oz_7d,
        "max_temp_f": max_temp_f,
        "total_water_oz_today": total_water_oz_today,
        "hydration_goal_oz": hydration_goal_oz,
        "water_today_oz": water_today_oz,
        "user_weight": current_user.weight_kg,
        "today_refuel": today_refuel,
        "today_drink_recs": today_drink_recs,
        "last_refuel": last_refuel,
    }

    return render_template("index.html", sessions=sessions, stats=stats, chart=chart_data)


# ------------------- REGISTER -------------------

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per minute")
def register():
    """
    Create a new user account.

    GET: render register form
    POST: validate username/password, create user, redirect to login
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Validate input formats
        if not valid_username(username):
            return "Invalid username. Use 3–20 letters, numbers, or underscore.", 400

        if not valid_password(password):
            return "Invalid password length. Use 6–64 characters.", 400

        # Enforce unique usernames in the database
        if User.query.filter_by(username=username).first():
            return "Username already taken", 400

        # Create and store the user (password hashing handled in your model)
        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ------------------- LOGIN -------------------

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    """
    Log a user in.

    GET: render login page
    POST: validate input, check password, create login session
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Basic validation first to avoid unnecessary DB queries
        if not valid_username(username) or not valid_password(password):
            return "Invalid username or password", 400

        user = User.query.filter_by(username=username).first()

        # If credentials are correct, log in and redirect to dashboard
        if user and user.check_password(password):
            login_user(user)
            return redirect("/")

        return "Invalid username or password", 400

    return render_template("login.html")


# ------------------- LOGOUT -------------------

@app.route("/logout")
@login_required
def logout():
    """
    End the user's session and redirect them back to login.
    """
    logout_user()
    return redirect("/login")


# ------------------- SETUP (FIRST-TIME PROFILE FORM) -------------------

@app.route("/setup", methods=["GET", "POST"])
@login_required
def setup():
    """
    First-time profile setup.

    Users must provide weight (lbs) and sex.
    This route computes and stores an initial daily hydration goal.
    """
    # If user already completed setup, skip setup screen
    if current_user.weight_kg is not None and current_user.sex is not None:
        return redirect("/")

    if request.method == "POST":
        weight_raw = request.form.get("weight")
        sex = request.form.get("sex")

        # Validate weight input
        try:
            weight_lbs = float(weight_raw)
        except (TypeError, ValueError):
            return "Invalid weight provided.", 400

        # Convert lbs → kg for internal consistency
        weight_kg = weight_lbs * 0.453592

        # Store profile data on the user record
        current_user.weight_kg = weight_kg
        current_user.sex = sex

        # ---------- Compute hydration goal ----------
        # Baseline: ~0.5 oz per lb (simple rule of thumb)
        baseline = weight_lbs * 0.5

        # Default assumptions until workout history exists
        avg_sweat_rate = 1.0
        sweat_component = avg_sweat_rate * 22

        # Default heat adjustment (you later compute dynamically on dashboard)
        temp_adjust = 0

        # Store daily goal on user
        current_user.daily_goal_oz = baseline + sweat_component + temp_adjust

        db.session.commit()

        return redirect("/")

    return render_template("setup.html")


# ------------------- CALCULATE HYDRATION -------------------

@app.route("/calculate", methods=["POST"])
@login_required
@limiter.limit("30 per minute")
def calculate():
    """
    JSON API endpoint that:
    - validates input fields
    - runs hydration_engine to compute water/electrolyte needs
    - saves the session to the database
    - returns the computed result as JSON
    """
    data = request.get_json(silent=True)

    # If the client didn't send valid JSON, fail early
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Pull raw values from the JSON payload
    raw_weight = data.get("weight")
    raw_sex = data.get("sex")
    raw_duration = data.get("duration")
    raw_hr = data.get("heart_rate")
    raw_temp = data.get("temp")

    # Validate numeric fields (expected to be metric for this endpoint)
    weight = validate_number(raw_weight, 30, 300)        # kg
    duration = validate_number(raw_duration, 1, 600)     # minutes
    heart_rate = validate_number(raw_hr, 30, 230)        # bpm
    temp = validate_number(raw_temp, -20, 60)            # °C

    # If any numeric field is invalid, return error
    if None in [weight, duration, heart_rate, temp]:
        return jsonify({"error": "Numeric fields out of allowed range"}), 400

    # Validate sex field
    if raw_sex not in ("male", "female"):
        return jsonify({"error": "Invalid sex value"}), 400

    # Run your hydration model/algorithm
    result = hydration_engine(
        weight=weight,
        sex=raw_sex,
        duration_min=duration,
        heart_rate=heart_rate,
        temp_c=temp,
    )

    # Convenience field for UI: convert mL -> oz
    # (Keeps frontend simple if you display ounces.)
    try:
        result["water_oz"] = float(result.get("water_ml", 0) or 0) / 29.5735
    except (TypeError, ValueError):
        result["water_oz"] = 0.0

    # Save this workout session to the database
    new_session = WorkoutSession(
        user_id=current_user.id,
        duration_min=duration,
        calories=result.get("calories", 0),
        avg_heart_rate=heart_rate,
        temperature_c=temp,
        sweat_rate=result["sweat_rate_L_per_hr"],
        total_sweat_loss=result["total_sweat_loss_L"],
        water_needed_ml=result["water_ml"],
        sodium_mg=result["sodium_mg"],
        potassium_mg=result["potassium_mg"],
        magnesium_mg=result["magnesium_mg"],
        dehydration_alert=result.get("alert", False),
    )

    db.session.add(new_session)
    db.session.commit()

    # Return computed values to the frontend
    return jsonify(result)


# ------------------- HISTORY PAGE -------------------

@app.route("/history")
@login_required
def history():
    """
    Render a page showing all previous workout sessions for the current user.
    """
    sessions = (
        WorkoutSession.query.filter_by(user_id=current_user.id)
        .order_by(WorkoutSession.timestamp.desc())
        .all()
    )
    return render_template("history.html", sessions=sessions)


# ------------------- WATER API (BOTTLE) -------------------

@app.route("/get_water")
@login_required
def get_water():
    """
    Read today's water intake (oz) from the DailyWater table and return JSON.
    This supports your "water bottle" UI feature.
    """
    today_key = get_today_str()
    record = DailyWater.query.filter_by(user_id=current_user.id, date=today_key).first()

    # If no record exists for today, treat as 0 (but you usually create it via ensure_daily_water_state)
    if not record:
        return jsonify({"water_oz": 0})

    return jsonify({"water_oz": record.water_oz})


@app.route("/add_water", methods=["POST"])
@login_required
def add_water():
    """
    Add ounces of water to today's DailyWater record.

    Expects JSON payload like: {"amount": 8}
    Returns updated total as JSON.
    """
    data = request.get_json(silent=True) or {}
    amount = data.get("amount")

    # Validate amount is a float
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    # Basic sanity bounds (prevents negative values and unrealistic huge entries)
    if amount <= 0 or amount > 200:
        return jsonify({"error": "Amount out of range"}), 400

    # Find or create today's DailyWater record
    today_key = get_today_str()
    record = DailyWater.query.filter_by(user_id=current_user.id, date=today_key).first()

    if not record:
        record = DailyWater(user_id=current_user.id, date=today_key, water_oz=0.0)
        db.session.add(record)

    # Update total intake and persist
    record.water_oz += amount
    db.session.commit()

    return jsonify({"water_oz": record.water_oz})


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    # debug=True enables auto-reload + interactive debug pages.
    # For production, run behind a real WSGI server and disable debug.
    app.run(debug=True)