"""
로깅 설정 모듈
Logging configuration module
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(log_file="saramin_bot.log", log_level="INFO"):
    """로거 설정"""
    
    # 로그 레벨 설정
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    level = level_map.get(log_level.upper(), logging.INFO)
    
    # 로거 생성
    logger = logging.getLogger("saramin_bot")
    logger.setLevel(level)
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 파일 핸들러 설정 (회전 로그)
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def log_application_summary(logger, applied_count, total_searched):
    """지원 결과 요약 로그"""
    logger.info("=" * 50)
    logger.info("지원 결과 요약")
    logger.info(f"검색한 채용공고 수: {total_searched}")
    logger.info(f"지원한 채용공고 수: {applied_count}")
    logger.info(f"지원 성공률: {(applied_count/total_searched*100):.1f}%" if total_searched > 0 else "0%")
    logger.info("=" * 50)

def log_daily_summary(logger, db):
    """일일 요약 로그"""
    try:
        stats = db.get_statistics()
        
        logger.info("=" * 50)
        logger.info("누적 통계 요약")
        logger.info(f"총 지원 수: {stats['total_applications']}")
        logger.info(f"이번 주 지원 수: {stats['week_applications']}")
        logger.info(f"이번 달 지원 수: {stats['month_applications']}")
        
        if stats['top_companies']:
            logger.info("가장 많이 지원한 회사:")
            for company, count in stats['top_companies']:
                logger.info(f"  - {company}: {count}회")
                
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"통계 요약 로그 생성 중 오류: {str(e)}")
