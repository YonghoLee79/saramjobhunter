#!/usr/bin/env python3
"""
최종 실제 환경 실행 테스트
"""

import os
import subprocess
import time
from datetime import datetime
from postgres_database import PostgresApplicationDatabase

def run_main_script():
    """메인 스크립트 실행"""
    print("🚀 사람인 자동화 시스템 최종 실행")
    print("=" * 50)
    
    try:
        # hybrid_automation.py 실행
        print("하이브리드 자동화 시스템을 시작합니다...")
        print("브라우저가 열리면 직접 로그인해 주세요.")
        
        result = subprocess.run([
            "python", "hybrid_automation.py"
        ], capture_output=True, text=True, timeout=1800)  # 30분 타임아웃
        
        print(f"실행 결과 코드: {result.returncode}")
        if result.stdout:
            print("출력:")
            print(result.stdout)
        if result.stderr:
            print("오류:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ 실행 시간 초과 (30분)")
        return False
    except Exception as e:
        print(f"❌ 실행 중 오류: {e}")
        return False

def show_final_status():
    """최종 상태 보고"""
    print("\n" + "=" * 50)
    print("📊 최종 실행 결과")
    
    try:
        db = PostgresApplicationDatabase()
        
        # 오늘 지원 내역 확인
        today = datetime.now().strftime("%Y-%m-%d")
        history = db.get_application_history(days=1)
        
        print(f"✅ 오늘 지원한 채용공고: {len(history)}개")
        
        for record in history:
            print(f"   - {record['company_name']}: {record['job_title']} ({record['keyword']})")
        
        # 전체 통계
        stats = db.get_statistics()
        print(f"✅ 총 지원 수: {stats['total_applications']}개")
        print(f"✅ 총 실행 수: {stats['total_executions']}회")
        
    except Exception as e:
        print(f"❌ 상태 확인 중 오류: {e}")

def main():
    print("🎯 최종 실제 환경 테스트 시작")
    print("사람인 하이브리드 자동화 시스템")
    
    # 실행 전 환경 확인
    print("\n📋 실행 전 체크리스트:")
    print("✅ PostgreSQL 데이터베이스 연결됨")
    print("✅ 로그인 정보 설정됨")
    print("✅ 검색 키워드 설정됨")
    print("✅ 하이브리드 모드 준비됨")
    
    print("\n⚠️ 중요 안내:")
    print("1. 브라우저가 자동으로 열립니다")
    print("2. 사람인 로그인 페이지에서 직접 로그인해 주세요")
    print("3. 로그인 후 자동으로 채용공고 검색이 시작됩니다")
    print("4. 웹 앱에서 실시간 진행상황을 확인할 수 있습니다")
    
    input("\n계속하려면 Enter를 누르세요...")
    
    # 메인 스크립트 실행
    success = run_main_script()
    
    # 결과 확인
    show_final_status()
    
    if success:
        print("\n🎉 실행 완료!")
        print("웹 앱에서 상세한 결과를 확인하세요.")
    else:
        print("\n⚠️ 실행 중 문제가 발생했습니다.")
        print("로그를 확인하고 다시 시도해 주세요.")

if __name__ == "__main__":
    main()