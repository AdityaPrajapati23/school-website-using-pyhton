from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.utils import secure_filename
import pandas as pd
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Email Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# ---------------- HOME ----------------
@app.route('/')
def home():
    return redirect('/login')
# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?",
                       (username, password, role))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
            session['role'] = role
            return redirect('/dashboard')
        else:
            return "Invalid Username or Password"

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, class, phone FROM students")
        students = cursor.fetchall()
        conn.close()
        return render_template('dashboard.html', students=students)
    return redirect('/login')

# ---------------- ADMISSION ----------------
@app.route('/admission')
def admission():
    return render_template('admission.html')

@app.route('/submit_admission', methods=['POST'])
def submit_admission():
    data = (
        request.form['name'],
        request.form['dob'],
        request.form['class'],
        request.form['father'],
        request.form['phone']
    )
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, dob, class, father, phone) VALUES (?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# ---------------- DELETE STUDENT ----------------
@app.route('/delete_student/<int:id>')
def delete_student(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# ---------------- NOTICE ----------------
@app.route('/add_notice', methods=['GET', 'POST'])
def add_notice():
    if request.method == 'POST':
        notice = request.form['notice']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notices (notice) VALUES (?)", (notice,))
        conn.commit()
        conn.close()
        return redirect('/dashboard')
    return render_template('add_notice.html')

# ---------------- GALLERY ----------------
@app.route('/gallery')
def gallery():
    images = os.listdir(UPLOAD_FOLDER)
    return render_template('gallery.html', images=images)

@app.route('/upload', methods=['POST'])
def upload():
    if 'role' in session and session['role'] == 'admin':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect('/gallery')

# ---------------- EXPORT EXCEL ----------------
@app.route('/export')
def export():
    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    df.to_excel("students.xlsx", index=False)
    return "Excel file created!"

# ---------------- ID CARD PDF ----------------
@app.route('/idcard/<int:id>')
def idcard(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, class, phone FROM students WHERE id=?", (id,))
    student = cursor.fetchone()
    conn.close()

    file_path = "static/idcard.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 700, "SCHOOL ID CARD")
    c.drawString(100, 650, f"Name: {student[0]}")
    c.drawString(100, 620, f"Class: {student[1]}")
    c.drawString(100, 590, f"Phone: {student[2]}")
    c.save()

    return redirect('/static/idcard.pdf')

# ---------------- EMAIL ----------------
@app.route('/send_email')
def send_email():
    msg = Message("School Notice",
                  sender="your_email@gmail.com",
                  recipients=["student_email@gmail.com"])
    msg.body = "New notice uploaded. Check school website."
    mail.send(msg)
    return "Email Sent!"

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)