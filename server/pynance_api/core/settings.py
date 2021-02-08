import sys, os, dotenv

### DIRECTORY CONFIGURATION ## 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
APP_DIR = os.path.join(PROJECT_DIR, 'app')
    # Add Application To Python Path
sys.path.append(PROJECT_DIR)

### ENVIRONMENT INITIALIZATION ###
dotenv.load_dotenv(os.path.join(os.path.join(PROJECT_DIR, 'env'),'.env'))

### APPLICATION ENVIRONMENT CONFIGURATION ###
## APP SETTINGS
APP_ENV = os.environ.setdefault('APP_ENV', 'local')
SECRET_KEY = os.environ.setdefault('SECRET_KEY', 'NoIAmYourFather')
DEBUG= True if os.getenv('DEBUG').lower() == 'true' else False
VERBOSE= True if os.getenv('VERBOSE').lower() == 'true' else False
## LOCALIZATION SETTINGS
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

### DJANGO CONFIGURATION ###
ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api.apps.ApiConfig',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]
STATIC_URL = '/static/'

### HEADER CONFIGURATION ###
ALLOWED_HOSTS = [ 'localhost' ]

### DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
