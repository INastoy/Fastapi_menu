from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)
Session = sessionmaker(engine)


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
