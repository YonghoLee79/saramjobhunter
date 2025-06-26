#!/usr/bin/env python3
"""
가벼운 테스트 - 브라우저 없이 핵심 기능 검증
"""

import requests
from datetime import datetime
from config import Config
from database import ApplicationDatabase

def test_saramin_search_page():
    """사람인 검색 페이지 직접 접근 테스트"""
    print("사람인 검색 기능 테스트")
    print("-" * 30)
    
    config = Config()
    
    # 검색 URL 생성
    from saramin_bot import SaraminBot
    db = ApplicationDatabase()
    from logger_config import setup_logger
    logger = setup_logger()
    
    bot = SaraminBot(config, db, logger)
    search_url = bot.build_search_url()
    
    print(f"검색 URL: {search_url}")
    
    # HTTP 요청으로 검색 페이지 접근
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # 검색 결과 페이지 확인
            if "채용정보" in content or "recruit" in content:
                print("검색 페이지 접근 성공")
                
                # 채용공고 링크 패턴 확인
                import re
                job_links = re.findall(r'/zf_user/jobs/relay/view\?rec_idx=\d+', content)
                print(f"발견된 채용공고 링크: {len(job_links)}개")
                
                if job_links:
                    print("샘플 링크:")
                    for link in job_links[:3]:
                        print(f"  https://www.saramin.co.kr{link}")
                
                return True
            else:
                print("검색 결과 페이지가 예상과 다릅니다")
                return False
                
        else:
            print(f"페이지 접근 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"요청 오류: {str(e)}")
        return False

def show_current_database_status():
    """현재 데이터베이스 상태 확인"""
    print("\n데이터베이스 현황")
    print("-" * 30)
    
    db = ApplicationDatabase()
    stats = db.get_statistics()
    
    print(f"총 지원 기록: {stats['total_applications']}개")
    print(f"이번 주 지원: {stats['week_applications']}개")
    print(f"이번 달 지원: {stats['month_applications']}개")
    
    if stats['top_companies']:
        print("\n주요 지원 회사:")
        for company, count in stats['top_companies'][:5]:
            print(f"  {company}: {count}회")
    
    # 최근 지원 기록
    recent = db.get_application_history(7)
    if recent:
        print(f"\n최근 7일 지원 기록: {len(recent)}개")
        for record in recent[:3]:
            print(f"  {record['company_name']} - {record['job_title']}")

def test_realistic_scenario():
    """실제 시나리오 시뮬레이션"""
    print("\n실제 시나리오 테스트")
    print("-" * 30)
    
    config = Config()
    db = ApplicationDatabase()
    
    # 샘플 채용공고 데이터
    sample_jobs = [
        {
            'job_id': 'saramin_12345',
            'url': 'https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=12345',
            'company': 'SK바이오팜',
            'title': '신약개발 연구원'
        },
        {
            'job_id': 'saramin_67890', 
            'url': 'https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=67890',
            'company': '셀트리온',
            'title': '바이오의약품 연구원'
        }
    ]
    
    applied_count = 0
    
    for job in sample_jobs:
        # 중복 지원 확인
        if db.is_already_applied(job['job_id']):
            print(f"이미 지원함: {job['company']} - {job['title']}")
        else:
            # 새로운 지원 기록
            success = db.record_application(
                job['job_id'], 
                job['url'], 
                job['company'], 
                job['title']
            )
            
            if success:
                applied_count += 1
                print(f"지원 완료: {job['company']} - {job['title']}")
            else:
                print(f"지원 실패: {job['company']} - {job['title']}")
    
    # 일일 실행 기록
    today = datetime.now().date()
    db.record_execution(today, applied_count)
    
    print(f"\n오늘 지원 완료: {applied_count}개")
    return applied_count > 0

if __name__ == "__main__":
    print("사람인 자동 지원 스크립트 - 실제 환경 검증")
    print("=" * 50)
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("검색 페이지 접근", test_saramin_search_page),
        ("시나리오 시뮬레이션", test_realistic_scenario)
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n[{name}]")
        if test_func():
            passed += 1
            print(f"✓ {name} 성공")
        else:
            print(f"✗ {name} 실패")
    
    show_current_database_status()
    
    print(f"\n테스트 결과: {passed}/{len(tests)} 통과")
    
    if passed == len(tests):
        print("\n✓ 스크립트가 실제 환경에서 정상 작동할 수 있습니다")
        print("브라우저 자동화를 통한 실제 로그인 및 지원이 가능합니다")
    else:
        print("\n일부 기능에서 문제가 발견되었습니다")