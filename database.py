"""
데이터베이스 관리 모듈
Database management module for tracking applications
"""

import sqlite3
import os
from datetime import datetime, date
from contextlib import contextmanager

class ApplicationDatabase:
    def __init__(self, db_file="applications.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 지원 기록 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    job_url TEXT NOT NULL,
                    company_name TEXT,
                    job_title TEXT,
                    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 실행 기록 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS execution_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_date DATE UNIQUE NOT NULL,
                    applications_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_id ON applications(job_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_execution_date ON execution_log(execution_date)')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def is_already_applied(self, job_id):
        """중복 지원 확인"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM applications WHERE job_id = ?",
                (job_id,)
            )
            return cursor.fetchone()[0] > 0
    
    def record_application(self, job_id, job_url, company_name, job_title):
        """지원 기록 저장"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO applications (job_id, job_url, company_name, job_title)
                    VALUES (?, ?, ?, ?)
                ''', (job_id, job_url, company_name, job_title))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # 이미 지원한 경우
                return False
    
    def is_executed_today(self, execution_date):
        """당일 실행 여부 확인"""
        if isinstance(execution_date, datetime):
            execution_date = execution_date.date()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM execution_log WHERE execution_date = ?",
                (execution_date,)
            )
            return cursor.fetchone()[0] > 0
    
    def record_execution(self, execution_date, applications_count):
        """실행 기록 저장"""
        if isinstance(execution_date, datetime):
            execution_date = execution_date.date()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO execution_log (execution_date, applications_count)
                VALUES (?, ?)
            ''', (execution_date, applications_count))
            conn.commit()
    
    def get_application_history(self, days=30):
        """지원 이력 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT job_id, job_url, company_name, job_title, applied_date
                FROM applications
                WHERE applied_date >= datetime('now', '-{} days')
                ORDER BY applied_date DESC
            '''.format(days))
            return cursor.fetchall()
    
    def get_execution_history(self, days=30):
        """실행 이력 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT execution_date, applications_count, created_at
                FROM execution_log
                WHERE execution_date >= date('now', '-{} days')
                ORDER BY execution_date DESC
            '''.format(days))
            return cursor.fetchall()
    
    def get_statistics(self):
        """통계 정보 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 총 지원 수
            cursor.execute("SELECT COUNT(*) FROM applications")
            total_applications = cursor.fetchone()[0]
            
            # 이번 주 지원 수
            cursor.execute('''
                SELECT COUNT(*) FROM applications
                WHERE applied_date >= datetime('now', 'weekday 0', '-7 days')
            ''')
            week_applications = cursor.fetchone()[0]
            
            # 이번 달 지원 수
            cursor.execute('''
                SELECT COUNT(*) FROM applications
                WHERE applied_date >= datetime('now', 'start of month')
            ''')
            month_applications = cursor.fetchone()[0]
            
            # 가장 많이 지원한 회사
            cursor.execute('''
                SELECT company_name, COUNT(*) as count
                FROM applications
                GROUP BY company_name
                ORDER BY count DESC
                LIMIT 5
            ''')
            top_companies = cursor.fetchall()
            
            return {
                'total_applications': total_applications,
                'week_applications': week_applications,
                'month_applications': month_applications,
                'top_companies': top_companies
            }
    
    def cleanup_old_records(self, days=90):
        """오래된 기록 정리"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 오래된 지원 기록 삭제
            cursor.execute('''
                DELETE FROM applications
                WHERE applied_date < datetime('now', '-{} days')
            '''.format(days))
            
            # 오래된 실행 기록 삭제
            cursor.execute('''
                DELETE FROM execution_log
                WHERE execution_date < date('now', '-{} days')
            '''.format(days))
            
            conn.commit()
            
            return cursor.rowcount
