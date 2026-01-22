#!/bin/bash

# 서버 로그 모니터링 스크립트
# Django와 Frontend 로그를 실시간으로 확인할 수 있습니다.

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 로그 함수
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

show_help() {
    echo -e "${GREEN}🔍 서버 로그 모니터링 도구${NC}"
    echo ""
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  -h, --help        이 도움말 표시"
    echo "  -d, --django      Django 로그만 표시"
    echo "  -v, --vite        Vite 로그만 표시"
    echo "  -e, --errors      에러 로그만 표시"
    echo "  -f, --follow      실시간 로그 추적 (tail -f)"
    echo "  -l, --list        사용 가능한 로그 파일 목록"
    echo "  --last [N]        마지막 N줄만 표시 (기본: 20)"
    echo "  --search [TEXT]   특정 텍스트가 포함된 로그만 표시"
    echo ""
    echo "예시:"
    echo "  $0 -f                    # 모든 로그 실시간 추적"
    echo "  $0 -d --last 50          # Django 로그 마지막 50줄"
    echo "  $0 -e --search '500'     # 500 에러가 포함된 로그"
    echo "  $0 --search 'POST'       # POST 요청 로그만 표시"
}

# 로그 파일 목록 표시
list_logs() {
    success "📋 사용 가능한 로그 파일:"
    echo ""
    
    if [ -f "django.log" ]; then
        size=$(ls -lh django.log | awk '{print $5}')
        lines=$(wc -l < django.log)
        echo -e "  ${CYAN}django.log${NC}          - Django 서버 기본 로그 (${size}, ${lines} 라인)"
    fi
    
    if [ -f "django_detailed.log" ]; then
        size=$(ls -lh django_detailed.log | awk '{print $5}')
        lines=$(wc -l < django_detailed.log)
        echo -e "  ${CYAN}django_detailed.log${NC} - Django 상세 로그 (${size}, ${lines} 라인)"
    fi
    
    if [ -f "django_errors.log" ]; then
        size=$(ls -lh django_errors.log | awk '{print $5}')
        lines=$(wc -l < django_errors.log)
        echo -e "  ${RED}django_errors.log${NC}   - Django 에러 전용 로그 (${size}, ${lines} 라인)"
    fi
    
    if [ -f "vite.log" ]; then
        size=$(ls -lh vite.log | awk '{print $5}')
        lines=$(wc -l < vite.log)
        echo -e "  ${PURPLE}vite.log${NC}            - Vite 개발 서버 로그 (${size}, ${lines} 라인)"
    fi
    
    echo ""
}

# 로그 내용 표시 함수
show_log() {
    local file=$1
    local lines=${2:-20}
    local follow=${3:-false}
    local search=${4:-""}
    
    if [ ! -f "$file" ]; then
        error "로그 파일을 찾을 수 없습니다: $file"
        return 1
    fi
    
    if [ "$follow" = "true" ]; then
        log "📱 $file 실시간 추적 중... (Ctrl+C로 종료)"
        if [ -n "$search" ]; then
            tail -f "$file" | grep --color=always "$search"
        else
            tail -f "$file"
        fi
    else
        log "📄 $file 마지막 $lines 라인:"
        echo ""
        if [ -n "$search" ]; then
            tail -n "$lines" "$file" | grep --color=always "$search"
        else
            tail -n "$lines" "$file"
        fi
    fi
}

# 에러 로그 하이라이트 표시
show_errors() {
    local lines=${1:-20}
    local follow=${2:-false}
    
    success "🚨 에러 로그 분석 중..."
    echo ""
    
    # Django 에러 로그가 있으면 우선 표시
    if [ -f "django_errors.log" ]; then
        warning "Django 에러 로그:"
        show_log "django_errors.log" "$lines" "$follow"
        echo ""
    fi
    
    # 일반 로그에서 에러 패턴 검색
    if [ -f "django.log" ]; then
        warning "Django 일반 로그에서 에러 검색:"
        if [ "$follow" = "true" ]; then
            tail -f django.log | grep --color=always -i "error\|500\|exception\|traceback"
        else
            tail -n 100 django.log | grep --color=always -i "error\|500\|exception\|traceback" | tail -n "$lines"
        fi
    fi
}

# 모든 로그 통합 표시
show_all_logs() {
    local lines=${1:-20}
    local follow=${2:-false}
    local search=${3:-""}
    
    success "📊 통합 로그 보기"
    echo ""
    
    if [ "$follow" = "true" ]; then
        log "모든 로그 실시간 추적 중..."
        if [ -n "$search" ]; then
            ( [ -f django.log ] && tail -f django.log & [ -f vite.log ] && tail -f vite.log ) | grep --color=always "$search"
        else
            ( [ -f django.log ] && tail -f django.log & [ -f vite.log ] && tail -f vite.log )
        fi
    else
        if [ -f "django.log" ]; then
            warning "Django 로그 (마지막 $lines 라인):"
            show_log "django.log" "$lines" false "$search"
            echo ""
        fi
        
        if [ -f "vite.log" ]; then
            warning "Vite 로그 (마지막 $lines 라인):"
            show_log "vite.log" "$lines" false "$search"
            echo ""
        fi
    fi
}

# 메인 스크립트
SHOW_DJANGO=false
SHOW_VITE=false
SHOW_ERRORS=false
FOLLOW=false
LINES=20
SEARCH=""

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--django)
            SHOW_DJANGO=true
            shift
            ;;
        -v|--vite)
            SHOW_VITE=true
            shift
            ;;
        -e|--errors)
            SHOW_ERRORS=true
            shift
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -l|--list)
            list_logs
            exit 0
            ;;
        --last)
            LINES="$2"
            shift 2
            ;;
        --search)
            SEARCH="$2"
            shift 2
            ;;
        *)
            error "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
done

# 프로젝트 디렉토리 확인
if [ ! -d "backend" ]; then
    error "프로젝트 루트 디렉토리에서 실행해주세요. (backend 폴더가 있는 위치)"
    exit 1
fi

# 로그 표시
if [ "$SHOW_ERRORS" = "true" ]; then
    show_errors "$LINES" "$FOLLOW"
elif [ "$SHOW_DJANGO" = "true" ]; then
    show_log "django.log" "$LINES" "$FOLLOW" "$SEARCH"
elif [ "$SHOW_VITE" = "true" ]; then
    show_log "vite.log" "$LINES" "$FOLLOW" "$SEARCH"
else
    show_all_logs "$LINES" "$FOLLOW" "$SEARCH"
fi