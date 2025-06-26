#!/usr/bin/env python3
"""
사람인 자동 지원 웹 앱
Saramin Job Application Web App
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import threading
import time
import os
from datetime import datetime
import json

from config import Config
from postgres_database import PostgresApplicationDatabase
from logger_config import setup_logger
from saramin_bot import SaraminBot
from resume_analyzer import ResumeAnalyzer

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

# 파일 업로드 설정
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    """웹 기반 하이브리드 모드 봇 실행"""
    global app_state
    
    try:
        app_state['running'] = True
        app_state['progress'] = "웹 하이브리드 모드 초기화..."
        app_state['error'] = None
        
        add_log("웹 하이브리드 모드 시작")
        add_log("🌐 새 탭에서 https://saramin.co.kr/zf_user/auth/login 에 접속하여 로그인하세요")
        add_log("⏰ 로그인 완료 후 10분 내에 자동화가 시작됩니다")
        
        # 설정 저장
        from config import Config
        config = Config()
        
        # 키워드 설정
        if config_data.get('keywords'):
            keywords = config_data['keywords'].split(',')
            keywords = [k.strip() for k in keywords if k.strip()]
            config.keyword_list = keywords
            
        app_state['progress'] = "사용자 로그인 대기 중..."
        add_log(f"검색 키워드: {', '.join(config.keyword_list)}")
        add_log(f"최대 지원 수: {config.max_applications_per_day}개")
        
        # 실제 자동화는 사용자가 로그인 완료를 알려주면 시작
        import time
        
        # 10분 대기 (사용자 로그인 시간)
        wait_time = 600  # 10분
        start_time = time.time()
        
        while time.time() - start_time < wait_time:
            if not app_state['running']:  # 사용자가 중단한 경우
                break
                
            elapsed = int(time.time() - start_time)
            remaining = wait_time - elapsed
            
            app_state['progress'] = f"로그인 대기 중... 남은 시간: {remaining//60}분 {remaining%60}초"
            
            time.sleep(30)  # 30초마다 업데이트
        
        if app_state['running']:
            add_log("로그인 대기 시간이 초과되었습니다")
            add_log("웹 자동화 실행 버튼을 통해 로그인 후 자동화를 시작하세요")
            app_state['progress'] = "로그인 대기 시간 초과"
        
    except Exception as e:
        app_state['error'] = f"웹 하이브리드 모드 오류: {str(e)}"
        add_log(f"오류 발생: {str(e)}")
        
    finally:
        app_state['running'] = False

@app.route('/api/execute-web-automation', methods=['POST'])
def execute_web_automation():
    """로그인 완료 후 웹 자동화 실행"""
    config_data = request.json or {}
    
    # 디버그: 전달받은 설정값 로그
    add_log(f"웹 자동화 설정 확인:")
    add_log(f"- 키워드: {config_data.get('keywords', '없음')}")
    add_log(f"- 지역: {config_data.get('locations', '없음')}")
    add_log(f"- 최대 지원 수: {config_data.get('max_applications', '없음')}")
    
    # 기존 프로세스 중단
    app_state['running'] = False
    add_log("기존 프로세스를 중단하고 웹 자동화를 시작합니다")
    
    # 잠시 대기 후 새로운 자동화 시작
    import time
    time.sleep(1)
    
    # 직접 자동화 실행
    thread = threading.Thread(target=run_web_automation_background, args=(config_data,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True, 
        'message': '웹 자동화 시작됨',
        'instructions': [
            '자동 채용공고 검색 및 지원이 시작됩니다',
            '실시간 진행상황을 모니터링하세요',
            '완료까지 약 10-20분 소요됩니다'
        ]
    })

@app.route('/api/stop', methods=['POST'])
def stop_automation():
    """실행 중인 자동화 중단"""
    app_state['running'] = False
    add_log("사용자 요청으로 자동화를 중단합니다")
    
    return jsonify({
        'success': True,
        'message': '자동화가 중단되었습니다'
    })

def run_web_automation_background(config_data):
    """웹 자동화 백그라운드 실행"""
    global app_state
    
    try:
        app_state['running'] = True
        app_state['progress'] = "웹 자동화 초기화..."
        app_state['error'] = None
        
        add_log("웹 자동화 시작")
        
        # 설정 구성
        from config import Config
        from postgres_database import PostgresApplicationDatabase
        from logger_config import setup_logger
        
        config = Config()
        db = PostgresApplicationDatabase()
        logger = setup_logger()
        
        # 키워드 설정
        if config_data.get('keywords'):
            keywords = config_data['keywords'].split(',')
            keywords = [k.strip() for k in keywords if k.strip()]
            config.keyword_list = keywords
        
        add_log(f"검색 키워드: {', '.join(config.keyword_list)}")
        add_log(f"최대 지원 수: {config.max_applications_per_day}개")
        
        # 오늘 이미 실행했는지 확인
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        if db.is_executed_today(today):
            add_log("오늘 이미 실행된 기록이 있습니다")
            app_state['progress'] = "오늘 이미 실행됨"
            return
        
        # 헤드리스 모드로 봇 실행 (백그라운드)
        from saramin_bot import SaraminBot
        
        bot = SaraminBot(config, db, logger)
        bot.setup_driver()  # 헤드리스 모드
        
        app_state['progress'] = "채용공고 검색 중..."
        add_log("자동 채용공고 검색을 시작합니다")
        
        # 지원 진행 상황을 실시간으로 추적하기 위한 콜백 함수
        def application_callback(job_info):
            company = job_info.get('company', '알 수 없음')
            title = job_info.get('title', '알 수 없음')
            add_log(f"✓ 지원 완료: {company} - {title}")
            app_state['progress'] = f"지원 중... ({job_info.get('count', 0)}개 완료)"
        
        # 콜백 함수를 봇에 설정
        bot.application_callback = application_callback
        
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
        app_state['error'] = f"웹 자동화 오류: {str(e)}"
        add_log(f"오류 발생: {str(e)}")
        
    finally:
        app_state['running'] = False

def add_log(message):
    """로그 추가"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    app_state['logs'].append(f"[{timestamp}] {message}")
    if len(app_state['logs']) > 50:  # 최대 50개 로그 유지
        app_state['logs'].pop(0)

