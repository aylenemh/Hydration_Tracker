from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # Optional: Strava OAuth tokens
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    expires_at = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-many: a user has many workout sessions
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

    # Workout metrics
    duration_min = db.Column(db.Float)
    calories = db.Column(db.Float)
    avg_heart_rate = db.Column(db.Float)
    temperature_c = db.Column(db.Float)
    weight_kg = db.Column(db.Float)   # <-- NEW FIELD

    # Hydration engine outputs
    sweat_rate = db.Column(db.Float)
    total_sweat_loss = db.Column(db.Float)
    water_needed_ml = db.Column(db.Float)
    sodium_mg = db.Column(db.Float)
    potassium_mg = db.Column(db.Float)
    magnesium_mg = db.Column(db.Float)

    dehydration_alert = db.Column(db.Boolean, default=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)