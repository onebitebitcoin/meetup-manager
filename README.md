# 한번 모임 - 모임 관리 플랫폼

## 📋 프로젝트 개요

**한번 모임**은 오프라인 모임을 쉽게 생성하고 관리할 수 있는 웹 애플리케이션입니다. 사용자들이 관심사를 공유하고 실제로 만날 수 있는 기회를 제공하는 것을 목표로 합니다.

### 🎯 주요 기능
- ✅ **모임 생성 및 관리**: 모임 정보, 일정, 장소, 참가자 수 제한 설정
- ✅ **참가 신청 시스템**: 원클릭 참가 신청 및 취소
- ✅ **대기열 관리**: 정원 초과 시 자동 대기열 등록 및 승격
- ✅ **실시간 알림**: 대기열 승격, 모임 공지 등 인앱 알림
- ✅ **다양한 보기 모드**: 달력 보기 및 목록 보기 지원
- ✅ **검색 및 필터링**: 모임 검색, 카테고리 필터
- ✅ **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원
- ✅ **다크 모드**: 라이트/다크 테마 전환
- ✅ **PWA 지원**: 모바일 앱처럼 설치 가능

## 🏗️ 시스템 아키텍처

```
한번 모임 플랫폼
├── 프론트엔드 (Vue.js 3)
│   ├── 사용자 인터페이스
│   ├── 상태 관리 (Pinia)
│   └── PWA 기능
├── 백엔드 (Django REST Framework)
│   ├── API 서버
│   ├── 데이터베이스 (SQLite)
│   └── 파일 관리
└── 배포 환경
    ├── 정적 파일 서빙
    └── 미디어 파일 관리
```

## 🛠️ 기술 스택

### 프론트엔드
- **Vue.js 3** - 메인 프레임워크 (Composition API)
- **Vue Router 4** - 라우팅 관리
- **Pinia** - 상태 관리
- **Tailwind CSS** - 스타일링 프레임워크
- **Vite** - 빌드 도구 및 개발 서버
- **Vite PWA Plugin** - Progressive Web App 기능

### 백엔드
- **Django 4.2** - 웹 프레임워크
- **Django REST Framework** - API 개발
- **Django CORS Headers** - CORS 정책 관리
- **Pillow** - 이미지 처리
- **SQLite** - 데이터베이스 (개발환경)

### 배포 및 프로덕션
- **Gunicorn** - WSGI 서버
- **WhiteNoise** - 정적 파일 서빙

## 📁 프로젝트 구조

```
training/
├── meetup-manager/          # Vue.js 프론트엔드
│   ├── public/             # 정적 파일
│   │   ├── icons/          # PWA 아이콘
│   │   └── favicon.ico     # 파비콘
│   ├── src/
│   │   ├── components/     # Vue 컴포넌트
│   │   ├── views/          # 페이지 뷰
│   │   ├── stores/         # Pinia 스토어
│   │   ├── router/         # Vue Router 설정
│   │   └── utils/          # 유틸리티 함수
│   ├── package.json        # 프론트엔드 의존성
│   └── vite.config.js      # Vite 설정
├── meetup_backend/          # Django 프로젝트 설정
│   ├── settings.py         # Django 설정
│   ├── urls.py            # 메인 URL 라우팅
│   └── wsgi.py            # WSGI 설정
├── meetups/                # Django 앱
│   ├── models.py          # 데이터 모델
│   ├── views.py           # API 뷰
│   ├── serializers.py     # DRF 시리얼라이저
│   ├── urls.py            # API URL 라우팅
│   └── utils.py           # 백엔드 유틸리티
├── media/                  # 업로드된 파일
├── staticfiles/           # 수집된 정적 파일
├── requirements.txt       # Python 의존성
└── manage.py             # Django 관리 스크립트
```

## 🎯 주요 기능 상세

### 1. 사용자 관리
- **회원가입/로그인**: 이메일 기반 인증
- **게스트 모드**: 회원가입 없이 모임 조회 가능
- **관리자 기능**: 사용자 및 모임 관리

### 2. 모임 관리
- **모임 생성**: 이름, 설명, 일시, 장소, 최대 참가자 수, 카테고리 설정
- **이미지 업로드**: 모임 대표 이미지 첨부
- **참가자 관리**: 생성자의 참가자 추가/제거 권한

### 3. 참가 시스템
- **즉시 참가**: 자리가 있을 때 즉시 참가 확정
- **대기열 시스템**: 정원 초과 시 자동 대기열 등록
- **자동 승격**: 기존 참가자 취소 시 대기순번에 따른 자동 승격

### 4. 알림 시스템
- **대기열 승격 알림**: 참가 확정 시 알림 발송
- **모임 공지 알림**: 생성자가 참가자들에게 보내는 알림
- **알림 관리**: 읽음/안읽음 상태, 삭제 기능

### 5. 사용자 인터페이스
- **대시보드**: 모임 목록을 달력 또는 리스트 형태로 표시
- **검색 및 필터**: 모임명 검색, 카테고리별 필터링
- **반응형 디자인**: 모든 화면 크기에 최적화
- **다크 모드**: 사용자 선호에 따른 테마 전환

## 🚀 개발 환경 설정

### 필수 요구사항
- **Node.js** 16.0+ 
- **Python** 3.8+
- **npm** 또는 **yarn**

### 1. 백엔드 설정

