#!/bin/bash
set -e

# Ubuntu 서버에서 실행하는 배포 스크립트

echo "=== Meet 앱 Ubuntu 배포 ==="

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "ERROR: .env 파일이 없습니다. .env.example을 복사하고 값을 채워넣으세요."
    echo "  cp .env.example .env && nano .env"
    exit 1
fi

# Docker / Docker Compose 확인
if ! command -v docker &> /dev/null; then
    echo "Docker 설치 중..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "Docker 설치 완료. 재로그인 후 다시 실행하세요."
    exit 0
fi

if ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose v2가 필요합니다. Docker를 최신 버전으로 업데이트하세요."
    exit 1
fi

# SSL 인증서 발급 (최초 1회)
if [ ! -d "/etc/letsencrypt/live/meet.onebitebitcoin.com" ]; then
    echo "=== SSL 인증서 발급 ==="
    # 먼저 nginx를 HTTP 전용으로 잠시 기동
    docker compose up -d nginx
    docker run --rm \
        -v $(pwd)/certbot_www:/var/www/certbot \
        -v /etc/letsencrypt:/etc/letsencrypt \
        certbot/certbot certonly \
        --webroot --webroot-path /var/www/certbot \
        -d meet.onebitebitcoin.com \
        --email onebitebitcoin@gmail.com \
        --agree-tos --non-interactive
    docker compose down
    echo "SSL 인증서 발급 완료"
fi

echo "=== 이미지 빌드 및 서비스 시작 ==="
docker compose pull db nginx
docker compose build web
docker compose up -d

echo "=== 배포 완료 ==="
echo "상태 확인: docker compose ps"
echo "로그 확인: docker compose logs -f web"
echo "사이트:    https://meet.onebitebitcoin.com"
