from flask import Blueprint, render_template, url_for, flash, redirect, abort
from flask_login import current_user, login_required
from app import db
from app.models import Course, Lesson
from app.forms import CourseForm, LessonForm

course_bp = Blueprint('courses', __name__)

# 1. CREATE COURSE
@course_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_course():
    # Security Check: Only instructors can create
    if current_user.role != 'instructor':
        abort(403) # Forbidden
        
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            instructor=current_user # Link to logged-in user
        )
        course.save()
        flash('Course Created Successfully!', 'success')
        return redirect(url_for('dashboard.index'))
        
    return render_template('create_course.html', form=form, legend='Create Course')

# 2. VIEW COURSE & ADD LESSONS
@course_bp.route('/<course_id>', methods=['GET', 'POST'])
@login_required
def view_course(course_id):
    # Fetch course by ID (MongoEngine uses 'pk' or 'id')
    course = Course.objects.get_or_404(id=course_id)
    lessons = Lesson.objects(course=course)
    
    # Form to add a lesson (Only shows for the course owner)
    form = LessonForm()
    
    # Logic: If Instructor submits the "Add Lesson" form
    if form.validate_on_submit() and current_user == course.instructor:
        lesson = Lesson(
            title=form.title.data,
            content=form.content.data,
            course=course
        )
        lesson.save()
        flash('Lesson added!', 'success')
        return redirect(url_for('courses.view_course', course_id=course.id))

    return render_template('view_course.html', course=course, lessons=lessons, form=form)