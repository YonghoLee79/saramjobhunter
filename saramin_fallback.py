#!/usr/bin/env python3
"""
사람인 서버 문제 대응 시스템
Fallback system for Saramin server issues
"""

import time
import requests
from datetime import datetime
from postgres_database import PostgresApplicationDatabase

class SaraminServerMonitor:
    """사람인 서버 상태 모니터링 및 대응"""
    
    def __init__(self):
        self.db = PostgresApplicationDatabase()
        self.base_url = "https://www.saramin.co.kr"
        
    def check_server_status(self):
        """사람인 서버 상태 확인"""
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                return True, "서버 정상"
            else:
                return False, f"서버 오류: {response.status_code}"
        except Exception as e:
            return False, f"연결 실패: {str(e)}"
    
    def log_server_issue(self, issue_type, description):
        """서버 문제 로그 기록"""
        self.db.log_system_message(
            "WARNING", 
            f"사람인 서버 문제: {issue_type} - {description}",
            "saramin_fallback",
            "log_server_issue"
        )
    
    def schedule_retry(self, hours=2):
        """재시도 스케줄링"""
        retry_time = datetime.now().timestamp() + (hours * 3600)
        self.db.set_configuration(
            "next_retry_time", 
            str(retry_time),
            f"{hours}시간 후 자동 재시도"
        )
        print(f"{hours}시간 후 자동 재시도가 예약되었습니다.")
    
    def should_retry_now(self):
        """현재 재시도 가능 여부 확인"""
        retry_time = self.db.get_configuration("next_retry_time", "0")
        try:
            if float(retry_time) <= datetime.now().timestamp():
                return True
        except:
            pass
        return False
    
    def get_alternative_recommendations(self):
        """대안 방법 추천"""
        recommendations = [
            "1. 사람인 웹사이트에서 직접 로그인하여 상태 확인",
            "2. 다른 시간대(오전 9-11시, 오후 2-4시)에 재시도",
            "3. 네트워크 연결 상태 확인",
            "4. 사람인 공지사항에서 서버 점검 여부 확인",
            "5. 1-2시간 후 자동 재시도 대기"
        ]
        return recommendations

def handle_server_failure():
    """서버 실패 상황 처리"""
    monitor = SaraminServerMonitor()
    
    print("사람인 서버 연결 문제 감지")
    print("=" * 40)
    
    # 서버 상태 확인
    is_online, status = monitor.check_server_status()
    print(f"서버 상태: {status}")
    
    # 문제 로그 기록
    monitor.log_server_issue("로그인 실패", "내부 서버 문제 지속 발생")
    
    # 재시도 스케줄링
    monitor.schedule_retry(2)
    
    # 대안 방법 제시
    print("\n권장 대응 방법:")
    for recommendation in monitor.get_alternative_recommendations():
        print(f"  {recommendation}")
    
    print(f"\n다음 자동 재시도: 2시간 후")
    print("웹 앱은 계속 실행되며, 수동으로 재시도할 수 있습니다.")

if __name__ == "__main__":
    handle_server_failure()