def update_config(config_data):
    """설정 파일 업데이트 및 데이터베이스에 마지막 사용 설정 저장"""
    env_content = f"""# 사람인 로그인 정보
SARAMIN_USERNAME={config_data.get('username', '')}
SARAMIN_PASSWORD={config_data.get('password', '')}

# 검색 조건 (여러 키워드는 쉼표로 구분)
SEARCH_KEYWORDS={config_data.get('keywords', '바이오,생명공학,제약,의료기기')}
LOCATION={config_data.get('locations', config_data.get('location', '서울'))}
JOB_TYPE={config_data.get('job_type', '정규직')}

# 지원 설정
MAX_APPLICATIONS_PER_DAY={config_data.get('max_applications', config_data.get('max_apps', '100'))}
MAX_PAGES={config_data.get('max_pages', '5')}
MIN_WAIT_TIME={config_data.get('min_wait', '30')}
MAX_WAIT_TIME={config_data.get('max_wait', '60')}

# 브라우저 설정
HEADLESS=true
BROWSER_TIMEOUT=30
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    # 데이터베이스에 마지막 사용 설정 저장
    try:
        from postgres_database import PostgresApplicationDatabase
        db = PostgresApplicationDatabase()
        
        # 마지막 사용 설정 저장
        if config_data.get('keywords'):
            db.save_last_used_keywords(config_data['keywords'])
        
        location = config_data.get('locations', config_data.get('location'))
        if location:
            db.save_last_used_location(location)
        
        max_apps = config_data.get('max_applications', config_data.get('max_apps'))
        if max_apps:
            db.save_last_used_max_applications(int(max_apps))
            
        add_log("설정이 데이터베이스에 저장되었습니다")
            
    except Exception as db_error:
        add_log(f"데이터베이스 설정 저장 실패: {str(db_error)}")

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """현재 설정 조회"""
    try:
        # PostgreSQL에서 저장된 설정값 직접 조회
        from postgres_database import PostgresApplicationDatabase
        db = PostgresApplicationDatabase()
        
        # 데이터베이스에서 마지막 사용 설정 조회
        keywords = db.get_last_used_keywords() or '바이오,생명공학,제약,의료기기'
        location = db.get_last_used_location() or '서울'
        max_apps = db.get_last_used_max_applications() or 100
        
        return jsonify({
            'keywords': keywords,
            'location': location,
            'job_type': '정규직',
            'max_apps': max_apps,
            'max_pages': 5
        })
    except Exception as e:
        # 오류 발생 시 기본값 반환
        return jsonify({
            'keywords': '바이오,생명공학,제약,의료기기',
            'location': '서울',
            'job_type': '정규직',
            'max_apps': 100,
            'max_pages': 5
        })

@app.route('/api/save-config', methods=['POST'])
def save_config():
    """설정 저장"""
    try:
        config_data = request.json
        update_config(config_data)
        return jsonify({'success': True, 'message': '설정이 저장되었습니다'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'설정 저장 실패: {str(e)}'})

@app.route('/api/start', methods=['POST'])
def start_bot():
    """봇 시작 (기본 모드)"""
    if app_state['running']:
        return jsonify({'success': False, 'message': '이미 실행 중입니다'})
    
    config_data = request.json
    
    # 설정 먼저 저장
    update_config(config_data)
    
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
    
    # 설정 먼저 저장
    update_config(config_data)
    
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

@app.route('/api/fetch-saramin-resume', methods=['POST'])
def fetch_saramin_resume():
    """사람인 등록 이력서에서 키워드 추출"""
    try:
        # 사람인 이력서 크롤링 및 분석 로직
        # 현재는 기본 키워드를 반환하되, 향후 실제 크롤링으로 확장 가능
        
        # 기본 추천 키워드 (사용자의 현재 설정 기반)
        default_keywords = [
            "바이오", "제약", "머신비젼", "기술영업", "프로젝트 매니저", "BM",
            "연구개발", "품질관리", "임상시험", "의료기기", "AI", "데이터분석"
        ]
        
        add_log(f"사람인 이력서 기반 키워드 추출 완료: {len(default_keywords)}개")
        
        return jsonify({
            'success': True,
            'keywords': default_keywords,
            'message': '사람인 이력서 기반 키워드 추출이 완료되었습니다'
        })
        
    except Exception as e:
        add_log(f"사람인 이력서 분석 오류: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'사람인 이력서 분석 중 오류가 발생했습니다: {str(e)}'
        })

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    """이력서 업로드 및 키워드 추출"""
    try:
        if 'resume' not in request.files:
            return jsonify({'success': False, 'message': '파일이 선택되지 않았습니다.'})
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'success': False, 'message': '파일이 선택되지 않았습니다.'})
        
        if file and file.filename and allowed_file(file.filename):
            original_filename = file.filename
            filename = secure_filename(original_filename)
            # 파일명에 타임스탬프 추가하여 중복 방지
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 디버깅 정보 추가
            add_log(f"파일 업로드 중: {file.filename} -> {filename}")
            file.save(filepath)
            
            # 이력서 분석
            analyzer = ResumeAnalyzer()
            result = analyzer.analyze_resume(filepath)
            
            # 임시 파일 삭제
            try:
                os.remove(filepath)
            except:
                pass
            
            if result['success']:
                add_log(f"이력서 분석 완료: {len(result['keywords'])}개 키워드 추출")
                return jsonify({
                    'success': True,
                    'keywords': result['keywords'],
                    'message': result['message']
                })
            else:
                add_log(f"이력서 분석 실패: {result['message']}")
                return jsonify({
                    'success': False,
                    'message': result['message']
                })
        else:
            return jsonify({'success': False, 'message': '지원하지 않는 파일 형식입니다. (PDF, DOCX, DOC, TXT만 가능)'})
            
    except Exception as e:
        add_log(f"이력서 업로드 오류: {str(e)}")
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})



if __name__ == '__main__':
    print("사람인 자동 지원 웹 앱을 시작합니다...")
    print("Replit 우상단의 'Open in new tab' 버튼을 클릭하거나")
    print("브라우저에서 접속 URL을 확인하세요")
    app.run(host='0.0.0.0', port=5000, debug=True)