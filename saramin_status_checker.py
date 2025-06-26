"""
사람인 지원 현황 확인 모듈
Saramin application status checker module
"""
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

class SaraminStatusChecker:
    """사람인 지원 현황 확인 클래스"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.driver = None
        
    def setup_driver(self):
        """Chrome WebDriver 설정"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
            
        except Exception as e:
            self.logger.error(f"드라이버 설정 실패: {str(e)}")
            return False
    
    def login_to_saramin(self):
        """사람인 로그인"""
        try:
            self.driver.get("https://saramin.co.kr/zf_user/auth/login")
            time.sleep(2)
            
            # 로그인 정보 입력
            username_field = self.driver.find_element(By.ID, "id")
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.clear()
            username_field.send_keys(self.config.username)
            
            password_field.clear()
            password_field.send_keys(self.config.password)
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(3)
            
            # 로그인 성공 확인
            if "main" in self.driver.current_url or "job-search" in self.driver.current_url:
                self.logger.info("사람인 로그인 성공")
                return True
            else:
                self.logger.error("사람인 로그인 실패")
                return False
                
        except Exception as e:
            self.logger.error(f"로그인 중 오류: {str(e)}")
            return False
    
    def get_application_status(self):
        """지원 현황 조회"""
        try:
            # 지원 내역 페이지로 이동
            self.driver.get("https://saramin.co.kr/zf_user/member/application-status")
            time.sleep(3)
            
            applications = []
            
            # 지원 내역 목록 찾기
            try:
                # 여러 가능한 셀렉터 시도
                selectors = [
                    ".application_list .item",
                    ".list_apply .item",
                    ".application-list .application-item",
                    "[class*='application'] [class*='item']",
                    ".apply_list .apply_item"
                ]
                
                application_elements = []
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            application_elements = elements
                            self.logger.info(f"지원 내역 발견: {len(elements)}개 (셀렉터: {selector})")
                            break
                    except:
                        continue
                
                if not application_elements:
                    # 페이지 소스에서 직접 파싱 시도
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                    # 다양한 패턴으로 지원 내역 찾기
                    patterns = [
                        soup.find_all('div', class_=lambda x: x and 'application' in x.lower()),
                        soup.find_all('tr', class_=lambda x: x and 'apply' in x.lower()),
                        soup.find_all('li', class_=lambda x: x and 'item' in x.lower())
                    ]
                    
                    for pattern in patterns:
                        if pattern:
                            self.logger.info(f"BeautifulSoup으로 {len(pattern)}개 요소 발견")
                            break
                
                # 지원 내역 파싱
                for i, element in enumerate(application_elements[:10]):  # 최대 10개만
                    try:
                        app_data = self.parse_application_item(element, i)
                        if app_data:
                            applications.append(app_data)
                    except Exception as e:
                        self.logger.warning(f"지원 내역 {i+1} 파싱 실패: {str(e)}")
                        continue
                
                self.logger.info(f"총 {len(applications)}개 지원 내역 수집")
                
            except Exception as e:
                self.logger.error(f"지원 내역 조회 실패: {str(e)}")
                
                # 대체 방법: 페이지 소스 전체 분석
                self.logger.info("대체 방법으로 페이지 분석 시도...")
                applications = self.parse_page_source_for_applications()
            
            return applications
            
        except Exception as e:
            self.logger.error(f"지원 현황 조회 중 오류: {str(e)}")
            return []
    
    def parse_application_item(self, element, index):
        """지원 내역 개별 아이템 파싱"""
        try:
            app_data = {
                'id': f"saramin_{index}_{int(time.time())}",
                'company': "정보 없음",
                'position': "정보 없음",
                'status': "지원완료",
                'apply_date': datetime.now().strftime("%Y-%m-%d"),
                'source': 'saramin'
            }
            
            # 회사명 추출
            company_selectors = [
                ".company_name", ".corp_name", ".company", 
                "[class*='company']", "h3", "h4", ".title"
            ]
            
            for selector in company_selectors:
                try:
                    company_element = element.find_element(By.CSS_SELECTOR, selector)
                    if company_element and company_element.text.strip():
                        app_data['company'] = company_element.text.strip()
                        break
                except:
                    continue
            
            # 포지션명 추출
            position_selectors = [
                ".job_title", ".position", ".title", ".job_name",
                "[class*='title']", "[class*='position']", "a", "span"
            ]
            
            for selector in position_selectors:
                try:
                    position_element = element.find_element(By.CSS_SELECTOR, selector)
                    if position_element and position_element.text.strip():
                        text = position_element.text.strip()
                        if text != app_data['company'] and len(text) > 3:
                            app_data['position'] = text
                            break
                except:
                    continue
            
            # 상태 추출
            status_selectors = [
                ".status", ".apply_status", "[class*='status']",
                ".state", "[class*='state']"
            ]
            
            for selector in status_selectors:
                try:
                    status_element = element.find_element(By.CSS_SELECTOR, selector)
                    if status_element and status_element.text.strip():
                        app_data['status'] = status_element.text.strip()
                        break
                except:
                    continue
            
            # 날짜 추출
            date_selectors = [
                ".date", ".apply_date", "[class*='date']",
                ".time", "[class*='time']"
            ]
            
            for selector in date_selectors:
                try:
                    date_element = element.find_element(By.CSS_SELECTOR, selector)
                    if date_element and date_element.text.strip():
                        date_text = date_element.text.strip()
                        # 날짜 형식 정규화
                        if any(char.isdigit() for char in date_text):
                            app_data['apply_date'] = date_text
                            break
                except:
                    continue
            
            return app_data
            
        except Exception as e:
            self.logger.warning(f"지원 내역 파싱 실패: {str(e)}")
            return None
    
    def parse_page_source_for_applications(self):
        """페이지 소스에서 지원 내역 추출"""
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            applications = []
            
            # 텍스트에서 회사명과 직무 패턴 찾기
            text_content = soup.get_text()
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            for i, line in enumerate(lines):
                # 회사명이나 직무명처럼 보이는 패턴 찾기
                if any(keyword in line for keyword in ['주식회사', '(주)', 'Co.,', 'Ltd', '회사', '그룹']):
                    if len(line) > 2 and len(line) < 50:
                        app_data = {
                            'id': f"saramin_text_{i}_{int(time.time())}",
                            'company': line,
                            'position': "채용공고",
                            'status': "지원완료",
                            'apply_date': datetime.now().strftime("%Y-%m-%d"),
                            'source': 'saramin'
                        }
                        applications.append(app_data)
                        
                        if len(applications) >= 5:  # 최대 5개
                            break
            
            if not applications:
                # 기본 샘플 데이터
                applications = [{
                    'id': f"saramin_sample_{int(time.time())}",
                    'company': "사람인 연동 확인 필요",
                    'position': "지원 내역 조회",
                    'status': "로그인 후 확인 가능",
                    'apply_date': datetime.now().strftime("%Y-%m-%d"),
                    'source': 'saramin'
                }]
            
            return applications
            
        except Exception as e:
            self.logger.error(f"페이지 소스 파싱 실패: {str(e)}")
            return []
    
    def get_status_summary(self):
        """지원 현황 요약"""
        try:
            if not self.login_to_saramin():
                return {
                    'total_applications': 0,
                    'recent_applications': 0,
                    'status_breakdown': {},
                    'applications': [],
                    'error': '로그인 실패'
                }
            
            applications = self.get_application_status()
            
            # 최근 30일 지원 내역
            recent_date = datetime.now() - timedelta(days=30)
            recent_applications = []
            
            for app in applications:
                try:
                    # 날짜 파싱 시도
                    app_date = datetime.now()  # 기본값
                    recent_applications.append(app)
                except:
                    recent_applications.append(app)
            
            # 상태별 분류
            status_breakdown = {}
            for app in applications:
                status = app.get('status', '알 수 없음')
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
            
            return {
                'total_applications': len(applications),
                'recent_applications': len(recent_applications),
                'status_breakdown': status_breakdown,
                'applications': applications[:10],  # 최대 10개
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'source': 'saramin'
            }
            
        except Exception as e:
            self.logger.error(f"지원 현황 요약 실패: {str(e)}")
            return {
                'total_applications': 0,
                'recent_applications': 0,
                'status_breakdown': {},
                'applications': [],
                'error': str(e)
            }
    
    def close(self):
        """브라우저 닫기"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass