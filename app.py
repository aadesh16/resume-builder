from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# -----------------------
# CONFIGURATION
# -----------------------

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# -----------------------
# DATABASE MODELS
# -----------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(200))


class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    skills = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    template = db.Column(db.String(50))
    photo = db.Column(db.String(200))


# -----------------------
# ROUTES
# -----------------------

@app.route('/')
def index():
    return render_template("index.html")


# -------- AUTH ---------

@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/register', methods=['POST'])
def register():

    username = request.form['username']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])

    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return redirect('/login')


@app.route('/login_user', methods=['POST'])
def login_user():

    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        return redirect('/dashboard')
    else:
        return "Invalid Login"


# -------- DASHBOARD ---------

@app.route('/dashboard')
def dashboard():
    resumes = Resume.query.all()
    return render_template("dashboard.html", resumes=resumes)


# -------- CREATE RESUME ---------

@app.route('/create')
def create_resume():
    return render_template("create_resume.html")


@app.route('/save_resume', methods=['POST'])
def save_resume():

    photo = request.files['photo']
    filename = ""

    if photo:
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    resume = Resume(
        name=request.form['name'],
        email=request.form['email'],
        phone=request.form['phone'],
        skills=request.form['skills'],
        education=request.form['education'],
        experience=request.form['experience'],
        template=request.form['template'],
        photo=filename
    )

    db.session.add(resume)
    db.session.commit()

    return redirect('/dashboard')


# -------- VIEW RESUME ---------

@app.route('/view/<int:id>')
def view_resume(id):

    resume = Resume.query.get(id)

    if resume.template == "template1":
        return render_template("template1.html", data=resume)
    else:
        return render_template("template2.html", data=resume)


# -------- EDIT RESUME ---------

@app.route('/edit/<int:id>')
def edit_resume(id):

    resume = Resume.query.get(id)
    return render_template("edit_resume.html", resume=resume)


@app.route('/update/<int:id>', methods=['POST'])
def update_resume(id):

    resume = Resume.query.get(id)

    resume.name = request.form['name']
    resume.email = request.form['email']
    resume.phone = request.form['phone']
    resume.skills = request.form['skills']
    resume.education = request.form['education']
    resume.experience = request.form['experience']
    resume.template = request.form['template']

    db.session.commit()

    return redirect('/dashboard')


# -------- DELETE RESUME ---------

@app.route('/delete/<int:id>')
def delete_resume(id):

    resume = Resume.query.get(id)

    db.session.delete(resume)
    db.session.commit()

    return redirect('/dashboard')


# -----------------------
# RUN APP (IMPORTANT FOR DEPLOYMENT)
# -----------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
    