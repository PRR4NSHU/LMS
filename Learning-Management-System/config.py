import os
from dotenv import load_dotenv

# .env file ko load karein
load_dotenv()

class Config:
    # --- FLASK CORE ---
    # Agar .env mein key nahi milti toh fallback ke liye ek random string rakhi hai
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-key-12345') 
    
    # --- MAIL CONFIGURATION ---
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # Sender ka naam define karna zaroori hai (e.g. "LearnHub <email@gmail.com>")
    MAIL_DEFAULT_SENDER = (os.getenv('MAIL_SENDER_NAME', 'LearnHub Support'), os.getenv('MAIL_USERNAME'))
    
    # --- MONGODB CONFIGURATION ---
    # Atlas ke liye 'connect': False aur serverSelectionTimeoutMS zaroori hote hain
    MONGODB_SETTINGS = {
        'host': os.getenv('MONGODB_URI'),
        'connect': False, # Connection request tabhi bhejega jab database ki zaroorat ho
        'serverSelectionTimeoutMS': 5000 # 5 seconds tak wait karega Atlas connect hone ka
    }

    # Security settings for Session
    SESSION_COOKIE_SECURE = False  # Localhost ke liye False, Production par True hoga
    REMEMBER_COOKIE_DURATION = 3600 # 1 hour tak login session rahega