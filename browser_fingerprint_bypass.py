#!/usr/bin/env python3
"""
브라우저 지문 완전 우회 시스템
Complete browser fingerprint bypass system
"""

import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from config import Config
from logger_config import setup_logger

class BrowserFingerprintBypass:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger("fingerprint_bypass.log")
        
    def create_undetectable_driver(self):
        """완전히 탐지 불가능한 드라이버 생성"""
        chrome_options = Options()
        
        # 기본 스텔스 옵션
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 실제 사용자처럼 보이는 설정
        chrome_options.add_argument("--disable-extensions-file-access-check")
        chrome_options.add_argument("--disable-extensions-http-throttling")
        chrome_options.add_argument("--disable-component-extensions-with-background-pages")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--autoplay-policy=user-gesture-required")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # 실제 사용자 에이전트와 언어 설정
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        chrome_options.add_argument("--lang=ko-KR")
        
        # 창 크기 랜덤화
        window_sizes = ["1920,1080", "1366,768", "1536,864", "1440,900"]
        chrome_options.add_argument(f"--window-size={random.choice(window_sizes)}")
        
        # 고급 설정
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "geolocation": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 1  # 이미지 로드 허용
            },
            "intl.accept_languages": "ko-KR,ko,en-US,en",
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # 초고급 지문 우회 스크립트
            fingerprint_bypass_script = """
                // 1. Navigator 객체 완전 재정의
                const originalNavigator = navigator;
                
                Object.defineProperty(window, 'navigator', {
                    value: new Proxy(originalNavigator, {
                        get: function(target, property) {
                            if (property === 'webdriver') {
                                return undefined;
                            }
                            if (property === 'plugins') {
                                return [
                                    {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                                    {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                                    {name: 'Native Client', filename: 'internal-nacl-plugin'},
                                    {name: 'Microsoft Edge PDF Viewer', filename: 'edge-pdf-viewer'}
                                ];
                            }
                            if (property === 'languages') {
                                return ['ko-KR', 'ko', 'en-US', 'en'];
                            }
                            if (property === 'hardwareConcurrency') {
                                return 8;
                            }
                            if (property === 'deviceMemory') {
                                return 8;
                            }
                            if (property === 'platform') {
                                return 'Win32';
                            }
                            if (property === 'userAgent') {
                                return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36';
                            }
                            return target[property];
                        }
                    }),
                    configurable: true
                });
                
                // 2. WebGL 지문 우회
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    if (parameter === 7936) return 'WebGL 1.0 (OpenGL ES 2.0 Chromium)';
                    if (parameter === 7937) return 'WebKit WebGL';
                    return getParameter.call(this, parameter);
                };
                
                // 3. Canvas 지문 우회
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(...args) {
                    const context = this.getContext('2d');
                    if (context) {
                        context.fillStyle = 'rgb(' + 
                            Math.floor(Math.random() * 256) + ',' + 
                            Math.floor(Math.random() * 256) + ',' + 
                            Math.floor(Math.random() * 256) + ')';
                        context.fillRect(0, 0, 1, 1);
                    }
                    return originalToDataURL.apply(this, args);
                };
                
                // 4. AudioContext 지문 우회
                const OriginalAudioContext = window.AudioContext || window.webkitAudioContext;
                if (OriginalAudioContext) {
                    const audioContext = new OriginalAudioContext();
                    const originalCreateOscillator = audioContext.createOscillator;
                    audioContext.createOscillator = function() {
                        const oscillator = originalCreateOscillator.call(this);
                        const originalStart = oscillator.start;
                        oscillator.start = function(when) {
                            return originalStart.call(this, when + Math.random() * 0.001);
                        };
                        return oscillator;
                    };
                }
                
                // 5. Screen 정보 우회
                Object.defineProperty(screen, 'width', {get: () => 1920});
                Object.defineProperty(screen, 'height', {get: () => 1080});
                Object.defineProperty(screen, 'availWidth', {get: () => 1920});
                Object.defineProperty(screen, 'availHeight', {get: () => 1040});
                Object.defineProperty(screen, 'colorDepth', {get: () => 24});
                Object.defineProperty(screen, 'pixelDepth', {get: () => 24});
                
                // 6. Timezone 정보 우회
                Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
                    value: function() {
                        return {
                            locale: 'ko-KR',
                            timeZone: 'Asia/Seoul',
                            calendar: 'gregory',
                            numberingSystem: 'latn'
                        };
                    }
                });
                
                // 7. Permission API 우회
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = function(parameters) {
                    return Promise.resolve({
                        state: parameters.name === 'notifications' ? 'granted' : 'prompt'
                    });
                };
                
                // 8. Chrome runtime 정보 삭제
                delete window.chrome.runtime;
                
                // 9. 자동화 감지 프로퍼티 완전 제거
                delete navigator.__proto__.webdriver;
                delete navigator.webdriver;
                
                // 10. 이벤트 리스너 조작
                const originalAddEventListener = EventTarget.prototype.addEventListener;
                EventTarget.prototype.addEventListener = function(type, listener, options) {
                    if (type === 'beforeunload' || type === 'unload') {
                        return;
                    }
                    return originalAddEventListener.call(this, type, listener, options);
                };
                
                console.log('✅ 완전한 브라우저 지문 우회 완료');
            """
            
            driver.execute_script(fingerprint_bypass_script)
            
            # 추가 스텔스 설정
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    window.chrome = {
                        app: { isInstalled: false },
                        webstore: { onInstallStageChanged: {}, onDownloadProgress: {} },
                        runtime: { onConnect: {}, onMessage: {} }
                    };
                '''
            })
            
            self.logger.info("완전 탐지 불가능한 드라이버 생성 완료")
            return driver
            
        except Exception as e:
            self.logger.error(f"드라이버 생성 실패: {e}")
            return None
    
    def human_behavior_simulation(self, driver):
        """극도로 사람다운 행동 시뮬레이션"""
        # 1. 랜덤 마우스 이동
        actions = ActionChains(driver)
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            actions.move_by_offset(x, y)
            actions.pause(random.uniform(0.1, 0.5))
        actions.perform()
        
        # 2. 스크롤 패턴
        scroll_patterns = [
            "window.scrollTo(0, 300);",
            "window.scrollTo(0, 100);", 
            "window.scrollTo(0, 500);",
            "window.scrollTo(0, 200);",
            "window.scrollTo(0, 0);"
        ]
        
        for pattern in scroll_patterns:
            driver.execute_script(pattern)
            time.sleep(random.uniform(0.5, 2.0))
        
        # 3. 페이지 상호작용
        try:
            # 페이지의 링크나 버튼에 마우스 올리기
            links = driver.find_elements(By.TAG_NAME, "a")[:3]
            for link in links:
                try:
                    actions = ActionChains(driver)
                    actions.move_to_element(link)
                    actions.pause(random.uniform(0.2, 0.8))
                    actions.perform()
                except:
                    continue
        except:
            pass
    
    def test_advanced_login(self):
        """고급 우회 로그인 테스트"""
        driver = self.create_undetectable_driver()
        if not driver:
            return False
        
        try:
            self.logger.info("=== 고급 브라우저 지문 우회 로그인 테스트 ===")
            
            # 1단계: 자연스러운 사이트 접근
            self.logger.info("사람인 메인 페이지 방문")
            driver.get("https://www.saramin.co.kr")
            time.sleep(random.uniform(5, 8))
            
            # 사람 행동 시뮬레이션
            self.human_behavior_simulation(driver)
            
            # 2단계: 로그인 페이지 이동
            self.logger.info("로그인 페이지로 이동")
            time.sleep(random.uniform(3, 5))
            driver.get("https://www.saramin.co.kr/zf_user/auth/login")
            time.sleep(random.uniform(6, 10))
            
            # 페이지 로딩 완료 대기
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(random.uniform(3, 6))
            
            # 3단계: 로그인 시도
            self.logger.info("로그인 정보 입력")
            
            # 아이디 필드 찾기
            id_field = None
            selectors = ["#loginId", "input[name='id']", "input[type='text']"]
            
            for selector in selectors:
                try:
                    id_field = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not id_field:
                self.logger.error("아이디 필드를 찾을 수 없음")
                return False
            
            # 극도로 자연스러운 입력
            id_field.click()
            time.sleep(random.uniform(0.8, 1.5))
            
            for char in self.config.username:
                id_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            # 비밀번호 필드
            time.sleep(random.uniform(1, 2))
            password_field = driver.find_element(By.CSS_SELECTOR, "#password")
            password_field.click()
            time.sleep(random.uniform(0.5, 1))
            
            for char in self.config.password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.03, 0.12))
            
            # 로그인 버튼 클릭
            time.sleep(random.uniform(2, 4))
            login_btn = driver.find_element(By.CSS_SELECTOR, ".btn_login")
            
            # 마우스 이동 후 클릭
            actions = ActionChains(driver)
            actions.move_to_element(login_btn)
            actions.pause(random.uniform(0.5, 1))
            actions.click()
            actions.perform()
            
            # 4단계: 결과 확인
            time.sleep(random.uniform(6, 10))
            
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                self.logger.warning(f"Alert: {alert_text}")
                alert.accept()
                
                if "서버" in alert_text:
                    self.logger.error("서버 문제 발생")
                    return False
                else:
                    self.logger.error(f"로그인 실패: {alert_text}")
                    return False
            except:
                pass
            
            current_url = driver.current_url
            self.logger.info(f"현재 URL: {current_url}")
            
            if "login" not in current_url.lower():
                self.logger.info("✅ 로그인 성공!")
                return True
            else:
                self.logger.error("로그인 실패")
                return False
                
        except Exception as e:
            self.logger.error(f"테스트 중 오류: {e}")
            return False
        finally:
            time.sleep(5)
            try:
                driver.quit()
            except:
                pass

def main():
    """메인 실행"""
    bypass = BrowserFingerprintBypass()
    
    print("🚀 고급 브라우저 지문 우회 테스트 시작...")
    success = bypass.test_advanced_login()
    
    if success:
        print("✅ 우회 테스트 성공!")
    else:
        print("❌ 우회 테스트 실패")

if __name__ == "__main__":
    main()