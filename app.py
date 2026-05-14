from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import pickle

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- MODEL LOADING (FIXED) ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "model", "house_model.pkl")

print("Loading model...")
model = pickle.load(open(model_path, "rb"))
print("Model loaded successfully")

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect("database.db")

# Create tables once
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    password TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    area INT,
    bedrooms INT,
    bathrooms INT,
    parking INT,
    age INT,
    price INT
)
""")

conn.commit()
conn.close()

# ---------------- AUTH ----------------
@app.route("/")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create_user", methods=["POST"])
def create_user():
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    conn.execute("INSERT INTO users(email, password) VALUES (?, ?)", (email, password))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/login_user", methods=["POST"])
def login_user():
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    ).fetchone()
    conn.close()

    if user:
        session["user"] = email
        return redirect("/home")

    return "Invalid Login ❌"


# ---------------- PAGES ----------------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("home.html")


@app.route("/predict_page")
def predict_page():
    if "user" not in session:
        return redirect("/")
    return render_template("predict.html")


@app.route("/about")
def about():
    return render_template("about.html")


# ---------------- PREDICTION ----------------
@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        return redirect("/")

    area = int(request.form["area"])
    bedrooms = int(request.form["bedrooms"])
    bathrooms = int(request.form["bathrooms"])
    parking = int(request.form["parking"])
    age = int(request.form["age"])

    price = int(model.predict([[area, bedrooms, bathrooms, parking, age]])[0])

    conn = get_db()
    conn.execute("""
        INSERT INTO history(user, area, bedrooms, bathrooms, parking, age, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session["user"], area, bedrooms, bathrooms, parking, age, price))
    conn.commit()
    conn.close()

    return render_template("result.html", price=price)


# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/")

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM history WHERE user=?",
        (session["user"],)
    ).fetchall()
    conn.close()

    return render_template("history.html", rows=rows)


# ---------------- ANALYTICS ----------------
@app.route("/analytics")
def analytics():
    conn = get_db()
    prices = conn.execute("SELECT price FROM history").fetchall()
    conn.close()

    prices = [p[0] for p in prices] if prices else [0]

    total = len(prices)
    avg = int(sum(prices) / len(prices))
    max_price = max(prices)
    min_price = min(prices)

    return render_template(
        "analytics.html",
        total=total,
        avg=avg,
        max=max_price,
        min=min_price
    )


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)