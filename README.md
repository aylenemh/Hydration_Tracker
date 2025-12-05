# HydrateTrack

HydrateTrack is a Flask-based hydration & workout tracking app that helps athletes and everyday users calculate hydration needs, track daily water intake, and monitor sweat-rate and electrolyte loss over time. It turns guesswork into data-driven hydration.

---

## 🚀 Features

- Personalized hydration calculations based on weight, heart rate, workout duration, and temperature  
- Sweat rate, water loss, and electrolyte (sodium, potassium, magnesium) recommendations  
- Persistent user accounts with secure login/registration  
- Daily water intake tracker with interactive “water bottle” animation  
- Analytics dashboard: sweat rate over time, water needs per workout, temperature vs sweat-rate charts  
- Workout history logging, date-based water tracking, and drink recommendations for post-exercise recovery  
- Basic security: password hashing, input validation, rate limiting, and session-based access control  

---

## 📦 Tech Stack & Dependencies

- **Python 3.9+**  
- **Flask** — web framework  
- **Flask-Login** — user authentication  
- **Flask-Limiter** — rate limiting for security  
- **SQLAlchemy + SQLite** — database ORM + storage  
- **HTML / CSS / JavaScript** (with Chart.js via CDN) — frontend & data visualization  

---

## 🛠 Installation & Setup (Replicable)

Follow these steps to run HydrateTrack locally:
1. Clone the repo
git clone https://github.com/<your-username>/Hydration_Tracker.git
cd Hydration_Tracker/Hydration_Track

2. (Optional but recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate      # macOS / Linux
or on Windows:
venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Run the application
python app.py

Then open your browser at: http://127.0.0.1:5000

The SQLite database (hydration.db) will be created automatically on first run.


## ✅ Usage Flow
	1.	Register a new account
	2.	Log in
	3.	On first login, complete the profile setup (weight + sex) — this sets your personal hydration goal
	4.	Use the “Hydration Calculator” tab after workouts to compute water & electrolyte needs
	5.	View your workout history and hydration analytics on the Dashboard & Analytics tabs
	6.	Add water intake throughout the day — watch the water bottle fill up!
	7.	Drink recommendations provided based on your total electrolyte loss

## 🔐 Security & Data Integrity
	•	Passwords are stored using secure hashing (no plain-text storage)
	•	Unique usernames enforced to prevent account duplication
	•	Rate limiting to prevent abuse or brute-force attempts
	•	Input validation on all numeric and form fields (prevents invalid or malicious data)
	•	Session-based authentication using Flask-Login
	•	ORM-based database operations (SQLAlchemy) to avoid SQL injection vulnerabilities

## 📁 Project Structure 




  <img width="396" height="347" alt="Screenshot 2025-12-05 at 1 45 31 PM" src="https://github.com/user-attachments/assets/003164f9-d55a-4959-8027-630080153911" />



## 🖼 Screenshots

These images help illustrate key parts of the application.

### Dashboard:

<img width="443" height="703" alt="Screenshot 2025-12-05 at 1 49 27 PM" src="https://github.com/user-attachments/assets/bf6697df-0779-4c31-b1ae-3c556163d9f0" />

### Hydration Calculator:
<img width="714" height="617" alt="Screenshot 2025-12-05 at 1 50 08 PM" src="https://github.com/user-attachments/assets/c8677617-d0b6-4c83-9ca6-5fb0e8adc704" />

### History Tab:
<img width="697" height="228" alt="Screenshot 2025-12-05 at 1 50 21 PM" src="https://github.com/user-attachments/assets/aade701f-58b8-4f5e-afb2-c8b93740fe70" />

### Analytics Chart:

<img width="439" height="708" alt="Screenshot 2025-12-05 at 1 50 35 PM" src="https://github.com/user-attachments/assets/0f2cf8e4-19af-4d37-af13-842ccfa5387e" />




## 🧑‍💻 Development Environment

This project was developed using PyCharm, but the codebase is IDE-independent. You can use any Python-based development environment (VS Code, Sublime, terminal, etc.) — the setup works from the command line and does not rely on IDE-specific features.


##  📝 Contribution & Extension Ideas

Want to help or extend HydrateTrack? Great! Possible future enhancements:
	•	Unit preference toggle (metric ↔ imperial)
	•	Profile editing (change weight, height, etc.)
	•	Integration with fitness trackers (e.g. wearables or Strava)
	•	Notification/reminder system for water intake
	•	Export history as CSV / PDF
	•	Dark mode / improved mobile responsiveness

Feel free to fork the repo and submit pull requests for new features or bug fixes.


##  🧾 License & Disclaimer

This project is provided for academic purposes and personal use only.
Hydration recommendations are based on a simplified model and should not substitute professional medical or dietary advice.


##  📬 Contact / Acknowledgments
Created by: Nathan Leppo & Aylene Noy

Thanks for checking out HydrateTrack! 💧

