from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)
Session = sessionmaker(engine)


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()

#
# def get_test_session():
#     session = Session()
#     try:
#         yield next(session)
#     finally:
#         session.close()

# async def get_session() -> AsyncSession:
#     async with async_session() as session:
#         yield session