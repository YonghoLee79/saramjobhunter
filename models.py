"""
PostgreSQL 데이터베이스 모델
Database models for PostgreSQL
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class JobApplication(Base):
    """채용 지원 기록"""
    __tablename__ = 'job_applications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(255), unique=True, nullable=False, index=True)
    job_url = Column(Text, nullable=False)
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(500), nullable=False)
    keyword = Column(String(100), nullable=True)  # 검색 키워드
    application_date = Column(DateTime, default=datetime.now, nullable=False)
    status = Column(String(50), default='applied', nullable=False)  # applied, interview, rejected, hired
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

class ExecutionLog(Base):
    """실행 기록"""
    __tablename__ = 'execution_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_date = Column(String(10), unique=True, nullable=False, index=True)  # YYYY-MM-DD
    applications_count = Column(Integer, default=0, nullable=False)
    keywords_searched = Column(Text, nullable=True)  # JSON string of keywords
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(50), default='completed', nullable=False)  # running, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

class UserConfiguration(Base):
    """사용자 설정"""
    __tablename__ = 'user_configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

class SystemLog(Base):
    """시스템 로그"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    log_level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True)
    function_name = Column(String(100), nullable=True)
    execution_id = Column(Integer, nullable=True)  # Reference to execution_logs.id
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

def get_database_url():
    """DATABASE_URL 환경변수에서 PostgreSQL 연결 URL 가져오기"""
    return os.environ.get('DATABASE_URL')

def create_engine():
    """SQLAlchemy 엔진 생성"""
    from sqlalchemy import create_engine as sa_create_engine
    
    database_url = get_database_url()
    if not database_url:
        raise ValueError("DATABASE_URL 환경변수가 설정되지 않았습니다")
    
    # PostgreSQL 엔진 생성
    engine = sa_create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    return engine

def create_session():
    """데이터베이스 세션 생성"""
    engine = create_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def init_database():
    """데이터베이스 테이블 초기화"""
    engine = create_engine()
    Base.metadata.create_all(bind=engine)
    print("PostgreSQL 데이터베이스 테이블이 초기화되었습니다")

if __name__ == "__main__":
    # 데이터베이스 초기화 테스트
    init_database()