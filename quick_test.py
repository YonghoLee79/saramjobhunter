#!/usr/bin/env python3
"""
빠른 로그인 테스트
Quick login test
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import Config
import time

def quick_login_test():
    """빠른 로그인 테스트"""
    config = Config()
    
    # Chrome 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        print("브라우저 시작...")
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        print("사람인 로그인 페이지로 이동...")
        driver.get("https://www.saramin.co.kr/zf_user/auth/login")
        time.sleep(2)
        
        print("현재 URL:", driver.current_url)
        print("페이지 제목:", driver.title)
        
        # 로그인 폼 요소 확인
        try:
            id_input = wait.until(EC.presence_of_element_located((By.NAME, "id")))
            print("✓ 아이디 입력 필드 발견")
            
            password_input = driver.find_element(By.NAME, "password")
            print("✓ 비밀번호 입력 필드 발견")
            
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            print("✓ 로그인 버튼 발견")
            
            # 로그인 시도
            print("로그인 정보 입력 중...")
            id_input.clear()
            id_input.send_keys(config.username)
            
            password_input.clear()
            password_input.send_keys(config.password)
            
            time.sleep(1)
            
            print("로그인 버튼 클릭...")
            login_btn.click()
            
            # 로그인 결과 확인
            time.sleep(3)
            new_url = driver.current_url
            print("로그인 후 URL:", new_url)
            
            if "login" not in new_url:
                print("✓ 로그인 성공!")
                return True
            else:
                print("✗ 로그인 실패 - URL이 변경되지 않음")
                # 페이지 소스에서 오류 메시지 확인
                page_source = driver.page_source
                if "아이디" in page_source and "확인" in page_source:
                    print("  아이디 또는 비밀번호 오류 가능성")
                return False
                
        except Exception as e:
            print(f"✗ 로그인 폼 처리 중 오류: {str(e)}")
            return False
            
    except Exception as e:
        print(f"✗ 브라우저 오류: {str(e)}")
        return False
        
    finally:
        if driver:
            driver.quit()
            print("브라우저 종료")

if __name__ == "__main__":
    success = quick_login_test()
    if success:
        print("\n테스트 성공! 메인 스크립트를 실행할 수 있습니다.")
    else:
        print("\n로그인에 문제가 있습니다. 계정 정보를 확인해주세요.")