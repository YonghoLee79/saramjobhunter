#!/usr/bin/env python3
"""
사람인 자동 지원 스크립트 메인 실행 파일
Main execution file for Saramin job application automation
"""

import os
import sys
import time
from datetime import datetime
from saramin_bot import SaraminBot
from config import Config
from logger_config import setup_logger
from database import ApplicationDatabase

def main():
    """메인 실행 함수"""
    logger = setup_logger()
    
    try:
        # 환경 변수 확인
        if not os.path.exists('.env'):
            logger.error(".env 파일이 존재하지 않습니다. .env.example을 참고하여 설정해주세요.")
            sys.exit(1)
            
        # 설정 로드
        config = Config()
        
        # 데이터베이스 초기화
        db = ApplicationDatabase()
        
        # 당일 실행 여부 확인
        today = datetime.now().date()
        if db.is_executed_today(today):
            logger.info("오늘 이미 스크립트가 실행되었습니다. 내일 다시 시도해주세요.")
            return
            
        logger.info("사람인 자동 지원 스크립트를 시작합니다.")
        
        # 봇 초기화 및 실행
        bot = SaraminBot(config, db, logger)
        
        try:
            # 로그인
            if not bot.login():
                logger.error("로그인에 실패했습니다.")
                return
                
            # 채용 공고 검색 및 지원
            applied_count = bot.search_and_apply_jobs()
            
            # 실행 기록 저장
            db.record_execution(today, applied_count)
            
            logger.info(f"스크립트 실행 완료. 총 {applied_count}개 채용공고에 지원했습니다.")
            
        except Exception as e:
            logger.error(f"봇 실행 중 오류 발생: {str(e)}")
        finally:
            bot.close()
            
    except Exception as e:
        logger.error(f"메인 실행 중 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
