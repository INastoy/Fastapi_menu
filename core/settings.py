import os

from dotenv import load_dotenv

if not load_dotenv() and not os.getenv('DATABASE_URL'):
    raise OSError(
        'Please, create .env file and put environment variables in it')

DATABASE_URL = os.getenv('DATABASE_URL')
CACHE_URL = os.getenv('CACHE_URL')
CACHE_EXPIRATION = 3600
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 3600
