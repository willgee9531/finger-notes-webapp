from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import MultipleFileField, StringField, SubmitField, SelectField, PasswordField, BooleanField, ValidationError, URLField, EmailField
from wtforms.validators import DataRequired, Email, InputRequired, EqualTo, Length, URL
from wtforms.widgets import TextArea
from fingerNotes.models import User
from fingerNotes import bcrypt


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "Name"})
    email = EmailField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email address"})
    telephone = StringField('Telephone', validators=[InputRequired()], render_kw={"placeholder": "Telephone number"})
    message = StringField('Message', validators=[DataRequired()], widget=TextArea(), render_kw={"placeholder": "Enter your message here"})
    submit = SubmitField('Send Message')



class UserForm(FlaskForm):
    schoolName = StringField('School Name', validators=[DataRequired()], render_kw={"placeholder": "School Name"})
    email = EmailField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    country = SelectField('Country', validators=[DataRequired()], 
                          choices=[("", "Select Country"), ("Nigeria", "Nigeria"), ("Ghana", "Ghana"), ("United States of America", "United States of America"), ("United Kingdom", "United Kingdom"), ("Canada", "Canada")])
    password_hash = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    password_hash2 = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password_hash', message='Passwords must match!')],
                                   render_kw={"placeholder": "Confirm Password"})
    terms = BooleanField('I accept', default=False, validators=[DataRequired()])
    submit = SubmitField('Sign Up')



class SignInForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password_hash = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign In')



class AdminSignInForm(FlaskForm):
    password_hash = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign In')



class UserUploadForm(FlaskForm):
    session = StringField('Session', validators=[DataRequired()], render_kw={"placeholder": "Session e.g. 2023/2024"})
    term = SelectField('Term', validators=[DataRequired()], 
                        choices=[("", "Select term"), ("First term", "First term"), ("Second term", "Second term"), ("Third term", "Third term")])
    grade = SelectField('Grade', validators=[DataRequired()], 
                        choices=[("", "Select grade"), ("Grade 7", "Grade 7"), ("Grade 8", "Grade 8"), ("Grade 9", "Grade 9"), ("Grade 10", "Grade 10"), ("Grade 11", "Grade 11"), ("Grade 12", "Grade 12")])
    slides = MultipleFileField('Slides', validators=[DataRequired()], render_kw={"multiple": True})
    submit = SubmitField('Upload Slides')



class UserDownloadForm(FlaskForm):
    grade = SelectField('Grade', validators=[DataRequired()], 
                          choices=[("", "Select grade"), ("Grade 7", "Grade 7"), ("Grade 8", "Grade 8"), ("Grade 9", "Grade 9"), 
                                   ("Grade 10", "Grade 10"), ("Grade 11", "Grade 11"), ("Grade 12", "Grade 12")])
    submit = SubmitField('Download')



class ProfileForm(FlaskForm):
    school_name = StringField('School Name', validators=[InputRequired()])
    country = StringField('Country', validators=[InputRequired()])
    telephone_number = StringField('Telephone Number')
    school_address = StringField('School Address')
    email_address = EmailField('Email Address', validators=[InputRequired(), Email()])
    school_website = URLField('School Website/Portal')
    submit = SubmitField('Save changes')

    def validate_email_address(self, email_address):
        if email_address.data != current_user.email:
            user = User.query.filter_by(email=email_address.data).first()
            if user:
                raise ValidationError("User with the same email already exists!")



class ProfilePictureForm(FlaskForm):
    picture = FileField('Profile Picture', validators=[InputRequired(), FileAllowed(['jpg', 'png'], 'Images only! JPG or PNG')])
    submit = SubmitField('Upload Photo')


class SettingsForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[InputRequired()], render_kw={"placeholder": "Old Password"})
    new_password = PasswordField('New Password', validators=[InputRequired(), EqualTo('confirm_password', message='Passwords must match!')], render_kw={"placeholder": "New Password"})
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired()], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Save Changes')

    # Custom validator to check if old password is correct (replace with your own logic)
    # def validate_old_password(self, old_password):
    #     # Example: check if old password matches the one stored in the database
    #     if not bcrypt.check_password_hash(current_user.password, old_password.data):
    #         raise ValidationError('Old password is incorrect')
        

class DeleteAccountForm(FlaskForm):
    account_activation = BooleanField('I confirm my account deactivation', validators=[InputRequired()])
    submit = SubmitField('Deactivate Account')
    

# class AdminDeleteAccountForm(FlaskForm):
#     pass

class AddPartnersForm(FlaskForm):
    school_name = StringField('School Name', validators=[DataRequired()])
    website = URLField('School website/Portal', validators=[DataRequired(), URL()])
    facebook = StringField('Facebook page', validators=[DataRequired(), URL()])
    twitter = StringField('Twitter page', validators=[DataRequired(), URL()])
    instagram = StringField('Instagram page', validators=[DataRequired(), URL()])
    image = FileField('School Logo', validators=[DataRequired(), DataRequired()])
    submit = SubmitField('Add')



class AdminUploadForm(FlaskForm):
    school = SelectField('School', choices=[], validators=[DataRequired()])
    grade = SelectField('Grade', choices=[
        ('', 'Select grade'),
        ('Grade 7', 'Grade 7'),
        ('Grade 8', 'Grade 8'),
        ('Grade 9', 'Grade 9'),
        ('Grade 10', 'Grade 10'),
        ('Grade 11', 'Grade 11'),
        ('Grade 12', 'Grade 12')
    ], validators=[DataRequired()])
    file = FileField('File', validators=[DataRequired()])
    submit = SubmitField('Upload e-note')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.school.choices = [('', 'Select school')] + [(user.school_name, user.school_name) for user in User.query.all()]


class StatusForm(FlaskForm):
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Active', 'Active')])
    submit = SubmitField('Go')


    