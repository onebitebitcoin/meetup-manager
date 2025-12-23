# 개발용 스크립트 사용법

이 프로젝트에는 개발 작업을 편리하게 하기 위한 여러 스크립트가 포함되어 있습니다.

## 📋 스크립트 목록

### 🚀 `dev-start.sh` - 개발 서버 시작
Frontend (Vue.js)와 Backend (Django)를 동시에 실행합니다.

```bash
./dev-start.sh
```

**기능:**
- Django 서버 (포트 7000) 자동 시작
- Vue.js 서버 (포트 7173) 자동 시작  
- 의존성 자동 확인
- 데이터베이스 마이그레이션 자동 실행
- 실시간 서버 상태 모니터링
- 로그 파일 생성 (django.log, vite.log)
- Ctrl+C로 두 서버 모두 안전하게 종료

### 🛑 `dev-stop.sh` - 개발 서버 중지
실행 중인 모든 개발 서버를 중지합니다.

```bash
./dev-stop.sh
```

**기능:**
- 포트 7000 (Django) 프로세스 종료
- 포트 7173 (Vue.js) 프로세스 종료
- 관련된 Node.js 및 Python 프로세스 정리

### ⚙️ `dev-setup.sh` - 개발 환경 초기 설정
프로젝트 첫 실행 시 필요한 모든 설정을 자동으로 수행합니다.

```bash
./dev-setup.sh
```

**기능:**
- Python 가상환경 생성
- Python 의존성 설치 (requirements.txt)
- Node.js 의존성 설치 (npm install)
- 데이터베이스 마이그레이션 실행
- 초기 데이터 생성 (seed_data)
- 슈퍼유저 생성 (선택사항)

### 📊 `dev-status.sh` - 서버 상태 확인
현재 실행 중인 개발 서버의 상태를 확인합니다.

```bash
./dev-status.sh
```

**기능:**
- Django 서버 실행 상태 확인
- Vue.js 서버 실행 상태 확인
- HTTP 응답 상태 테스트
- 프로세스 수 확인
- 로그 파일 상태 확인

## 🔧 사용 순서

### 1. 최초 설정 (한 번만 실행)
```bash
# 개발 환경 초기 설정
./dev-setup.sh
```

### 2. 일상적인 개발 작업
```bash
# 개발 서버 시작
./dev-start.sh

# 다른 터미널에서 상태 확인
./dev-status.sh

# 작업 완료 후 서버 중지
./dev-stop.sh
```

## 🌐 서비스 주소

| 서비스 | 주소 | 설명 |
|--------|------|------|
| Frontend | http://localhost:7173 | Vue.js 개발 서버 |
| Backend API | http://localhost:7000 | Django REST API |
| Admin Panel | http://localhost:7000/admin | Django 관리자 패널 |

## 📄 로그 파일

- `django.log` - Django 서버 로그
- `vite.log` - Vue.js 개발 서버 로그

## 🚨 문제 해결

### 포트가 이미 사용 중인 경우
```bash
# 서버 강제 중지
./dev-stop.sh

# 또는 수동으로 포트 확인 및 종료
lsof -ti:7000 | xargs kill -9  # Django
lsof -ti:7173 | xargs kill -9  # Vue.js
```

### 의존성 문제
```bash
# 개발 환경 재설정
./dev-setup.sh
```

### 데이터베이스 문제
```bash
# 마이그레이션 재실행
python3 manage.py migrate

# 새로운 마이그레이션 생성
python3 manage.py makemigrations
python3 manage.py migrate
```

## 💡 팁

1. **VS Code Terminal**: VS Code에서 통합 터미널을 사용하면 더욱 편리합니다.
2. **백그라운드 실행**: `nohup ./dev-start.sh &`로 백그라운드에서 실행 가능합니다.
3. **자동 재시작**: 파일 변경 시 서버가 자동으로 재시작됩니다.
4. **로그 모니터링**: `tail -f django.log` 또는 `tail -f vite.log`로 실시간 로그 확인 가능합니다.

## 🔍 고급 사용법

### 특정 포트로 실행
환경 변수를 설정하여 다른 포트 사용 가능:
```bash
export DJANGO_PORT=8080
export VITE_PORT=3000
./dev-start.sh
```

### 디버그 모드로 실행
```bash
export DEBUG=true
./dev-start.sh
```
