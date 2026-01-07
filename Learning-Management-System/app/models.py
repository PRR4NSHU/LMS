from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app


# =======================
# Flask-Login user loader
# =======================
@login_manager.user_loader
def load_user(user_id):
    # MongoDB uses ObjectId (stored as string in Flask-Login)
    return User.objects(id=user_id).first()


# =======================
# 1. USER DOCUMENT
# =======================
class User(db.Document, UserMixin):
    username = db.StringField(max_length=20, required=True, unique=True)
    email = db.StringField(max_length=120, required=True, unique=True)
    image_file = db.StringField(default="default.jpg")
    password = db.StringField(required=True)
    signature_filename = db.StringField()
    email_verification_code = db.StringField()
    pending_new_email = db.StringField()
    profile_pic = db.StringField()       # Profile Photo
    qualification = db.StringField()     # Degree (e.g. M.Tech, PhD)
    institution = db.StringField()       # College/Company (e.g. IIT Delhi)
    
    # 🟢 NEW: Social Links
    linkedin_url = db.StringField()
    twitter_url = db.StringField()
    website_url = db.StringField()

    # Roles: student / instructor / admin
    role = db.StringField(default="student")

    meta = {
        "collection": "users"
    }

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': str(self.id)})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.objects(pk=user_id).first()


class UserProgress(db.Document):
    student = db.ReferenceField('User', required=True)
    course = db.ReferenceField('Course', required=True)
    completed_lessons = db.ListField(db.ReferenceField('Lesson')) # Finished lessons ki ID list
    last_updated = db.DateTimeField(default=datetime.utcnow)


# =======================
# 2. COURSE DOCUMENT
# =======================
class Course(db.Document):
    title = db.StringField(max_length=100, required=True)
    description = db.StringField(required=True)
    date_posted = db.DateTimeField(default=datetime.utcnow)
    is_active = db.BooleanField(default=True)  # False hone par user ko nahi dikhega
    is_hidden = db.BooleanField(default=False) # Instructor hide kar sakega

    # Instructor reference
    instructor = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    # Database mein filenames save karne ke liye fields
    video_filename = db.StringField()    
    resource_filename = db.StringField() 
    
    is_active = db.BooleanField(default=True)
    date_created = db.DateTimeField(default=datetime.utcnow)
    certificate_enabled = db.BooleanField(default=False)
    price = db.IntField(default=0)

    meta = {
        "collection": "courses"
    }

    def __repr__(self):
        return f"Course('{self.title}')"


# =======================
# 3. LESSON DOCUMENT
# =======================
class Lesson(db.Document):
    title = db.StringField(max_length=100, required=True)
    content = db.StringField(required=True)  # text or video URL

    course = db.ReferenceField(Course, reverse_delete_rule=db.CASCADE)
    # 👇 Har lesson ki apni files
    video_filename = db.StringField()
    resource_filename = db.StringField()
    
    date_created = db.DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "lessons"
    }

    def __repr__(self):
        return f"Lesson('{self.title}')"


# =======================
# 4. ENROLLMENT DOCUMENT
# =======================
class Enrollment(db.Document):
    student = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    course = db.ReferenceField(Course, reverse_delete_rule=db.CASCADE)
    student = db.ReferenceField('User')
    course = db.ReferenceField('Course')

    date_enrolled = db.DateTimeField(default=datetime.utcnow)
    progress = db.IntField(default=0)  # 0–100
    amount_paid = db.IntField(default=0)
    transaction_id = db.StringField()
    payment_status = db.StringField(default='completed') # pending/completed

    meta = {
        "collection": "enrollments"
    }

    def __repr__(self):
        return f"Enrollment(Student={self.student.username}, Course={self.course.title})"
