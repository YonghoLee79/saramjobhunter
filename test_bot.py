#!/usr/bin/env python3
"""
사람인 봇 테스트 스크립트
Test script for Saramin bot functionality
"""

import os
import sys
from datetime import datetime
from saramin_bot import SaraminBot
from config import Config
from logger_config import setup_logger
from database import ApplicationDatabase

def test_configuration():
    """설정 테스트"""
    print("=== 설정 테스트 ===")
    try:
        config = Config()
        print("✓ 설정 로드 성공")
        
        # 필수 설정 확인
        if config.username and config.password:
            print("✓ 로그인 정보 설정됨")
        else:
            print("✗ 로그인 정보가 설정되지 않았습니다.")
            print("  .env 파일에서 SARAMIN_USERNAME과 SARAMIN_PASSWORD를 설정해주세요.")
            return False
            
        print(f"  검색 키워드: {config.search_keyword}")
        print(f"  지역: {config.location}")
        print(f"  고용형태: {config.job_type}")
        print(f"  최대 지원수: {config.max_applications_per_day}개/일")
        
        return True
        
    except Exception as e:
        print(f"✗ 설정 오류: {str(e)}")
        return False

def test_database():
    """데이터베이스 테스트"""
    print("\n=== 데이터베이스 테스트 ===")
    try:
        db = ApplicationDatabase()
        print("✓ 데이터베이스 초기화 성공")
        
        # 테스트 데이터 추가
        test_job_id = "test_" + str(int(datetime.now().timestamp()))
        db.record_application(test_job_id, "https://test.com", "테스트회사", "테스트직무")
        print("✓ 테스트 기록 추가 성공")
        
        # 중복 확인 테스트
        if db.is_already_applied(test_job_id):
            print("✓ 중복 지원 방지 기능 정상")
        else:
            print("✗ 중복 지원 방지 기능 오류")
            
        return True
        
    except Exception as e:
        print(f"✗ 데이터베이스 오류: {str(e)}")
        return False

def test_logging():
    """로깅 테스트"""
    print("\n=== 로깅 테스트 ===")
    try:
        logger = setup_logger()
        logger.info("로깅 테스트 메시지")
        print("✓ 로깅 시스템 정상")
        return True
        
    except Exception as e:
        print(f"✗ 로깅 오류: {str(e)}")
        return False

def test_browser_setup():
    """브라우저 설정 테스트"""
    print("\n=== 브라우저 설정 테스트 ===")
    try:
        # 테스트용 헤드리스 설정
        os.environ['HEADLESS'] = 'true'
        
        config = Config()
        db = ApplicationDatabase()
        logger = setup_logger()
        
        bot = SaraminBot(config, db, logger)
        
        if bot.setup_driver():
            print("✓ Chrome WebDriver 설정 성공")
            bot.close()
            return True
        else:
            print("✗ Chrome WebDriver 설정 실패")
            print("  Chrome 브라우저가 설치되어 있는지 확인해주세요.")
            return False
            
    except Exception as e:
        print(f"✗ 브라우저 설정 오류: {str(e)}")
        return False

def main():
    """메인 테스트 함수"""
    print("사람인 자동 지원 스크립트 테스트를 시작합니다.\n")
    
    tests = [
        ("설정", test_configuration),
        ("데이터베이스", test_database),
        ("로깅", test_logging),
        ("브라우저", test_browser_setup)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"\n{name} 테스트에서 문제가 발견되었습니다.")
    
    print(f"\n=== 테스트 결과 ===")
    print(f"통과: {passed}/{total}")
    
    if passed == total:
        print("✓ 모든 테스트가 통과했습니다!")
        print("\n다음 단계:")
        print("1. .env 파일에서 사람인 로그인 정보를 설정하세요")
        print("2. python main.py 명령으로 봇을 실행하세요")
        print("3. python scheduler.py 명령으로 스케줄러를 실행하세요")
    else:
        print("✗ 일부 테스트가 실패했습니다. 위의 오류를 확인하고 수정해주세요.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())