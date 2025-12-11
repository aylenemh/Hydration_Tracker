# HydrateTrack 💧  
Smart Hydration & Electrolyte Guidance for Athletes

HydrateTrack is a Flask-based web app that helps athletes and active users understand **how much water and electrolytes they should consume** after a workout. It combines workout inputs (duration, heart rate, temperature, sex, weight) with a custom hydration model to estimate:

- Sweat rate (L/hr)  
- Total sweat loss (L)  
- Recommended water intake (mL / oz)  
- Sodium, potassium, and magnesium needs (mg)  
- Daily hydration goal and bottle-style progress visualization  

---

## Table of Contents

1. [Overview](#overview)  
2. [Core Features](#core-features)  
3. [Tech Stack](#tech-stack)  
4. [Project Structure](#project-structure)  
5. [Installation & Setup (Replicable)](#installation--setup-replicable)  
   - [Using the Terminal](#using-the-terminal)  
   - [Using an IDE (PyCharm--VS-Code)](#using-an-ide-pycharm--vs-code)  
6. [Usage Flow](#usage-flow)  
7. [Security & Data Integrity](#security--data-integrity)  
8. [Screenshots](#screenshots)  
9. [Development Environment](#development-environment)  
10. [Contribution & Extension Ideas](#contribution--extension-ideas)  
11. [License & Disclaimer](#license--disclaimer)  
12. [Contact / Acknowledgments](#contact--acknowledgments)

---

## Overview

**HydrateTrack** helps answer a common question for athletes:

> *“How much should I drink and what electrolytes do I need after this workout?”*

The app uses:

- Heart rate  
- Workout duration  
- Temperature  
- Body weight  
- Sex  

to estimate **sweat rate, total sweat loss, and personalized hydration recommendations**, then visualizes progress through a **water bottle fill UI** and basic analytics.

The goal is to give users **clear, actionable guidance** instead of generic “drink more water” advice.

---

## Core Features

- 🔐 **User Accounts & Authentication**
  - Register / login / logout (Flask-Login)
  - Unique usernames enforced
  - Simple access control (must be logged in to use the app)

- 🧾 **First-Time Profile Setup**
  - Lightweight onboarding at `/setup`
  - User enters weight (lbs) and sex once
  - Used to compute an initial **daily hydration goal**

- 💧 **Hydration Calculator**
  - Inputs: weight, sex, duration, heart rate, temperature
  - Computes:
    - Sweat rate (L/hr)
    - Total sweat loss (L)
    - Water needed (mL & oz)
    - Sodium, potassium, magnesium recommendations (mg)
  - Temperature adjustment factors for hot conditions

- 📊 **Dashboard & Analytics**
  - Daily hydration progress with **animated water bottle**
  - Today’s workouts & water needs
  - 7-day average sweat rate
  - Water needed per workout (bar chart)
  - Temperature vs sweat rate (scatter plot)

- 🥤 **Refuel Suggestions**
  - Suggests drink options (e.g., water, sports drink, electrolyte mix)
  - Based on **today’s total electrolyte needs**

- 🗂️ **History**
  - Table of past workout sessions
  - Date/time, duration, water, sodium, and dehydration alert

- 🚰 **Daily Water Tracker**
  - Adds water consumed in oz
  - Visual bottle fill based on **personalized daily hydration goal**

---

## Tech Stack

- **Backend**
  - Python 3.x
  - Flask
  - Flask-Login (auth)
  - Flask-Limiter (rate limiting)
  - SQLAlchemy (ORM)

- **Frontend**
  - HTML / CSS / Jinja2 templates
  - JavaScript (fetch API)
  - Chart.js (charts)

- **Database**
  - SQLite (`hydration.db`)

---

## Installation & Setup (Replicable)

For more details look at Build Instructions.md

HydrateTrack can be run from any Python environment (terminal, VS Code, PyCharm, etc.). Follow the steps below to install and launch the application.

### Using the Terminal

Follow these steps to run HydrateTrack locally:
1. Clone the repo
   
		git clone https://github.com/aylenemh/Hydration_Tracker.git

		cd Hydration_Tracker/Hydration_Track

3. (Optional but recommended) Create a virtual environment
   	macOS / Linux:
   
		python3 -m venv venv
		
		source venv/bin/activate     
	Windows:

		venv\Scripts\activate

5. Install dependencies
   	
		pip install -r requirements.txt

7. Run the application
		
		ython app.py

Then open your browser at: http://127.0.0.1:5000

### Using an IDE (PyCharm / VS Code)
	1.	Open the Hydration_Track folder in your IDE
	2.	Create a virtual environment (IDE will prompt or allow through settings)
	3.	Install dependencies using: pip install -r requirements.txt
	4.	Run app.py using the IDE’s built-in run configuration

The app will launch exactly the same as the terminal method.

## Environment Variables

HydrateTrack uses a .env file to store application settings.

In the project root, create: .env

Add:


	SECRET_KEY=supersecretkey123
	DATABASE_URL=sqlite:///hydration.db

## Database Initialization & Reset

The SQLite database is automatically generated when the app is started:

To reset the database:

	rm hydration.db
	python app.py


## Usage Flow
	1.	Register a new account
	2.	Log in
	3.	On first login, complete the profile setup (weight + sex) — this sets your personal hydration goal
	4.	Use the “Hydration Calculator” tab after workouts to compute water & electrolyte needs
	5.	View your workout history and hydration analytics on the Dashboard & Analytics tabs
	6.	Add water intake throughout the day — watch the water bottle fill up!
	7.	Drink recommendations provided based on your total electrolyte loss

## Security & Data Integrity
	•	Passwords are stored using secure hashing (no plain-text storage)
	•	Unique usernames enforced to prevent account duplication
	•	Rate limiting to prevent abuse or brute-force attempts
	•	Input validation on all numeric and form fields (prevents invalid or malicious data)
	•	Session-based authentication using Flask-Login
	•	ORM-based database operations (SQLAlchemy) to avoid SQL injection vulnerabilities

## Project Structure 




  <img width="396" height="347" alt="Screenshot 2025-12-05 at 1 45 31 PM" src="https://github.com/user-attachments/assets/003164f9-d55a-4959-8027-630080153911" />



## Screenshots

These images help illustrate key parts of the application.

### Dashboard:

<img width="443" height="703" alt="Screenshot 2025-12-05 at 1 49 27 PM" src="https://github.com/user-attachments/assets/bf6697df-0779-4c31-b1ae-3c556163d9f0" />

### Hydration Calculator:
<img width="714" height="617" alt="Screenshot 2025-12-05 at 1 50 08 PM" src="https://github.com/user-attachments/assets/c8677617-d0b6-4c83-9ca6-5fb0e8adc704" />

### History Tab:
<img width="697" height="228" alt="Screenshot 2025-12-05 at 1 50 21 PM" src="https://github.com/user-attachments/assets/aade701f-58b8-4f5e-afb2-c8b93740fe70" />

### Analytics Chart:

<img width="439" height="708" alt="Screenshot 2025-12-05 at 1 50 35 PM" src="https://github.com/user-attachments/assets/0f2cf8e4-19af-4d37-af13-842ccfa5387e" />




## Development Environment

This project was developed using PyCharm, but the codebase is IDE-independent. You can use any Python-based development environment (VS Code, Sublime, terminal, etc.) — the setup works from the command line and does not rely on IDE-specific features.


##  Contribution & Extension Ideas

Want to help or extend HydrateTrack? Great! Possible future enhancements:

	•	Unit preference toggle (metric ↔ imperial)
	•	Profile editing (change weight, height, etc.)
	•	Integration with fitness trackers (e.g. wearables or Strava)
	•	Notification/reminder system for water intake
	•	Export history as CSV / PDF
	•	Dark mode / improved mobile responsiveness

Feel free to fork the repo and submit pull requests for new features or bug fixes.


##  License & Disclaimer

This project is provided for academic purposes and personal use only.
Hydration recommendations are based on a simplified model and should not substitute professional medical or dietary advice.


##  Contact / Acknowledgments
Created by: Nathan Leppo & Aylene Noy

Thanks for checking out HydrateTrack! 💧

