from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date   # ⬅ add date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Authentication
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # Profile (NEW)
    weight_kg = db.Column(db.Float)        # stores user weight in kg
    sex = db.Column(db.String(10))         # "male" or "female"
    daily_goal_oz = db.Column(db.Float)    # personalized hydration goal

    # OAuth (optional)
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    expires_at = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Daily hydration tracking
    water_today_oz = db.Column(db.Float, default=0.0)
    water_last_reset = db.Column(db.Date, default=date.today)

    # Relationships
    sessions = db.relationship("WorkoutSession", backref="user", lazy=True)

    # Password helpers
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    strava_activity_id = db.Column(db.Text, unique=True)

    # NEW FIELD
    weight_kg = db.Column(db.Float)

    duration_min = db.Column(db.Float)
    calories = db.Column(db.Float)
    avg_heart_rate = db.Column(db.Float)
    temperature_c = db.Column(db.Float)

    sweat_rate = db.Column(db.Float)
    total_sweat_loss = db.Column(db.Float)
    water_needed_ml = db.Column(db.Float)
    sodium_mg = db.Column(db.Float)
    potassium_mg = db.Column(db.Float)
    magnesium_mg = db.Column(db.Float)

    dehydration_alert = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class DailyWater(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.String(10))  # "YYYY-MM-DD"
    water_oz = db.Column(db.Float, default=0)