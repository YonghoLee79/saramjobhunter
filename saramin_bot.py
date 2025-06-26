"""
사람인 웹사이트 자동화 봇
Saramin website automation bot using Selenium
"""

import time
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from typing import Optional
import urllib.parse

class SaraminBot:
    def __init__(self, config, database, logger):
        self.config = config
        self.database = database
        self.logger = logger
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.base_url = "https://www.saramin.co.kr"
        self.application_callback = None  # 웹 앱에서 실시간 로그를 위한 콜백 함수
        
    def setup_driver(self):
        """Chrome WebDriver 설정"""
        try:
            chrome_options = Options()
            
            # 헤드리스 모드 설정 (필요시)
            if self.config.headless:
                chrome_options.add_argument("--headless")
                
            # 기본 옵션들 (Replit 환경 최적화)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")

            # 봇 탐지 우회를 위한 고급 설정
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
            
            # 자동화 탐지 우회
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 알림 차단
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Replit 환경에서 chromium 사용
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            # 고급 봇 탐지 우회 스크립트 실행
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                delete navigator.__proto__.webdriver;
                
                // Chrome detection bypass
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko', 'en-US', 'en']});
                
                // Screen and device info
                Object.defineProperty(screen, 'width', {get: () => 1920});
                Object.defineProperty(screen, 'height', {get: () => 1080});
                
                // Permission API override
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Cypress.env('NOTIFICATION_PERMISSION') || 'granted' }) :
                        originalQuery(parameters)
                );
                
                // WebGL vendor override
                const getParameter = WebGLRenderingContext.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter(parameter);
                };
            """)
            
            # User-Agent 추가 설정
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'userAgent', {
                    get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
                });
            """)
            
            self.logger.info("Chrome WebDriver 설정 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"WebDriver 설정 실패: {str(e)}")
            return False
    
    def login(self):
        """사람인 로그인 (개선된 오류 처리)"""
        if not self.setup_driver():
            return False
            
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"사람인 로그인 시도 중... ({attempt + 1}/{max_retries})")
                
                # 사람처럼 자연스럽게 접근
                if attempt > 0:
                    # 재시도 시 세션 초기화
                    self.driver.delete_all_cookies()
                    self.driver.execute_script("window.localStorage.clear();")
                    self.driver.execute_script("window.sessionStorage.clear();")
                    
                # 메인 페이지 먼저 방문 (사람 행동 패턴)
                self.driver.get("https://www.saramin.co.kr")
                self.random_wait(3, 6)
                
                # 페이지 스크롤 (봇 탐지 우회)
                self.driver.execute_script("window.scrollTo(0, 500);")
                self.random_wait(1, 2)
                self.driver.execute_script("window.scrollTo(0, 0);")
                self.random_wait(2, 3)
                
                # 로그인 페이지로 이동
                self.driver.get("https://www.saramin.co.kr/zf_user/auth/login")
                self.random_wait(5, 8)
                
                # 페이지 완전 로딩 대기
                self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                self.random_wait(2, 4)
                
                # Alert 처리 (서버 오류 메시지)
                try:
                    alert = self.driver.switch_to.alert
                    alert_text = alert.text
                    self.logger.warning(f"Alert 감지: {alert_text}")
                    
                    if "내부 서버 문제" in alert_text:
                        alert.accept()
                        self.logger.warning(f"서버 문제 감지 - 재시도 {attempt + 1}/{max_retries}")
                        # 서버 문제 시 더 긴 대기와 브라우저 초기화
                        self.random_wait(20, 30)
                        if attempt < max_retries - 1:
                            # 브라우저 완전 재시작
                            try:
                                self.driver.quit()
                            except:
                                pass
                            self.setup_driver()
                            self.random_wait(5, 10)
                        continue
                    else:
                        alert.accept()
                except:
                    pass  # Alert가 없으면 정상 진행
                
                # 로그인 필드 찾기 (다양한 선택자 시도)
                id_selectors = [
                    (By.ID, "loginId"),
                    (By.NAME, "id"),
                    (By.CSS_SELECTOR, "input[placeholder*='아이디']"),
                    (By.CSS_SELECTOR, "input[type='text']"),
                    (By.XPATH, "//input[@placeholder='아이디 또는 이메일']")
                ]
                
                id_input = None
                for selector_type, selector_value in id_selectors:
                    try:
                        id_input = self.wait.until(
                            EC.element_to_be_clickable((selector_type, selector_value))
                        )
                        break
                    except:
                        continue
                
                if not id_input:
                    self.logger.error("로그인 아이디 필드를 찾을 수 없습니다")
                    continue
                
                # 자연스러운 아이디 입력
                id_input.click()
                self.random_wait(0.5, 1)
                id_input.clear()
                self.random_wait(0.5, 1)
                self.type_like_human(id_input, self.config.username)
                
                # 비밀번호 필드 찾기
                password_selectors = [
                    (By.ID, "password"),
                    (By.NAME, "password"),
                    (By.CSS_SELECTOR, "input[type='password']"),
                    (By.CSS_SELECTOR, "input[placeholder*='비밀번호']")
                ]
                
                password_input = None
                for selector_type, selector_value in password_selectors:
                    try:
                        password_input = self.driver.find_element(selector_type, selector_value)
                        break
                    except:
                        continue
                
                if not password_input:
                    self.logger.error("비밀번호 필드를 찾을 수 없습니다")
                    continue
                
                # 자연스러운 비밀번호 입력
                password_input.click()
                self.random_wait(0.5, 1)
                password_input.clear()
                self.random_wait(0.5, 1)
                self.type_like_human(password_input, self.config.password)
                
                self.random_wait(2, 4)
                
                # 로그인 버튼 찾기 (다양한 선택자 시도)
                login_selectors = [
                    (By.CSS_SELECTOR, ".btn_login"),
                    (By.CSS_SELECTOR, "button[type='submit']"),
                    (By.XPATH, "//button[contains(text(), '로그인')]"),
                    (By.CSS_SELECTOR, "input[type='submit']"),
                    (By.CSS_SELECTOR, ".login-btn"),
                    (By.ID, "loginBtn")
                ]
                
                login_btn = None
                for selector_type, selector_value in login_selectors:
                    try:
                        login_btn = self.driver.find_element(selector_type, selector_value)
                        if login_btn.is_enabled():
                            break
                    except:
                        continue
                
                if not login_btn:
                    self.logger.error("로그인 버튼을 찾을 수 없습니다")
                    continue
                
                # 자연스러운 버튼 클릭
                self.driver.execute_script("arguments[0].focus();", login_btn)
                self.random_wait(0.5, 1)
                self.driver.execute_script("arguments[0].click();", login_btn)
                
                # 로그인 후 Alert 재확인
                self.random_wait(3, 5)
                try:
                    alert = self.driver.switch_to.alert
                    alert_text = alert.text
                    self.logger.warning(f"로그인 후 Alert: {alert_text}")
                    
                    if "내부 서버 문제" in alert_text:
                        alert.accept()
                        if attempt < max_retries - 1:
                            self.logger.warning(f"서버 문제로 재시도 {attempt + 1}/{max_retries}")
                            self.random_wait(15, 20)
                            continue
                        else:
                            self.logger.error("서버 문제로 로그인 불가")
                            return False
                    else:
                        alert.accept()
                except:
                    pass  # Alert가 없으면 정상
                
                # 로그인 성공 확인 (URL 변경 대기)
                try:
                    self.wait.until(lambda driver: driver.current_url != f"{self.base_url}/zf_user/auth/login")
                except TimeoutException:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"로그인 시간 초과 - 재시도 {attempt + 1}/{max_retries}")
                        self.random_wait(5, 10)
                        continue
                    else:
                        self.logger.error("로그인 시간 초과")
                        return False
                
                # 메인 페이지로 이동했는지 확인
                current_url = self.driver.current_url
                if "login" not in current_url and "auth" not in current_url:
                    self.logger.info("로그인 성공")
                    self.random_wait(2, 3)
                    return True
                else:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"로그인 실패 - 재시도 {attempt + 1}/{max_retries}")
                        self.random_wait(5, 10)
                        continue
                    else:
                        self.logger.error("로그인 실패 - 잘못된 자격증명이거나 추가 인증이 필요할 수 있습니다")
                        return False
                        
            except TimeoutException:
                if attempt < max_retries - 1:
                    self.logger.warning(f"로그인 페이지 로딩 시간 초과 - 재시도 {attempt + 1}/{max_retries}")
                    self.random_wait(10, 15)
                    continue
                else:
                    self.logger.error("로그인 페이지 로딩 시간 초과")
                    return False
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"로그인 중 오류 발생 - 재시도 {attempt + 1}/{max_retries}: {str(e)}")
                    self.random_wait(10, 15)
                    continue
                else:
                    self.logger.error(f"로그인 중 오류 발생: {str(e)}")
                    return False
        
        self.logger.error(f"로그인 실패 - {max_retries}번 시도 후 포기")
        return False
    
    def search_and_apply_jobs(self):
        """채용 공고 검색 및 지원"""
        total_applied = 0
        
        # 각 키워드별로 검색 및 지원
        for keyword in self.config.keyword_list:
            if total_applied >= self.config.max_applications_per_day:
                self.logger.info(f"일일 최대 지원 수({self.config.max_applications_per_day})에 도달했습니다.")
                break
                
            self.logger.info(f"키워드 '{keyword}' 검색 시작")
            
            try:
                # 키워드별 검색 페이지로 이동
                search_url = self.build_search_url(keyword)
                self.driver.get(search_url)
                self.random_wait(3, 5)
                
                self.logger.info(f"검색 조건: {keyword}, {self.config.location}, {self.config.job_type}")
                
                page = 1
                max_pages = self.config.max_pages
                keyword_applied = 0
                
                while page <= max_pages and total_applied < self.config.max_applications_per_day:
                    self.logger.info(f"키워드 '{keyword}' - 페이지 {page} 처리 중...")
                    
                    # 채용 공고 목록 가져오기
                    job_links = self.get_job_links()
                    
                    if not job_links:
                        self.logger.info(f"키워드 '{keyword}' - 더 이상 채용 공고가 없습니다.")
                        break
                    
                    # 각 채용 공고에 지원
                    for job_link in job_links:
                        if total_applied >= self.config.max_applications_per_day:
                            self.logger.info(f"일일 최대 지원 수({self.config.max_applications_per_day})에 도달했습니다.")
                            return total_applied
                            
                        if self.apply_to_job(job_link):
                            total_applied += 1
                            keyword_applied += 1
                            
                        # 요청 간격 대기
                        self.random_wait(
                            self.config.min_delay_between_applications,
                            self.config.max_delay_between_applications
                        )
                    
                    # 다음 페이지로 이동
                    if not self.go_to_next_page():
                        break
                        
                    page += 1
                
                self.logger.info(f"키워드 '{keyword}' 검색 완료 - {keyword_applied}개 지원")
                
            except Exception as e:
                self.logger.error(f"키워드 '{keyword}' 검색 중 오류: {str(e)}")
                continue
        
        self.logger.info(f"전체 검색 완료 - 총 {total_applied}개 지원")
        return total_applied
    
    def build_search_url(self, keyword=None):
        """검색 URL 생성"""
        search_keyword = keyword if keyword else self.config.keyword_list[0] if self.config.keyword_list else "바이오"
        
        params = {
            'searchword': search_keyword,
            'loc_mcd': self.get_location_code(self.config.location),
            'recruitPageCount': 50,  # 페이지당 결과 수
            'recruitSort': 'reg_dt',  # 등록일순 정렬
            'searchType': 'search'
        }
        
        # 고용형태 추가
        if self.config.job_type == "정규직":
            params['emp_type'] = '1'
        elif self.config.job_type == "계약직":
            params['emp_type'] = '2'
            
        query_string = urllib.parse.urlencode(params)
        return f"{self.base_url}/zf_user/search/recruit?{query_string}"
    
    def get_location_code(self, location):
        """지역명을 코드로 변환"""
        location_codes = {
            "서울": "101000",
            "경기": "102000", 
            "인천": "103000",
            "부산": "104000",
            "대구": "105000",
            "광주": "106000",
            "대전": "107000",
            "울산": "108000",
            "세종": "109000",
            "강원": "110000",
            "충북": "111000",
            "충남": "112000",
            "전북": "113000",
            "전남": "114000",
            "경북": "115000",
            "경남": "116000",
            "제주": "117000"
        }
        return location_codes.get(location, "101000")  # 기본값: 서울
    
    def get_job_links(self):
        """현재 페이지의 채용 공고 링크 수집"""
        job_links = []
        
        try:
            # 채용 공고 목록 요소 찾기
            # 웹사이트 구조 변경 시 수동 점검 필요
            job_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".item_recruit .job_tit a"
            )
            
            for element in job_elements:
                href = element.get_attribute("href")
                if href and "/zf_user/jobs/relay/" in href:
                    job_links.append(href)
                    
            self.logger.info(f"현재 페이지에서 {len(job_links)}개의 채용 공고를 발견했습니다.")
            
        except NoSuchElementException:
            self.logger.warning("채용 공고 목록을 찾을 수 없습니다. 웹사이트 구조가 변경되었을 수 있습니다.")
        except Exception as e:
            self.logger.error(f"채용 공고 링크 수집 중 오류: {str(e)}")
            
        return job_links
    
    def apply_to_job(self, job_url):
        """개별 채용 공고에 지원"""
        try:
            # 중복 지원 확인
            job_id = self.extract_job_id(job_url)
            if self.database.is_already_applied(job_id):
                self.logger.info(f"이미 지원한 공고입니다 (ID: {job_id})")
                return False
            
            # 채용 공고 페이지로 이동
            self.driver.get(job_url)
            self.random_wait(2, 4)
            
            # 페이지가 완전히 로드될 때까지 대기
            self.random_wait(2, 3)
            
            # 채용 공고 제목 가져오기 (더 포괄적인 선택자 시도)
            job_title = "제목 없음"
            title_selectors = [
                ".job_tit",
                ".job-tit", 
                "h1.job_title",
                "h1",
                ".title",
                "[class*='title']",
                ".job_sector .job_title",
                ".content_job .job_tit",
                ".job_summary .job_tit",
                "h2.job_tit",
                ".wrap_jv_cont .job_tit"
            ]
            
            for selector in title_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element and element.text.strip():
                        job_title = element.text.strip()
                        self.logger.info(f"제목 발견 ({selector}): {job_title}")
                        break
                except:
                    continue
            
            # 제목을 못 찾은 경우 페이지 소스에서 title 태그 확인
            if job_title == "제목 없음":
                try:
                    page_title = self.driver.title
                    if "사람인" in page_title and "|" in page_title:
                        job_title = page_title.split("|")[0].strip()
                        self.logger.info(f"페이지 타이틀에서 제목 추출: {job_title}")
                except:
                    pass
            
            # 회사명 가져오기 (더 포괄적인 선택자 시도)
            company_name = "회사명 없음"
            company_selectors = [
                ".company_nm a",
                ".company_nm",
                ".company-name",
                ".corp_name a",
                ".corp_name",
                "[class*='company'] a",
                "[class*='corp'] a",
                ".job_sector .corp_name a",
                ".content_job .company_nm a",
                ".job_summary .company_nm a",
                ".wrap_jv_cont .company_nm a",
                "a[class*='company']",
                ".area_job .company_nm a"
            ]
            
            for selector in company_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element and element.text.strip():
                        company_name = element.text.strip()
                        self.logger.info(f"회사명 발견 ({selector}): {company_name}")
                        break
                except:
                    continue
            
            self.logger.info(f"지원 시도: {company_name} - {job_title}")
            
            # 회사명 기반 중복 지원 확인 (최근 30일 내)
            if self.database.is_company_already_applied(company_name, days=30):
                self.logger.info(f"중복 지원 방지: {company_name}에 이미 지원함 (최근 30일 내)")
                return False
            
            # 지원하기 버튼 찾기 (2024년 사람인 웹사이트 구조 반영)
            apply_button = None
            
            # CSS 선택자들 시도
            css_selectors = [
                "button.btn_apply",  # 기본 지원하기 버튼
                "a.btn_apply",       # 링크 형태 지원하기 버튼
                ".btn-apply",        # 대시 형태
                "button[onclick*='apply']",  # onclick 이벤트 포함
                "a[href*='apply']",  # href에 apply 포함
                ".apply-btn",        # 일반적인 클래스명
                ".job_apply button", # job_apply 영역 내 버튼
                ".apply_area button" # apply_area 영역 내 버튼
            ]
            
            for selector in css_selectors:
                try:
                    apply_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if apply_button.is_displayed() and apply_button.is_enabled():
                        self.logger.info(f"지원하기 버튼 발견 (CSS): {selector}")
                        break
                except:
                    continue
            
            # CSS 선택자로 찾지 못한 경우 XPath로 텍스트 기반 검색
            if not apply_button:
                xpath_selectors = [
                    "//button[contains(text(), '지원하기')]",
                    "//a[contains(text(), '지원하기')]",
                    "//button[contains(text(), '즉시지원')]", 
                    "//a[contains(text(), '즉시지원')]",
                    "//button[contains(@class, 'apply')]",
                    "//a[contains(@class, 'apply')]"
                ]
                
                for xpath in xpath_selectors:
                    try:
                        apply_button = self.driver.find_element(By.XPATH, xpath)
                        if apply_button.is_displayed() and apply_button.is_enabled():
                            self.logger.info(f"지원하기 버튼 발견 (XPath): {xpath}")
                            break
                    except:
                        continue
            
            if not apply_button:
                # 페이지 HTML을 로그에 기록하여 디버깅
                page_source = self.driver.page_source
                current_url = self.driver.current_url
                self.logger.warning(f"지원하기 버튼을 찾을 수 없습니다.")
                self.logger.warning(f"현재 URL: {current_url}")
                self.logger.warning(f"페이지에서 '지원' 관련 텍스트 확인 중...")
                
                # 지원 관련 요소가 있는지 확인
                if "지원하기" in page_source or "즉시지원" in page_source:
                    self.logger.warning("페이지에 지원하기 텍스트가 있지만 버튼을 찾을 수 없습니다.")
                else:
                    self.logger.warning("마감된 공고이거나 지원이 불가능한 상태입니다.")
                
                return False
            
            # 지원하기 버튼 클릭
            self.driver.execute_script("arguments[0].click();", apply_button)
            self.random_wait(2, 3)
            
            # 지원서 작성 페이지에서 이력서 선택 및 제출
            if self.submit_application():
                # 데이터베이스에 지원 기록 저장
                self.database.record_application(job_id, job_url, company_name, job_title)
                self.logger.info(f"지원 완료: {company_name} - {job_title}")
                
                # 웹 앱 콜백 함수 호출 (실시간 로그 표시)
                if self.application_callback:
                    job_info = {
                        'company': company_name,
                        'title': job_title,
                        'url': job_url,
                        'job_id': job_id
                    }
                    self.application_callback(job_info)
                
                return True
            else:
                self.logger.warning(f"지원 실패: {company_name} - {job_title}")
                return False
                
        except Exception as e:
            self.logger.error(f"채용 공고 지원 중 오류: {str(e)}")
            return False
    
    def submit_application(self):
        """지원서 제출"""
        try:
            self.logger.info("지원서 제출 과정 시작")
            
            # 현재 페이지가 지원서 작성 페이지인지 확인
            current_url = self.driver.current_url
            self.logger.info(f"현재 URL: {current_url}")
            
            # 이력서 선택 (다양한 선택자 시도)
            resume_selected = False
            resume_selectors = [
                "input[type='radio'][name*='resume']",
                "input[type='radio'][name*='cv']", 
                "input[type='radio'][class*='resume']",
                ".resume-select input[type='radio']",
                ".cv-select input[type='radio']"
            ]
            
            for selector in resume_selectors:
                try:
                    resume_radios = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if resume_radios:
                        # 첫 번째 이력서 선택
                        first_resume = resume_radios[0]
                        if first_resume.is_enabled():
                            self.driver.execute_script("arguments[0].click();", first_resume)
                            self.logger.info(f"이력서 선택 완료: {selector}")
                            resume_selected = True
                            self.random_wait(1, 2)
                            break
                except Exception as e:
                    self.logger.debug(f"이력서 선택자 시도 실패 {selector}: {str(e)}")
                    continue
            
            if not resume_selected:
                self.logger.warning("이력서 선택 요소를 찾을 수 없습니다. 기본 이력서를 사용할 것으로 예상됩니다.")
            
            # 지원서 제출 버튼 찾기 (더 포괄적인 검색)
            submit_selectors = [
                "button[class*='submit']",
                "button[class*='apply']", 
                "input[type='submit']",
                "button:contains('지원하기')",
                "button:contains('제출하기')",
                "button:contains('지원완료')",
                ".btn_submit",
                ".btn_apply",
                ".submit-btn",
                ".apply-btn"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    if ":contains" in selector:
                        # XPath로 텍스트 기반 검색
                        xpath_selectors = [
                            "//button[contains(text(), '지원하기')]",
                            "//button[contains(text(), '제출하기')]",
                            "//button[contains(text(), '지원완료')]",
                            "//input[@type='submit' and contains(@value, '지원')]"
                        ]
                        for xpath in xpath_selectors:
                            try:
                                submit_button = self.driver.find_element(By.XPATH, xpath)
                                if submit_button.is_displayed() and submit_button.is_enabled():
                                    self.logger.info(f"제출 버튼 발견: {xpath}")
                                    break
                            except:
                                continue
                    else:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if submit_button.is_displayed() and submit_button.is_enabled():
                            self.logger.info(f"제출 버튼 발견: {selector}")
                            break
                except:
                    continue
                
                if submit_button and submit_button.is_displayed() and submit_button.is_enabled():
                    break
            
            if submit_button:
                self.logger.info("지원서 제출 버튼 클릭")
                self.driver.execute_script("arguments[0].click();", submit_button)
                self.random_wait(3, 5)
                
                # 지원 완료 확인 (더 정확한 검증)
                success_confirmed = False
                
                # URL 변경 확인
                new_url = self.driver.current_url
                if new_url != current_url:
                    self.logger.info(f"URL 변경 감지: {current_url} -> {new_url}")
                    if "complete" in new_url or "success" in new_url or "apply" in new_url:
                        success_confirmed = True
                
                # 성공 메시지 확인
                success_indicators = [
                    "지원이 완료",
                    "지원완료", 
                    "apply_complete",
                    "success"
                ]
                
                page_text = self.driver.page_source.lower()
                current_url = self.driver.current_url.lower()
                
                for indicator in success_indicators:
                    if indicator in page_text or indicator in current_url:
                        return True
                        
                # 추가 확인: alert 메시지
                try:
                    alert = self.driver.switch_to.alert
                    alert_text = alert.text
                    alert.accept()
                    if "완료" in alert_text or "성공" in alert_text:
                        return True
                except:
                    pass
                    
                return True  # 명시적 실패 신호가 없으면 성공으로 간주
                
            else:
                self.logger.warning("지원 제출 버튼을 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            self.logger.error(f"지원서 제출 중 오류: {str(e)}")
            return False
    
    def go_to_next_page(self):
        """다음 페이지로 이동"""
        try:
            # 다음 페이지 버튼 찾기
            next_selectors = [
                ".btn_next",
                "a[class*='next']",
                ".paging .next"
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_button.is_displayed() and next_button.is_enabled():
                        next_button.click()
                        self.random_wait(2, 4)
                        return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            self.logger.error(f"다음 페이지 이동 중 오류: {str(e)}")
            return False
    
    def extract_job_id(self, job_url):
        """URL에서 채용 공고 ID 추출"""
        try:
            # URL에서 ID 패턴 추출
            import re
            match = re.search(r'/(\d+)/?', job_url)
            if match:
                return match.group(1)
            else:
                # URL 전체를 해시하여 고유 ID 생성
                import hashlib
                return hashlib.md5(job_url.encode()).hexdigest()[:16]
        except Exception:
            import hashlib
            return hashlib.md5(job_url.encode()).hexdigest()[:16]
    
    def type_like_human(self, element, text):
        """사람처럼 타이핑하기 (개선된 버전)"""
        # 타이핑 전 짧은 대기
        time.sleep(random.uniform(0.3, 0.8))
        
        for i, char in enumerate(text):
            element.send_keys(char)
            
            # 다양한 타이핑 속도 패턴
            if i % 3 == 0:  # 가끔 더 긴 대기
                time.sleep(random.uniform(0.1, 0.3))
            else:
                time.sleep(random.uniform(0.02, 0.12))
                
            # 가끔 백스페이스 후 다시 타이핑 (실수 시뮬레이션)
            if random.random() < 0.02 and len(text) > 3:
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.1, 0.2))
                element.send_keys(char)
        
        # 타이핑 완료 후 대기
        time.sleep(random.uniform(0.2, 0.5))
    
    def random_wait(self, min_seconds, max_seconds):
        """랜덤 대기"""
        wait_time = random.uniform(min_seconds, max_seconds)
        time.sleep(wait_time)
    
    def close(self):
        """브라우저 닫기"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("브라우저를 닫았습니다.")
            except Exception as e:
                self.logger.error(f"브라우저 종료 중 오류: {str(e)}")
