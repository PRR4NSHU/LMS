from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required, current_user
from app.models import Course, Enrollment

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required # 🔒 Protects the route
def index():
    if current_user.role == 'instructor':
        # Fetch courses created by THIS instructor
        my_courses = Course.objects(instructor=current_user)
        return render_template('dashboard_instructor.html', courses=my_courses)
    
    elif current_user.role == 'admin':
        return "Admin Dashboard (Coming Soon)"
        
    else:
        # Student: Fetch enrollments
        enrollments = Enrollment.objects(student=current_user)
        return render_template('dashboard_student.html', enrollments=enrollments)
    
@dashboard_bp.route('/student')
def student_index():
    if current_user.role != 'student':
        return redirect(url_for('dashboard.index')) # Agar instructor hai toh use instructor dashboard pe bhejo
        
    # Yahan Enrollment model se data uthayein (Agar Enrollment model hai toh)
    # enrolled_courses = Enrollment.objects(student=current_user)
    return render_template('student_dashboard.html')