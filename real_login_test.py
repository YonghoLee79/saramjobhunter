#!/usr/bin/env python3
"""
실제 로그인 테스트 - 고급 봇 탐지 우회 적용
Real login test with advanced bot detection evasion
"""

import sys
import os
from datetime import datetime
from config import Config
from postgres_database import PostgresApplicationDatabase
from logger_config import setup_logger
from saramin_bot import SaraminBot

def test_real_login():
    """실제 로그인 테스트"""
    print("=" * 60)
    print("🔐 실제 사람인 로그인 테스트 (봇 탐지 우회 적용)")
    print("=" * 60)
    
    try:
        # 설정 로드
        config = Config()
        print(f"✅ 설정 로드 완료")
        print(f"📧 사용자명: {config.username}")
        print(f"🔍 검색 키워드: {', '.join(config.keyword_list)}")
        
        # 데이터베이스 연결
        database = PostgresApplicationDatabase()
        database.init_database()
        
        # 로거 설정
        logger = setup_logger("real_login_test.log", "INFO")
        
        # 봇 초기화
        bot = SaraminBot(config, database, logger)
        
        print("\n🚀 고급 봇 탐지 우회 시스템 적용 중...")
        
        # 브라우저 설정
        if bot.setup_driver():
            print("✅ 스텔스 브라우저 설정 완료")
        else:
            print("❌ 브라우저 설정 실패")
            return False
        
        print("\n🔐 사람인 로그인 시도 중...")
        
        # 실제 로그인 테스트
        login_success = bot.login()
        
        if login_success:
            print("🎉 로그인 성공!")
            print("✅ 봇 탐지 우회 시스템이 효과적으로 작동")
            
            # 간단한 페이지 이동 테스트
            try:
                print("\n📋 채용 정보 페이지 접근 테스트...")
                bot.driver.get("https://www.saramin.co.kr/zf_user/jobs/list")
                bot.random_wait(2, 4)
                
                current_url = bot.driver.current_url
                print(f"✅ 현재 페이지: {current_url}")
                
                if "jobs" in current_url.lower():
                    print("✅ 채용 페이지 접근 성공")
                    
                    # 검색 기능 테스트
                    print("\n🔍 검색 기능 테스트...")
                    search_url = bot.build_search_url("바이오")
                    print(f"🔗 생성된 검색 URL: {search_url}")
                    
                    bot.driver.get(search_url)
                    bot.random_wait(3, 5)
                    
                    if "search" in bot.driver.current_url or "list" in bot.driver.current_url:
                        print("✅ 검색 페이지 접근 성공")
                    else:
                        print("⚠️ 예상과 다른 페이지로 이동됨")
                        
                else:
                    print("⚠️ 예상과 다른 페이지")
                    
            except Exception as e:
                print(f"⚠️ 페이지 테스트 중 문제: {str(e)}")
                
        else:
            print("❌ 로그인 실패")
            print("🔧 가능한 원인:")
            print("   - 사람인 서버 일시적 문제 (HTTP 307)")
            print("   - 로그인 정보 확인 필요")
            print("   - 추가 봇 탐지 메커니즘")
        
        # 정리
        bot.close()
        print("\n✅ 테스트 완료")
        
        return login_success
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {str(e)}")
        return False

def main():
    """메인 실행"""
    print("실제 로그인 테스트를 시작합니다...")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_real_login()
    
    if success:
        print("\n🎉 로그인 테스트 성공!")
        print("💡 이제 웹 앱에서 '자동 지원 시작'을 클릭하여 실제 지원을 진행할 수 있습니다.")
    else:
        print("\n⚠️ 로그인 테스트에서 문제가 발생했습니다.")
        print("🔄 사람인 서버 상태를 확인하거나 나중에 다시 시도해보세요.")

if __name__ == "__main__":
    main()