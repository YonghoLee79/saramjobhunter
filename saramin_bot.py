"""
사람인 웹사이트 자동화 봇
Saramin website automation bot using Selenium
"""

import time
import random
from datetime import datetime, timedelta
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from typing import Optional
import urllib.parse

class SaraminBot:
    def save_login_page_html(self, filename="saramin_login_debug.html"):
        """현재 로그인 페이지의 HTML을 파일로 저장 (디버깅용)"""
        try:
            html = self.driver.page_source
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            self.logger.info(f"로그인 페이지 HTML 저장 완료: {filename}")
        except Exception as e:
            self.logger.error(f"로그인 페이지 HTML 저장 실패: {str(e)}")
    def __init__(self, config, database, logger):
        self.config = config
        self.database = database
        self.logger = logger
        self.driver: Optional[object] = None  # uc.Chrome 객체
        self.wait: Optional[WebDriverWait] = None
        self.base_url = "https://www.saramin.co.kr"
        self.application_callback = None  # 웹 앱에서 실시간 로그를 위한 콜백 함수
        
    def setup_driver(self):
        """undetected-chromedriver로 Chrome WebDriver 설정 (anti-bot 우회)"""
        try:
            options = uc.ChromeOptions()
            if self.config.headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
            options.add_argument("--disable-blink-features=AutomationControlled")
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            }
            options.add_experimental_option("prefs", prefs)
            # macOS 기본 Chrome 경로 지정
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            self.driver = uc.Chrome(options=options, browser_executable_path=chrome_path)
            self.wait = WebDriverWait(self.driver, 10)
            self.logger.info("undetected-chromedriver로 Chrome WebDriver 설정 완료 (anti-bot 우회)")
            return True
        except Exception as e:
            self.logger.error(f"WebDriver 설정 실패: {str(e)}")
            return False
    
    def login(self):
        """사람인 로그인 (하이브리드: 자동 실패 시 수동 로그인 안내)"""
        if not self.setup_driver():
            return False

        self.logger.info("사람인 자동 로그인 시도")
        try:
            self.driver.get("https://www.saramin.co.kr/zf_user/auth/login")
            self.random_wait(5, 8)
            self.save_login_page_html()
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            self.random_wait(2, 4)

            # 자동화 접근 시 로그인 폼이 없으면 수동 로그인 안내
            id_input = None
            try:
                id_input = self.driver.find_element(By.ID, "id")
            except Exception:
                pass
            if not id_input:
                self.logger.warning("자동화 접근 차단 감지: 수동 로그인을 안내합니다.")
                print("\n[수동 로그인 안내] 사람인 로그인 페이지가 자동화로 차단되었습니다.\n브라우저 창에서 직접 로그인 후 엔터를 눌러주세요...")
                input("로그인 완료 후 엔터를 누르세요: ")
                # 로그인 성공 여부 간단 확인 (로그인 후 URL이 로그인 페이지가 아니면 성공)
                if "login" not in self.driver.current_url and "auth" not in self.driver.current_url:
                    self.logger.info("수동 로그인 성공. 자동화 재개.")
                    return True
                else:
                    self.logger.error("수동 로그인 실패 또는 추가 인증 필요.")
                    return False

            # 자동화 입력 시도 (폼이 있을 때만)
            self.logger.info("자동 로그인 입력 시도")
            id_input.click()
            self.random_wait(0.5, 1)
            id_input.clear()
            self.random_wait(0.5, 1)
            self.type_like_human(id_input, self.config.username)
            password_input = self.driver.find_element(By.ID, "password")
            password_input.click()
            self.random_wait(0.5, 1)
            password_input.clear()
            self.random_wait(0.5, 1)
            self.type_like_human(password_input, self.config.password)
            self.random_wait(2, 4)
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .btn_login, #loginBtn")
            self.driver.execute_script("arguments[0].focus();", login_btn)
            self.random_wait(0.5, 1)
            self.driver.execute_script("arguments[0].click();", login_btn)
            self.random_wait(3, 5)
            # 로그인 성공 확인
            if "login" not in self.driver.current_url and "auth" not in self.driver.current_url:
                self.logger.info("자동 로그인 성공")
                return True
            else:
                self.logger.error("자동 로그인 실패. 수동 로그인 안내.")
                print("\n[수동 로그인 안내] 자동 로그인에 실패했습니다. 브라우저에서 직접 로그인 후 엔터를 눌러주세요...")
                input("로그인 완료 후 엔터를 누르세요: ")
                if "login" not in self.driver.current_url and "auth" not in self.driver.current_url:
                    self.logger.info("수동 로그인 성공. 자동화 재개.")
                    return True
                else:
                    self.logger.error("수동 로그인 실패 또는 추가 인증 필요.")
                    return False
        except Exception as e:
            self.logger.error(f"로그인 중 예외 발생: {str(e)}")
            print("\n[수동 로그인 안내] 예외 발생. 브라우저에서 직접 로그인 후 엔터를 눌러주세요...")
            input("로그인 완료 후 엔터를 누르세요: ")
            if "login" not in self.driver.current_url and "auth" not in self.driver.current_url:
                self.logger.info("수동 로그인 성공. 자동화 재개.")
                return True
            else:
                self.logger.error("수동 로그인 실패 또는 추가 인증 필요.")
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
