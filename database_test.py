#!/usr/bin/env python3
"""
PostgreSQL 데이터베이스 테스트 스크립트
Test script for PostgreSQL database functionality
"""

from postgres_database import PostgresApplicationDatabase
from datetime import datetime
import json

def test_database_operations():
    """데이터베이스 기본 작업 테스트"""
    print("PostgreSQL 데이터베이스 테스트 시작")
    print("=" * 50)
    
    db = PostgresApplicationDatabase()
    
    # 지원 기록 테스트
    print("\n1. 지원 기록 테스트")
    test_applications = [
        ("TEST001", "https://test1.com", "테스트회사1", "백엔드 개발자", "개발자"),
        ("TEST002", "https://test2.com", "테스트회사2", "프론트엔드 개발자", "개발자"),
        ("TEST003", "https://test3.com", "테스트회사3", "바이오 연구원", "바이오"),
        ("TEST004", "https://test4.com", "테스트회사4", "제약 연구원", "제약"),
    ]
    
    for job_id, url, company, title, keyword in test_applications:
        success = db.record_application(job_id, url, company, title, keyword)
        print(f"  {'✓' if success else '✗'} {company} - {title}")
    
    # 중복 지원 테스트
    print("\n2. 중복 지원 방지 테스트")
    duplicate_success = db.record_application("TEST001", "https://test1.com", "테스트회사1", "백엔드 개발자", "개발자")
    print(f"  {'✓' if not duplicate_success else '✗'} 중복 방지: {'성공' if not duplicate_success else '실패'}")
    
    # 실행 기록 테스트
    print("\n3. 실행 기록 테스트")
    today = datetime.now().strftime('%Y-%m-%d')
    keywords = ["개발자", "바이오", "제약"]
    
    success = db.record_execution(today, 4, keywords, "completed")
    print(f"  {'✓' if success else '✗'} 실행 기록 저장")
    
    # 당일 실행 확인
    already_executed = db.is_executed_today(today)
    print(f"  {'✓' if already_executed else '✗'} 당일 실행 확인: {'이미 실행됨' if already_executed else '실행 안됨'}")
    
    # 통계 조회 테스트
    print("\n4. 통계 조회 테스트")
    stats = db.get_statistics()
    print(f"  총 지원 수: {stats['total_applications']}")
    print(f"  오늘 지원 수: {stats['today_applications']}")
    print(f"  이번 주 지원 수: {stats['week_applications']}")
    print(f"  총 실행 수: {stats['total_executions']}")
    
    if stats['keyword_statistics']:
        print("  키워드별 통계:")
        for keyword, count in stats['keyword_statistics'].items():
            print(f"    {keyword}: {count}개")
    
    # 지원 이력 조회
    print("\n5. 지원 이력 조회 테스트")
    applications = db.get_application_history(days=7)
    print(f"  최근 7일 지원 기록: {len(applications)}개")
    
    for app in applications[:3]:  # 처음 3개만 표시
        print(f"    - {app['company_name']}: {app['job_title']} ({app['keyword']})")
    
    # 실행 이력 조회
    print("\n6. 실행 이력 조회 테스트")
    executions = db.get_execution_history(days=7)
    print(f"  최근 7일 실행 기록: {len(executions)}개")
    
    for exec_log in executions:
        keywords_str = ', '.join(exec_log['keywords']) if exec_log['keywords'] else '없음'
        print(f"    - {exec_log['execution_date']}: {exec_log['applications_count']}개 지원 (키워드: {keywords_str})")
    
    # 설정 테스트
    print("\n7. 설정 관리 테스트")
    test_configs = [
        ("last_execution", today, "마지막 실행 날짜"),
        ("max_applications", "10", "일일 최대 지원 수"),
        ("preferred_keywords", "바이오,제약,개발자", "선호 키워드")
    ]
    
    for key, value, desc in test_configs:
        success = db.set_configuration(key, value, desc)
        print(f"  {'✓' if success else '✗'} 설정 저장: {key}")
        
        retrieved_value = db.get_configuration(key, "기본값")
        print(f"    조회된 값: {retrieved_value}")
    
    # 시스템 로그 테스트
    print("\n8. 시스템 로그 테스트")
    log_messages = [
        ("INFO", "테스트 시작", "database_test", "test_database_operations"),
        ("WARNING", "테스트 경고", "database_test", "test_database_operations"),
        ("ERROR", "테스트 오류", "database_test", "test_database_operations")
    ]
    
    for level, message, module, func in log_messages:
        success = db.log_system_message(level, message, module, func)
        print(f"  {'✓' if success else '✗'} {level} 로그 기록")
    
    print("\n" + "=" * 50)
    print("PostgreSQL 데이터베이스 테스트 완료")
    
    return True

def test_web_app_integration():
    """웹 앱 통합 테스트"""
    print("\n웹 앱 통합 테스트")
    print("=" * 30)
    
    db = PostgresApplicationDatabase()
    
    # 웹 앱에서 사용하는 API 기능 테스트
    try:
        # 통계 API 테스트
        stats = db.get_statistics()
        print(f"✓ 통계 API: {stats['total_applications']}개 지원 기록")
        
        # 이력 API 테스트
        applications = db.get_application_history(days=30)
        executions = db.get_execution_history(days=30)
        print(f"✓ 이력 API: 지원 {len(applications)}개, 실행 {len(executions)}개")
        
        # 중복 확인 API 테스트
        is_duplicate = db.is_already_applied("TEST001")
        print(f"✓ 중복 확인 API: {'중복 있음' if is_duplicate else '중복 없음'}")
        
        # 실행 확인 API 테스트
        today = datetime.now().strftime('%Y-%m-%d')
        is_executed = db.is_executed_today(today)
        print(f"✓ 실행 확인 API: {'오늘 실행됨' if is_executed else '오늘 실행 안됨'}")
        
        return True
        
    except Exception as e:
        print(f"✗ 웹 앱 통합 테스트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # 기본 데이터베이스 작업 테스트
        basic_test_success = test_database_operations()
        
        # 웹 앱 통합 테스트
        webapp_test_success = test_web_app_integration()
        
        print(f"\n최종 결과:")
        print(f"  기본 데이터베이스 테스트: {'성공' if basic_test_success else '실패'}")
        print(f"  웹 앱 통합 테스트: {'성공' if webapp_test_success else '실패'}")
        
        if basic_test_success and webapp_test_success:
            print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
            print("PostgreSQL 데이터베이스가 정상적으로 작동하고 있습니다.")
        else:
            print("\n⚠️ 일부 테스트가 실패했습니다. 로그를 확인해주세요.")
            
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {str(e)}")
        print("데이터베이스 연결 또는 설정을 확인해주세요.")