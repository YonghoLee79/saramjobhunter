#!/usr/bin/env python3
"""
사람인 봇 데모 스크립트 - 로그인 정보 없이 주요 기능 시연
Demo script for Saramin bot - demonstrates main features without login
"""

import os
import sys
from datetime import datetime
from saramin_bot import SaraminBot
from config import Config
from logger_config import setup_logger
from database import ApplicationDatabase

def demo_without_login():
    """로그인 없이 주요 기능 데모"""
    print("🚀 사람인 자동 지원 스크립트 데모")
    print("=" * 50)
    
    # 설정 로드
    try:
        config = Config()
        print(f"✓ 검색 키워드: {config.search_keyword}")
        print(f"✓ 지역: {config.location}")
        print(f"✓ 고용형태: {config.job_type}")
        print(f"✓ 일일 최대 지원: {config.max_applications_per_day}개")
        print(f"✓ 지원 간격: {config.min_delay_between_applications}-{config.max_delay_between_applications}초")
    except Exception as e:
        print(f"✗ 설정 오류: {str(e)}")
        return
    
    print("\n📊 데이터베이스 기능 시연")
    print("-" * 30)
    
    # 데이터베이스 기능 시연
    db = ApplicationDatabase()
    
    # 샘플 데이터 추가
    sample_jobs = [
        ("job_001", "https://www.saramin.co.kr/job/001", "바이오텍회사", "바이오 연구원"),
        ("job_002", "https://www.saramin.co.kr/job/002", "제약회사", "신약개발 연구원"),
        ("job_003", "https://www.saramin.co.kr/job/003", "병원", "임상연구 코디네이터")
    ]
    
    for job_id, url, company, title in sample_jobs:
        if not db.is_already_applied(job_id):
            db.record_application(job_id, url, company, title)
            print(f"✓ 지원 기록: {company} - {title}")
        else:
            print(f"⚠ 이미 지원함: {company} - {title}")
    
    # 통계 출력
    stats = db.get_statistics()
    print(f"\n📈 현재 통계:")
    print(f"  총 지원 수: {stats['total_applications']}개")
    print(f"  이번 주: {stats['week_applications']}개")
    print(f"  이번 달: {stats['month_applications']}개")
    
    if stats['top_companies']:
        print(f"\n🏢 주요 지원 회사:")
        for company, count in stats['top_companies'][:3]:
            print(f"  - {company}: {count}회")
    
    print("\n🔄 중복 지원 방지 테스트")
    print("-" * 30)
    
    test_job_id = "job_001"
    if db.is_already_applied(test_job_id):
        print(f"✓ 중복 방지 정상: {test_job_id}는 이미 지원한 공고")
    else:
        print(f"✗ 중복 방지 오류")
    
    print("\n⏰ 일일 실행 제한 테스트")
    print("-" * 30)
    
    today = datetime.now().date()
    if db.is_executed_today(today):
        print("✓ 오늘 이미 실행됨 - 추가 실행 방지")
    else:
        print("✓ 오늘 첫 실행 - 진행 가능")
        db.record_execution(today, 3)  # 데모용 실행 기록
    
    print("\n🔍 검색 URL 생성 테스트")
    print("-" * 30)
    
    # 임시 봇 인스턴스로 URL 생성 테스트
    logger = setup_logger()
    bot = SaraminBot(config, db, logger)
    search_url = bot.build_search_url()
    print(f"✓ 생성된 검색 URL:")
    print(f"  {search_url}")
    
    print("\n🎯 실제 사용을 위한 단계")
    print("-" * 30)
    print("1. .env 파일에서 SARAMIN_USERNAME과 SARAMIN_PASSWORD 설정")
    print("2. 사람인에서 이력서 미리 등록")
    print("3. python main.py 실행으로 봇 시작")
    print("4. python scheduler.py 실행으로 매일 자동 실행")
    
    print("\n✅ 데모 완료!")

if __name__ == "__main__":
    demo_without_login()