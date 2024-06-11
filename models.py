from sqlalchemy import Column, String, INT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MLEntity(Base):
    __tablename__ = 'music'  # 데이터베이스에 있는 테이블 이름

    id = Column(INT, primary_key=True, autoincrement=True)
    model = Column(String)
    instrument_type = Column(String)
    file_name = Column(String)
    file_path = Column(String)
    user_email = Column(String)  # ForeignKey 제거
    spleeter_output_path = Column(String)
    basic_pitch_output_path = Column(String)
