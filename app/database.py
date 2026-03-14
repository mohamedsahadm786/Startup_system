from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This is the database URL
# sqlite:///./app.db means: create a file called app.db in the project root
DATABASE_URL = "sqlite:///./app.db"

# Create the database engine
# connect_args is needed only for SQLite (not for PostgreSQL or MySQL)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal is a factory — every time we need to talk to the DB,
# we create a new session from this factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base is the parent class for all our models (tables)
# Every table we define will inherit from this Base
Base = declarative_base()


# This function is used in every router as a dependency
# It opens a DB session, gives it to the route, then closes it when done
# Think of it like: open file → use file → close file
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()