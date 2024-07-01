import io
import zipfile
import os
import secrets
from flask import abort, send_file
from PIL import Image
from fingerNotes.forms import *
from flask import render_template, url_for, flash, redirect, request
from fingerNotes.models import *
from fingerNotes import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename



ALLOWED_EXTENSIONS = {'ppsx', 'ppsm'}
ALLOWED_EXTENSION = {'exe'}

def allowed_file(file):
    return '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_exe(file):
    return '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION



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

    partners = Partner.query.all()
    return render_template('partners.html', partners=partners)



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
                flash("User with the same email already exists", "danger")
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
    uploads = UploadInfo.query.filter_by(user_id=current_user.id).order_by(UploadInfo.date.desc()).all()
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


@app.route("/download", methods=["GET", "POST"])
@login_required
def enote_download():
    form = UserDownloadForm(grade=0)
    if form.validate_on_submit():
        grade = form.grade.data
        upload = UploadEnote.query.filter_by(user_id=current_user.id, grade=grade).first()
        if upload:
            file_path = os.path.join(app.root_path, 'static/exe', current_user.school_name, upload.exe_file)
            return send_file(file_path, download_name=f"{current_user.school_name}_{grade}_enote.exe", as_attachment=True)
        else:
            flash("E-note not ready, be patient!", "info")
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
            current_ppp = os.path.join(app.root_path, 'static/img/profile_pics', current_user.image_file)
            # Delete the user's current profile picture file
            os.remove(current_ppp)
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


@app.route("/admin/dashboard", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    uploads = UploadInfo.query.order_by(UploadInfo.date.desc()).all()
    forms = {upload.id: StatusForm(status=upload.status) for upload in uploads}
    return render_template("admin_dashboard.html", uploads=uploads, form=forms)


@app.route('/update_status/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    post = UploadInfo.query.get(id)
    form = StatusForm(status=post.status)
    if form.validate_on_submit():
        status = form.status.data
        post = UploadInfo.query.get(id)
        # Add logic to update the status in the database
        try:
            if post:
                post.status = status
                db.session.commit()
                flash(f"Status updated to {status} successfully!", "success")
            else:
                raise ValueError("User not found")
        except Exception as e:
            flash(f"An error occurred while updating status: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_dashboard'))



@app.route('/admin/download/<school_name>/<int:files_id>')
@login_required
def download(school_name, files_id):
    ppsx_files = UploadInfo.query.get_or_404(files_id)
    memory_file = io.BytesIO()

    with zipfile.ZipFile(memory_file, 'w') as zf:
        for file in ppsx_files.files:
            file_path = os.path.join(app.root_path, 'static/slides', school_name, file.ppsx_file)
            if os.path.exists(file_path):
                zf.write(file_path, os.path.basename(file_path))
            else:
                abort(404, description=f"File {file.ppsx_file} not found")

    memory_file.seek(0)
        
    return send_file(memory_file, download_name=f"{school_name}_{ppsx_files.grade}_{ppsx_files.term}_slides.zip", as_attachment=True)        


@app.route("/admin/upload", methods=["GET", "POST"])
@login_required
def admin_upload():
    form = AdminUploadForm(school=0, grade=0)
    uploads = UploadEnote.query.all()
    if form.validate_on_submit():
        school = form.school.data
        grade = form.grade.data
        file = form.file.data

        user = User.query.filter_by(school_name=school).first()

        if user:
            if not allowed_exe(file):
                        flash("Extension not supported. Upload only Application (.exe) files", "warning")
                        return redirect(url_for("admin_upload"))
            # Delete previous .exe file for the same grade if exists
            previous_upload = UploadEnote.query.filter_by(user_id=user.id, grade=grade).first()
            if previous_upload:
                # Assuming the file path is stored in exe_file attribute
                file_path = os.path.join(app.root_path, 'static/exe', user.school_name, previous_upload.exe_file)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    db.session.delete(previous_upload)
                    db.session.commit()
            
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(file.filename)
            exe_fn = random_hex + f_ext
            directory = os.path.join(app.root_path, 'static/exe', user.school_name)
            
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            exe_path = os.path.join(directory, exe_fn)
            file.save(exe_path)

            new_upload = UploadEnote(grade=grade, exe_file=exe_fn, user_id=user.id)
            db.session.add(new_upload)
            db.session.commit()
            
            flash('E-note uploaded successfully!', 'success')
            return redirect(url_for('admin_upload'))
    return render_template("admin_upload.html", form=form, uploads=uploads)



@app.route("/admin/upload/delete/<int:id>")
def delete_exe(id):
    upload_to_delete = UploadEnote.query.get_or_404(id)
    try:
        directory = os.path.join(app.root_path, 'static/exe', upload_to_delete.user.school_name, upload_to_delete.exe_file)
        if os.path.exists(directory):
            os.remove(directory)
            db.session.delete(upload_to_delete)
            db.session.commit()
            flash("Upload deleted successfully", "success")
            return redirect(url_for('admin_upload'))
    except:
        flash("There was a problem deleting the upload", "info")
        return redirect(url_for('admin_upload'))


@app.route("/admin/partners", methods=["GET", "POST"])
@login_required
def admin_partners():
    form = AddPartnersForm()
    page = request.args.get('page', 1, type=int)
    partners = Partner.query.order_by(Partner.date.desc()).paginate(page=page, per_page=2)
    if form.validate_on_submit():
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form.image.data.filename)
        image_file = random_hex + f_ext
        image_path = os.path.join(app.root_path, 'static/img/LPage_img/partners', image_file)
        if not os.path.exists(image_path):
            os.makedirs(image_path)
        form.image.data.save(image_path)

        partner = Partner(
            school_name=form.school_name.data,
            website=form.website.data,
            facebook=form.facebook.data,
            twitter=form.twitter.data,
            instagram=form.instagram.data,
            image_file=image_file
        )
        db.session.add(partner)
        db.session.commit()
        flash('New partner added!', 'success')
        return redirect(url_for('admin_partners'))
    
    return render_template('admin_partners.html', form=form, partners=partners)


@app.route("/admin/settings", methods=["GET", "POST"])
@login_required
def admin_settings():
    users = User.query.all()
    if request.method == "POST":
        school = request.form['delete-account']
        user = User.query.filter_by(school_name=school).first()
        if user:
            current_ppp = os.path.join(app.root_path, 'static/img/profile_pics', user.image_file)
            # Delete the user's current profile picture file
            os.remove(current_ppp)
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
