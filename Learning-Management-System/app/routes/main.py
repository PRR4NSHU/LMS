from flask import Blueprint, render_template
from flask_login import current_user
from app.models import Course

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    all_courses = Course.objects(is_active=True, is_hidden=False).order_by('-date_posted').limit(6)
    
    # 'courses' variable ko template mein bhej rahe hain
    return render_template('home.html', courses=all_courses)