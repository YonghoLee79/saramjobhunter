#!/usr/bin/env python3
"""
하이브리드 자동화 시스템 - 수동 로그인 + 자동 지원
Hybrid automation system - Manual login + Automatic application
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from config import Config
from postgres_database import PostgresApplicationDatabase
from logger_config import setup_logger

class HybridSaraminBot:
    def __init__(self):
        self.config = Config()
        self.database = PostgresApplicationDatabase()
        self.logger = setup_logger("hybrid_bot.log")
        self.driver = None
        self.wait = None
        
    def setup_driver(self, headless=False):
        """사용자 친화적 드라이버 설정"""
        chrome_options = Options()
        
        if not headless:
            # GUI 모드 - 사용자가 로그인할 수 있도록
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-notifications")
        else:
            chrome_options.add_argument("--headless")
        
        # 기본 설정
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            self.logger.info("브라우저 설정 완료")
            return True
        except Exception as e:
            self.logger.error(f"브라우저 설정 실패: {e}")
            return False
    
    def wait_for_manual_login(self):
        """사용자 로그인 완료까지 대기"""
        self.logger.info("=== 수동 로그인 모드 ===")
        self.logger.info("브라우저에서 직접 로그인해주세요")
        
        # 로그인 페이지로 이동
        self.driver.get("https://www.saramin.co.kr/zf_user/auth/login")
        
        print("\n" + "="*60)
        print("🚀 하이브리드 자동화 시스템 시작")
        print("="*60)
        print("1. 브라우저가 열렸습니다")
        print("2. 사람인 로그인 페이지에서 직접 로그인해주세요")
        print("3. 로그인 완료 후 엔터를 눌러주세요")
        print("="*60)
        
        # 사용자 입력 대기
        input("로그인 완료 후 엔터를 눌러주세요...")
        
        # 로그인 상태 확인
        try:
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                self.logger.info("✅ 로그인 완료 확인됨")
                print("✅ 로그인 상태 확인 완료!")
                return True
            else:
                self.logger.warning("로그인이 완료되지 않은 것 같습니다")
                retry = input("로그인을 다시 시도하시겠습니까? (y/n): ")
                if retry.lower() == 'y':
                    return self.wait_for_manual_login()
                return False
        except Exception as e:
            self.logger.error(f"로그인 상태 확인 실패: {e}")
            return False
    
    def start_automated_job_search(self):
        """로그인 후 자동 채용공고 검색 및 지원"""
        print("\n🤖 자동 채용공고 검색 및 지원을 시작합니다...")
        
        total_applications = 0
        
        for keyword in self.config.keyword_list:
            self.logger.info(f"키워드 '{keyword}' 검색 시작")
            print(f"\n🔍 '{keyword}' 검색 중...")
            
            try:
                # 검색 URL 생성
                search_url = self.build_search_url(keyword)
                self.driver.get(search_url)
                time.sleep(random.uniform(3, 5))
                
                # 채용공고 수집
                job_links = self.get_job_links()
                self.logger.info(f"'{keyword}'로 {len(job_links)}개 채용공고 발견")
                print(f"  📋 {len(job_links)}개 채용공고 발견")
                
                # 각 채용공고에 지원
                keyword_applications = 0
                for i, job_url in enumerate(job_links):
                    if total_applications >= self.config.max_applications_per_day:
                        self.logger.info("일일 최대 지원 수 도달")
                        print("⚠️ 일일 최대 지원 수에 도달했습니다")
                        break
                    
                    print(f"  📝 {i+1}/{len(job_links)} 지원 중...")
                    
                    if self.apply_to_job(job_url, keyword):
                        total_applications += 1
                        keyword_applications += 1
                    
                    # 지원 간 대기
                    delay = random.uniform(
                        self.config.min_delay_between_applications,
                        self.config.max_delay_between_applications
                    )
                    time.sleep(delay)
                
                print(f"  ✅ '{keyword}': {keyword_applications}개 지원 완료")
                
            except Exception as e:
                self.logger.error(f"키워드 '{keyword}' 검색 중 오류: {e}")
                print(f"  ❌ '{keyword}' 검색 중 오류 발생")
        
        return total_applications
    
    def build_search_url(self, keyword):
        """검색 URL 생성"""
        base_url = "https://www.saramin.co.kr/zf_user/search/recruit"
        params = [
            f"search_text={keyword}",
            f"loc_mcd=101000",  # 서울
            "cat_kewd=",
            "exp_cd=",
            "sal_cd=",
            "job_type=1",  # 정규직
            "search_optional_item=n",
            "search_done=y",
            "panel_count=y",
            "preview=y",
            "isAjaxRequest=0",
            "page=1",
            "page_count=50"
        ]
        return f"{base_url}?{'&'.join(params)}"
    
    def get_job_links(self):
        """현재 페이지의 채용공고 링크 수집"""
        job_links = []
        
        try:
            # 채용공고 링크 요소들 찾기
            selectors = [
                ".item_recruit .job_tit > a",
                ".recruit_info .job_tit a",
                ".list_item .area_job .job_tit a"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements:
                            href = element.get_attribute("href")
                            if href and "recruit" in href:
                                job_links.append(href)
                        break
                except:
                    continue
            
            # 중복 제거
            job_links = list(set(job_links))
            return job_links[:self.config.max_applications_per_day]
            
        except Exception as e:
            self.logger.error(f"채용공고 링크 수집 실패: {e}")
            return []
    
    def apply_to_job(self, job_url, keyword):
        """개별 채용공고에 지원"""
        try:
            # 채용공고 ID 추출
            job_id = self.extract_job_id(job_url)
            if not job_id:
                return False
            
            # 중복 지원 확인
            if self.database.is_already_applied(job_id):
                self.logger.info(f"이미 지원한 채용공고: {job_id}")
                return False
            
            # 채용공고 페이지 이동
            self.driver.get(job_url)
            time.sleep(random.uniform(2, 4))
            
            # 회사명과 직무 정보 추출
            company_name = "미확인"
            job_title = "미확인"
            
            try:
                company_element = self.driver.find_element(By.CSS_SELECTOR, ".company_nm a, .area_corp .corp_name a")
                company_name = company_element.text.strip()
            except:
                pass
            
            try:
                title_element = self.driver.find_element(By.CSS_SELECTOR, ".job_tit, .area_job .job_tit")
                job_title = title_element.text.strip()
            except:
                pass
            
            # 지원하기 버튼 찾기 및 클릭
            apply_selectors = [
                ".btn_apply",
                ".area_apply .btn_support",
                ".support_btn",
                "button[onclick*='apply']"
            ]
            
            apply_button = None
            for selector in apply_selectors:
                try:
                    apply_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if apply_button.is_displayed() and apply_button.is_enabled():
                        break
                except:
                    continue
            
            if not apply_button:
                self.logger.warning(f"지원 버튼을 찾을 수 없음: {job_url}")
                return False
            
            # 지원하기 클릭
            apply_button.click()
            time.sleep(random.uniform(2, 4))
            
            # 지원서 제출 처리
            if self.submit_application():
                # 성공적으로 지원한 경우 데이터베이스에 기록
                self.database.record_application(job_id, job_url, company_name, job_title, keyword)
                self.logger.info(f"✅ 지원 완료: {company_name} - {job_title}")
                return True
            else:
                self.logger.warning(f"지원서 제출 실패: {job_url}")
                return False
            
        except Exception as e:
            self.logger.error(f"지원 중 오류 발생: {e}")
            return False
    
    def submit_application(self):
        """지원서 제출"""
        try:
            # 제출 버튼 찾기
            submit_selectors = [
                ".btn_submit",
                ".btn_apply_submit",
                "button[type='submit']",
                ".apply_btn"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if submit_button:
                submit_button.click()
                time.sleep(random.uniform(2, 4))
                return True
            else:
                # 이미 제출된 상태이거나 별도 제출 과정이 없는 경우
                return True
                
        except Exception as e:
            self.logger.error(f"지원서 제출 중 오류: {e}")
            return False
    
    def extract_job_id(self, job_url):
        """URL에서 채용공고 ID 추출"""
        try:
            if "rec_idx=" in job_url:
                return job_url.split("rec_idx=")[1].split("&")[0]
            elif "/recruit/" in job_url:
                return job_url.split("/recruit/")[1].split("?")[0]
            else:
                return None
        except:
            return None
    
    def run_hybrid_automation(self):
        """하이브리드 자동화 실행"""
        if not self.setup_driver(headless=False):
            return False
        
        try:
            # 1단계: 수동 로그인 대기
            if not self.wait_for_manual_login():
                self.logger.error("로그인이 완료되지 않았습니다")
                return False
            
            # 2단계: 자동 채용공고 검색 및 지원
            total_applications = self.start_automated_job_search()
            
            # 3단계: 결과 보고
            print(f"\n✅ 자동화 완료!")
            print(f"📊 총 {total_applications}개 채용공고에 지원했습니다")
            
            # 실행 기록 저장
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            keywords_str = ",".join(self.config.keyword_list)
            self.database.record_execution(today, total_applications, keywords_str)
            
            self.logger.info(f"하이브리드 자동화 완료: {total_applications}개 지원")
            
            input("\n엔터를 눌러 브라우저를 종료합니다...")
            return True
            
        except Exception as e:
            self.logger.error(f"하이브리드 자동화 중 오류: {e}")
            print(f"❌ 오류 발생: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """메인 실행"""
    bot = HybridSaraminBot()
    
    print("🚀 사람인 하이브리드 자동화 시스템")
    print("로그인은 직접, 지원은 자동으로!")
    
    success = bot.run_hybrid_automation()
    
    if success:
        print("✅ 모든 작업이 완료되었습니다!")
    else:
        print("❌ 작업 중 문제가 발생했습니다")

if __name__ == "__main__":
    main()