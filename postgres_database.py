"""
PostgreSQL 데이터베이스 관리 모듈
PostgreSQL database management module for tracking applications
"""

from models import JobApplication, ExecutionLog, UserConfiguration, SystemLog, create_session, init_database
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json
import logging

class PostgresApplicationDatabase:
    """PostgreSQL 기반 애플리케이션 데이터베이스"""
    
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        try:
            init_database()
            print("PostgreSQL 데이터베이스 초기화 완료")
        except Exception as e:
            print(f"데이터베이스 초기화 실패: {str(e)}")
            raise
    
    def is_already_applied(self, job_id):
        """중복 지원 확인"""
        session = create_session()
        try:
            application = session.query(JobApplication).filter_by(job_id=job_id).first()
            return application is not None
        except Exception as e:
            print(f"중복 지원 확인 오류: {str(e)}")
            return False
        finally:
            session.close()
    
    def is_company_already_applied(self, company_name, days=30):
        """회사명 기반 중복 지원 확인 (최근 30일 내)"""
        session = create_session()
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            application = session.query(JobApplication)\
                .filter(JobApplication.company_name == company_name)\
                .filter(JobApplication.application_date >= cutoff_date)\
                .first()
            return application is not None
        except Exception as e:
            print(f"회사 중복 지원 확인 오류: {str(e)}")
            return False
        finally:
            session.close()
    
    def record_application(self, job_id, job_url, company_name, job_title, keyword=None):
        """지원 기록 저장"""
        session = create_session()
        try:
            # 중복 확인
            if self.is_already_applied(job_id):
                return False
            
            application = JobApplication(
                job_id=job_id,
                job_url=job_url,
                company_name=company_name,
                job_title=job_title,
                keyword=keyword,
                application_date=datetime.now()
            )
            
            session.add(application)
            session.commit()
            print(f"지원 기록 저장: {company_name} - {job_title}")
            return True
            
        except IntegrityError:
            session.rollback()
            print(f"중복 지원 시도: {job_id}")
            return False
        except Exception as e:
            session.rollback()
            print(f"지원 기록 저장 오류: {str(e)}")
            return False
        finally:
            session.close()
    
    def is_executed_today(self, execution_date):
        """당일 실행 여부 확인"""
        session = create_session()
        try:
            log = session.query(ExecutionLog).filter_by(execution_date=execution_date).first()
            return log is not None
        except Exception as e:
            print(f"당일 실행 확인 오류: {str(e)}")
            return False
        finally:
            session.close()
    
    def record_execution(self, execution_date, applications_count, keywords=None, status='completed', error_message=None):
        """실행 기록 저장"""
        session = create_session()
        try:
            # 기존 기록 확인
            existing_log = session.query(ExecutionLog).filter_by(execution_date=execution_date).first()
            
            if existing_log:
                # 기존 기록 업데이트
                existing_log.applications_count = applications_count
                existing_log.keywords_searched = json.dumps(keywords) if keywords else None
                existing_log.end_time = datetime.now()
                existing_log.status = status
                existing_log.error_message = error_message
                existing_log.updated_at = datetime.now()
            else:
                # 새 기록 생성
                execution_log = ExecutionLog(
                    execution_date=execution_date,
                    applications_count=applications_count,
                    keywords_searched=json.dumps(keywords) if keywords else None,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    status=status,
                    error_message=error_message
                )
                session.add(execution_log)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"실행 기록 저장 오류: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_application_history(self, days=30):
        """지원 이력 조회"""
        session = create_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            applications = session.query(JobApplication)\
                .filter(JobApplication.application_date >= cutoff_date)\
                .order_by(desc(JobApplication.application_date))\
                .all()
            
            result = []
            for app in applications:
                result.append({
                    'id': app.id,
                    'job_id': app.job_id,
                    'company_name': app.company_name,
                    'job_title': app.job_title,
                    'keyword': app.keyword,
                    'application_date': app.application_date.isoformat(),
                    'status': app.status
                })
            
            return result
            
        except Exception as e:
            print(f"지원 이력 조회 오류: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_execution_history(self, days=30):
        """실행 이력 조회"""
        session = create_session()
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            executions = session.query(ExecutionLog)\
                .filter(ExecutionLog.execution_date >= cutoff_date)\
                .order_by(desc(ExecutionLog.execution_date))\
                .all()
            
            result = []
            for exec_log in executions:
                keywords = json.loads(exec_log.keywords_searched) if exec_log.keywords_searched else []
                result.append({
                    'id': exec_log.id,
                    'execution_date': exec_log.execution_date,
                    'applications_count': exec_log.applications_count,
                    'keywords': keywords,
                    'status': exec_log.status,
                    'start_time': exec_log.start_time.isoformat() if exec_log.start_time else None,
                    'end_time': exec_log.end_time.isoformat() if exec_log.end_time else None
                })
            
            return result
            
        except Exception as e:
            print(f"실행 이력 조회 오류: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_statistics(self):
        """통계 정보 조회"""
        session = create_session()
        try:
            # 총 지원 수
            total_applications = session.query(func.count(JobApplication.id)).scalar()
            
            # 오늘 지원 수
            today = datetime.now().strftime('%Y-%m-%d')
            today_applications = session.query(func.count(JobApplication.id))\
                .filter(func.date(JobApplication.application_date) == today)\
                .scalar()
            
            # 이번 주 지원 수
            week_ago = datetime.now() - timedelta(days=7)
            week_applications = session.query(func.count(JobApplication.id))\
                .filter(JobApplication.application_date >= week_ago)\
                .scalar()
            
            # 최근 실행 수
            recent_executions = session.query(func.count(ExecutionLog.id))\
                .filter(ExecutionLog.status == 'completed')\
                .scalar()
            
            # 키워드별 통계
            keyword_stats = session.query(JobApplication.keyword, func.count(JobApplication.id))\
                .filter(JobApplication.keyword.isnot(None))\
                .group_by(JobApplication.keyword)\
                .all()
            
            keyword_counts = {keyword: count for keyword, count in keyword_stats}
            
            return {
                'total_applications': total_applications or 0,
                'today_applications': today_applications or 0,
                'week_applications': week_applications or 0,
                'total_executions': recent_executions or 0,
                'keyword_statistics': keyword_counts
            }
            
        except Exception as e:
            print(f"통계 조회 오류: {str(e)}")
            return {
                'total_applications': 0,
                'today_applications': 0,
                'week_applications': 0,
                'total_executions': 0,
                'keyword_statistics': {}
            }
        finally:
            session.close()
    
    def cleanup_old_records(self, days=90):
        """오래된 기록 정리"""
        session = create_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 오래된 지원 기록 삭제
            deleted_apps = session.query(JobApplication)\
                .filter(JobApplication.application_date < cutoff_date)\
                .delete()
            
            # 오래된 실행 로그 삭제
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
            deleted_logs = session.query(ExecutionLog)\
                .filter(ExecutionLog.execution_date < cutoff_date_str)\
                .delete()
            
            # 오래된 시스템 로그 삭제
            deleted_sys_logs = session.query(SystemLog)\
                .filter(SystemLog.created_at < cutoff_date)\
                .delete()
            
            session.commit()
            
            print(f"정리 완료: 지원기록 {deleted_apps}개, 실행로그 {deleted_logs}개, 시스템로그 {deleted_sys_logs}개")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"기록 정리 오류: {str(e)}")
            return False
        finally:
            session.close()
    
    def log_system_message(self, level, message, module=None, function_name=None, execution_id=None):
        """시스템 로그 기록"""
        session = create_session()
        try:
            system_log = SystemLog(
                log_level=level.upper(),
                message=message,
                module=module,
                function_name=function_name,
                execution_id=execution_id
            )
            
            session.add(system_log)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"시스템 로그 기록 오류: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_configuration(self, key, default_value=None):
        """설정값 조회"""
        session = create_session()
        try:
            config = session.query(UserConfiguration).filter_by(config_key=key).first()
            return config.config_value if config else default_value
        except Exception as e:
            print(f"설정 조회 오류: {str(e)}")
            return default_value
        finally:
            session.close()
    
    def set_configuration(self, key, value, description=None):
        """설정값 저장"""
        session = create_session()
        try:
            config = session.query(UserConfiguration).filter_by(config_key=key).first()
            
            if config:
                config.config_value = str(value)
                config.description = description
                config.updated_at = datetime.now()
            else:
                config = UserConfiguration(
                    config_key=key,
                    config_value=str(value),
                    description=description
                )
                session.add(config)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_last_used_keywords(self):
        """마지막으로 사용한 검색 키워드 조회"""
        session = create_session()
        try:
            # 가장 최근 실행 기록에서 키워드 조회
            latest_execution = session.query(ExecutionLog)\
                .filter(ExecutionLog.keywords_searched.isnot(None))\
                .order_by(ExecutionLog.created_at.desc())\
                .first()
            
            if latest_execution and latest_execution.keywords_searched:
                import json
                try:
                    keywords = json.loads(latest_execution.keywords_searched)
                    return ",".join(keywords) if isinstance(keywords, list) else latest_execution.keywords_searched
                except:
                    return latest_execution.keywords_searched
            
            # 실행 기록이 없으면 설정값에서 조회
            return self.get_configuration('last_keywords', 'bio')
        except Exception as e:
            return 'bio'  # 기본값
        finally:
            session.close()
    
    def save_last_used_keywords(self, keywords):
        """마지막 사용 키워드 저장"""
        try:
            self.set_configuration('last_keywords', keywords, '마지막으로 사용한 검색 키워드')
        except Exception as e:
            pass  # 저장 실패해도 진행
    
    def get_last_used_location(self):
        """마지막으로 사용한 지역 조회"""
        try:
            # 가장 최근 실행 기록이나 설정에서 지역 조회
            return self.get_configuration('last_location', '서울')
        except Exception as e:
            return '서울'  # 기본값
    
    def save_last_used_location(self, location):
        """마지막 사용 지역 저장"""
        try:
            self.set_configuration('last_location', location, '마지막으로 사용한 검색 지역')
        except Exception as e:
            pass  # 저장 실패해도 진행
    
    def get_last_used_max_applications(self):
        """마지막으로 사용한 최대 지원수 조회"""
        try:
            return int(self.get_configuration('last_max_applications', '100'))
        except Exception as e:
            return 100  # 기본값
    
    def save_last_used_max_applications(self, max_apps):
        """마지막 사용 최대 지원수 저장"""
        try:
            self.set_configuration('last_max_applications', str(max_apps), '마지막으로 사용한 최대 지원수')
        except Exception as e:
            pass  # 저장 실패해도 진행

if __name__ == "__main__":
    # 데이터베이스 테스트
    db = PostgresApplicationDatabase()
    print("PostgreSQL 데이터베이스 연결 테스트 완료")