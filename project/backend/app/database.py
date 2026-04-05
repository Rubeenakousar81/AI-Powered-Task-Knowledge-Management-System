from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# change this to your mysql password before running!
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ai_task_db"

# TODO: move this to a .env file later

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# this is used in every api route to get db connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
