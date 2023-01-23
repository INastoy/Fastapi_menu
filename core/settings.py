import os
from dotenv import load_dotenv

if not load_dotenv() and not os.getenv('DATABASE_URL'):
    raise EnvironmentError('Please, create .env file and put environment variables in it')

DATABASE_URL = os.getenv('DATABASE_URL')
