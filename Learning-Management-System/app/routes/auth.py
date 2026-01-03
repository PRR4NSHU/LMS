from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__)

# ---------------- REGISTER ROUTE ----------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Agar user pehle se login hai, toh dashboard bhej do
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = RegistrationForm()
    
    # Jab user form submit karega
    if form.validate_on_submit():
        
        # 👇 1. PASSWORD ENCRYPTION (Is line se password encrypt ho raha hai)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # 👇 2. CREATE USER (MongoDB Document)
        user = User(
            username=form.username.data, 
            email=form.email.data, 
            password=hashed_password,  # Yahan hum ENCRYPTED password save kar rahe hain
            role=form.role.data
        )
        
        # 👇 3. SAVE TO DATABASE
        user.save() 
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html', title='Register', form=form)

# ---------------- LOGIN ROUTE ----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        # Database mein email dhoondo
        user = User.objects(email=form.email.data).first()
        
        # 👇 PASSWORD CHECK (Bcrypt user ke password ko database ke encrypted password se match karega)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            
    return render_template('login.html', title='Login', form=form)

# ---------------- LOGOUT ROUTE ----------------
@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))