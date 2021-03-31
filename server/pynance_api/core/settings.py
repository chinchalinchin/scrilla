import sys, os, dotenv

"""
Server Configuration
--------------------

Not to be confused with app.settings, which configures the optimization and statistical calculations 
performed by the application. These settings only affect the server side of the application. 

"""


### DIRECTORY CONFIGURATION ## 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
APP_DIR = os.path.join(PROJECT_DIR, 'app')
    # Add Application To Python Path
sys.path.append(PROJECT_DIR)

### ENVIRONMENT INITIALIZATION ###

APP_ENV = os.environ.setdefault('APP_ENV', 'local').strip()

# Load in local.env file if not running application container. Container should 
# already have the container.env file preloaded in its environment.
if APP_ENV != 'container':
    dotenv.load_dotenv(os.path.join(os.path.join(PROJECT_DIR, 'env'),'local.env'))

### APPLICATION ENVIRONMENT CONFIGURATION ###
## APP SETTINGS
SECRET_KEY = os.environ.setdefault('SECRET_KEY', 'NoIAmYourFather').strip()
DEBUG= os.getenv('DEBUG').strip().lower() == 'true'
LOG_LEVEL = str(os.environ.setdefault('LOG_LEVEL', "info")).strip().lower()

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
    'corsheaders',
    'api.apps.ApiConfig',
    'data.apps.DataConfig'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.LogMiddleware',
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
ALLOWED_HOSTS = [ '*' ]
# TODO: restrict origins once frontend is working
CORS_ALLOW_ALL_ORIGINS = True


### DATABASE CONFIGURATION
if APP_ENV == 'local':
    ## DATABASES = {
       ## 'default': {
        ##   'ENGINE': 'django.db.backends.sqlite3',
        ##    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        ## }
    ## }
    DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('POSTGRES_HOST').strip(),
        'NAME': os.getenv('POSTGRES_DB').strip(),
        'USER': os.getenv('POSTGRES_USER').strip(),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD').strip(),
        'PORT': os.getenv('POSTGRES_PORT').strip()
        }
    }
elif APP_ENV == 'container':
    DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('POSTGRES_HOST').strip(),
        'NAME': os.getenv('POSTGRES_DB').strip(),
        'USER': os.getenv('POSTGRES_USER').strip(),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD').strip(),
        'PORT': os.getenv('POSTGRES_PORT').strip()
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

### API CONFIGURATOIN
REQUEST_PARAMS = {
    'tickers': 'tickers',
    'start_date': 'start',
    'end_date': 'end',
    'target_return': 'target',
    'investment': 'invest',
    'discount_rate': 'discount',
    'sharpe_ratio': 'sharpe',
    'jpeg': 'jpeg'
}