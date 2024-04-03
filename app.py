import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask import Flask, render_template, url_for, flash, redirect, request
from forms import ContactForm, UserForm, SignInForm
from models import db, Users

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fingernotes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with your Flask app
db.init_app(app)


with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"An error occurred while creating database tables: {e}")


@app.route("/", methods=["GET", "POST"])
def homepage():
    form = ContactForm()
    if form.validate_on_submit():
        # Process form data
        name = form.name.data
        telephone = form.telephone.data
        email = form.email.data
        message = form.message.data
        return render_template('landingPage.html', form=form, submitted=True)
        
    return render_template('landingPage.html', form=form, submitted=False)

@app.route("/signin", methods=["GET", "POST"])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        return render_template("dashboard.html")
    return render_template("login.html", form=form)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = UserForm(country=0)
    if form.validate_on_submit():
        
        # Process form data
        school = form.schoolName.data
        email = form.email.data
        country = form.country.data
        password = form.password_hash.data

        try:
            # Check if user with the same email already exists
            existing_user = Users.query.filter_by(email=email).first()
            if existing_user:
                flash("User with the same email already exists", "danger")
            else:
                # Create new user
                new_user = Users(
                    school_name=school,
                    email=email,
                    country=country
                )
                db.session.add(new_user)
                db.session.commit()
                flash("Account created successfully! Sign in now.", "success")
                return redirect(url_for("signin"))  # Redirect to sign-in page after successful sign-up
        except Exception as e:
            # Handle any exceptions that occur during database operations
            flash(f"An error occurred: {str(e)}", "danger")

    # If form is not submitted or validation fails, render the sign-up form template
    users = Users.query.all()  # Fetch all users for demonstration (remove in production)
    return render_template("register.html", form=form, users=users)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
    
@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/download")
def download():
    return render_template("download.html")

if __name__ == "__main__":
    app.run(debug=True)