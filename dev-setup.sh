#!/bin/bash

# 개발 환경 초기 설정 스크립트
# 의존성 설치, 데이터베이스 설정, 초기 데이터 생성

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

log "🚀 개발 환경을 설정합니다..."

# Python 가상환경 생성 (선택사항)
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    log "Python 가상환경을 생성합니다..."
    python3 -m venv venv
    success "가상환경이 생성되었습니다."
fi

# Python 가상환경 활성화
if [ -d "venv" ]; then
    log "Python 가상환경을 활성화합니다..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    log "Python 가상환경을 활성화합니다..."
    source .venv/bin/activate
fi

# Backend 의존성 설치
if [ -f "requirements.txt" ]; then
    log "Python 의존성을 설치합니다..."
    pip install -r requirements.txt
    success "Python 의존성 설치가 완료되었습니다."
else
    warning "requirements.txt가 없습니다."
fi

# Frontend 의존성 설치
if [ -f "meetup-manager/package.json" ]; then
    log "Node.js 의존성을 설치합니다..."
    cd meetup-manager
    npm install
    cd ..
    success "Node.js 의존성 설치가 완료되었습니다."
else
    error "meetup-manager/package.json이 없습니다."
    exit 1
fi

# 데이터베이스 마이그레이션
log "데이터베이스 마이그레이션을 실행합니다..."
python3 manage.py makemigrations
python3 manage.py migrate
success "데이터베이스 마이그레이션이 완료되었습니다."

# 초기 데이터 생성 (있는 경우)
if python3 manage.py help | grep -q "seed_data"; then
    log "초기 데이터를 생성합니다..."
    python3 manage.py seed_data
    success "초기 데이터 생성이 완료되었습니다."
fi

# 슈퍼유저 생성 (선택사항)
read -p "Django 슈퍼유저를 생성하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "슈퍼유저를 생성합니다..."
    python3 manage.py createsuperuser
fi

echo ""
success "🎉 개발 환경 설정이 완료되었습니다!"
echo ""
echo -e "${GREEN}다음 단계:${NC}"
echo -e "  1. ${BLUE}./dev-start.sh${NC} - 개발 서버 시작"
echo -e "  2. ${BLUE}./dev-stop.sh${NC}  - 개발 서버 중지"
echo ""
echo -e "${YELLOW}유용한 명령어:${NC}"
echo -e "  📊 Django Admin: ${BLUE}http://localhost:8000/admin${NC}"
echo -e "  🌐 Frontend:     ${BLUE}http://localhost:5173${NC}"
echo ""