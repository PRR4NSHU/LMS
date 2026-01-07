import os
import random
import string
from datetime import datetime
from flask import Blueprint, redirect, render_template, url_for, request, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import Course, Enrollment, User 

dashboard_bp = Blueprint('dashboard', __name__)

# --- Helper Functions ---

def save_signature_file(file_data):
    if not file_data:
        return None
    
    filename = secure_filename(file_data.filename)
    filename = f"sig_{current_user.id}_{int(datetime.now().timestamp())}_{filename}"
    upload_path = os.path.join(current_app.root_path, 'static/uploads/signatures')
    
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
        
    file_data.save(os.path.join(upload_path, filename))
    return filename

# 🟢 NEW: Profile Picture Saver
def save_profile_pic(file_data):
    if not file_data:
        return None
    
    filename = secure_filename(file_data.filename)
    filename = f"pfp_{current_user.id}_{int(datetime.now().timestamp())}_{filename}"
    upload_path = os.path.join(current_app.root_path, 'static/uploads/profile_pics')
    
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
        
    file_data.save(os.path.join(upload_path, filename))
    return filename

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


# --- Routes ---

@dashboard_bp.route('/')
@login_required 
def index():
    if current_user.role == 'instructor':
        return redirect(url_for('courses.instructor_index'))
    elif current_user.role == 'student':
        return redirect(url_for('dashboard.student_index'))
    elif current_user.role == 'admin':
        return "Admin Dashboard (Coming Soon)"
    return "Unknown Role"


@dashboard_bp.route('/instructor/profile', methods=['GET', 'POST'])
@login_required
def instructor_profile():
    if current_user.role != 'instructor':
        abort(403)
        
    if request.method == 'POST':
        
        # 🟢 CASE 1: FULL Profile Update (Photo, Bio, Socials, Signature)
        if 'update_profile' in request.form:
            try:
                # 1. Basic Text Fields
                current_user.update(
                    set__username=request.form.get('username'),
                    set__qualification=request.form.get('qualification'),
                    set__institution=request.form.get('institution'),
                    set__linkedin_url=request.form.get('linkedin'),
                    set__twitter_url=request.form.get('twitter'),
                    set__website_url=request.form.get('website')
                )
                
                # 2. Profile Picture Upload
                if 'profile_pic' in request.files:
                    file = request.files['profile_pic']
                    if file.filename != '':
                        new_pfp = save_profile_pic(file)
                        current_user.update(set__profile_pic=new_pfp)

                # 3. Signature Upload
                if 'signature' in request.files:
                    file = request.files['signature']
                    if file.filename != '':
                        new_sig = save_signature_file(file)
                        current_user.update(set__signature_filename=new_sig)
                
                flash('Profile updated successfully!', 'success')
            
            except Exception as e:
                flash(f'Error updating profile: {str(e)}', 'danger')
            
            return redirect(url_for('dashboard.instructor_profile'))

        # 🟢 CASE 2: Email Change Request
        elif 'request_email_change' in request.form:
            new_email = request.form.get('email')
            
            if not new_email or new_email == current_user.email:
                flash('Please enter a different email address.', 'warning')
                return redirect(url_for('dashboard.instructor_profile'))
            
            if User.objects(email=new_email).first():
                flash('This email is already registered.', 'danger')
                return redirect(url_for('dashboard.instructor_profile'))
            
            otp = generate_otp()
            current_user.update(
                set__email_verification_code=otp,
                set__pending_new_email=new_email
            )
            
            print(f"DEBUG: OTP for {current_user.username} is: {otp}")
            
            flash('Verification code sent! Check your console/email.', 'info')
            return redirect(url_for('dashboard.verify_email_change'))

    return render_template('instructor_profile.html')


@dashboard_bp.route('/instructor/verify-email', methods=['GET', 'POST'])
@login_required
def verify_email_change():
    if not current_user.pending_new_email:
        flash('No pending email change request found.', 'warning')
        return redirect(url_for('dashboard.instructor_profile'))
        
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        
        if entered_otp == current_user.email_verification_code:
            current_user.update(
                set__email=current_user.pending_new_email,
                unset__email_verification_code=1,
                unset__pending_new_email=1
            )
            flash('Success! Your email address has been updated.', 'success')
            return redirect(url_for('dashboard.instructor_profile'))
        else:
            flash('Invalid Verification Code.', 'danger')
            
    return render_template('verify_email.html')


@dashboard_bp.route('/student')
@login_required
def student_index():
    if current_user.role != 'student':
        return redirect(url_for('dashboard.index'))
    all_enrollments = Enrollment.objects(student=current_user)

    enrolled = Enrollment.objects(student=current_user)
    enrolled_ids = [e.course.id for e in enrolled]
    active_enrollments = [e for e in all_enrollments if e.course.is_active]
    available = Course.objects(id__nin=enrolled_ids, is_active=True, is_hidden=False)
    
    return render_template('student_dashboard.html', 
                           enrolled_courses=active_enrollments, 
                           available_courses=available)