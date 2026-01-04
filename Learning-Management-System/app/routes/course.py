from flask import Blueprint, render_template, url_for, flash, redirect, abort, request
from flask_login import current_user, login_required
from app.models import Course, Lesson
from app.forms import CourseForm, LessonForm

course_bp = Blueprint('courses', __name__)

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
        course = Course(
            title=form.title.data,
            description=form.description.data,
            instructor=current_user
        )
        course.save()
        flash('Course Created Successfully!', 'success')
        return redirect(url_for('dashboard.index'))
        
    return render_template('create_course.html', form=form, legend='Create Course')

# -----------------------
# 2. VIEW COURSE & ADD LESSONS
# -----------------------
@course_bp.route('/<course_id>', methods=['GET', 'POST'])
@login_required
def view_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    lessons = Lesson.objects(course=course)
    form = LessonForm()
    
    if form.validate_on_submit() and current_user == course.instructor:
        lesson = Lesson(
            title=form.title.data,
            content=form.content.data,
            course=course
        )
        lesson.save()
        flash('Lesson added!', 'success')
        return redirect(url_for('courses.view_course', course_id=course.id))

    # Fix: Return statement ko logic se bahar nikala gaya hai
    return render_template('view_course.html', course=course, lessons=lessons, form=form)

# -----------------------
# 3. EDIT COURSE
# -----------------------
@course_bp.route('/course/<course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    if course.instructor != current_user:
        abort(403)
        
    form = CourseForm()
    if form.validate_on_submit():
        course.update(
            set__title=form.title.data,
            set__description=form.description.data
        )
        flash('Course has been updated!', 'success')
        return redirect(url_for('dashboard.index'))
    
    # Form mein purana data bharne ke liye
    elif request.method == 'GET':
        form.title.data = course.title
        form.description.data = course.description
        
    return render_template('create_course.html', form=form, legend='Edit Course')

# -----------------------
# 4. HIDE / UNHIDE COURSE
# -----------------------
@course_bp.route('/course/<course_id>/hide', methods=['POST'])
@login_required
def hide_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    if course.instructor != current_user:
        abort(403)
    
    # Toggle logic
    new_status = not course.is_hidden
    course.update(set__is_hidden=new_status)
    
    status_text = "Hidden" if new_status else "Visible"
    flash(f'Course is now {status_text}', 'info')
    return redirect(url_for('dashboard.index'))

# -----------------------
# 5. SOFT DELETE (ARCHIVE)
# -----------------------
@course_bp.route('/course/<course_id>/delete', methods=['POST'])
@login_required
def soft_delete_course(course_id):
    course = Course.objects.get_or_404(id=course_id)
    if course.instructor != current_user:
        abort(403)
        
    course.update(set__is_active=False)
    flash('Course moved to trash (Soft Deleted)', 'warning')
    return redirect(url_for('dashboard.index'))