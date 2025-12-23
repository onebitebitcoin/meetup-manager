#!/bin/bash

# 통합 개발 스크립트
# - 실행 중인 개발 서버를 정리하고 Django/Vue 개발 서버를 다시 시작합니다.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    log "서버를 종료합니다..."
    if [ -n "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null
        success "Backend 서버가 종료되었습니다."
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID 2>/dev/null
        success "Frontend 서버가 종료되었습니다."
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

ensure_project_root() {
    if [ ! -f "manage.py" ] || [ ! -d "meetup-manager" ]; then
        error "프로젝트 루트 디렉토리에서 실행해주세요. (manage.py와 meetup-manager 폴더가 있는 위치)"
        exit 1
    fi
}

kill_existing_processes() {
    log "기존 실행 중인 개발 서버를 종료합니다..."

    local DJANGO_PIDS=$(lsof -t -i:8000 2>/dev/null)
    if [ -n "$DJANGO_PIDS" ]; then
        log "기존 Django 서버 종료 중... (PIDs: $DJANGO_PIDS)"
        echo $DJANGO_PIDS | xargs kill -9 2>/dev/null
        success "기존 Django 서버가 종료되었습니다."
    fi

    local VITE_PIDS=$(lsof -t -i:7173 2>/dev/null)
    if [ -n "$VITE_PIDS" ]; then
        log "기존 Vue.js 서버 종료 중... (PIDs: $VITE_PIDS)"
        echo $VITE_PIDS | xargs kill -9 2>/dev/null
        success "기존 Vue.js 서버가 종료되었습니다."
    fi

    local NODE_PIDS=$(pgrep -f "vite|vue-cli-service|npm.*dev" 2>/dev/null)
    if [ -n "$NODE_PIDS" ]; then
        log "Node.js 개발 프로세스를 정리합니다... (PIDs: $NODE_PIDS)"
        echo $NODE_PIDS | xargs kill -9 2>/dev/null
        success "Node.js 프로세스가 종료되었습니다."
    fi

    local PYTHON_PIDS=$(pgrep -f "manage.py runserver" 2>/dev/null)
    if [ -n "$PYTHON_PIDS" ]; then
        log "Django runserver 프로세스를 정리합니다... (PIDs: $PYTHON_PIDS)"
        echo $PYTHON_PIDS | xargs kill -9 2>/dev/null
        success "Django 프로세스가 종료되었습니다."
    fi
}

activate_virtualenv() {
    if [ -d "venv" ]; then
        log "Python 가상환경을 활성화합니다..."
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        log "Python 가상환경을 활성화합니다..."
        source .venv/bin/activate
    fi
}

check_backend_dependencies() {
    log "Backend 의존성을 확인합니다..."
    python3 -c "import django" 2>/dev/null || {
        error "Django가 설치되지 않았습니다. pip install -r requirements.txt를 실행해주세요."
        exit 1
    }
}

ensure_frontend_dependencies() {
    log "Frontend 의존성을 확인합니다..."
    if [ ! -d "meetup-manager/node_modules" ]; then
        warning "node_modules가 없습니다. npm install을 실행합니다..."
        pushd meetup-manager >/dev/null
        npm install
        popd >/dev/null
    fi
}

apply_pending_migrations() {
    log "데이터베이스 마이그레이션을 확인합니다..."
    if python3 manage.py showmigrations --plan | grep -q '\\[ \\]'; then
        log "새로운 마이그레이션을 적용합니다..."
        python3 manage.py migrate
    fi
}

start_backend() {
    log "Django 백엔드 서버를 시작합니다... (포트: 8000)"
    > django.log
    python3 manage.py runserver 8000 > django.log 2>&1 &
    BACKEND_PID=$!
    sleep 5

    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        error "Django 서버 프로세스가 종료되었습니다."
        [ -f django.log ] && tail -20 django.log
        exit 1
    fi

    local retries=0
    while [ $retries -lt 10 ]; do
        if lsof -t -i:8000 >/dev/null 2>&1; then
            success "Django 서버가 시작되었습니다. (PID: $BACKEND_PID)"
            return
        fi
        retries=$((retries + 1))
        log "Django 서버 포트 확인 중... ($retries/10)"
        sleep 1
    done

    error "Django 서버가 포트 8000을 리스닝하지 않습니다."
    [ -f django.log ] && tail -20 django.log
    kill $BACKEND_PID 2>/dev/null
    exit 1
}

start_frontend() {
    log "Vue.js 프론트엔드 서버를 시작합니다... (포트: 7173)"
    > vite.log

    local NODE_PIDS=$(pgrep -f "vite|vue-cli-service|npm.*dev" 2>/dev/null)
    if [ -n "$NODE_PIDS" ]; then
        log "남아있는 Node.js 프로세스를 정리합니다..."
        echo $NODE_PIDS | xargs kill -9 2>/dev/null
    fi

    pushd meetup-manager >/dev/null
    npm run dev > ../vite.log 2>&1 &
    FRONTEND_PID=$!
    popd >/dev/null

    sleep 5
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        error "Vue.js 서버 프로세스가 종료되었습니다."
        [ -f vite.log ] && tail -20 vite.log
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi

    local retries=0
    while [ $retries -lt 15 ]; do
        if lsof -t -i:7173 >/dev/null 2>&1; then
            success "Vue.js 서버가 시작되었습니다. (PID: $FRONTEND_PID)"
            return
        fi
        retries=$((retries + 1))
        log "Vue.js 서버 포트 확인 중... ($retries/15)"
        sleep 1
    done

    error "Vue.js 서버가 포트 7173을 리스닝하지 않습니다."
    [ -f vite.log ] && tail -20 vite.log
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 1
}

print_summary() {
    echo ""
    success "🚀 개발 서버가 성공적으로 시작되었습니다!"
    echo ""
    echo -e "${GREEN}📍 서비스 주소:${NC}"
    echo -e "  🌐 Frontend: ${BLUE}http://localhost:7173${NC}"
    echo -e "  ⚙️  Backend:  ${BLUE}http://localhost:8000${NC}"
    echo -e "  📊 Admin:    ${BLUE}http://localhost:8000/admin${NC}"
    echo ""
    echo -e "${YELLOW}📋 로그 파일:${NC}"
    echo -e "  📄 Django: django.log"
    echo -e "  📄 Vite:   vite.log"
    echo ""
    echo -e "${RED}종료하려면 Ctrl+C를 누르세요${NC}"
    echo ""
}

monitor_processes() {
    while true; do
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            error "Django 서버가 중단되었습니다."
            break
        fi
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            error "Vue.js 서버가 중단되었습니다."
            break
        fi
        sleep 5
    done
    cleanup
}

main() {
    ensure_project_root
    kill_existing_processes
    activate_virtualenv
    check_backend_dependencies
    ensure_frontend_dependencies
    apply_pending_migrations
    start_backend
    start_frontend
    print_summary
    monitor_processes
}

main "$@"
