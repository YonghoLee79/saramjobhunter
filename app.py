#!/usr/bin/env python3
"""
사람인 자동 지원 웹 앱
Saramin Job Application Web App
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import threading
import time
import os
from datetime import datetime
import json

from config import Config
from database import ApplicationDatabase
from logger_config import setup_logger
from saramin_bot import SaraminBot

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# 글로벌 상태 관리
app_state = {
    'running': False,
    'progress': '',
    'logs': [],
    'stats': {},
    'error': None
}

def run_bot_background(config_data):
    """백그라운드에서 봇 실행"""
    global app_state
    
    try:
        app_state['running'] = True
        app_state['error'] = None
        app_state['logs'] = []
        
        # 설정 업데이트
        update_config(config_data)
        
        # 로거 설정
        logger = setup_logger("saramin_bot.log", "INFO")
        
        # 데이터베이스 초기화
        db = ApplicationDatabase()
        db.init_database()
        
        # 당일 실행 확인
        today = datetime.now().strftime('%Y-%m-%d')
        if db.is_executed_today(today):
            app_state['error'] = "오늘 이미 실행되었습니다."
            app_state['running'] = False
            return
        
        app_state['progress'] = "설정 로드 완료"
        add_log("설정 및 데이터베이스 초기화 완료")
        
        # 봇 실행
        config = Config()
        bot = SaraminBot(config, db, logger)
        
        app_state['progress'] = "브라우저 시작 중..."
        add_log("Chrome 브라우저 시작")
        
        # 로그인
        app_state['progress'] = "사람인 로그인 중..."
        if not bot.login():
            app_state['error'] = "로그인 실패"
            app_state['running'] = False
            bot.close()
            return
        
        add_log("로그인 성공")
        
        # 채용공고 검색 및 지원
        app_state['progress'] = "채용공고 검색 및 지원 중..."
        applied_count = bot.search_and_apply_jobs()
        
        # 실행 기록
        db.record_execution(today, applied_count)
        
        # 결과 업데이트
        app_state['stats'] = {
            'applied_count': applied_count,
            'execution_date': today,
            'keywords': config.keyword_list
        }
        
        app_state['progress'] = f"완료: {applied_count}개 지원"
        add_log(f"총 {applied_count}개 채용공고에 지원 완료")
        
        bot.close()
        
    except Exception as e:
        app_state['error'] = f"오류 발생: {str(e)}"
        add_log(f"오류: {str(e)}")
    finally:
        app_state['running'] = False

def add_log(message):
    """로그 추가"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    app_state['logs'].append(f"[{timestamp}] {message}")
    if len(app_state['logs']) > 50:  # 최대 50개 로그 유지
        app_state['logs'].pop(0)

def update_config(config_data):
    """설정 파일 업데이트"""
    env_content = f"""# 사람인 로그인 정보
SARAMIN_USERNAME={config_data.get('username', '')}
SARAMIN_PASSWORD={config_data.get('password', '')}

# 검색 조건 (여러 키워드는 쉼표로 구분)
SEARCH_KEYWORDS={config_data.get('keywords', '바이오,제약,기술영업,PM,설비,머신비젼,프로젝트 매니저')}
LOCATION={config_data.get('location', '서울')}
JOB_TYPE={config_data.get('job_type', '정규직')}

# 지원 설정
MAX_APPLICATIONS_PER_DAY={config_data.get('max_apps', '10')}
MAX_PAGES={config_data.get('max_pages', '5')}
MIN_WAIT_TIME={config_data.get('min_wait', '30')}
MAX_WAIT_TIME={config_data.get('max_wait', '60')}

# 브라우저 설정
HEADLESS=true
BROWSER_TIMEOUT=30
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """현재 설정 조회"""
    try:
        config = Config()
        return jsonify({
            'keywords': ','.join(config.keyword_list),
            'location': config.location,
            'job_type': config.job_type,
            'max_apps': config.max_applications_per_day,
            'max_pages': config.max_pages
        })
    except:
        return jsonify({
            'keywords': '바이오,제약,기술영업,PM,설비,머신비젼,프로젝트 매니저',
            'location': '서울',
            'job_type': '정규직',
            'max_apps': 10,
            'max_pages': 5
        })

@app.route('/api/start', methods=['POST'])
def start_bot():
    """봇 시작"""
    if app_state['running']:
        return jsonify({'success': False, 'message': '이미 실행 중입니다'})
    
    config_data = request.json
    
    # 필수 정보 확인
    if not config_data.get('username') or not config_data.get('password'):
        return jsonify({'success': False, 'message': '로그인 정보를 입력해주세요'})
    
    # 백그라운드에서 봇 실행
    thread = threading.Thread(target=run_bot_background, args=(config_data,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '자동 지원을 시작합니다'})

@app.route('/api/status', methods=['GET'])
def get_status():
    """현재 상태 조회"""
    return jsonify({
        'running': app_state['running'],
        'progress': app_state['progress'],
        'logs': app_state['logs'][-10:],  # 최근 10개 로그
        'error': app_state['error'],
        'stats': app_state['stats']
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """지원 이력 조회"""
    try:
        db = ApplicationDatabase()
        
        # 최근 지원 이력
        applications = db.get_application_history(days=30)
        
        # 실행 이력
        executions = db.get_execution_history(days=30)
        
        # 통계
        stats = db.get_statistics()
        
        return jsonify({
            'applications': applications,
            'executions': executions,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/test-login', methods=['POST'])
def test_login():
    """로그인 테스트"""
    config_data = request.json
    
    if not config_data.get('username') or not config_data.get('password'):
        return jsonify({'success': False, 'message': '로그인 정보를 입력해주세요'})
    
    try:
        # 임시 설정 업데이트
        update_config(config_data)
        
        # 로그인 테스트
        config = Config()
        db = ApplicationDatabase()
        logger = setup_logger()
        
        bot = SaraminBot(config, db, logger)
        
        success = bot.login()
        bot.close()
        
        if success:
            return jsonify({'success': True, 'message': '로그인 성공'})
        else:
            return jsonify({'success': False, 'message': '로그인 실패'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

if __name__ == '__main__':
    print("사람인 자동 지원 웹 앱을 시작합니다...")
    print("브라우저에서 http://0.0.0.0:5000 에 접속하세요")
    app.run(host='0.0.0.0', port=5000, debug=True)