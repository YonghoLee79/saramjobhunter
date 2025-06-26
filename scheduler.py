"""
스케줄링 모듈
Scheduling module for daily execution
"""

import schedule
import time
import subprocess
import sys
from datetime import datetime
from logger_config import setup_logger

def run_saramin_bot():
    """사람인 봇 실행"""
    logger = setup_logger("scheduler.log")
    
    try:
        logger.info("스케줄된 사람인 봇 실행 시작")
        
        # main.py 실행
        result = subprocess.run([sys.executable, "main.py"], 
                              capture_output=True, 
                              text=True,
                              encoding='utf-8')
        
        if result.returncode == 0:
            logger.info("사람인 봇 실행 완료")
            logger.info(f"출력: {result.stdout}")
        else:
            logger.error(f"사람인 봇 실행 실패 (코드: {result.returncode})")
            logger.error(f"오류: {result.stderr}")
            
    except Exception as e:
        logger.error(f"스케줄러 실행 중 오류: {str(e)}")

def main():
    """스케줄러 메인 함수"""
    logger = setup_logger("scheduler.log")
    
    # 매일 오전 9시에 실행
    schedule.every().day.at("09:00").do(run_saramin_bot)
    
    # 또는 매일 특정 시간에 실행 (환경 변수로 설정 가능)
    import os
    scheduled_time = os.getenv("SCHEDULED_TIME", "09:00")
    schedule.every().day.at(scheduled_time).do(run_saramin_bot)
    
    logger.info(f"스케줄러 시작 - 매일 {scheduled_time}에 실행됩니다.")
    
    # 즉시 실행 옵션
    if "--run-now" in sys.argv:
        logger.info("즉시 실행 모드")
        run_saramin_bot()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
            
    except KeyboardInterrupt:
        logger.info("스케줄러 중지됨")
    except Exception as e:
        logger.error(f"스케줄러 오류: {str(e)}")

if __name__ == "__main__":
    main()
