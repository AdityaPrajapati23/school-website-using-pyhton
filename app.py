
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# Home Page
@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT notice FROM notices")
    notices = cursor.fetchall()
    conn.close()

    return render_template('index.html', notices=notices)

# Login Page
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





@app.route('/upload', methods=['POST'])
def upload():
    if 'role' in session and session['role'] == 'admin':
        import os
        from werkzeug.utils import secure_filename

        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join('static/uploads', filename))

        return redirect('/gallery')
    else:
        return "Only admin can upload images!"

# Dashboard (Show Students)
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, class, phone FROM students")
        students = cursor.fetchall()

        conn.close()

        return render_template('dashboard.html', students=students)
    else:
        return redirect('/login')

# Admission Page
@app.route('/admission')
def admission():
    return render_template('admission.html')

# Save Admission Form
@app.route('/submit_admission', methods=['POST'])
def submit_admission():
    name = request.form['name']
    dob = request.form['dob']
    student_class = request.form['class']
    father = request.form['father']
    phone = request.form['phone']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, dob, class, father, phone) VALUES (?, ?, ?, ?, ?)",
        (name, dob, student_class, father, phone)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect('/login')

@app.route('/delete_student/<int:id>')
def delete_student(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

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

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    student_id = request.form['student_id']
    date = request.form['date']
    status = request.form['status']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                   (student_id, date, status))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/add_result', methods=['POST'])
def add_result():
    student_id = request.form['student_id']
    subject = request.form['subject']
    marks = request.form['marks']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO results (student_id, subject, marks) VALUES (?, ?, ?)",
                   (student_id, subject, marks))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/fees')
def fees():
    return render_template('fees.html')

@app.route('/add_fees', methods=['POST'])
def add_fees():
    student_id = request.form['student_id']
    amount = request.form['amount']
    status = request.form['status']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO fees (student_id, amount, status) VALUES (?, ?, ?)",
                   (student_id, amount, status))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/gallery')
def gallery():
    images = os.listdir('static/uploads')
    return render_template('gallery.html', images=images)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect('/gallery')

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        student_class = request.form['class']
        phone = request.form['phone']

        cursor.execute("UPDATE students SET name=?, class=?, phone=? WHERE id=?",
                       (name, student_class, phone, id))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()
    conn.close()

    return render_template('edit_student.html', student=student)


@app.route('/student/<int:id>')
def student_profile(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()

    conn.close()
    return render_template('student_profile.html', student=student)


import pandas as pd

@app.route('/export')
def export():
    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()

    df.to_excel("students.xlsx", index=False)
    return "Excel file created!"


from PIL import Image, ImageDraw

@app.route('/id_card/<int:id>')
def id_card(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()
    conn.close()

    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)

    d.text((20, 50), f"Name: {student[1]}", fill=(0,0,0))
    d.text((20, 100), f"Class: {student[3]}", fill=(0,0,0))

    img.save("static/id_card.png")

    return '<img src="/static/id_card.png">'


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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


from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

@app.route('/send_email')
def send_email():
    msg = Message("School Notice",
                  sender="your_email@gmail.com",
                  recipients=["student_email@gmail.com"])
    msg.body = "New notice uploaded. Check school website."
    mail.send(msg)
    return "Email Sent!"

import openai

openai.api_key = "YOUR_API_KEY"

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.form['message']

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )

    reply = response['choices'][0]['message']['content']
    return reply
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# Home Page
@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT notice FROM notices")
    notices = cursor.fetchall()
    conn.close()

    return render_template('index.html', notices=notices)

# Login Page
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





@app.route('/upload', methods=['POST'])
def upload():
    if 'role' in session and session['role'] == 'admin':
        import os
        from werkzeug.utils import secure_filename

        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join('static/uploads', filename))

        return redirect('/gallery')
    else:
        return "Only admin can upload images!"

# Dashboard (Show Students)
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, class, phone FROM students")
        students = cursor.fetchall()

        conn.close()

        return render_template('dashboard.html', students=students)
    else:
        return redirect('/login')

# Admission Page
@app.route('/admission')
def admission():
    return render_template('admission.html')

# Save Admission Form
@app.route('/submit_admission', methods=['POST'])
def submit_admission():
    name = request.form['name']
    dob = request.form['dob']
    student_class = request.form['class']
    father = request.form['father']
    phone = request.form['phone']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, dob, class, father, phone) VALUES (?, ?, ?, ?, ?)",
        (name, dob, student_class, father, phone)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect('/login')

@app.route('/delete_student/<int:id>')
def delete_student(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

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

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    student_id = request.form['student_id']
    date = request.form['date']
    status = request.form['status']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                   (student_id, date, status))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/add_result', methods=['POST'])
def add_result():
    student_id = request.form['student_id']
    subject = request.form['subject']
    marks = request.form['marks']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO results (student_id, subject, marks) VALUES (?, ?, ?)",
                   (student_id, subject, marks))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/fees')
def fees():
    return render_template('fees.html')

@app.route('/add_fees', methods=['POST'])
def add_fees():
    student_id = request.form['student_id']
    amount = request.form['amount']
    status = request.form['status']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO fees (student_id, amount, status) VALUES (?, ?, ?)",
                   (student_id, amount, status))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/gallery')
def gallery():
    images = os.listdir('static/uploads')
    return render_template('gallery.html', images=images)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect('/gallery')

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        student_class = request.form['class']
        phone = request.form['phone']

        cursor.execute("UPDATE students SET name=?, class=?, phone=? WHERE id=?",
                       (name, student_class, phone, id))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()
    conn.close()

    return render_template('edit_student.html', student=student)


@app.route('/student/<int:id>')
def student_profile(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()

    conn.close()
    return render_template('student_profile.html', student=student)


import pandas as pd

@app.route('/export')
def export():
    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()

    df.to_excel("students.xlsx", index=False)
    return "Excel file created!"


from PIL import Image, ImageDraw

@app.route('/id_card/<int:id>')
def id_card(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()
    conn.close()

    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)

    d.text((20, 50), f"Name: {student[1]}", fill=(0,0,0))
    d.text((20, 100), f"Class: {student[3]}", fill=(0,0,0))

    img.save("static/id_card.png")

    return '<img src="/static/id_card.png">'


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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


from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

@app.route('/send_email')
def send_email():
    msg = Message("School Notice",
                  sender="your_email@gmail.com",
                  recipients=["student_email@gmail.com"])
    msg.body = "New notice uploaded. Check school website."
    mail.send(msg)
    return "Email Sent!"

import openai

openai.api_key = "YOUR_API_KEY"

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.form['message']

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )

    reply = response['choices'][0]['message']['content']
    return reply
if __name__ == '__main__':
    app.run(debug=True)

