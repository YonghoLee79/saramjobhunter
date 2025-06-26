#!/usr/bin/env python3
"""
다중 키워드 검색 기능 테스트
"""

from config import Config
from database import ApplicationDatabase

def test_multi_keyword_config():
    """다중 키워드 설정 테스트"""
    print("다중 키워드 설정 테스트")
    print("=" * 40)
    
    config = Config()
    
    print(f"설정된 키워드 문자열: {config.search_keywords}")
    print(f"파싱된 키워드 목록: {config.keyword_list}")
    print(f"키워드 개수: {len(config.keyword_list)}")
    
    for i, keyword in enumerate(config.keyword_list, 1):
        print(f"  {i}. {keyword}")
    
    return len(config.keyword_list) > 0

def test_search_url_generation():
    """각 키워드별 검색 URL 생성 테스트"""
    print("\n키워드별 검색 URL 생성 테스트")
    print("=" * 40)
    
    from saramin_bot import SaraminBot
    from logger_config import setup_logger
    
    config = Config()
    db = ApplicationDatabase()
    logger = setup_logger()
    
    bot = SaraminBot(config, db, logger)
    
    for keyword in config.keyword_list:
        search_url = bot.build_search_url(keyword)
        print(f"\n키워드: {keyword}")
        print(f"URL: {search_url}")
        
        # URL에 키워드가 포함되어 있는지 확인
        import urllib.parse
        encoded_keyword = urllib.parse.quote(keyword)
        if encoded_keyword in search_url:
            print(f"✓ 키워드 정상 포함")
        else:
            print(f"✗ 키워드 누락")

def simulate_multi_keyword_search():
    """다중 키워드 검색 시뮬레이션"""
    print("\n다중 키워드 검색 시뮬레이션")
    print("=" * 40)
    
    config = Config()
    db = ApplicationDatabase()
    
    # 키워드별 샘플 검색 결과
    sample_results = {
        "바이오": [
            {"company": "삼성바이오로직스", "title": "생물의약품 연구원"},
            {"company": "셀트리온", "title": "항체의약품 개발자"}
        ],
        "생명공학": [
            {"company": "메디톡스", "title": "생명공학 연구원"},
            {"company": "한국생명공학연구원", "title": "연구원"}
        ],
        "제약": [
            {"company": "한미약품", "title": "신약개발 연구원"},
            {"company": "유한양행", "title": "의약품 연구원"}
        ],
        "의료기기": [
            {"company": "메디아나", "title": "의료기기 개발자"},
            {"company": "루닛", "title": "AI 의료영상 분석가"}
        ]
    }
    
    total_applied = 0
    
    for keyword in config.keyword_list:
        if keyword in sample_results:
            keyword_count = 0
            print(f"\n키워드 '{keyword}' 검색:")
            
            for job in sample_results[keyword]:
                job_id = f"{keyword}_{job['company']}_{hash(job['title']) % 1000}"
                
                if not db.is_already_applied(job_id):
                    success = db.record_application(
                        job_id,
                        f"https://www.saramin.co.kr/job/{job_id}",
                        job['company'],
                        job['title']
                    )
                    
                    if success:
                        keyword_count += 1
                        total_applied += 1
                        print(f"  ✓ 지원: {job['company']} - {job['title']}")
                    else:
                        print(f"  ✗ 지원 실패: {job['company']} - {job['title']}")
                else:
                    print(f"  ⚠ 이미 지원: {job['company']} - {job['title']}")
            
            print(f"  키워드 '{keyword}' 결과: {keyword_count}개 지원")
        else:
            print(f"\n키워드 '{keyword}': 샘플 데이터 없음")
    
    print(f"\n총 지원 완료: {total_applied}개")
    return total_applied

def show_keyword_management_guide():
    """키워드 관리 가이드"""
    print("\n키워드 관리 가이드")
    print("=" * 40)
    
    print("1. .env 파일에서 SEARCH_KEYWORDS 설정:")
    print("   SEARCH_KEYWORDS=바이오,생명공학,제약,의료기기,생명과학")
    
    print("\n2. 키워드 추가 예시:")
    print("   SEARCH_KEYWORDS=바이오,제약,의료,연구원,개발자,엔지니어")
    
    print("\n3. 주의사항:")
    print("   - 쉼표(,)로 키워드를 구분하세요")
    print("   - 공백은 자동으로 제거됩니다")
    print("   - 각 키워드별로 별도 검색이 실행됩니다")
    print("   - 키워드 순서대로 검색합니다")
    
    print("\n4. 추천 키워드 조합:")
    print("   생명과학 분야: 바이오,생명공학,제약,의료기기,생명과학")
    print("   IT 분야: 개발자,프로그래머,소프트웨어,웹개발,앱개발")
    print("   마케팅 분야: 마케팅,광고,브랜딩,디지털마케팅,콘텐츠")

if __name__ == "__main__":
    print("사람인 다중 키워드 검색 기능 테스트")
    print("=" * 50)
    
    # 테스트 실행
    tests = [
        ("키워드 설정", test_multi_keyword_config),
        ("URL 생성", test_search_url_generation),
        ("검색 시뮬레이션", simulate_multi_keyword_search)
    ]
    
    passed = 0
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {name} 성공")
            else:
                print(f"✗ {name} 실패")
        except Exception as e:
            print(f"✗ {name} 오류: {str(e)}")
    
    print(f"\n테스트 결과: {passed}/{len(tests)} 통과")
    
    # 사용법 가이드
    show_keyword_management_guide()