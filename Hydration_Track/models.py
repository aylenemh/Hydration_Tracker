from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# -------------------------------------------------------------------
# USER MODEL
# -------------------------------------------------------------------
class User(UserMixin, db.Model):
    """
    Represents an application user.
    Stores authentication info, profile data (weight, sex),
    hydration goal, and daily water tracking.
    """

    id = db.Column(db.Integer, primary_key=True)

    # -----------------------------
    # Authentication fields
    # -----------------------------
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # -----------------------------
    # User profile (collected once)
    # Used to calculate hydration needs
    # -----------------------------
    weight_kg = db.Column(db.Float)      # stored in kilograms for consistency
    sex = db.Column(db.String(10))       # "male" or "female"
    daily_goal_oz = db.Column(db.Float)  # personalized hydration goal (oz)

    # -----------------------------
    # OAuth tokens (optional future Strava integration)
    # -----------------------------
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    expires_at = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # -----------------------------
    # Daily hydration tracking
    # Tracks how much the user has consumed today.
    # Reset each day in ensure_daily_water_state()
    # -----------------------------
    water_today_oz = db.Column(db.Float, default=0.0)
    water_last_reset = db.Column(db.Date, default=date.today)

    # -----------------------------
    # Relationships
    # A user → many workout sessions
    # -----------------------------
    sessions = db.relationship("WorkoutSession", backref="user", lazy=True)

    # -----------------------------
    # Password helpers
    # -----------------------------
    def set_password(self, password):
        """Hashes and stores a password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Validates password against stored hash."""
        return check_password_hash(self.password_hash, password)


# -------------------------------------------------------------------
# WORKOUT SESSION MODEL
# -------------------------------------------------------------------
class WorkoutSession(db.Model):
    """
    Stores hydration-related results for a single workout.
    Each session records sweat rate, environmental conditions,
    electrolyte loss, and recommended water intake.
    """

    id = db.Column(db.Integer, primary_key=True)

    # Link to User
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # Optional Strava integration
    strava_activity_id = db.Column(db.Text, unique=True)

    # Store user weight at time of workout
    weight_kg = db.Column(db.Float)

    # Core workout metrics
    duration_min = db.Column(db.Float)
    calories = db.Column(db.Float)
    avg_heart_rate = db.Column(db.Float)
    temperature_c = db.Column(db.Float)

    # Hydration calculations
    sweat_rate = db.Column(db.Float)           # L/hr
    total_sweat_loss = db.Column(db.Float)     # L
    water_needed_ml = db.Column(db.Float)      # ml required
    sodium_mg = db.Column(db.Float)
    potassium_mg = db.Column(db.Float)
    magnesium_mg = db.Column(db.Float)

    dehydration_alert = db.Column(db.Boolean, default=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------------------------------------------------------
# DAILY WATER MODEL
# -------------------------------------------------------------------
class DailyWater(db.Model):
    """
    Tracks the user's *actual* water consumption per day.
    Used for the water bottle fill UI.

    Storing date as a string ("YYYY-MM-DD") avoids timezone issues
    and simplifies queries.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # Store date as a simple string for ease of comparison
    date = db.Column(db.String(10))  # ex: "2025-11-27"

    # Ounces consumed today
    water_oz = db.Column(db.Float, default=0)