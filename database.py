from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

DB_URL = 'mysql+pymysql://capstone-project:team05@db:3306/capstone-project'

engine = create_engine(DB_URL, pool_recycle=500)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
