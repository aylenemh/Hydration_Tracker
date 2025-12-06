# Build Instructions

This section explains how another developer can fully set up, run, and test the HydrateTrack application from scratch.

1. Development Environment

This project was developed using PyCharm, but the codebase is fully IDE-independent.
Any Python-based development environment may be used, including:
	•	VS Code
	•	PyCharm
	•	Sublime Text
	•	Terminal-only workflow
	•	Jupyter / Colab (for helper scripts)

⚠️ Important:
If using VS Code or PyCharm, you may simply open the project folder, install dependencies, and run python app.py from the built-in terminal to get everything to work.

All setup, dependency installation, and application execution can be performed entirely from the terminal.

2. System Requirements

To successfully run HydrateTrack, the following environment is recommended:
	•	Python: 3.8 – 3.11
	•	Operating System: macOS, Windows, or Linux
	•	Disk space: < 200 MB
	•	Browser: Chrome / Safari / Firefox (for viewing the web UI)

3. Project Structure
  Hydration_Track/

    app.py
    models.py
    hydration_engine.py
    requirements.txt
    
    static/
      bottle.svg
      styles.css
      script.js
      
    templates/
      index.html
      login.html
      register.html
      setup.html
      history.html
      layout.html
      
    hydration.db   (auto-generated on first run)

4. Dependencies

All dependencies are listed in requirements.txt.

Key packages include:
	•	Flask – main web framework
	•	Flask-Login – authentication
	•	Flask-Limiter – rate-limiting for security
	•	SQLAlchemy – ORM database layer
	•	Werkzeug – password hashing
	•	Jinja2 – HTML templating
	•	WTForms (optional) – form handling
	•	Python 3.x Standard Library

  Install dependencies with:
    pip install -r requirements.txt

5. Environment Setup
   Step 1 — Clone the project repository
     git clone <your_repo_url_here>
     cd Hydration_Track
   Step 2 - Create a virtual environment
     -macOS / Linux:
       python3 -m venv venv
       source venv/bin/activate
    -windows
       python -m venv venv
       venv\Scripts\activate
   Step 3 - Install all project dependencies
      pip install -r requirements.txt

6. Configure (.env file)
   Create a file called: .env
   and include:
     SECRET_KEY=supersecretkey123
     DATABASE_URL=sqlite:///hydration.db
   (A sample file may be provided as env.example.)
   
7. Initialize the Database
   Flask will automatically create hydration.db when running:
   Run - python app.py
   If resetting the database is needed:
     Delete hydration.db, then: python app.py

8. Running the Application
   Start the Flask server with: python app.py
   Then open a browser and navigate to: http://127.0.0.1:5000

   You will automatically be redirected to:
    	•	/register if no account exists yet
    	•	/login
    	•	/setup for the initial profile questionnaire

9. Optional: Development Build (Debug Mode)
    To run with debug auto-reload:
       export FLASK_ENV=development
       python app.py

   Windows:
       set FLASK_ENV=development
       python app.py

10. Replication Checklist
A developer should be able to reproduce this project if they follow:
  Clone repo
  Create a virtual environment
  Install dependencies
  Create .env file
  Run python app.py
  Application becomes fully functional




   
