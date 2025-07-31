from flask import Flask, render_template, request, redirect, url_for, session
import csv
import joblib
from datetime import timedelta
from datetime import datetime


app = Flask(__name__)
app.secret_key = "your_secret_key"
app.permanent_session_lifetime = timedelta(minutes=30)

# Load model
model = joblib.load("drug_model.pkl")

# Encoding maps
sex_map = {"Male": 0, "Female": 1}
bp_map = {"LOW": 0, "NORMAL": 1, "HIGH": 2}
chol_map = {"NORMAL": 0, "HIGH": 1}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "welcome":
            session.permanent = True
            session["user"] = username
            return redirect(url_for("form"))
        else:
            return render_template("login.html", error="Invalid Credentials")
    return render_template("login.html")

@app.route("/form")
def form():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("form.html")

def new_func(name, age, sex, bp, chol, sodium, potassium, sugar, pulse, bmi, prediction, csv_module):
    with open("patient_history.csv", "a", newline="") as f:
        writer = csv_module.writer(f)
        writer.writerow([name, age, sex, bp, chol, sodium, potassium, sugar, pulse, bmi, prediction])

@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        name = request.form["name"]
        age = int(request.form["age"])
        sex_str = request.form["sex"]
        bp_str = request.form["bp"]
        chol_str = request.form["chol"]
        sodium = float(request.form["sodium"])
        potassium = float(request.form["potassium"])
        sugar = float(request.form["sugar"])
        pulse = float(request.form["pulse"])
        bmi = float(request.form["bmi"])

        # Encode categorical fields
        sex = sex_map[sex_str]
        bp = bp_map[bp_str]
        chol = chol_map[chol_str]

        # Make prediction
        input_data = [[sex, bp, chol, age, sodium, potassium, pulse, sugar, bmi]]
        prediction = model.predict(input_data)[0]

        # Save history with Date & Time
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with open("patient_history.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([name, age, sex_str, bp_str, chol_str, sodium, potassium, sugar, pulse, bmi, prediction, now])
        except Exception as e:
            print("Failed to write to CSV:", e)

        # Load history for this patient
        history = []
        try:
            with open("patient_history.csv", "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0].strip().lower() == name.strip().lower():
                        history.append(row)
        except FileNotFoundError:
            pass

        return render_template("result.html", name=name, age=age, sex=sex_str, 
                               bp=bp_str, chol=chol_str, sodium=sodium, potassium=potassium,
                               sugar=sugar, pulse=pulse, bmi=bmi, prediction=prediction, history=history)

    except Exception as e:
        return f"Prediction failed: {e}", 400



@app.route("/history")
def history():
    name_filter = request.args.get("name")
    records = []

    try:
        with open("patient_history.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if not name_filter or row[0] == name_filter:
                    records.append(row)
    except FileNotFoundError:
        pass

    return render_template("history.html", records=records)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

def new_func(name, age, sex, bp, chol, sodium, potassium, sugar, pulse, bmi, prediction, csv_module):
    try:
        rows = []
        found = False

        # Read existing rows
        with open("patient_history.csv", "r") as f:
            reader = csv_module.reader(f)
            for row in reader:
                if row[0] == name and row[1] == str(age):
                    found = True
                else:
                    rows.append(row)

        # Add new/updated row
        rows.append([name, age, sex, bp, chol, sodium, potassium, sugar, pulse, bmi, prediction])

        # Rewrite the file
        with open("patient_history.csv", "w", newline="") as f:
            writer = csv_module.writer(f)
            writer.writerows(rows)

    except FileNotFoundError:
        # File doesn't exist yet, create and write the first row
        with open("patient_history.csv", "w", newline="") as f:
            writer = csv_module.writer(f)
            writer.writerow([name, age, sex, bp, chol, sodium, potassium, sugar, pulse, bmi, prediction])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

