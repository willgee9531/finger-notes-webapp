import os
import secrets
from flask import current_app
from PIL import Image
from fingerNotes.forms import ContactForm, UserDownloadForm, UserForm, SignInForm, AdminSignInForm, ProfileForm, SettingsForm, DeleteAccountForm, ProfilePictureForm, UserUploadForm
from flask import render_template, url_for, flash, redirect, request
from fingerNotes.models import User, Admin, UploadInfo, File
from fingerNotes import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

ALLOWED_EXTENSIONS = {'ppsx', 'ppsm'}

def allowed_file(file):
    return '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    
    current_profile_picture_path = current_user.image_file
    if current_profile_picture_path != "default.png":
        current_ppp = os.path.join(app.root_path, 'static/img/profile_pics', current_profile_picture_path)
        # Delete the user's current profile picture file if it exists
        if os.path.exists(current_ppp):
            os.remove(current_ppp)

    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img/profile_pics', picture_fn)
    output_size = (200, 200)
    i = Image.open(form_picture)
    thumbnail_width, thumbnail_height = i.size
    if thumbnail_width > 200 and thumbnail_height > 200:
        i.thumbnail(output_size)
    if i.mode == 'RGBA':
        i = i.convert('RGB')
    i.save(picture_path)
    return picture_fn



def save_ppsx(ppsx, school_name):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(ppsx.filename)
    ppsx_fn = random_hex + f_ext
    directory = os.path.join(app.root_path, 'static/slides', school_name)
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    ppsx_path = os.path.join(directory, ppsx_fn)
    ppsx.save(ppsx_path)
    return ppsx_fn

def delete_upload(ppsx, school_name):
    directory = os.path.join(app.root_path, 'static/slides', school_name, ppsx)
    if os.path.exists(directory):
            os.remove(directory)



@app.route("/", methods=["GET", "POST"])
def homepage():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Process form data
            name = form.name.data
            telephone = form.telephone.data
            email = form.email.data
            message = form.message.data
            flash("Your message has been submitted successfully! Check your inbox.", "success")
            return redirect(url_for('homepage'))
        
    return render_template('landingPage.html', form=form)


@app.route("/partners")
def partners():
    return render_template("partners.html")



@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = UserForm(country=0)
    if form.validate_on_submit():
        # Process form data
        hashed_password = bcrypt.generate_password_hash(form.password_hash.data).decode('utf-8')
        school = form.schoolName.data
        email = form.email.data
        country = form.country.data
        try:
            # Check if user with the same email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("User with the same email already exists", "warning")
            else:
                # Create new user
                new_user = User(
                    school_name=school,
                    email=email,
                    country=country,
                    password=hashed_password
                )
                db.session.add(new_user)
                db.session.commit()
                flash("Account created successfully! Sign in now.", "success")
                return redirect(url_for("signin"))  # Redirect to sign-in page after successful sign-up
        except Exception as e:
            # Handle any exceptions that occur during database operations
            flash(f"An error occurred: {str(e)}", "danger")
    return render_template("register.html", form=form)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password_hash.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f"Welcome back {current_user.school_name}!", "success")
            return redirect(next_page) if next_page else redirect(url_for('loading'))
        else:
            flash("Invalid email or password!", "danger")
    return render_template("login.html", form=form)


@app.route("/loading")
def loading():
    return render_template("loading.html")

@app.route("/signout")
def signout():
    logout_user()
    return redirect(url_for('homepage'))


@app.route("/dashboard")
@login_required
def dashboard():
    uploads = UploadInfo.query.all()
    return render_template("dashboard.html", uploads=uploads)    

@app.route("/upload/delete/<int:id>")
def delete_uploads(id):
    upload_to_delete = UploadInfo.query.get_or_404(id)
    try:
        for slide in upload_to_delete.files:
            delete_upload(slide.ppsx_file, current_user.school_name)
        db.session.delete(upload_to_delete)
        db.session.commit()
        flash("Upload deleted successfully", "success")
        return redirect(url_for('dashboard'))
    except:
        flash("There was a problem deleting the upload", "info")
        return redirect(url_for('dashboard'))



