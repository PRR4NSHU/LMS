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


# =======================
# 2. COURSE DOCUMENT
# =======================
class Course(db.Document):
    title = db.StringField(max_length=100, required=True)
    description = db.StringField(required=True)
    date_posted = db.DateTimeField(default=datetime.utcnow)

    # Instructor reference
    instructor = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)

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

    date_enrolled = db.DateTimeField(default=datetime.utcnow)
    progress = db.IntField(default=0)  # 0–100

    meta = {
        "collection": "enrollments"
    }

    def __repr__(self):
        return f"Enrollment(Student={self.student.username}, Course={self.course.title})"
