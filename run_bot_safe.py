#!/usr/bin/env python3
"""
안전한 봇 실행 스크립트 - 시간 제한과 예외 처리
"""

import sys
import signal
import subprocess
from datetime import datetime

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("실행 시간 초과")

def run_bot_with_timeout(timeout_seconds=300):
    """타임아웃과 함께 봇 실행"""
    print(f"사람인 봇을 {timeout_seconds}초 제한으로 실행합니다...")
    print("=" * 50)
    
    # 타임아웃 설정
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        # main.py 실행
        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        
        signal.alarm(0)  # 타임아웃 해제
        
        print("실행 결과:")
        print("-" * 30)
        print("표준 출력:")
        print(result.stdout)
        
        if result.stderr:
            print("오류 출력:")
            print(result.stderr)
        
        print(f"종료 코드: {result.returncode}")
        
        if result.returncode == 0:
            print("✓ 봇 실행 완료")
        else:
            print("✗ 봇 실행 중 오류 발생")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⚠ 실행 시간 초과로 중단됨")
        return False
    except TimeoutError:
        print("⚠ 시스템 타임아웃으로 중단됨")
        return False
    except Exception as e:
        print(f"✗ 실행 중 예외 발생: {str(e)}")
        return False
    finally:
        signal.alarm(0)  # 안전하게 타임아웃 해제

def check_logs():
    """로그 파일 확인"""
    print("\n로그 파일 확인:")
    print("-" * 30)
    
    try:
        with open("saramin_bot.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            # 최근 10줄만 출력
            recent_lines = lines[-10:] if len(lines) > 10 else lines
            for line in recent_lines:
                print(line.strip())
    except FileNotFoundError:
        print("로그 파일이 아직 생성되지 않았습니다.")
    except Exception as e:
        print(f"로그 읽기 오류: {str(e)}")

if __name__ == "__main__":
    print(f"시작 시간: {datetime.now()}")
    
    # 봇 실행
    success = run_bot_with_timeout(180)  # 3분 제한
    
    # 로그 확인
    check_logs()
    
    print(f"\n완료 시간: {datetime.now()}")
    
    if success:
        print("\n✅ 사람인 자동 지원 스크립트가 성공적으로 실행되었습니다!")
    else:
        print("\n⚠ 스크립트 실행이 완전히 완료되지 않았습니다.")
        print("로그를 확인하여 구체적인 상황을 파악할 수 있습니다.")