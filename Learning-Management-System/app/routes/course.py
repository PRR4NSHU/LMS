import os
from flask import Blueprint, render_template, url_for, flash, redirect, abort, request, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.models import Course, Lesson, Enrollment
from app.forms import CourseForm, LessonForm

course_bp = Blueprint('courses', __name__)

# Helper function to save files and delete old ones
def save_uploaded_file(file_data, folder_name, old_file=None):
    if not file_data:
        return old_file 
    
    filename = secure_filename(file_data.filename)
    upload_path = os.path.join(current_app.root_path, 'static/uploads', folder_name)
    
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    # Old file cleanup
    if old_file:
        old_path = os.path.join(upload_path, old_file)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass 

    file_data.save(os.path.join(upload_path, filename))
    return filename

# -----------------------
# 1. CREATE COURSE
# -----------------------
@course_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'instructor':
        abort(403) 
        
    form = CourseForm()
    if form.validate_on_submit():
        v_file = save_uploaded_file(form.video.data, 'videos')
        r_file = save_uploaded_file(form.resource_file.data, 'resources')

        course = Course(
            title=form.title.data,
            description=form.description.data,
            instructor=current_user,
            video_filename=v_file,
            resource_filename=r_file
        )
        course.save()
        flash('Course Created Successfully!', 'success')
        return redirect(url_for('dashboard.index'))
        
    return render_template('create_course.html', form=form, legend='Create Course')

# -----------------------
# 2. EDIT COURSE (Fixed AttributeError logic)
# -----------------------
@course_bp.route('/course/<course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    if course.instructor != current_user:
        abort(403)
        
    form = CourseForm()
    
    if form.validate_on_submit():
        update_data = {
            'set__title': form.title.data,
            'set__description': form.description.data
        }

        # ✅ Safe Access using getattr to prevent AttributeError
        current_v = getattr(course, 'video_filename', None)
        current_r = getattr(course, 'resource_filename', None)

        if form.video.data:
            v_file = save_uploaded_file(form.video.data, 'videos', current_v)
            update_data['set__video_filename'] = v_file
            
        if form.resource_file.data:
            r_file = save_uploaded_file(form.resource_file.data, 'resources', current_r)
            update_data['set__resource_filename'] = r_file

        course.update(**update_data)
        course.reload() 
        
        flash('Course updated successfully!', 'success')
        return redirect(url_for('dashboard.index'))
    
    elif request.method == 'GET':
        form.title.data = course.title
        form.description.data = course.description
        
    return render_template('create_course.html', form=form, legend='Edit Course', course=course)

# -----------------------
# 3. ENROLL, VIEW, HIDE, DELETE
# -----------------------
@course_bp.route('/course/<course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    if current_user.role != 'student':
        flash('Only students can enroll.', 'danger')
        return redirect(url_for('main.home'))
    course = Course.objects.get_or_404(id=course_id)
    existing = Enrollment.objects(student=current_user, course=course).first()
    if not existing:
        Enrollment(student=current_user, course=course).save()
        flash(f'Enrolled in {course.title}!', 'success')
    return redirect(url_for('dashboard.student_index'))

@course_bp.route('/<course_id>', methods=['GET', 'POST'])
@login_required
def view_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    if current_user.role == 'student':
        is_enrolled = Enrollment.objects(student=current_user, course=course).first()
        if not is_enrolled:
            return redirect(url_for('dashboard.student_index'))
    lessons = Lesson.objects(course=course)
    form = LessonForm()
    return render_template('view_course.html', course=course, lessons=lessons, form=form)

@course_bp.route('/course/<course_id>/hide', methods=['POST'])
@login_required
def hide_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    if course.instructor == current_user:
        course.update(set__is_hidden=not course.is_hidden)
        flash('Status updated!', 'info')
    return redirect(url_for('dashboard.index'))

@course_bp.route('/course/<course_id>/delete', methods=['POST'])
@login_required
def soft_delete_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    if course.instructor == current_user:
        course.update(set__is_active=False)
        flash('Course archived!', 'warning')
    return redirect(url_for('dashboard.index'))