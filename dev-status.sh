#!/bin/bash

# 개발 서버 상태 확인 스크립트

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log "개발 서버 상태를 확인합니다..."
echo ""

# Django 서버 상태 확인 (포트 7000)
if lsof -t -i:7000 >/dev/null 2>&1; then
    DJANGO_PID=$(lsof -t -i:7000)
    success "Django 서버가 실행 중입니다. (PID: $DJANGO_PID, 포트: 7000)"
    
    # Django 서버 응답 확인
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:7000 | grep -q "200\\|301\\|302"; then
        success "Django 서버가 정상적으로 응답합니다."
    else
        warning "Django 서버가 응답하지 않습니다."
    fi
else
    error "Django 서버가 실행되지 않았습니다."
fi

echo ""

# Vue.js 서버 상태 확인 (포트 7173)
if lsof -t -i:7173 >/dev/null 2>&1; then
    VITE_PID=$(lsof -t -i:7173)
    success "Vue.js 서버가 실행 중입니다. (PID: $VITE_PID, 포트: 7173)"
    
    # Vue.js 서버 응답 확인
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:7173 | grep -q "200"; then
        success "Vue.js 서버가 정상적으로 응답합니다."
    else
        warning "Vue.js 서버가 응답하지 않습니다."
    fi
else
    error "Vue.js 서버가 실행되지 않았습니다."
fi

echo ""

# 추가 프로세스 확인
NODE_PROCESSES=$(pgrep -f "vite|vue-cli-service" 2>/dev/null | wc -l)
PYTHON_PROCESSES=$(pgrep -f "manage.py runserver" 2>/dev/null | wc -l)

if [ $NODE_PROCESSES -gt 0 ]; then
    log "실행 중인 Node.js 프로세스: $NODE_PROCESSES개"
fi

if [ $PYTHON_PROCESSES -gt 0 ]; then
    log "실행 중인 Python 서버 프로세스: $PYTHON_PROCESSES개"
fi

echo ""

# 로그 파일 상태 확인
if [ -f "django.log" ]; then
    DJANGO_LOG_SIZE=$(wc -l < django.log)
    log "Django 로그 파일: django.log ($DJANGO_LOG_SIZE 라인)"
fi

if [ -f "vite.log" ]; then
    VITE_LOG_SIZE=$(wc -l < vite.log)
    log "Vite 로그 파일: vite.log ($VITE_LOG_SIZE 라인)"
fi

echo ""
log "상태 확인이 완료되었습니다."
