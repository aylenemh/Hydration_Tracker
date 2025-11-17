from flask import Flask, render_template, request, jsonify
from functions.hydration_engine import hydration_engine  # import your engine function

app = Flask(__name__)

# Serve the HTML page
@app.route("/")
def index():
    return render_template("index.html")

# Hydration calculation endpoint
@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()

    weight = data.get("weight", 0)
    sex = data.get("sex", "male")
    duration = data.get("duration", 0)
    heart_rate = data.get("heart_rate", 0)
    temp = data.get("temp", 22)

    # Call your engine
    results = hydration_engine(weight, sex, duration, heart_rate, temp)

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)



