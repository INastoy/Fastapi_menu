import os
from dotenv import load_dotenv

if not load_dotenv():
    raise EnvironmentError('Please, create .env file and put environment variables in it')

IS_RUN_TESTS = int(os.getenv('IS_RUN_TESTS', 0))

if IS_RUN_TESTS:
    DATABASE_URL = os.getenv('TEST_DATABASE_URL')
else:
    DATABASE_URL = os.getenv('DATABASE_URL')
