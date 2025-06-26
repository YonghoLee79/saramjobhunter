#!/usr/bin/env python3
"""
사람인 서버 문제 대응 시스템
Fallback system for Saramin server issues
"""

import time
import json
import logging
from datetime import datetime, timedelta
from postgres_database import PostgresApplicationDatabase

class SaraminServerMonitor:
    """사람인 서버 상태 모니터링 및 대응"""
    
    def __init__(self):
        self.db = PostgresApplicationDatabase()
        self.last_check = None
        self.consecutive_failures = 0
        self.retry_after = None
        
    def check_server_status(self):
        """사람인 서버 상태 확인"""
        try:
            import requests
            
            # 사람인 메인 페이지 상태 확인
            response = requests.get("https://www.saramin.co.kr", timeout=10)
            
            if response.status_code == 200:
                self.consecutive_failures = 0
                self.last_check = datetime.now()
                return True
            else:
                self.consecutive_failures += 1
                self.log_server_issue("HTTP_ERROR", f"Status code: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.consecutive_failures += 1
            self.log_server_issue("CONNECTION_ERROR", str(e))
            return False
            
    def log_server_issue(self, issue_type, description):
        """서버 문제 로그 기록"""
        try:
            self.db.log_system_message(
                level="ERROR",
                message=f"사람인 서버 문제: {issue_type} - {description}",
                module="saramin_fallback",
                function_name="log_server_issue"
            )
            
            # 연속 실패 횟수에 따른 대기 시간 설정
            if self.consecutive_failures >= 3:
                hours_to_wait = min(2 ** (self.consecutive_failures - 3), 8)  # 최대 8시간
                self.retry_after = datetime.now() + timedelta(hours=hours_to_wait)
                
        except Exception as e:
            logging.error(f"로그 기록 실패: {e}")
            
    def schedule_retry(self, hours=2):
        """재시도 스케줄링"""
        self.retry_after = datetime.now() + timedelta(hours=hours)
        
    def should_retry_now(self):
        """현재 재시도 가능 여부 확인"""
        if self.retry_after is None:
            return True
            
        return datetime.now() >= self.retry_after
        
    def get_alternative_recommendations(self):
        """대안 방법 추천"""
        recommendations = [
            "하이브리드 모드 사용: 직접 로그인 후 자동 지원",
            "몇 시간 후 다시 시도",
            "사람인 웹사이트에서 직접 지원",
            "다른 구직 사이트 이용 고려"
        ]
        
        return recommendations

def handle_server_failure():
    """서버 실패 상황 처리"""
    print("🔧 사람인 서버 문제 대응 시스템")
    print("=" * 50)
    
    monitor = SaraminServerMonitor()
    
    # 서버 상태 확인
    print("사람인 서버 상태를 확인하는 중...")
    server_ok = monitor.check_server_status()
    
    if server_ok:
        print("✅ 사람인 서버는 정상입니다.")
        print("문제는 다른 원인일 수 있습니다:")
        print("- 봇 탐지 시스템")
        print("- 네트워크 연결")
        print("- 로그인 정보 오류")
    else:
        print("❌ 사람인 서버에 문제가 있습니다.")
        print(f"연속 실패 횟수: {monitor.consecutive_failures}")
        
        if monitor.retry_after:
            print(f"다음 재시도 시간: {monitor.retry_after.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n📋 권장 대안:")
        for i, rec in enumerate(monitor.get_alternative_recommendations(), 1):
            print(f"{i}. {rec}")
    
    # 하이브리드 모드 안내
    print("\n🎯 하이브리드 모드 사용법:")
    print("1. python hybrid_automation.py 실행")
    print("2. 브라우저에서 직접 로그인")
    print("3. 자동 채용공고 검색 및 지원 시작")
    
    return server_ok

if __name__ == "__main__":
    handle_server_failure()