@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = UserUploadForm(term=0, grade=0)
    if form.validate_on_submit():
        session = form.session.data
        term = form.term.data
        grade = form.grade.data
        files = form.slides.data
        try:
            if files:
                for file in files:
                    if not allowed_file(file):
                        flash("Extension not supported. Upload only .ppsx or .ppsm files", "warning")
                        return redirect(url_for("upload"))
                    
                upload = UploadInfo(
                    session=session,
                    term=term,
                    grade=grade,
                    user_id=current_user.id
                )
                
                db.session.add(upload)
                db.session.flush()  # Flush to get the `upload.id` without committing
                file_objects = []
                for file in files:
                    ppsx_fn = save_ppsx(file, current_user.school_name)
                    new_file = File(ppsx_file=ppsx_fn, upload_id=upload.id)
                    file_objects.append(new_file)
                db.session.add_all(file_objects)
                db.session.commit()
                flash("Slides uploaded successfully!", "success")
                return redirect(url_for("upload"))
            else:
                flash("No slide(s) selected!", "warning")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
    else:
        print('Form validation failed')
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field - {error}", "danger")
    return render_template("upload.html", form=form)


# @app.route("/upload/delete")
# @login_required
# def delete_upload():
#     return render_template("upload.html")


@app.route("/download")
@login_required
def download():
    form = UserDownloadForm(grade=0)
    return render_template("download.html", form=form)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile_form = ProfileForm()
    pics_form = ProfilePictureForm()
    
    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    if request.method == 'POST':
        if profile_form.validate_on_submit():
            # Process change password form submission
            current_user.school_name = profile_form.school_name.data
            current_user.email = profile_form.email_address.data
            current_user.country = profile_form.country.data
            current_user.telephone_no = profile_form.telephone_number.data
            current_user.school_address = profile_form.school_address.data
            current_user.school_website = profile_form.school_website.data
            db.session.commit()
            flash("Account Updated Successfully!", "success")
            return redirect(url_for('profile'))
        elif pics_form.validate_on_submit():
            if pics_form.picture.data:
                picture_file = save_picture(pics_form.picture.data)
                current_user.image_file = picture_file
                db.session.commit()
                flash("Profile picture Updated Successfully!", "success")
                return redirect(url_for('profile'))
    
    profile_form.school_name.data = current_user.school_name
    profile_form.email_address.data = current_user.email
    profile_form.country.data = current_user.country
    profile_form.telephone_number.data = current_user.telephone_no
    profile_form.school_address.data = current_user.school_address
    profile_form.school_website.data = current_user.school_website
    return render_template("profile.html", form=profile_form, pics_form=pics_form, image_file=image_file)


@app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    change_form = SettingsForm()
    delete_form = DeleteAccountForm()
    if request.method == 'POST':
        if change_form.validate_on_submit():
            # Process change password form submission
            if not bcrypt.check_password_hash(current_user.password, change_form.old_password.data):
                flash("Old password is incorrect", "warning")
            elif bcrypt.check_password_hash(current_user.password, change_form.new_password.data):
                flash("New password must be different from old password", "warning")
            else:
                hashed_password = bcrypt.generate_password_hash(change_form.new_password.data).decode('utf-8')
                current_user.password = hashed_password
                db.session.commit()
                flash("Password Changed Successfully!", "success")
            return redirect(url_for('settings'))
        elif delete_form.validate_on_submit():
            # Process delete account form submission
            user = User.query.filter_by(id=current_user.id).first()
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('signup'))
    return render_template("settings.html", cform=change_form, dform=delete_form)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    form = AdminSignInForm()
    if form.validate_on_submit():
        password = form.password_hash.data
        admin1 = Admin.query.filter_by(password=password).first()
        if admin1:
            login_user(admin1)
            flash("Welcome Back Admin!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid password", "danger")
    return render_template("login.html", form=form, admin=True)


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    return render_template("admin_dashboard.html")


@app.route("/admin/upload")
@login_required
def admin_upload():
    return render_template("admin_upload.html")


@app.route("/admin/partners")
@login_required
def admin_partners():
    return render_template("admin_partners.html")


@app.route("/admin/settings", methods=["GET", "POST"])
@login_required
def admin_settings():
    users = User.query.all()
    if request.method == "POST":
        school = request.form['delete-account']
        user = User.query.filter_by(school_name=school).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            flash("School has been deleted!", "success")
            return redirect(url_for('admin_settings'))
        else:
            flash(f"Select a school to delete", "info")
        
    return render_template("admin_settings.html", users=users)

@app.route("/admin/signout")
def admin_signout():
    logout_user()
    return redirect(url_for('homepage'))
