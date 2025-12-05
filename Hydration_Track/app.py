from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime, timedelta
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from models import db, User, WorkoutSession
from hydration_engine import hydration_engine

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re

# ---------------------------------------------------------
# APP + CONFIG
# ---------------------------------------------------------

app = Flask(__name__)
app.secret_key = "supersecretkey123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hydration.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------------------------------------------------
# RATE LIMITER
# ---------------------------------------------------------

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
)

# ---------------------------------------------------------
# LOGIN MANAGER
# ---------------------------------------------------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    # LegacyAPIWarning is fine for this project
    return User.query.get(int(user_id))


# ---------------------------------------------------------
# VALIDATION HELPERS
# ---------------------------------------------------------

def validate_number(value, min_val, max_val):
    """Return float(value) if numeric and within [min_val, max_val], else None."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v < min_val or v > max_val:
        return None
    return v


USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")


def valid_username(username: str) -> bool:
    if not isinstance(username, str):
        return False
    username = username.strip()
    return bool(USERNAME_RE.fullmatch(username))


def valid_password(password: str) -> bool:
    if not isinstance(password, str):
        return False
    length = len(password)
    return 6 <= length <= 64  # no complexity rules, just length


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

@app.route("/")
@login_required
def home():
    from datetime import datetime, timedelta

    base_query = WorkoutSession.query.filter_by(user_id=current_user.id)
    sessions = (
        base_query.order_by(WorkoutSession.timestamp.desc()).all()
    )

    # Time windows
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    seven_days_ago = now - timedelta(days=7)

    # Today’s workouts
    todays_count = (
        base_query.filter(WorkoutSession.timestamp >= today_start).count()
    )

    # Water needed today
    todays_sessions = (
        base_query.filter(WorkoutSession.timestamp >= today_start).all()
    )
    total_water_ml_today = sum(s.water_needed_ml for s in todays_sessions)
    total_water_oz_today = total_water_ml_today / 29.5735

    # Last 7 days
    last_7d = (
        base_query.filter(WorkoutSession.timestamp >= seven_days_ago).all()
    )

    # ----------------------------
    # WEIGHT (latest session)
    # ----------------------------
    if sessions:
        last_weight_kg = sessions[0].weight_kg
        last_weight_lbs = last_weight_kg * 2.205 if last_weight_kg else None
    else:
        last_weight_kg = None
        last_weight_lbs = None

    # ----------------------------
    # AVG SWEAT RATE (7 days)
    # ----------------------------
    if last_7d:
        avg_sweat_rate = sum(s.sweat_rate for s in last_7d) / len(last_7d)
    else:
        avg_sweat_rate = None

    # ----------------------------
    # TEMP ADJUSTMENT (from last 7d)
    # ----------------------------
    if last_7d:
        avg_temp_f = sum((s.temperature_c * 9/5 + 32) for s in last_7d) / len(last_7d)
    else:
        avg_temp_f = None

    temp_adjust = 0
    if avg_temp_f is not None:
        if avg_temp_f > 85:
            temp_adjust = 24
        elif avg_temp_f > 75:
            temp_adjust = 12

    # ----------------------------
    # HYDRATION GOAL CALCULATION
    # ----------------------------
    if last_weight_lbs and avg_sweat_rate is not None:
        baseline = last_weight_lbs * 0.5               # ½ oz per lb
        sweat_component = avg_sweat_rate * 22          # 22 oz per 1 L/hr
        hydration_goal_oz = baseline + sweat_component + temp_adjust
    else:
        hydration_goal_oz = None

    # ----------------------------
    # 7-day stats (existing)
    # ----------------------------
    if last_7d:
        total_water_ml_7d = sum(s.water_needed_ml for s in last_7d)
        total_water_oz_7d = total_water_ml_7d / 29.5735

        temps = [s.temperature_c for s in last_7d]
        max_temp_f = (max(temps) * 9/5 + 32) if temps else None
    else:
        total_water_oz_7d = None
        max_temp_f = None

    stats = {
        "today_workouts": todays_count,
        "lifetime_workouts": base_query.count(),
        "avg_sweat_rate": avg_sweat_rate,
        "total_water_oz_7d": total_water_oz_7d,
        "max_temp_f": max_temp_f,
        "total_water_oz_today": total_water_oz_today,

        # NEW FIELD FOR DASHBOARD
        "hydration_goal_oz": hydration_goal_oz
    }

    # ----------------------------
    # CHART DATA (unchanged)
    # ----------------------------
    chart_data = {
        "dates": [s.timestamp.strftime("%m/%d") for s in sessions],
        "sweat_rate": [s.sweat_rate for s in sessions],
        "water_oz": [round(s.water_needed_ml / 29.5735, 1) for s in sessions],
        "temp_f": [round((s.temperature_c * 9/5 + 32), 1) for s in sessions],
        "temp_vs_sweat": [
            {
                "x": round((s.temperature_c * 9 / 5) + 32, 1),
                "y": s.sweat_rate
            }
            for s in sessions
        ]
    }

    return render_template(
        "index.html",
        sessions=sessions,
        stats=stats,
        chart=chart_data
    )

# ------------------- REGISTER -------------------

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per minute")
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Basic sanity checks
        if not valid_username(username):
            return "Invalid username. Use 3–20 letters, numbers, or underscore.", 400

        if not valid_password(password):
            return "Invalid password length. Use 6–64 characters.", 400

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return "Username already taken", 400

        # Create user
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
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Avoid leaking which part is wrong
        if not valid_username(username) or not valid_password(password):
            return "Invalid username or password", 400

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect("/")

        return "Invalid username or password", 400

    return render_template("login.html")


# ------------------- LOGOUT -------------------

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


# ------------------- CALCULATE HYDRATION -------------------

@app.route("/calculate", methods=["POST"])
@login_required
@limiter.limit("30 per minute")
def calculate():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Extract raw values
    raw_weight = data.get("weight")
    raw_sex = data.get("sex")
    raw_duration = data.get("duration")
    raw_hr = data.get("heart_rate")
    raw_temp = data.get("temp")

    # Validate numeric fields (all in metric at this point)
    weight = validate_number(raw_weight, 30, 300)        # kg
    duration = validate_number(raw_duration, 1, 600)     # minutes
    heart_rate = validate_number(raw_hr, 30, 230)        # bpm
    temp = validate_number(raw_temp, -20, 60)            # °C

    if None in [weight, duration, heart_rate, temp]:
        return jsonify({"error": "Numeric fields out of allowed range"}), 400

    # Validate sex
    if raw_sex not in ("male", "female"):
        return jsonify({"error": "Invalid sex value"}), 400

    # Run hydration engine (already expects metric units)
    result = hydration_engine(
        weight=weight,
        sex=raw_sex,
        duration_min=duration,
        heart_rate=heart_rate,
        temp_c=temp,
    )

    # Save to DB
    new_session = WorkoutSession(
        user_id=current_user.id,
        duration_min=duration,
        calories=result.get("calories", 0),
        avg_heart_rate=heart_rate,
        temperature_c=temp,
        weight_kg=weight,  # <--- ADD THIS LINE
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

    return jsonify(result)


# ------------------- (Optional) SEPARATE HISTORY PAGE -------------------

@app.route("/history")
@login_required
def history():
    sessions = (
        WorkoutSession.query.filter_by(user_id=current_user.id)
        .order_by(WorkoutSession.timestamp.desc())
        .all()
    )
    return render_template("history.html", sessions=sessions)


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)