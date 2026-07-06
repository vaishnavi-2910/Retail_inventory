
from flask import Flask, render_template, request, redirect, session, flash, jsonify
import sqlite3
import os
import numpy as np
import pickle

# ---------------- BASE SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "safeher_secret_key_123"
app.config["SESSION_PERMANENT"] = True


# ---------------- LOAD ML MODEL (SAFE VERSION) ----------------
MODEL_PATH = os.path.join(BASE_DIR, "risk_model.pkl")

if os.path.exists(MODEL_PATH):
    model = pickle.load(open(MODEL_PATH, "rb"))
    print("✅ ML Model loaded successfully")
else:
    model = None
    print("⚠️ WARNING: risk_model.pkl not found! Run MLmodel.py first.")


# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(os.path.join(BASE_DIR, "database.db"))
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE TABLES ----------------
def create_tables():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            type TEXT,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()

create_tables()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO users(name,email,password) VALUES (?,?,?)",
                (name, email, password)
            )
            conn.commit()
            return redirect("/login")
        except:
            flash("Email already exists!")
        finally:
            conn.close()

    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect("/dashboard")
        else:
            flash("Invalid login credentials")

    return render_template("login.html")


# ---------------- LOGIN CHECK ----------------
def login_required():
    return session.get("user_id") is not None


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect("/login")

    return render_template("dashboard.html", user=session.get("user_name"))


# ---------------- MAP ----------------
@app.route("/map")
def map_page():
    if not login_required():
        return redirect("/login")

    return render_template("map.html")


# ---------------- EMERGENCY ----------------
@app.route("/emergency")
def emergency():
    if not login_required():
        return redirect("/login")

    return render_template("emergency.html")


# ---------------- REPORT ----------------
@app.route("/report", methods=["GET", "POST"])
def report():
    if not login_required():
        return redirect("/login")

    if request.method == "POST":
        location = request.form["location"]
        type_ = request.form["type"]
        description = request.form["description"]

        conn = get_db()
        c = conn.cursor()

        c.execute("""
            INSERT INTO reports(location,type,description)
            VALUES (?,?,?)
        """, (location, type_, description))

        conn.commit()
        conn.close()

        flash("Report submitted successfully!")

    return render_template("report.html")


# ---------------- ML RISK PREDICTION ----------------
@app.route("/predict-risk", methods=["POST"])
def predict_risk():

    if model is None:
        return jsonify({
            "error": "ML model not loaded. Run MLmodel.py first."
        }), 500

    try:
        data = request.json
        features = np.array(data["features"]).reshape(1, -1)

        risk = model.predict(features)[0]
        safety = (1 - risk) * 100

        return jsonify({
            "risk": float(risk),
            "safety_score": float(safety)
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


# ---------------- ROUTES ----------------
@app.route("/routes")
def routes():
    if not login_required():
        return redirect("/login")

    return render_template("routes.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict_page')
def predict_page():
    return render_template('predict.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()

        stock = int(data.get('stock', 0))
        sales = list(map(int, data.get('sales', [])))

        
        df = pd.DataFrame({
            "Month": range(1, len(sales) + 1),
            "Sales": sales
        })

       
        X = df[["Month"]]
        y = df["Sales"]

        model = LinearRegression()
        model.fit(X, y)

        # Predict next month
        next_month = np.array([[len(sales) + 1]])
        prediction = int(model.predict(next_month)[0])

       
        growth = 0
        if len(sales) > 1 and sales[-2] != 0:
            growth = ((sales[-1] - sales[-2]) / sales[-2]) * 100

       
        if stock > prediction:
            status = "Sufficient Stock"
            color = "green"
        elif stock < prediction:
            status = "Low Stock"
            color = "red"
        else:
            status = "Optimal"
            color = "orange"

        labels = [f"Month {i+1}" for i in range(len(sales))]
        labels.append("Next Month")

        values = sales.copy()
        values.append(prediction)

        return jsonify({
            "prediction": prediction,
            "growth": round(growth, 2),
            "status": status,
            "color": color,
            "labels": labels,
            "values": values
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Something went wrong"}), 500



if __name__ == '__main__':

    app.run(debug=True)