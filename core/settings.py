import os

from dotenv import load_dotenv

if not load_dotenv() and not os.getenv('DATABASE_URL'):
    raise OSError(
        'Please, create .env file and put environment variables in it')

DATABASE_USER = os.getenv('POSTGRES_USER')
DATABASE_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DATABASE_URL = os.getenv('DATABASE_URL')
TEST_DB_NAME = os.getenv('TEST_DB_NAME', default='test_database')

CACHE_DB_NUM = os.getenv('REDIS_DB_NUM')
TEST_CACHE_DB_NUM = '7'
CACHE_URL = os.getenv('CACHE_URL')
CACHE_EXPIRATION = 3600
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 3600

GENERATED_FILES_DIRNAME = 'generated_files'
