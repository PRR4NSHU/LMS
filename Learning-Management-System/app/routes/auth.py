from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from app import bcrypt, mail
from app.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm # Forms import kiye
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

auth_bp = Blueprint('auth', __name__)

# ---------------- REGISTER ROUTE ----------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data, 
            email=form.email.data, 
            password=hashed_password,
            role=form.role.data
        )
        user.save()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

# ---------------- LOGIN ROUTE ----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

# ---------------- FORGOT PASSWORD LOGIC ----------------

def send_reset_email(user):
    token = user.get_reset_token()
    # 👇 .env se MAIL_USERNAME ko sender banane ke liye current_app ka use kiya
    msg = Message('Password Reset Request - LearnHub',
                  sender=current_app.config['MAIL_USERNAME'], 
                  recipients=[user.email])
    
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email.
'''
    mail.send(msg)

@auth_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user:
            send_reset_email(user)
        # Security ke liye hum hamesha flash dikhate hain, chahe email mile ya na mile
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.update(set__password=hashed_password)
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

# ---------------- LOGOUT ROUTE ----------------
@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))