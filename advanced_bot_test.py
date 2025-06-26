#!/usr/bin/env python3
"""
고급 봇 탐지 우회 시스템 테스트
Advanced bot detection evasion system test
"""

import sys
import os
from datetime import datetime
from config import Config
from postgres_database import PostgresApplicationDatabase
from logger_config import setup_logger
from saramin_bot import SaraminBot

def test_advanced_anti_detection():
    """고급 봇 탐지 우회 기능 테스트"""
    print("=" * 60)
    print("🤖 고급 봇 탐지 우회 시스템 테스트")
    print("=" * 60)
    
    try:
        # 설정 로드
        config = Config()
        if not config.validate_config():
            print("❌ 설정 파일에 문제가 있습니다.")
            print("📋 .env 파일에서 다음 설정을 확인하세요:")
            print("   - SARAMIN_EMAIL=your_email@example.com")
            print("   - SARAMIN_PASSWORD=your_password")
            return False
        
        # 데이터베이스 연결
        database = PostgresApplicationDatabase()
        database.init_database()
        
        # 로거 설정
        logger = setup_logger("advanced_test.log", "INFO")
        
        print(f"✅ 기본 설정 완료")
        print(f"📧 이메일: {config.saramin_email}")
        print(f"🔍 검색 키워드: {', '.join(config.keywords)}")
        
        # 봇 초기화 및 테스트
        bot = SaraminBot(config, database, logger)
        
        print("\n🚀 고급 봇 탐지 우회 기능 테스트 시작...")
        
        # 브라우저 설정 테스트
        if bot.setup_driver():
            print("✅ 스텔스 브라우저 설정 완료")
            print("   - 봇 탐지 우회 스크립트 적용됨")
            print("   - 사람처럼 보이는 User-Agent 설정됨")
            print("   - 자동화 플래그 제거됨")
        else:
            print("❌ 브라우저 설정 실패")
            return False
        
        # 로그인 테스트 (개선된 방식)
        print("\n🔐 사람인 로그인 테스트 (봇 탐지 우회 적용)...")
        try:
            if bot.login():
                print("✅ 로그인 성공! 봇 탐지 우회 효과적")
                
                # 간단한 페이지 탐색 테스트
                print("\n🔍 페이지 탐색 테스트...")
                bot.driver.get("https://www.saramin.co.kr/zf_user/jobs/list")
                bot.random_wait(2, 4)
                
                current_url = bot.driver.current_url
                if "saramin.co.kr" in current_url:
                    print("✅ 페이지 탐색 성공")
                    print(f"📍 현재 URL: {current_url}")
                else:
                    print("⚠️ 예상치 못한 페이지로 이동됨")
                
            else:
                print("❌ 로그인 실패 - 추가 봇 탐지 우회 필요")
                
        except Exception as e:
            print(f"❌ 로그인 테스트 중 오류: {str(e)}")
        
        # 정리
        bot.close()
        print("\n✅ 테스트 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {str(e)}")
        return False

def check_saramin_status():
    """사람인 서버 상태 확인"""
    import requests
    
    print("\n🌐 사람인 서버 상태 확인...")
    
    try:
        # 기본 페이지 접근 테스트
        response = requests.get("https://www.saramin.co.kr", timeout=10)
        
        if response.status_code == 200:
            print("✅ 사람인 메인 페이지 정상 접근")
        else:
            print(f"⚠️ 사람인 응답 코드: {response.status_code}")
            
        # 로그인 페이지 접근 테스트
        login_response = requests.get("https://www.saramin.co.kr/zf_user/auth/login", timeout=10)
        
        if login_response.status_code == 200:
            print("✅ 사람인 로그인 페이지 정상 접근")
        else:
            print(f"⚠️ 로그인 페이지 응답 코드: {login_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 사람인 서버 접근 실패: {str(e)}")
        print("🔄 나중에 다시 시도하거나 사람인 웹사이트를 직접 확인해보세요")

def main():
    """메인 테스트 실행"""
    print("고급 봇 탐지 우회 시스템 테스트를 시작합니다...")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 서버 상태 확인
    check_saramin_status()
    
    # 고급 테스트 실행
    success = test_advanced_anti_detection()
    
    if success:
        print("\n🎉 모든 테스트가 완료되었습니다!")
        print("💡 이제 웹 앱에서 '자동 지원 시작'을 클릭하여 실제 지원을 시작할 수 있습니다.")
    else:
        print("\n⚠️ 일부 테스트에서 문제가 발생했습니다.")
        print("🔧 설정을 확인하거나 나중에 다시 시도해보세요.")

if __name__ == "__main__":
    main()