#!/usr/bin/env python3
"""
기능 시연 스크립트 - 로그인 없이 주요 기능 검증
"""

import requests
from config import Config
from database import ApplicationDatabase
from logger_config import setup_logger
from saramin_bot import SaraminBot
import time

def test_saramin_connectivity():
    """사람인 웹사이트 접근 테스트"""
    print("사람인 웹사이트 연결 테스트...")
    try:
        # 검색 페이지 접근 테스트
        response = requests.get("https://www.saramin.co.kr", timeout=10)
        if response.status_code == 200:
            print("✓ 사람인 웹사이트 접근 가능")
            return True
        else:
            print(f"⚠ 응답 코드: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 연결 오류: {str(e)}")
        return False

def test_search_url_generation():
    """검색 URL 생성 테스트"""
    print("\n검색 URL 생성 테스트...")
    try:
        config = Config()
        db = ApplicationDatabase()
        logger = setup_logger()
        
        bot = SaraminBot(config, db, logger)
        search_url = bot.build_search_url()
        
        print(f"✓ 생성된 검색 URL:")
        print(f"  {search_url}")
        
        # URL 구성 요소 확인 (URL 인코딩된 상태로 확인)
        if "%EB%B0%94%EC%9D%B4%EC%98%A4" in search_url and "101000" in search_url and "emp_type=1" in search_url:
            print("✓ 검색 조건이 올바르게 포함됨 (키워드: 바이오, 지역: 서울, 고용형태: 정규직)")
            return True
        else:
            print("✗ 검색 조건 누락")
            return False
            
    except Exception as e:
        print(f"✗ URL 생성 오류: {str(e)}")
        return False

def test_database_operations():
    """데이터베이스 기능 테스트"""
    print("\n데이터베이스 기능 테스트...")
    try:
        db = ApplicationDatabase()
        
        # 테스트 데이터 추가
        test_jobs = [
            ("test_001", "https://test1.com", "테스트회사A", "연구원"),
            ("test_002", "https://test2.com", "테스트회사B", "개발자"),
        ]
        
        for job_id, url, company, title in test_jobs:
            if not db.is_already_applied(job_id):
                success = db.record_application(job_id, url, company, title)
                if success:
                    print(f"✓ 지원 기록 추가: {company} - {title}")
                else:
                    print(f"✗ 지원 기록 추가 실패")
            else:
                print(f"⚠ 이미 지원함: {company} - {title}")
        
        # 통계 확인
        stats = db.get_statistics()
        print(f"✓ 총 지원 기록: {stats['total_applications']}개")
        
        return True
        
    except Exception as e:
        print(f"✗ 데이터베이스 오류: {str(e)}")
        return False

def test_configuration():
    """설정 테스트"""
    print("\n설정 로드 테스트...")
    try:
        config = Config()
        
        print(f"✓ 검색 키워드: {', '.join(config.keyword_list)}")
        print(f"✓ 지역: {config.location}")
        print(f"✓ 고용형태: {config.job_type}")
        print(f"✓ 일일 최대 지원: {config.max_applications_per_day}개")
        print(f"✓ 지원 간격: {config.min_delay_between_applications}-{config.max_delay_between_applications}초")
        
        # 로그인 정보 확인 (실제 값은 표시하지 않음)
        if config.username and config.password:
            print("✓ 로그인 정보 설정됨")
            return True
        else:
            print("✗ 로그인 정보 미설정")
            return False
            
    except Exception as e:
        print(f"✗ 설정 오류: {str(e)}")
        return False

def main():
    """메인 테스트 실행"""
    print("🤖 사람인 자동 지원 스크립트 기능 검증")
    print("=" * 50)
    
    tests = [
        ("웹사이트 연결", test_saramin_connectivity),
        ("설정 로드", test_configuration),
        ("검색 URL 생성", test_search_url_generation),
        ("데이터베이스", test_database_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"❌ {name} 테스트 실패")
    
    print(f"\n📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("✅ 모든 핵심 기능이 정상 작동합니다!")
        print("\n🎯 실행 준비 완료:")
        print("- 설정 파일 로드 성공")
        print("- 데이터베이스 시스템 정상")
        print("- 검색 URL 생성 기능 정상") 
        print("- 사람인 웹사이트 접근 가능")
        print("\n💡 실제 사용:")
        print("python main.py 명령으로 실제 자동 지원을 시작할 수 있습니다.")
    else:
        print("❌ 일부 기능에 문제가 있습니다.")

if __name__ == "__main__":
    main()