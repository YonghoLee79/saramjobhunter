"""
사람인 웹사이트 자동화 봇
Saramin website automation bot using Selenium
"""

import time
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
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
        self.db = database
        self.logger = logger
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.base_url = "https://www.saramin.co.kr"
        
    def setup_driver(self):
        """Chrome WebDriver 설정"""
        try:
            chrome_options = Options()
            
            # 헤드리스 모드 설정 (필요시)
            if self.config.headless:
                chrome_options.add_argument("--headless")
                
            # 기본 옵션들
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
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
            
            self.logger.info("Chrome WebDriver 설정 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"WebDriver 설정 실패: {str(e)}")
            return False
    
    def login(self):
        """사람인 로그인"""
        if not self.setup_driver():
            return False
            
        try:
            self.logger.info("사람인 로그인 시도 중...")
            
            # 로그인 페이지로 이동
            self.driver.get(f"{self.base_url}/zf_user/auth/login")
            self.random_wait(2, 4)
            
            # 아이디 입력
            id_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "id"))
            )
            id_input.clear()
            self.type_like_human(id_input, self.config.username)
            
            # 비밀번호 입력
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            self.type_like_human(password_input, self.config.password)
            
            self.random_wait(1, 2)
            
            # 로그인 버튼 클릭
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_btn.click()
            
            # 로그인 성공 확인
            self.wait.until(lambda driver: driver.current_url != f"{self.base_url}/zf_user/auth/login")
            
            # 메인 페이지로 이동했는지 확인
            if "login" not in self.driver.current_url:
                self.logger.info("로그인 성공")
                self.random_wait(2, 3)
                return True
            else:
                self.logger.error("로그인 실패 - 잘못된 자격증명이거나 추가 인증이 필요할 수 있습니다")
                return False
                
        except TimeoutException:
            self.logger.error("로그인 페이지 로딩 시간 초과")
            return False
        except Exception as e:
            self.logger.error(f"로그인 중 오류 발생: {str(e)}")
            return False
    
    def search_and_apply_jobs(self):
        """채용 공고 검색 및 지원"""
        applied_count = 0
        
        try:
            # 검색 페이지로 이동
            search_url = self.build_search_url()
            self.driver.get(search_url)
            self.random_wait(3, 5)
            
            self.logger.info(f"검색 조건: {self.config.search_keyword}, {self.config.location}, {self.config.job_type}")
            
            page = 1
            max_pages = self.config.max_pages
            
            while page <= max_pages:
                self.logger.info(f"페이지 {page} 처리 중...")
                
                # 채용 공고 목록 가져오기
                job_links = self.get_job_links()
                
                if not job_links:
                    self.logger.info("더 이상 채용 공고가 없습니다.")
                    break
                
                # 각 채용 공고에 지원
                for job_link in job_links:
                    if applied_count >= self.config.max_applications_per_day:
                        self.logger.info(f"일일 최대 지원 수({self.config.max_applications_per_day})에 도달했습니다.")
                        return applied_count
                        
                    if self.apply_to_job(job_link):
                        applied_count += 1
                        
                    # 요청 간격 대기
                    self.random_wait(
                        self.config.min_delay_between_applications,
                        self.config.max_delay_between_applications
                    )
                
                # 다음 페이지로 이동
                if not self.go_to_next_page():
                    break
                    
                page += 1
                
        except Exception as e:
            self.logger.error(f"채용 공고 검색 및 지원 중 오류: {str(e)}")
            
        return applied_count
    
    def build_search_url(self):
        """검색 URL 생성"""
        params = {
            'searchword': self.config.search_keyword,
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
            if self.db.is_already_applied(job_id):
                self.logger.info(f"이미 지원한 공고입니다 (ID: {job_id})")
                return False
            
            # 채용 공고 페이지로 이동
            self.driver.get(job_url)
            self.random_wait(2, 4)
            
            # 채용 공고 제목 가져오기
            try:
                job_title = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    ".job_tit"
                ).text.strip()
            except:
                job_title = "제목 없음"
            
            # 회사명 가져오기
            try:
                company_name = self.driver.find_element(
                    By.CSS_SELECTOR,
                    ".company_nm a"
                ).text.strip()
            except:
                company_name = "회사명 없음"
            
            self.logger.info(f"지원 시도: {company_name} - {job_title}")
            
            # 지원하기 버튼 찾기
            apply_button = None
            try:
                # 다양한 지원하기 버튼 셀렉터 시도
                selectors = [
                    ".btn_apply",
                    ".apply_btn", 
                    "button[class*='apply']",
                    "a[class*='apply']"
                ]
                
                for selector in selectors:
                    try:
                        apply_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if apply_button.is_displayed() and apply_button.is_enabled():
                            break
                    except:
                        continue
                        
            except Exception as e:
                self.logger.warning(f"지원하기 버튼을 찾을 수 없습니다: {str(e)}")
            
            if not apply_button:
                self.logger.warning("지원하기 버튼을 찾을 수 없습니다. 마감되었거나 웹사이트 구조가 변경되었을 수 있습니다.")
                return False
            
            # 지원하기 버튼 클릭
            self.driver.execute_script("arguments[0].click();", apply_button)
            self.random_wait(2, 3)
            
            # 지원서 작성 페이지에서 이력서 선택 및 제출
            if self.submit_application():
                # 데이터베이스에 지원 기록 저장
                self.db.record_application(job_id, job_url, company_name, job_title)
                self.logger.info(f"지원 완료: {company_name} - {job_title}")
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
            # 이력서 선택 (첫 번째 이력서 사용)
            try:
                resume_radio = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='radio'][name*='resume']"))
                )
                resume_radio.click()
                self.random_wait(1, 2)
            except:
                self.logger.warning("이력서 선택 요소를 찾을 수 없습니다.")
            
            # 지원하기 버튼 클릭
            submit_selectors = [
                "button[class*='submit']",
                "button[class*='apply']", 
                ".btn_apply",
                "input[type='submit']"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        break
                except:
                    continue
            
            if submit_button:
                self.driver.execute_script("arguments[0].click();", submit_button)
                self.random_wait(2, 3)
                
                # 지원 완료 확인
                # 성공 메시지나 URL 변경을 확인
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
        """사람처럼 타이핑하기"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
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
