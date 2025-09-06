#!/bin/bash

# 개발 서버 시작 스크립트
# Frontend (Vue.js)와 Backend (Django)를 동시에 실행합니다

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 프로젝트 루트 디렉토리 확인
if [ ! -f "manage.py" ] || [ ! -d "meetup-manager" ]; then
    error "프로젝트 루트 디렉토리에서 실행해주세요. (manage.py와 meetup-manager 폴더가 있는 위치)"
    exit 1
fi

log "개발 서버를 시작합니다..."

# 기존 프로세스 종료
cleanup() {
    log "서버를 종료합니다..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        success "Backend 서버가 종료되었습니다."
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        success "Frontend 서버가 종료되었습니다."
    fi
    exit 0
}

# 기존 실행 중인 서버들 종료
kill_existing_servers() {
    log "기존 실행 중인 서버를 확인하고 종료합니다..."
    
    # Django 서버 종료 (포트 8000)
    DJANGO_PIDS=$(lsof -t -i:8000 2>/dev/null)
    if [ ! -z "$DJANGO_PIDS" ]; then
        log "기존 Django 서버를 종료합니다... (PIDs: $DJANGO_PIDS)"
        echo $DJANGO_PIDS | xargs kill -9 2>/dev/null
        sleep 1
        success "기존 Django 서버가 종료되었습니다."
    fi
    
    # Vue.js/Vite 서버 종료 (포트 5173)
    VITE_PIDS=$(lsof -t -i:5173 2>/dev/null)
    if [ ! -z "$VITE_PIDS" ]; then
        log "기존 Vue.js 서버를 종료합니다... (PIDs: $VITE_PIDS)"
        echo $VITE_PIDS | xargs kill -9 2>/dev/null
        sleep 1
        success "기존 Vue.js 서버가 종료되었습니다."
    fi
    
    # 추가 Node.js 프로세스 정리 (vite, vue-cli-service 등)
    NODE_PIDS=$(pgrep -f "vite|vue-cli-service|npm.*dev" 2>/dev/null)
    if [ ! -z "$NODE_PIDS" ]; then
        log "기존 Node.js 개발 프로세스를 종료합니다... (PIDs: $NODE_PIDS)"
        echo $NODE_PIDS | xargs kill -9 2>/dev/null
        sleep 1
        success "기존 Node.js 프로세스가 종료되었습니다."
    fi
    
    # Python manage.py runserver 프로세스 정리
    PYTHON_PIDS=$(pgrep -f "manage.py runserver" 2>/dev/null)
    if [ ! -z "$PYTHON_PIDS" ]; then
        log "기존 Django runserver 프로세스를 종료합니다... (PIDs: $PYTHON_PIDS)"
        echo $PYTHON_PIDS | xargs kill -9 2>/dev/null
        sleep 1
        success "기존 Django 프로세스가 종료되었습니다."
    fi
    
    # 포트 해제 확인
    sleep 2
    if lsof -t -i:8000 >/dev/null 2>&1; then
        warning "포트 8000이 여전히 사용 중입니다."
    fi
    if lsof -t -i:5173 >/dev/null 2>&1; then
        warning "포트 5173이 여전히 사용 중입니다."
    fi
}

# Ctrl+C 처리
trap cleanup SIGINT SIGTERM

# 기존 서버들 종료
kill_existing_servers

# Python 가상환경 활성화 (선택사항)
if [ -d "venv" ]; then
    log "Python 가상환경을 활성화합니다..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    log "Python 가상환경을 활성화합니다..."
    source .venv/bin/activate
fi

# Backend 의존성 확인
log "Backend 의존성을 확인합니다..."
python3 -c "import django" 2>/dev/null || {
    error "Django가 설치되지 않았습니다. pip install -r requirements.txt를 실행해주세요."
    exit 1
}

# Frontend 의존성 확인
log "Frontend 의존성을 확인합니다..."
if [ ! -d "meetup-manager/node_modules" ]; then
    warning "node_modules가 없습니다. npm install을 실행합니다..."
    cd meetup-manager
    npm install
    cd ..
fi

# 데이터베이스 마이그레이션 확인
log "데이터베이스 마이그레이션을 확인합니다..."
python3 manage.py showmigrations --plan | grep -q '\[ \]' && {
    log "새로운 마이그레이션이 있습니다. 마이그레이션을 실행합니다..."
    python3 manage.py migrate
}

# Backend 서버 시작 (Django)
log "Django 백엔드 서버를 시작합니다... (포트: 8000)"

# 로그 파일 초기화
> django.log

# Django 서버 시작
python3 manage.py runserver 8000 > django.log 2>&1 &
BACKEND_PID=$!

# Backend 서버 시작 대기 및 확인
log "Django 서버 시작을 확인합니다..."
sleep 5

# 프로세스 상태 확인
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    error "Django 서버 프로세스가 종료되었습니다."
    if [ -f "django.log" ]; then
        error "Django 로그 내용:"
        tail -10 django.log
    fi
    exit 1
fi

# 포트 리스닝 확인
PORT_CHECK_COUNT=0
while [ $PORT_CHECK_COUNT -lt 10 ]; do
    if lsof -t -i:8000 >/dev/null 2>&1; then
        success "Django 서버가 시작되었습니다. (PID: $BACKEND_PID)"
        break
    fi
    sleep 1
    PORT_CHECK_COUNT=$((PORT_CHECK_COUNT + 1))
    log "Django 서버 포트 확인 중... ($PORT_CHECK_COUNT/10)"
done

if [ $PORT_CHECK_COUNT -eq 10 ]; then
    error "Django 서버가 포트 8000을 리스닝하지 않습니다."
    if [ -f "django.log" ]; then
        error "Django 로그 내용:"
        tail -10 django.log
    fi
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Frontend 서버 시작 (Vue.js)
log "Vue.js 프론트엔드 서버를 시작합니다... (포트: 5173)"

# Vite 로그 파일 초기화
> vite.log

# Node.js 관련 기존 프로세스 한번 더 정리
NODE_PIDS=$(pgrep -f "vite|vue-cli-service|npm.*dev" 2>/dev/null)
if [ ! -z "$NODE_PIDS" ]; then
    log "남아있는 Node.js 프로세스를 정리합니다..."
    echo $NODE_PIDS | xargs kill -9 2>/dev/null
    sleep 2
fi

cd meetup-manager
npm run dev > ../vite.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Frontend 서버 시작 대기 및 확인
log "Vue.js 서버 시작을 확인합니다..."
sleep 5

# 프로세스 상태 확인
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    error "Vue.js 서버 프로세스가 종료되었습니다."
    if [ -f "vite.log" ]; then
        error "Vite 로그 내용:"
        tail -10 vite.log
    fi
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 포트 리스닝 확인
VITE_PORT_CHECK_COUNT=0
while [ $VITE_PORT_CHECK_COUNT -lt 15 ]; do
    if lsof -t -i:5173 >/dev/null 2>&1; then
        success "Vue.js 서버가 시작되었습니다. (PID: $FRONTEND_PID)"
        break
    fi
    sleep 1
    VITE_PORT_CHECK_COUNT=$((VITE_PORT_CHECK_COUNT + 1))
    log "Vue.js 서버 포트 확인 중... ($VITE_PORT_CHECK_COUNT/15)"
done

if [ $VITE_PORT_CHECK_COUNT -eq 15 ]; then
    error "Vue.js 서버가 포트 5173을 리스닝하지 않습니다."
    if [ -f "vite.log" ]; then
        error "Vite 로그 내용:"
        tail -10 vite.log
    fi
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
success "🚀 개발 서버가 성공적으로 시작되었습니다!"
echo ""
echo -e "${GREEN}📍 서비스 주소:${NC}"
echo -e "  🌐 Frontend: ${BLUE}http://localhost:5173${NC}"
echo -e "  ⚙️  Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "  📊 Admin:    ${BLUE}http://localhost:8000/admin${NC}"
echo ""
echo -e "${YELLOW}📋 로그 파일:${NC}"
echo -e "  📄 Django: django.log"
echo -e "  📄 Vite:   vite.log"
echo ""
echo -e "${RED}종료하려면 Ctrl+C를 누르세요${NC}"
echo ""

# 서버 상태 모니터링
while true; do
    # Backend 상태 확인
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        error "Django 서버가 중단되었습니다."
        break
    fi
    
    # Frontend 상태 확인  
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        error "Vue.js 서버가 중단되었습니다."
        break
    fi
    
    sleep 5
done

# 정리
cleanup