```bash
# 프로젝트 클론
git clone <repository-url>
cd training

# Python 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는 Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
python manage.py migrate

# 관리자 계정 생성 (선택사항)
python manage.py createsuperuser

# 개발 서버 실행
python manage.py runserver
```

### 2. 프론트엔드 설정

```bash
# 프론트엔드 디렉토리로 이동
cd meetup-manager

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 3. 접속 정보
- **프론트엔드**: http://localhost:5173
- **백엔드 API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

## 📊 데이터베이스 모델

### 주요 모델
1. **MeetupUser**: 사용자 정보
2. **Meetup**: 모임 정보
3. **Registration**: 참가 신청
4. **Waitlist**: 대기열
5. **Notification**: 알림

### 관계도
```
MeetupUser ──┬─── Registration ─── Meetup
             ├─── Waitlist ────── Meetup
             └─── Notification ── Meetup
```

## 🔄 API 엔드포인트

### 인증 관련
- `POST /api/auth/register/` - 회원가입
- `POST /api/auth/login/` - 로그인
- `POST /api/auth/logout/` - 로그아웃

### 모임 관련
- `GET /api/meetups/` - 모임 목록 조회
- `POST /api/meetups/` - 모임 생성
- `GET /api/meetups/{id}/` - 모임 상세 조회
- `POST /api/meetups/{id}/register/` - 모임 참가 신청
- `DELETE /api/meetups/{id}/unregister/` - 참가 취소

### 대기열 관련
- `POST /api/meetups/{id}/waitlist/` - 대기열 등록
- `DELETE /api/meetups/{id}/waitlist/remove/` - 대기열 취소
- `GET /api/meetups/{id}/waitlist/status/` - 대기열 상태 확인

### 알림 관련
- `GET /api/notifications/` - 알림 목록
- `POST /api/notifications/{id}/read/` - 알림 읽음 처리
- `POST /api/notifications/mark-all-read/` - 모든 알림 읽음 처리

## 🎨 스타일 가이드

### 컬러 팔레트
- **Primary**: Blue (#3b82f6)
- **Success**: Green (#10b981)
- **Warning**: Orange (#f59e0b)
- **Error**: Red (#ef4444)
- **Dark Mode**: 자동 다크 테마 지원

### 컴포넌트 규칙
- **명명 규칙**: PascalCase for 컴포넌트, camelCase for 변수
- **반응형**: Mobile-first 접근법
- **접근성**: ARIA 레이블 및 키보드 탐색 지원

## 📱 PWA 기능

### 지원 기능
- **오프라인 캐싱**: 중요 리소스 캐시
- **홈 스크린 설치**: 모바일 앱처럼 설치
- **자동 업데이트**: 새 버전 자동 감지 및 업데이트
- **푸시 알림**: 브라우저 알림 지원 (계획 중)

## 🚀 배포 가이드

### 프로덕션 빌드

```bash
# 프론트엔드 빌드
cd meetup-manager
npm run build

# Django 정적 파일 수집
cd ..
python manage.py collectstatic

# 프로덕션 서버 실행
gunicorn meetup_backend.wsgi:application
```

### 환경 변수
```bash
# Django 설정
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# 데이터베이스 (프로덕션)
DATABASE_URL=your-database-url

# 미디어 파일
MEDIA_ROOT=/path/to/media
STATIC_ROOT=/path/to/static
```

## 🤝 기여 가이드

### 개발 프로세스
1. **이슈 생성**: 새 기능이나 버그 리포트
2. **브랜치 생성**: `feature/기능명` 또는 `fix/버그명`
3. **개발 및 테스트**: 로컬에서 충분한 테스트
4. **Pull Request**: 코드 리뷰 요청
5. **머지**: 리뷰 완료 후 메인 브랜치에 머지

### 코딩 규칙
- **Vue.js**: Composition API 사용
- **Python**: PEP 8 스타일 가이드 준수
- **커밋 메시지**: 한국어로 명확하게 작성
- **테스트**: 새 기능은 테스트 코드 포함

### 주요 개발 영역
- 🎨 **UI/UX 개선**: 사용자 경험 향상
- 🔧 **새 기능 개발**: 모임 관리 기능 확장
- 🐛 **버그 수정**: 안정성 개선
- 📱 **모바일 최적화**: 모바일 사용성 향상
- ⚡ **성능 최적화**: 로딩 속도 개선

## 📞 문의 및 지원

### 개발 문의
- **이메일**: onebitebitcoin@proton.me
- **기능 제안**: GitHub Issues 활용
- **버그 리포트**: 상세한 재현 단계와 함께 이슈 생성

### 사용자 가이드
- **사용 설명서**: 애플리케이션 내 `/help` 페이지 참고
- **FAQ**: 자주 묻는 질문들을 정리된 도움말 제공

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참고하세요.

## 🔄 업데이트 히스토리

### v1.0.0 (현재)
- ✅ 기본 모임 생성 및 참가 기능
- ✅ 대기열 시스템
- ✅ 알림 시스템
- ✅ PWA 지원
- ✅ 다크 모드
- ✅ 반응형 디자인

### 계획된 기능
- 🔄 실시간 채팅
- 🔄 소셜 로그인 (Google, Kakao)
- 🔄 이메일 알림
- 🔄 모임 리뷰 시스템
- 🔄 통계 및 분석 대시보드

---

**한번 모임**과 함께 더 나은 오프라인 커뮤니티를 만들어보세요! 🎉
