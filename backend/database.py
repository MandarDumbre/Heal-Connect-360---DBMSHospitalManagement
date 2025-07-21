# hms_backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL configuration.
# For development, SQLite is simple and file-based.
# For production and scalability, you MUST use PostgreSQL.
# Example PostgreSQL URL: "postgresql://user:password@host:port/dbname"
# Current default uses SQLite for easy local setup:
SQLALCHEMY_DATABASE_URL = "postgresql://Test:12345678@localhost:5432/MED1"

# If you intend to use PostgreSQL, you would change the line above to something like:
# SQLALCHEMY_DATABASE_URL = "postgresql://your_user:your_password@localhost:5432/your_db_name"
# (Replace your_user, your_password, and your_db_name with your PostgreSQL credentials and database name)


# Create the SQLAlchemy engine.
# For SQLite, `check_same_thread=False` is needed to allow multiple threads to interact.
# For PostgreSQL, this argument is NOT used.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

# Create a SessionLocal class.
# This class will be used to create individual database sessions.
# `autocommit=False` means changes are not committed automatically.
# `autoflush=False` means changes are not flushed to the database automatically.
# `bind=engine` connects the session to our database engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models.
# All SQLAlchemy models will inherit from this Base.
Base = declarative_base()