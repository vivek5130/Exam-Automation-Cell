from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re;
from dotenv import load_dotenv
import os
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from transformers import pipeline
import textdistance

load_dotenv()
app = Flask(__name__)

# app.secret_key = 'your_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# db = SQLAlchemy(app)

#Mysql
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = os.getenv('HOST')
app.config['MYSQL_USER'] = os.getenv('USER')
app.config['MYSQL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DATABASE')

 
mysql = MySQL(app)

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'roll' in request.form and 'password' in request.form:
        roll = request.form['roll']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE roll = % s AND password = % s', (roll, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['roll'] = account['roll']
            msg = 'Logged in successfully !'
            return render_template('dashboard.html', msg = msg)
        else:
            msg = 'Incorrect roll / password !'
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('roll', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'roll' in request.form and 'password' in request.form and 'email' in request.form :
        roll = request.form['roll']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE roll = % s', (roll, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', roll):
            msg = 'roll must contain only characters and numbers !'
        elif not roll or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts (roll, password, email) VALUES (%s, %s, %s)', (roll, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app.route('/dashboard')
def dashboard():
    subjects = ['Math', 'Science', 'History']  # Replace with dynamic data if needed
    return render_template('dashboard.html', subjects=subjects)

#---------------------------------------------------

import google.generativeai as genai
import requests 

genai.configure(api_key= os.getenv('API_KEY'))
model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content("generate upto 10 questions on maths with options")
# print(response.text)


@app.route('/exam/<subject>', methods=['GET', 'POST'])
def exam(subject):
    if request.method == 'GET':
        prompt = f"Generate 5 exam questions on the topic of {subject}."
        response = model.generate_content(prompt)

        # Extract and structure the questions
        if response and response.text:
            print(response)
            questions = [q.strip() for q in response.text.split('\n') if q.strip()]
        else:
            questions = []  # Handle API failure gracefully

        return render_template('exam.html', subject=subject, questions=questions)

    # POST logic (e.g., handle form submission for answers)
    return redirect(url_for('dashboard'))  # Temporary redirect after POST

# @app.route('/result')
# def result():
#     score = request.args.get('score', 0)
#     return render_template('result.html', score=score)

# # Utilities

# def evaluate_descriptive_answer(student_answer, correct_answer):
#     # Mocked evaluation logic
#     similarity = textdistance.jaro_winkler(student_answer, correct_answer)
#     return similarity * 10  # Scale similarity to a score out of 10

if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)
