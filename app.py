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
from postgres_database import PostgresApplicationDatabase
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
        db = PostgresApplicationDatabase()
        
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

def run_hybrid_bot_background(config_data):
    """하이브리드 모드 봇 실행"""
    global app_state
    
    try:
        app_state['running'] = True
        app_state['progress'] = "하이브리드 모드 초기화..."
        app_state['error'] = None
        
        add_log("하이브리드 모드 시작")
        
        # hybrid_automation.py를 subprocess로 실행
        import subprocess
        import os
        
        app_state['progress'] = "브라우저 열고 있습니다..."
        add_log("브라우저가 열립니다. saramin.co.kr에서 직접 로그인해주세요.")
        
        # 환경 변수 설정
        env = os.environ.copy()
        env['HEADLESS'] = 'false'  # GUI 모드로 실행
        
        # hybrid_automation.py 실행
        process = subprocess.Popen(
            ['python', 'hybrid_automation.py'],
            cwd='/home/runner/workspace',
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        app_state['progress'] = "수동 로그인 대기 중..."
        add_log("열린 브라우저에서 로그인을 완료해주세요.")
        
        # 프로세스 완료 대기 (타임아웃 30분)
        try:
            stdout, stderr = process.communicate(timeout=1800)
            
            if process.returncode == 0:
                app_state['progress'] = "하이브리드 모드 완료"
                add_log("하이브리드 자동화가 성공적으로 완료되었습니다.")
                if stdout:
                    add_log(f"실행 결과: {stdout}")
            else:
                app_state['error'] = f"하이브리드 모드 실행 실패"
                add_log(f"오류: {stderr}")
                
        except subprocess.TimeoutExpired:
            process.kill()
            app_state['error'] = "하이브리드 모드 타임아웃 (30분)"
            add_log("실행 시간이 초과되었습니다.")
        
    except Exception as e:
        app_state['error'] = f"하이브리드 모드 오류: {str(e)}"
        add_log(f"하이브리드 모드 실행 중 오류: {str(e)}")
        
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
    """봇 시작 (기본 모드)"""
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

@app.route('/api/start-hybrid', methods=['POST'])
def start_hybrid_bot():
    """하이브리드 모드 봇 시작"""
    if app_state['running']:
        return jsonify({'success': False, 'message': '이미 실행 중입니다'})
    
    config_data = request.json or {}
    
    # 하이브리드 모드 안내
    app_state['logs'].append("하이브리드 모드 시작: 브라우저에서 직접 로그인해주세요")
    
    # 하이브리드 봇 실행
    thread = threading.Thread(target=run_hybrid_bot_background, args=(config_data,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True, 
        'message': '하이브리드 모드 시작됨',
        'instructions': [
            '1. 열린 브라우저에서 saramin.co.kr에 직접 로그인하세요',
            '2. 로그인 완료 후 자동으로 채용공고 검색이 시작됩니다',
            '3. 웹 앱에서 실시간 진행상황을 확인할 수 있습니다'
        ]
    })

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
        db = PostgresApplicationDatabase()
        
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
    """고급 봇 탐지 우회 로그인 테스트"""
    config_data = request.json
    
    if not config_data.get('username') or not config_data.get('password'):
        return jsonify({'success': False, 'message': '로그인 정보를 입력해주세요'})
    
    try:
        add_log("고급 봇 탐지 우회 로그인 테스트 시작...")
        add_log(f"사용자: {config_data.get('username')}")
        
        # 임시 설정 업데이트
        update_config(config_data)
        
        # 고급 봇 탐지 우회 시스템 적용
        config = Config()
        db = PostgresApplicationDatabase()
        logger = setup_logger()
        
        bot = SaraminBot(config, db, logger)
        
        if bot.setup_driver():
            add_log("스텔스 브라우저 설정 완료")
            add_log("- 봇 탐지 우회 스크립트 적용됨")
            add_log("- 사람처럼 보이는 User-Agent 설정됨")
            
            try:
                add_log("사람인 로그인 시도 중...")
                success = bot.login()
                
                if success:
                    add_log("로그인 성공! 봇 탐지 우회 효과적")
                    bot.close()
                    return jsonify({'success': True, 'message': '로그인 테스트 성공 - 봇 탐지 우회 시스템 작동'})
                else:
                    add_log("로그인 실패 - 사람인 서버 문제 또는 추가 우회 필요")
                    bot.close()
                    return jsonify({'success': False, 'message': '로그인 실패 - 사람인 서버 상태 확인 필요'})
            except Exception as e:
                add_log(f"로그인 테스트 오류: {str(e)}")
                bot.close()
                return jsonify({'success': False, 'message': f'로그인 오류: {str(e)}'})
        else:
            add_log("브라우저 설정 실패")
            return jsonify({'success': False, 'message': '브라우저 설정 실패'})
            
    except Exception as e:
        add_log(f"로그인 테스트 오류: {str(e)}")
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

if __name__ == '__main__':
    print("사람인 자동 지원 웹 앱을 시작합니다...")
    print("브라우저에서 http://0.0.0.0:5000 에 접속하세요")
    app.run(host='0.0.0.0', port=5000, debug=True)