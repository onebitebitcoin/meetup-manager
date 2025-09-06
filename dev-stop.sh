#!/bin/bash

# 개발 서버 중지 스크립트
# 실행 중인 Django와 Vue.js 서버를 중지합니다

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
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log "개발 서버를 중지합니다..."

# Django 서버 중지 (포트 8000)
DJANGO_PIDS=$(lsof -t -i:8000 2>/dev/null)
if [ ! -z "$DJANGO_PIDS" ]; then
    echo $DJANGO_PIDS | xargs kill -9 2>/dev/null
    success "Django 서버가 중지되었습니다."
else
    warning "실행 중인 Django 서버를 찾을 수 없습니다."
fi

# Vue.js 서버 중지 (포트 5173)
VITE_PIDS=$(lsof -t -i:5173 2>/dev/null)
if [ ! -z "$VITE_PIDS" ]; then
    echo $VITE_PIDS | xargs kill -9 2>/dev/null
    success "Vue.js 서버가 중지되었습니다."
else
    warning "실행 중인 Vue.js 서버를 찾을 수 없습니다."
fi

# node 프로세스 중에서 vite 관련 중지
NODE_PIDS=$(pgrep -f "vite|vue-cli-service" 2>/dev/null)
if [ ! -z "$NODE_PIDS" ]; then
    echo $NODE_PIDS | xargs kill -9 2>/dev/null
    success "추가 Node.js 프로세스가 중지되었습니다."
fi

# Python manage.py runserver 프로세스 중지
PYTHON_PIDS=$(pgrep -f "manage.py runserver" 2>/dev/null)
if [ ! -z "$PYTHON_PIDS" ]; then
    echo $PYTHON_PIDS | xargs kill -9 2>/dev/null
    success "추가 Django 프로세스가 중지되었습니다."
fi

success "🛑 모든 개발 서버가 중지되었습니다."