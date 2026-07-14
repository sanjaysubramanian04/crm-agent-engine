from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from dotenv import load_dotenv

load_dotenv(override=True)

import urllib.parse

# Use Supabase/Postgres URL from environment, fallback to SQLite for local dev if missing
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crm_local.db")

# Fix for special characters in password (like @)
if SQLALCHEMY_DATABASE_URL.startswith("postgresql://") or SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    try:
        # Parse the URL
        parsed = urllib.parse.urlparse(SQLALCHEMY_DATABASE_URL)
        if parsed.password and "@" in parsed.password:
            # Reconstruct with encoded password
            username = parsed.username
            password = urllib.parse.quote_plus(parsed.password)
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip("/")
            SQLALCHEMY_DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    except Exception as e:
        print(f"WARNING: Could not auto-encode DB password: {e}")

# Fix for SQLAlchemy 1.4+ where postgres:// is not supported
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Adjust engine parameters based on DB type
try:
    print(f"DEBUG: Using database URL: {SQLALCHEMY_DATABASE_URL}")
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        # Increase pool size for cloud databases
        engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    print(f"ERROR: Failed to create database engine: {e}")
    # Fallback engine to prevent import crashes
    engine = create_engine("sqlite:///./fallback.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String, index=True)
    interaction_type = Column(String)
    date = Column(String)
    time = Column(String)
    attendees = Column(String)
    topics_discussed = Column(Text)
    materials_shared = Column(Text)
    sentiment = Column(String)
    outcomes = Column(Text)
    follow_up_actions = Column(Text)
    next_best_action = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Initialize tables safely
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"WARNING: Could not initialize database tables: {e}")
