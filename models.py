from sqlalchemy import Column, String, INT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MLEntity(Base):
    __tablename__ = 'music'  # 데이터베이스에 있는 테이블 이름

    id = Column(INT, primary_key=True, autoincrement=True)
    model = Column(String)
    instrumentType = Column(String)
    fileName = Column(String)
    filePath = Column(String)
    userEmail = Column(String)  # ForeignKey 제거
    generateSheet = Column(String)
    spleeterOutputPath = Column(String)
    basicPitchOutputPath = Column(String)
