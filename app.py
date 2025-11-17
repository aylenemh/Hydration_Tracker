from flask import Flask, render_template
from hydration_engine import hydration_engine

app = Flask(__name__)

@app.route("/calculate", methods=["POST"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True,port=5001)


