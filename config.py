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
        
        # 검색 조건
        self.search_keyword = os.getenv("SEARCH_KEYWORD", "바이오")
        self.location = os.getenv("LOCATION", "서울")
        self.job_type = os.getenv("JOB_TYPE", "정규직")
        
        # 지원 설정
        self.max_applications_per_day = int(os.getenv("MAX_APPLICATIONS_PER_DAY", "10"))
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
