from flask import Flask, render_template, request, redirect, session, send_from_directory, url_for
from models import db, User, Course
import os

app = Flask(__name__)
app.secret_key = 'secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['username'], password=request.form['password'], role='student')
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            session['user'] = user.username
            session['role'] = user.role
            if user.role == 'admin':
                return redirect('/admin')
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    courses = Course.query.all()
    return render_template('dashboard.html', courses=courses)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session.get('role') != 'admin':
        return redirect('/login')
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        course_type = "video" if filename.lower().endswith(('.mp4','.webm','.ogg')) else "file"

        course = Course(title=request.form['title'], filename=filename, type=course_type)
        db.session.add(course)
        db.session.commit()

    courses = Course.query.all()
    return render_template('admin.html', courses=courses)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/view/<filename>')
def view_video(filename):
    return render_template('video.html', filename=filename)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
