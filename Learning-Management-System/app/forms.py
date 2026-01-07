from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import IntegerField, StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
# 🟢 Fixed: Added 'NumberRange' to imports
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import User

# ---------------- REGISTER FORM ----------------
class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    role = SelectField('Register as:', choices=[('student', 'Student'), ('instructor', 'Instructor')])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered.')

# ---------------- LOGIN FORM ----------------
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# ---------------- COURSE FORM (With File Support) ----------------
class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    
    # 🟢 Fixed: NumberRange ab upar import ho gaya hai
    price = IntegerField('Price (in ₹)', default=0, validators=[NumberRange(min=0)])
    
    # Video upload (Optional taaki edit ke waqt hamesha upload na karni pade)
    video = FileField('Upload Intro Video', 
                      validators=[FileAllowed(['mp4', 'mov', 'avi', 'mkv'], 'Videos only!')])
    
    # Resource file (Optional)
    resource_file = FileField('Upload Course Material', 
                              validators=[FileAllowed(['pdf', 'docx', 'zip', 'jpg', 'png'], 'Documents/Images only!')])
    
    submit = SubmitField('Save Course')

# ---------------- LESSON FORM ----------------
class LessonForm(FlaskForm):
    title = StringField('Lesson Title', validators=[DataRequired()])
    content = TextAreaField('Description/Content', validators=[DataRequired()])
    
    # Lesson specific uploads
    video = FileField('Lesson Video', 
                      validators=[FileAllowed(['mp4', 'mov', 'avi', 'mkv'], 'Videos only!')])
    
    resource_file = FileField('Lesson PDF/Material', 
                              validators=[FileAllowed(['pdf', 'zip', 'docx', 'pptx'], 'Documents only!')])
    
    submit = SubmitField('Add Lesson')

# ---------------- PASSWORD RESET FORMS ----------------
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')