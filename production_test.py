#!/usr/bin/env python3
"""
실제 환경 테스트 스크립트
Production environment test script
"""

import os
import sys
import time
from datetime import datetime
from saramin_bot import SaraminBot
from config import Config
from logger_config import setup_logger
from database import ApplicationDatabase

def clear_today_execution():
    """오늘 실행 기록 삭제 (테스트용)"""
    db = ApplicationDatabase()
    today = datetime.now().date()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM execution_log WHERE execution_date = ?', (today,))
        conn.commit()
        print(f"오늘({today}) 실행 기록을 삭제했습니다.")

def production_test():
    """실제 환경 테스트"""
    print("🚀 사람인 자동 지원 스크립트 - 실제 환경 테스트")
    print("=" * 60)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 오늘 실행 기록 삭제 (테스트를 위해)
    clear_today_execution()
    
    # 설정 로드
    try:
        config = Config()
        print(f"✓ 설정 로드 완료")
        print(f"  검색 키워드: {config.search_keyword}")
        print(f"  지역: {config.location}")
        print(f"  고용형태: {config.job_type}")
        print(f"  헤드리스 모드: {config.headless}")
    except Exception as e:
        print(f"✗ 설정 오류: {str(e)}")
        return False
    
    # 데이터베이스 초기화
    try:
        db = ApplicationDatabase()
        print("✓ 데이터베이스 초기화 완료")
    except Exception as e:
        print(f"✗ 데이터베이스 오류: {str(e)}")
        return False
    
    # 로거 설정
    try:
        logger = setup_logger()
        print("✓ 로깅 시스템 준비 완료")
    except Exception as e:
        print(f"✗ 로깅 오류: {str(e)}")
        return False
    
    print("\n🔄 봇 실행 시작...")
    print("-" * 40)
    
    # 봇 초기화 및 실행
    bot = SaraminBot(config, db, logger)
    
    try:
        # 1단계: 브라우저 설정
        print("1단계: 브라우저 설정 중...")
        if not bot.setup_driver():
            print("✗ 브라우저 설정 실패")
            return False
        print("✓ 브라우저 설정 완료")
        
        # 2단계: 로그인
        print("\n2단계: 사람인 로그인 시도...")
        login_start = time.time()
        
        if bot.login():
            login_time = time.time() - login_start
            print(f"✓ 로그인 성공 (소요시간: {login_time:.1f}초)")
            
            # 3단계: 채용공고 검색 및 지원
            print("\n3단계: 채용공고 검색 및 지원...")
            search_start = time.time()
            
            applied_count = bot.search_and_apply_jobs()
            search_time = time.time() - search_start
            
            print(f"✓ 지원 완료: {applied_count}개 공고 (소요시간: {search_time:.1f}초)")
            
            # 4단계: 실행 기록 저장
            today = datetime.now().date()
            db.record_execution(today, applied_count)
            print(f"✓ 실행 기록 저장 완료")
            
            # 통계 출력
            stats = db.get_statistics()
            print(f"\n📊 현재 통계:")
            print(f"  총 지원 수: {stats['total_applications']}개")
            print(f"  오늘 지원: {applied_count}개")
            
            return True
            
        else:
            print("✗ 로그인 실패")
            print("  계정 정보를 확인하거나 사람인에서 추가 인증이 필요할 수 있습니다.")
            return False
            
    except Exception as e:
        print(f"✗ 실행 중 오류: {str(e)}")
        logger.error(f"실행 중 오류: {str(e)}")
        return False
        
    finally:
        bot.close()
        print("브라우저 종료 완료")

def show_execution_summary():
    """실행 결과 요약"""
    print(f"\n📋 실행 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 로그 파일 확인
    try:
        with open("saramin_bot.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            print(f"\n📄 최근 로그 (총 {len(lines)}줄):")
            recent_lines = lines[-15:] if len(lines) > 15 else lines
            for line in recent_lines:
                print(f"  {line.strip()}")
    except Exception as e:
        print(f"로그 읽기 오류: {str(e)}")

if __name__ == "__main__":
    success = production_test()
    show_execution_summary()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 실제 환경 테스트 성공!")
        print("스크립트가 정상적으로 작동하며 실제 사용 준비가 완료되었습니다.")
    else:
        print("⚠️ 테스트 중 일부 문제가 발생했습니다.")
        print("로그를 확인하여 구체적인 원인을 파악할 수 있습니다.")
    
    print("\n🎯 다음 단계:")
    print("- 매일 자동 실행: python scheduler.py")
    print("- 수동 실행: python main.py")
    print("- 통계 확인: python -c \"from database import ApplicationDatabase; db = ApplicationDatabase(); print(db.get_statistics())\"")