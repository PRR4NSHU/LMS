import os
from dotenv import load_dotenv

# .env file ko load karein
load_dotenv()

class Config:
    # Secret Key bhi .env se lein (Security ke liye)
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-key-please-change'
    
    # MongoDB Config
    MONGODB_SETTINGS = {
        # 'host' key mein poora URI daal dein, Flask-MongoEngine khud samajh jayega
        'host': os.getenv('MONGODB_URI') or 'mongodb://localhost:27017/lms_db'
    }