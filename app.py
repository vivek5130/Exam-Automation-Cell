from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re;
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
# from transformers import pipeline
import textdistance

app = Flask(__name__)

# app.secret_key = 'your_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# db = SQLAlchemy(app)

#Mysql
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'vivek5926'
app.config['MYSQL_DB'] = 'miniproject'
 
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

# @app.route('/exam/<subject>', methods=['GET', 'POST'])
# def exam(subject):
#     if request.method == 'POST':
#         answers = request.form.to_dict()
#         total_score = 0
#         for question_id, answer in answers.items():
#             question = Question.query.get(int(question_id))
#             if question.question_type == 'MCQ':
#                 if answer.strip().lower() == question.correct_answer.strip().lower():
#                     score = 1  # Full score for correct MCQ
#                 else:
#                     score = 0
#             else:  # Descriptive
#                 score = evaluate_descriptive_answer(answer, question.correct_answer)
#             total_score += score
#             new_answer = Answer(user_id=session['user_id'], question_id=question.id, answer_text=answer, score=score)
#             db.session.add(new_answer)
#         db.session.commit()
#         return redirect(url_for('result', score=total_score))

#     # Fetch questions using Gemini API (Mocked for now)
#     questions = Question.query.filter_by(subject=subject).all()
#     return render_template('exam.html', questions=questions)

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
