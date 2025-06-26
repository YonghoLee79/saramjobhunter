"""
설정 관리 모듈
Configuration management module
"""

import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # .env 파일 로드
        load_dotenv()
        
        # 로그인 정보
        self.username = os.getenv("SARAMIN_USERNAME", "")
        self.password = os.getenv("SARAMIN_PASSWORD", "")
        
        # 마지막 사용 설정 불러오기 (데이터베이스 우선, 환경변수는 백업)
        try:
            from postgres_database import PostgresApplicationDatabase
            db = PostgresApplicationDatabase()
            
            # 검색 조건 - 데이터베이스에서 마지막 사용한 값 우선 사용
            last_keywords = db.get_last_used_keywords()
            last_location = db.get_last_used_location()
            last_max_apps = db.get_last_used_max_applications()
            
            # 데이터베이스 값이 있으면 우선 사용, 없으면 환경변수나 기본값 사용
            self.search_keywords = last_keywords if last_keywords else os.getenv("SEARCH_KEYWORDS", "바이오,생명공학,제약,의료기기")
            self.location = last_location if last_location else os.getenv("LOCATION", "서울")
            self.max_applications_per_day = last_max_apps if last_max_apps else int(os.getenv("MAX_APPLICATIONS_PER_DAY", "100"))
            
        except Exception as e:
            # 데이터베이스 오류 시 환경변수 또는 기본값 사용
            self.search_keywords = os.getenv("SEARCH_KEYWORDS", "바이오,생명공학,제약,의료기기")
            self.location = os.getenv("LOCATION", "서울")
            self.max_applications_per_day = int(os.getenv("MAX_APPLICATIONS_PER_DAY", "100"))
        
        self.job_type = os.getenv("JOB_TYPE", "정규직")
        
        # 키워드 목록 파싱 (쉼표로 구분된 값들)
        self.keyword_list = [keyword.strip() for keyword in self.search_keywords.split(",") if keyword.strip()]
        
        # 지원 설정
        self.max_pages = int(os.getenv("MAX_PAGES", "5"))
        
        # 대기 시간 설정 (초)
        self.min_delay_between_applications = int(os.getenv("MIN_DELAY_BETWEEN_APPLICATIONS", "30"))
        self.max_delay_between_applications = int(os.getenv("MAX_DELAY_BETWEEN_APPLICATIONS", "60"))
        
        # 브라우저 설정
        self.headless = os.getenv("HEADLESS", "false").lower() == "true"
        
        # 로그 설정
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "saramin_bot.log")
        
        # 데이터베이스 설정
        self.db_file = os.getenv("DB_FILE", "applications.db")
        
        self.validate_config()
    
    def validate_config(self):
        """설정 유효성 검사"""
        if not self.username or not self.password:
            raise ValueError("사람인 로그인 정보가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        if self.max_applications_per_day <= 0:
            raise ValueError("일일 최대 지원 수는 1 이상이어야 합니다.")
        
        if self.max_pages <= 0:
            raise ValueError("최대 페이지 수는 1 이상이어야 합니다.")
        
        if self.min_delay_between_applications < 0:
            raise ValueError("최소 대기 시간은 0 이상이어야 합니다.")
        
        if self.max_delay_between_applications < self.min_delay_between_applications:
            raise ValueError("최대 대기 시간은 최소 대기 시간 이상이어야 합니다.")
