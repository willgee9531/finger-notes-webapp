from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, SelectField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, InputRequired, EqualTo, Length
from wtforms.widgets import TextArea

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "Name"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email address"})
    telephone = StringField('Telephone', validators=[InputRequired()], render_kw={"placeholder": "Telephone number"})
    message = StringField('Message', validators=[DataRequired()], widget=TextArea(), render_kw={"placeholder": "Enter your message here"})
    submit = SubmitField('Send Message')

class UserForm(FlaskForm):
    schoolName = StringField('School Name', validators=[DataRequired()], render_kw={"placeholder": "School Name"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    country = SelectField('Country', validators=[DataRequired()], choices=[
        ("", "Select Country"), ("Nigeria", "Nigeria"), ("Ghana", "Ghana"),
        ("United States of America", "United States of America"), ("United Kingdom", "United Kingdom"), ("Canada", "Canada")
    ])
    password_hash = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password_hash', message='Passwords must match!')], render_kw={"placeholder": "Confirm Password"})
    terms = BooleanField('Accept terms and conditions', default=False)
    submit = SubmitField('Sign Up')

class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password_hash = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign In')
