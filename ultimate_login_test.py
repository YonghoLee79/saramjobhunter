#!/usr/bin/env python3
"""
최고급 사람인 로그인 테스트 - 완전한 사람 시뮬레이션
Ultimate Saramin login test with complete human simulation
"""

import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from config import Config
from logger_config import setup_logger

class UltimateSaraminTest:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger("ultimate_test.log")
        self.driver = None
        self.wait = None
        
    def setup_ultra_stealth_driver(self):
        """완전 스텔스 모드 드라이버 설정"""
        chrome_options = Options()
        
        # 기본 옵션
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript-harmony-shipping")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # 봇 탐지 우회
        chrome_options.add_experimental_option("excludeSwitches", [
            "enable-automation", 
            "enable-logging",
            "disable-default-apps",
            "disable-extensions-file-access-check",
            "disable-extensions-http-throttling"
        ])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 사용자 에이전트 (실제 사용자 에이전트)
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        
        # 언어 설정
        chrome_options.add_argument("--lang=ko-KR")
        chrome_options.add_argument("--accept-lang=ko-KR,ko,en-US,en")
        
        # 윈도우 크기 (실제 모니터 크기)
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # 실험적 설정
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "geolocation": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 2
            },
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
            "intl.accept_languages": "ko-KR,ko,en-US,en"
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            
            # 고급 자바스크립트 봇 탐지 우회
            stealth_script = """
                // 모든 webdriver 흔적 제거
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                delete navigator.__proto__.webdriver;
                
                // Chrome runtime 정보 수정
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                        {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                        {name: 'Native Client', filename: 'internal-nacl-plugin'}
                    ]
                });
                
                // 언어 설정
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['ko-KR', 'ko', 'en-US', 'en']
                });
                
                // 디바이스 정보
                Object.defineProperty(screen, 'width', {get: () => 1920});
                Object.defineProperty(screen, 'height', {get: () => 1080});
                Object.defineProperty(screen, 'availWidth', {get: () => 1920});
                Object.defineProperty(screen, 'availHeight', {get: () => 1040});
                
                // WebGL 정보
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter.call(this, parameter);
                };
                
                // User Agent 재정의
                Object.defineProperty(navigator, 'userAgent', {
                    get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
                });
                
                // Automation detection 우회
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: 'granted' }) :
                        originalQuery(parameters)
                );
                
                // Chrome detection 완전 우회
                Object.defineProperty(window, 'chrome', {
                    get: () => ({
                        app: { isInstalled: false },
                        webstore: { onInstallStageChanged: {}, onDownloadProgress: {} },
                        runtime: { onConnect: {}, onMessage: {} }
                    })
                });
                
                console.log('고급 스텔스 모드 활성화 완료');
            """
            
            self.driver.execute_script(stealth_script)
            self.logger.info("Ultra stealth mode 드라이버 설정 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"드라이버 설정 실패: {e}")
            return False
    
    def human_like_typing(self, element, text, typing_speed='normal'):
        """완전한 사람 타이핑 시뮬레이션"""
        element.clear()
        time.sleep(random.uniform(0.3, 0.8))
        
        # 타이핑 속도 설정
        if typing_speed == 'fast':
            base_delay = 0.02
            var_delay = 0.05
        elif typing_speed == 'slow':
            base_delay = 0.08
            var_delay = 0.15
        else:  # normal
            base_delay = 0.05
            var_delay = 0.1
        
        for i, char in enumerate(text):
            element.send_keys(char)
            
            # 사람의 타이핑 패턴 시뮬레이션
            if i % 3 == 0:  # 가끔 더 긴 대기
                delay = random.uniform(base_delay * 2, var_delay * 2)
            elif random.random() < 0.1:  # 10% 확률로 실수/망설임
                delay = random.uniform(var_delay, var_delay * 3)
            else:
                delay = random.uniform(base_delay, var_delay)
            
            time.sleep(delay)
    
    def human_mouse_movement(self, element):
        """사람다운 마우스 이동"""
        actions = ActionChains(self.driver)
        
        # 현재 마우스 위치에서 요소까지 자연스럽게 이동
        actions.move_to_element_with_offset(element, 
                                          random.randint(-5, 5), 
                                          random.randint(-5, 5))
        actions.pause(random.uniform(0.1, 0.3))
        actions.move_to_element(element)
        actions.pause(random.uniform(0.05, 0.15))
        actions.perform()
        
        time.sleep(random.uniform(0.2, 0.5))
    
    def natural_page_interaction(self):
        """자연스러운 페이지 상호작용"""
        # 페이지 스크롤 (사람 행동)
        scroll_actions = [
            "window.scrollTo(0, 300);",
            "window.scrollTo(0, 150);", 
            "window.scrollTo(0, 0);",
            "window.scrollBy(0, 100);",
            "window.scrollTo(0, 0);"
        ]
        
        for action in scroll_actions:
            self.driver.execute_script(action)
            time.sleep(random.uniform(0.8, 2.0))
    
    def ultimate_login_test(self):
        """최고급 로그인 테스트"""
        if not self.setup_ultra_stealth_driver():
            return False
        
        try:
            self.logger.info("=== 최고급 사람인 로그인 테스트 시작 ===")
            
            # 1단계: 자연스럽게 웹사이트 방문
            self.logger.info("1단계: 사람인 메인 페이지 방문")
            self.driver.get("https://www.saramin.co.kr")
            time.sleep(random.uniform(4, 7))
            
            # 페이지 로딩 완료 대기
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            time.sleep(random.uniform(2, 4))
            
            # 2단계: 자연스러운 페이지 탐색
            self.logger.info("2단계: 자연스러운 페이지 상호작용")
            self.natural_page_interaction()
            
            # 3단계: 로그인 페이지 이동
            self.logger.info("3단계: 로그인 페이지로 이동")
            time.sleep(random.uniform(2, 4))
            self.driver.get("https://www.saramin.co.kr/zf_user/auth/login")
            time.sleep(random.uniform(5, 8))
            
            # 페이지 로딩 완료 대기
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            time.sleep(random.uniform(3, 5))
            
            # 4단계: 로그인 필드 찾기
            self.logger.info("4단계: 로그인 필드 검색")
            
            # 아이디 필드 찾기 (모든 가능한 선택자)
            id_selectors = [
                "input[name='id']",
                "input[id='loginId']", 
                "input[placeholder*='아이디']",
                "input[type='text']",
                "input[name='email']",
                "#id", "#loginId", ".login-id"
            ]
            
            id_field = None
            for selector in id_selectors:
                try:
                    id_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if id_field.is_displayed() and id_field.is_enabled():
                        self.logger.info(f"아이디 필드 발견: {selector}")
                        break
                except:
                    continue
            
            if not id_field:
                self.logger.error("아이디 필드를 찾을 수 없습니다")
                return False
            
            # 5단계: 자연스러운 로그인 정보 입력
            self.logger.info("5단계: 로그인 정보 입력")
            
            # 아이디 입력
            self.human_mouse_movement(id_field)
            id_field.click()
            time.sleep(random.uniform(0.5, 1.2))
            self.human_like_typing(id_field, self.config.username)
            
            # 비밀번호 필드 찾기
            password_selectors = [
                "input[name='password']",
                "input[id='password']",
                "input[type='password']",
                "input[placeholder*='비밀번호']",
                "#password", ".login-password"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if password_field.is_displayed() and password_field.is_enabled():
                        self.logger.info(f"비밀번호 필드 발견: {selector}")
                        break
                except:
                    continue
            
            if not password_field:
                self.logger.error("비밀번호 필드를 찾을 수 없습니다")
                return False
            
            # 비밀번호 입력
            time.sleep(random.uniform(1, 2))
            self.human_mouse_movement(password_field)
            password_field.click()
            time.sleep(random.uniform(0.5, 1.2))
            self.human_like_typing(password_field, self.config.password, 'slow')
            
            # 6단계: 로그인 버튼 클릭
            self.logger.info("6단계: 로그인 버튼 클릭")
            time.sleep(random.uniform(2, 4))
            
            # 로그인 버튼 찾기
            login_selectors = [
                "button[type='submit']",
                ".btn_login",
                "input[type='submit']",
                "button.login",
                ".login-btn",
                "button:contains('로그인')"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    if ':contains' in selector:
                        login_button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '로그인')]")
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if login_button.is_displayed() and login_button.is_enabled():
                        self.logger.info(f"로그인 버튼 발견: {selector}")
                        break
                except:
                    continue
            
            if not login_button:
                self.logger.error("로그인 버튼을 찾을 수 없습니다")
                return False
            
            # 자연스러운 버튼 클릭
            self.human_mouse_movement(login_button)
            time.sleep(random.uniform(0.5, 1))
            login_button.click()
            
            # 7단계: 로그인 결과 확인
            self.logger.info("7단계: 로그인 결과 확인")
            time.sleep(random.uniform(5, 8))
            
            # Alert 처리
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.logger.warning(f"Alert 감지: {alert_text}")
                alert.accept()
                
                if "서버" in alert_text or "내부" in alert_text:
                    self.logger.error("서버 문제로 로그인 실패")
                    return False
                else:
                    self.logger.error(f"로그인 실패: {alert_text}")
                    return False
            except:
                # Alert가 없으면 성공
                pass
            
            # URL 확인
            current_url = self.driver.current_url
            self.logger.info(f"현재 URL: {current_url}")
            
            if "login" not in current_url.lower():
                self.logger.info("✅ 로그인 성공!")
                
                # 추가 확인
                try:
                    # 로그인 상태 확인을 위한 요소 찾기
                    user_elements = [
                        ".user_name", ".username", ".my-info", 
                        ".btn_logout", "a[href*='logout']"
                    ]
                    
                    for selector in user_elements:
                        try:
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if element.is_displayed():
                                self.logger.info(f"로그인 상태 확인됨: {selector}")
                                return True
                        except:
                            continue
                    
                    # URL로만 판단
                    self.logger.info("로그인 성공으로 판단됨 (URL 기준)")
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"로그인 상태 확인 중 오류: {e}")
                    return True
            else:
                self.logger.error("로그인 실패 - 여전히 로그인 페이지에 있음")
                return False
                
        except Exception as e:
            self.logger.error(f"로그인 테스트 중 오류: {e}")
            return False
        finally:
            try:
                if self.driver:
                    time.sleep(5)  # 결과 확인을 위한 대기
                    self.driver.quit()
            except:
                pass

def main():
    """메인 실행"""
    tester = UltimateSaraminTest()
    
    try:
        print("🚀 최고급 사람인 로그인 테스트를 시작합니다...")
        success = tester.ultimate_login_test()
        
        if success:
            print("✅ 로그인 테스트 성공!")
        else:
            print("❌ 로그인 테스트 실패")
    except Exception as e:
        print(f"❌ 설정 오류: {e}")

if __name__ == "__main__":
    main()