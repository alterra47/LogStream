from sqlalchemy import create_engine, Column, BigInteger, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Configuration --- 
# For PostgreSQL: "postgresql://user:password@localhost/logstream_db"
DATABASE_URL = "postgresql://postgres:password@localhost/logstream_db"

# --- Setup ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Model Definition ---
# This MUST match the table created by your C# Entity Framework
# --- Model Definition ---
class LogEntrySQL(Base):
    __tablename__ = "Logs"
    __table_args__ = {'quote': True} 

    # We must provide the exact string name "Id" as the first argument
    id = Column("Id", BigInteger, primary_key=True, index=True)
    timestamp = Column("Timestamp", String)
    service = Column("Service", String)
    level = Column("Level", String)
    message = Column("Message", String)

# Helper to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()