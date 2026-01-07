import os
from datetime import datetime
from flask import Blueprint, render_template, url_for, flash, redirect, abort, request, current_app, jsonify
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.models import Course, Lesson, Enrollment, UserProgress
from app.forms import CourseForm, LessonForm

# Blueprint definition
course_bp = Blueprint('courses', __name__)

# --- Helper Function to save files ---
def save_uploaded_file(file_data, folder_name):
    if not file_data:
        return None 
    
    filename = secure_filename(file_data.filename)
    # Unique timestamp needed specifically for updates so browser doesn't cache old file
    filename = f"{int(datetime.now().timestamp())}_{filename}"
    upload_path = os.path.join(current_app.root_path, 'static/uploads', folder_name)
    
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    file_data.save(os.path.join(upload_path, filename))
    return filename


# ==========================================
# 1. PUBLIC / STUDENT ROUTES (Explore, Enroll, Payment)
# ==========================================

@course_bp.route('/explore')
@login_required
def explore():
    # 1. Fetch all active public courses
    courses = Course.objects(is_active=True, is_hidden=False)
    
    # 2. Find which courses student already bought
    my_enrollments = Enrollment.objects(student=current_user)
    enrolled_ids = [e.course.id for e in my_enrollments]
    
    return render_template('explore_courses.html', courses=courses, enrolled_ids=enrolled_ids)


