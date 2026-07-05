"""
Django settings for HRFlow Pro project.

This file contains the main configuration for the HR Payroll ERP SYSTEM.
For now, the project uses SQLite for quick development.
Later, I will move the database to PostgreSQL to make it more professional.
"""

from pathlib import Path

#BASE__DIR points to the main project folder.
#Example : C:/Users/pepik/Desktop/HRFlow Pro
BASE_DIR = Path(__file__).resolve().parent.parent

#Development secret key.
#In a real production system, this key should be stored in evnvironment variables.
SECRET_KEY = 'django-insecure-0!2k4uauf78f%=@vv)4kog2y5s=9f&x++e$r@x*9wu8mf2k$lj'

#DEBUD is True only foe local development.
#In production, this must be changed to False.
DEBUG = True

#Empty list is fine for local development.
#Last, when deployed online, we will add the real domain here.
ALLOWED_HOSTS = []

#Django applications that are installed in this project.
#The first apps are built-in Django apps.
#The secound group contains my custom HRFlow Pro modules.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #HRFlow Pro custom apps
    'accounts',
    'employees',
    'payroll',
    'departments',
    'attendance',
    'leave_management',
    'dashboard',
    'reports',
    'audit',
]

#Middleware controls request/response processing.
#These are standard Django middleware settings foe security, sessions, and authentication.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#Main URL configuration for the project.
ROOT_URLCONF = 'config.urls'

#Template configuration.
#DIRS tells Django where to look for global templates.
#APP_DIRS=True allows Django to find templates insiade each app.
TEMPLATES = [
    {
        'BACKEND' : 'django.template.backends.django.DjangoTemplates',

        #Global templates folder.
        #I will create this folder later.
        'DIRS' : [
            BASE_DIR / 'templates'
        ],

        'APP_DIRS' : True,

        'OPTIONS' : {
            'context_processors' : [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }
    }
]

#WSGI application for the project.
WSGI_APPLICATION = 'config.wsgi.application'

#Database configuration.
#FOR THE FIRST DEVELOPMENT STAGE, I USE sqlITE BECAUSE IT WORKS IMMEDIATELY.
##Later, I will switch this to PostgreSQL and connect with DBeaver.
DATABASES = {
    'default' : {
        'ENGINE' : 'django.db.backends.sqlite3',
        'NAME' : BASE_DIR / 'db.sqlite3',
    }
}

#Password validation settings.
#These are standard Django password validators for security.
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME' : 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME' : 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME' : 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME' : 'django.contrib.auth.password_validation.NumericPasswordValidator',
    }
]

#Language and timezone settings.
#The system uses English beacause this is better for professional portfolio project.
LANGUAGE_CODE = 'en-us'

#UK timezone because the project is designed for a UK-style HR/payroll system.
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_TZ = True

#Static files configuration.
#Static files are CSS, JavaScript, images and icons.
STATIC_URL = '/static/'

#This is the global static folder that I will create later.
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

#Default primary key field type type.
#BigAutoField is recommended for modern Django projects.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#Login logout redirects.
#These settings will be used later when I build the login system.
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
