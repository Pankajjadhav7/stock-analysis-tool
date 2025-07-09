from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session,flash, redirect, url_for
from datetime import datetime, timedelta
import pymongo
import pandas as pd
from json_response import JSONResponse
from common_function import *
from stock_calculation import *
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # For session management

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Connect to MongoDB
db = client["MyStock"]  # Database name
collection = db["custom_symbol"]  # Collection name
stock_collection = db["stock_collection"]
signup_collection = db["signup_collection"]

# Route for the home page (login page)
@app.route("/")
def index():
    # Check if the user is logged in
    if 'username' in session:
        return render_template('index.html')  # Show main dashboard if logged in
    return redirect(url_for("login"))  # Redirect to login page if not logged in


@app.route("/login", methods=["POST", "GET"])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get("username")
            password = request.form.get("password")

            if not all([username, password]):
                flash("All fields are required", "error")
                return redirect(url_for("login"))

            user = signup_collection.find_one({"username": username})
            if user and user["password"] == password:
                session['username'] = username
                flash("Login successful", "success")
                return redirect(url_for('index'))  # Redirect to index route
            else:
                flash("Invalid username or password", "error")
                return redirect(url_for("login"))

        return render_template("login.html")  # GET request
    except Exception as e:
        flash("Error: " + str(e), "error")
        return redirect(url_for("login"))


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        try:
            email_id = request.form.get("email_id")
            username = request.form.get("username")
            password = request.form.get("password")
            mobileno = request.form.get("mobile")

            if not all([email_id, username, password, mobileno]):
                flash("All fields are required", "error")
                return redirect(url_for("signup"))

            # if signup_collection.find({"email_id": email_id}):
            #     flash("email_id already registered", "error")
            #     return redirect(url_for("signup"))

            # Insert user data into the database
            user_data = {
                "email_id": email_id,
                "username": username,
                "password": password,
                "mobileno": mobileno
            }

            signup_collection.insert_one(user_data)
            flash("Signup successful", "success")
            return redirect(url_for("signup"))

        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for("signup"))
    
    return render_template("signup.html")


# Route for handling upload functionality (after login)
@app.route("/upload-data", methods=["GET", "POST"])
def upload_data():
    if 'username' not in session:
        return redirect(url_for('index'))  # Redirect to login page if not logged in
    
    if request.method == 'POST':
        try:
            # Check if a file is uploaded
            if 'file' not in request.files:
                message = "No file part"
                response = jsonify(error=message), 400
                return response

            file = request.files['file']

            # If no file is selected
            if file.filename == '':
                message = "No selected file"
                response = jsonify(error=message), 400
                return response

            # Save the file temporarily
            file.save("files/output/temp.csv")

            # Try reading the file with different encodings
            encodings = ["utf-8", "latin-1"]
            for encoding in encodings:
                try:
                    df = pd.read_csv("files/output/temp.csv", encoding=encoding)
                    df.columns = df.columns.str.strip()  # Strip any extra spaces from column names
                    break
                except UnicodeDecodeError:
                    continue

            # Check if all expected columns are present
            expected_header = ['Symbol', 'Date', 'Price', 'Open', 'High', 'Low', 'Vol.']
            missing_headers = [header for header in expected_header if header not in df.columns]
            if missing_headers:
                message = f"Headers missing in the file: {', '.join(missing_headers)}"
                response = jsonify(error=message), 400
                return response

            # Rename columns to standardized names
            df.rename(columns={
                'Symbol': 'Symbol',
                'Date': 'Date',
                'Price': 'Price',
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Vol.': 'Vol',
            }, inplace=True)

            # Add 'CreatedOn' column with current date
            created_on = get_utc_date()
            df["CreatedOn"] = created_on

            # Try to convert date column to standard format
            try:
                convert_date_column(df, "Date", ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"], "%d-%m-%Y")
            except Exception as e:
                message = "Date format doesn't match yyyy-mm-dd."
                response = jsonify(error=message), 400
                return response

            # Prepare data for insertion
            data = df.to_dict(orient="records")
            header = ['Symbol', 'Date', 'Price', 'Open', 'High', 'Low', 'Vol', "CreatedOn"]

            # Insert each row into the database
            stock_collection.drop()
            inserted_count = 0
            for each in data:
                row = {field: str(each[field]) if field in header else each[field] for field in header}
                stock_collection.insert_one(row)
                inserted_count += 1

            message = f"Inserted {inserted_count} rows into Stock Data."
            response = jsonify(message=message), 200
            return response

        except Exception as e:
            message = str(e)
            response = jsonify(error=message), 500
            return response

    return render_template("upload_data.html")

@app.route("/get-report", methods=["POST", "GET"])
def get_stock_report():
    if 'username' not in session:
        return redirect(url_for('index'))

    try:
        if request.method == 'POST':
            start_date_str = request.form.get("start_date")
            end_date_str = request.form.get("end_date")

            start_date = pd.to_datetime(start_date_str)
            end_date = pd.to_datetime(end_date_str) + timedelta(days=1)

            # Load data
            all_data_df = lst_yrd_10_df(stock_collection)
            stock_df = stock_data_calculation(stock_collection, start_date, end_date)

            # Get both views data
            report_data, yearwise_report = report_calculation(all_data_df, stock_df, start_date, end_date)

            # Get last 10 years list
            years_list = sorted([start_date.year - i for i in range(1, 11)], reverse=True)

            return render_template(
                "test.html",
                report_data=report_data,
                yearwise_report=yearwise_report,
                years_list=years_list
            )

    except Exception as e:
        print("Error:", str(e))
        return render_template(
            "test.html",
            report_data=[],
            yearwise_report={},
            years_list=[]
        )



# Route for logging out
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('index'))  # Redirect to login page

if __name__ == "__main__":
    app.run(debug=True, port=5002)