@course_bp.route('/course/<course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    if current_user.role != 'student':
        flash('Only students can enroll.', 'danger')
        return redirect(url_for('main.home'))
    
    course = Course.objects.get_or_404(id=course_id)
    
    # 1. Check if already enrolled
    existing = Enrollment.objects(student=current_user, course=course).first()
    if existing:
        return redirect(url_for('courses.view_course', course_id=course.id))
    
    # 2. Check Price Logic (Redirect to Payment if Paid)
    if course.price > 0:
        return redirect(url_for('courses.payment_page', course_id=course.id))
    
    # 3. If Free, Direct Enroll
    Enrollment(student=current_user, course=course).save()
    flash(f'Enrolled in {course.title}!', 'success')
        
    return redirect(url_for('dashboard.student_index'))


@course_bp.route('/payment/<course_id>', methods=['GET'])
@login_required
def payment_page(course_id):
    course = Course.objects.get_or_404(id=course_id)
    return render_template('payment.html', course=course)


@course_bp.route('/payment/<course_id>/process', methods=['POST'])
@login_required
def process_payment(course_id):
    course = Course.objects.get_or_404(id=course_id)
    
    # Mock Payment Logic (Here you would integrate Stripe/Razorpay)
    fake_txn_id = f"PAY_{int(datetime.now().timestamp())}_{current_user.id}"
    
    # Save Enrollment
    Enrollment(
        student=current_user, 
        course=course,
        amount_paid=course.price,
        transaction_id=fake_txn_id,
        payment_status='completed'
    ).save()
    
    flash(f'Payment Successful! You are enrolled in {course.title}.', 'success')
    return redirect(url_for('courses.view_course', course_id=course.id))


@course_bp.route('/<course_id>', methods=['GET', 'POST'])
@login_required
def view_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    lessons = Lesson.objects(course=course).order_by('date_created')
    if not course.is_active:
        abort(404)
    user_progress = None
    enrollment = None
    
    if current_user.role == 'student':
        enrollment = Enrollment.objects(student=current_user, course=course).first()
        if not enrollment:
            flash('Please enroll to access this course.', 'warning')
            return redirect(url_for('courses.explore'))
            
        user_progress = UserProgress.objects(student=current_user, course=course).first()

    # Instructor Add Lesson Form Handling
    form = LessonForm()
    if form.validate_on_submit() and current_user == course.instructor:
        v_file = save_uploaded_file(form.video.data, 'videos')
        r_file = save_uploaded_file(form.resource_file.data, 'resources')
        Lesson(
            title=form.title.data,
            content=form.content.data,
            course=course,
            video_filename=v_file,
            resource_filename=r_file
        ).save()
        flash('Lesson added successfully!', 'success')
        return redirect(url_for('courses.view_course', course_id=course.id))

    return render_template('view_course.html', course=course, lessons=lessons, form=form, user_progress=user_progress, enrollment=enrollment)


# ==========================================
# 2. INSTRUCTOR DASHBOARD & MANAGEMENT
# ==========================================

@course_bp.route('/dashboard/instructor')
@login_required
def instructor_index():
    if current_user.role != 'instructor':
        abort(403)
    courses = Course.objects(instructor=current_user, is_active=True).order_by('date_created')
    return render_template('dashboard_instructor.html', courses=courses)


@course_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'instructor':
        abort(403) 
    form = CourseForm()
    if form.validate_on_submit():
        v_file = save_uploaded_file(form.video.data, 'videos')
        r_file = save_uploaded_file(form.resource_file.data, 'resources')
        try:
            Course(
                title=form.title.data,
                description=form.description.data,
                price=form.price.data,  # 🟢 Save Price
                instructor=current_user,
                video_filename=v_file,
                resource_filename=r_file
            ).save()
            flash('Course Created Successfully!', 'success')
            return redirect(url_for('courses.instructor_index'))
        except Exception as e:
            flash(f'Database Error: {str(e)}', 'danger')
    return render_template('create_course.html', form=form, legend='Create Course')


@course_bp.route('/course/<course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    if course.instructor != current_user:
        abort(403)
    
    form = CourseForm()
    
    if form.validate_on_submit():
        # 1. Update Course Details
        course.update(
            set__title=form.title.data,
            set__description=form.description.data,
            set__price=form.price.data  # 🟢 Update Price
        )

        # 2. Add New Lesson via Edit Page (Optional)
        if form.video.data or form.resource_file.data:
            v_file = save_uploaded_file(form.video.data, 'videos')
            r_file = save_uploaded_file(form.resource_file.data, 'resources')

            Lesson(
                title=f"New Lesson: {datetime.now().strftime('%d %b')}",
                content="Added via edit page.",
                course=course,
                video_filename=v_file,
                resource_filename=r_file
            ).save()
            flash('Course updated & new content added!', 'success')
        else:
            flash('Course details updated!', 'info')

        return redirect(url_for('courses.instructor_index'))

    elif request.method == 'GET':
        form.title.data = course.title
        form.description.data = course.description
        form.price.data = course.price  # 🟢 Pre-fill Price
        
    return render_template('create_course.html', form=form, legend='Edit Course', course=course)


@course_bp.route('/lesson/<lesson_id>/update', methods=['POST'])
@login_required
def update_lesson_details(lesson_id):
    lesson = Lesson.objects.get_or_404(id=lesson_id)
    if lesson.course.instructor != current_user:
        abort(403)

    # Update Title
    new_title = request.form.get('title')
    if new_title:
        lesson.title = new_title

    # Replace Video
    if 'video' in request.files:
        file = request.files['video']
        if file.filename != '':
            if lesson.video_filename:
                old_path = os.path.join(current_app.root_path, 'static/uploads/videos', lesson.video_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            lesson.video_filename = save_uploaded_file(file, 'videos')

    # Replace Resource
    if 'resource' in request.files:
        file = request.files['resource']
        if file.filename != '':
            if lesson.resource_filename:
                old_path = os.path.join(current_app.root_path, 'static/uploads/resources', lesson.resource_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            lesson.resource_filename = save_uploaded_file(file, 'resources')

    lesson.save()
    flash('Lesson updated successfully!', 'success')
    return redirect(url_for('courses.edit_course', course_id=lesson.course.id))


# ==========================================
# 3. ACTIONS (Complete, Hide, Delete, Certificate)
# ==========================================

@course_bp.route('/lesson/<lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    lesson = Lesson.objects.get_or_404(id=lesson_id)
    progress = UserProgress.objects(student=current_user, course=lesson.course).first()
    if not progress:
        progress = UserProgress(student=current_user, course=lesson.course, completed_lessons=[]).save()
    if lesson not in progress.completed_lessons:
        progress.completed_lessons.append(lesson)
        progress.save()

    total = Lesson.objects(course=lesson.course).count()
    percent = int((len(progress.completed_lessons) / total) * 100) if total > 0 else 0
    Enrollment.objects(student=current_user, course=lesson.course).update(set__progress=percent)
    return jsonify({"status": "success", "percent": percent})


@course_bp.route('/course/<course_id>/hide', methods=['POST'])
@login_required
def hide_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    if course.instructor == current_user:
        course.update(set__is_hidden=not course.is_hidden)
        flash('Course Visibility Updated', 'info')
    return redirect(url_for('courses.instructor_index'))


@course_bp.route('/course/<course_id>/delete', methods=['POST'])
@login_required
def soft_delete_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    if course.instructor == current_user:
        course.update(set__is_active=False)
        flash('Course Archived Successfully', 'warning')
    return redirect(url_for('courses.instructor_index'))


@course_bp.route('/course/<course_id>/toggle-certificate', methods=['POST'])
@login_required
def toggle_certificate(course_id):
    course = Course.objects.get_or_404(id=course_id)
    if course.instructor != current_user:
        abort(403)
        
    course.update(set__certificate_enabled=not course.certificate_enabled)
    status = "Enabled" if not course.certificate_enabled else "Disabled"
    flash(f'Certificate option is now {status}.', 'success')
    return redirect(url_for('courses.instructor_index'))


@course_bp.route('/course/<course_id>/certificate')
@login_required
def get_certificate(course_id):
    course = Course.objects.get_or_404(id=course_id)
    enrollment = Enrollment.objects(student=current_user, course=course).first()

    if not enrollment:
        flash("You are not enrolled in this course.", "danger")
        return redirect(url_for('main.home'))

    if not course.certificate_enabled:
        flash("Certificate is not enabled for this course.", "warning")
        return redirect(url_for('courses.view_course', course_id=course_id))

    if enrollment.progress < 100:
        flash("Please complete 100% of the course to get the certificate.", "warning")
        return redirect(url_for('courses.view_course', course_id=course_id))

    return render_template('certificate.html', 
                           student=current_user, 
                           course=course, 
                           date=datetime.now().strftime("%d %B, %Y"))