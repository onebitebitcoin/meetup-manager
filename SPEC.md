# Meetup Manager - Project Specification

## 1. Overview

### 1.1 Purpose
모임 관리 웹 애플리케이션으로, 사용자가 모임을 생성하고 참가할 수 있으며, 과제 관리 및 알림 기능을 제공합니다.

### 1.2 Key Features
- 사용자 인증 (회원가입, 로그인, 로그아웃)
- 설정 페이지 (비밀번호 변경, Lightning Address 관리)
- 모임 CRUD (생성, 조회, 수정, 삭제)
- 모임 참가 신청 및 취소
- 대기열 (Waitlist) 관리 및 자동 승격
- 과제 생성 및 제출
- 알림 시스템
- Lightning Address 기반 1 sats 인보이스 생성 검증 (LNURL)
- 관리자 기능

---

## 2. Tech Stack

### 2.1 Backend
| Category | Technology |
|----------|------------|
| Framework | Django 4.2 |
| API | Django REST Framework 3.16 |
| Database | SQLite (개발), PostgreSQL (프로덕션) |
| CORS | django-cors-headers |
| Image Processing | Pillow |
| WSGI Server | Gunicorn |
| Static Files | WhiteNoise |

### 2.2 Frontend
| Category | Technology |
|----------|------------|
| Framework | Vue.js 3 |
| State Management | Pinia |
| Routing | Vue Router 4 |
| CSS Framework | Tailwind CSS 3 |
| Build Tool | Vite 4 |
| PWA Support | vite-plugin-pwa |

---

## 3. Directory Structure

```
meet/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3
│   ├── debug.log
│   ├── meetup_backend/          # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── meetups/                 # Main app
│       ├── models.py            # Data models
│       ├── serializers.py       # DRF serializers
│       ├── urls.py              # URL routes
│       ├── views/               # View modules
│       │   ├── auth.py
│       │   ├── meetups.py
│       │   ├── tasks.py
│       │   ├── waitlist.py
│       │   ├── notifications.py
│       │   └── admin.py
│       ├── utils/
│       └── middleware/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── router/
│       ├── stores/
│       │   ├── auth.js
│       │   ├── meetups.js
│       │   ├── tasks.js
│       │   └── theme.js
│       ├── components/
│       │   ├── CalendarView.vue
│       │   ├── MeetupTable.vue
│       │   ├── MeetupDetailModal.vue
│       │   ├── ThemeToggle.vue
│       │   └── ...
│       ├── views/
│       └── utils/
├── tests/
│   └── test.sh
├── SPEC.md
├── README.md
├── dev.sh
└── deploy.sh
```

---

## 4. Database Schema

### 4.1 Models

#### MeetupUser
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary Key |
| user | OneToOneField(User) | Django User 연결 (nullable) |
| name | CharField(100) | 사용자 이름 |
| email | EmailField | 이메일 |
| phone | CharField(20) | 전화번호 (optional) |
| lightning_address | CharField(255) | Lightning Address (optional) |
| is_admin | BooleanField | 관리자 여부 |
| created_at | DateTimeField | 생성일시 |

#### Meetup
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary Key |
| name | CharField(200) | 모임 이름 |
| description | TextField | 모임 설명 (optional) |
| date_time | DateTimeField | 시작 일시 |
| end_time | DateTimeField | 종료 일시 (optional) |
| location | CharField(200) | 장소 |
| max_participants | IntegerField | 최대 참가자 수 |
| current_participants | IntegerField | 현재 참가자 수 |
| creator | ForeignKey(MeetupUser) | 생성자 |
| image | ImageField | 모임 이미지 (optional) |
| image_url | URLField | 외부 이미지 URL (optional) |
| hashtags | TextField | 해시태그 (comma-separated) |
| created_at | DateTimeField | 생성일시 |

**Properties:**
- `is_full`: 정원 초과 여부
- `available_spots`: 남은 자리 수
- `hashtags_list`: 해시태그 리스트

#### Registration
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary Key |
| user | ForeignKey(MeetupUser) | 참가자 |
| meetup | ForeignKey(Meetup) | 모임 |
| registered_at | DateTimeField | 등록일시 |

**Constraints:**
- unique_together: (user, meetup)

#### Waitlist
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary Key |
| user | ForeignKey(MeetupUser) | 대기자 |
| meetup | ForeignKey(Meetup) | 모임 |
| position | IntegerField | 대기 순서 |
| waitlisted_at | DateTimeField | 대기 등록일시 |

**Constraints:**
- unique_together: (user, meetup)
- ordering: ['position']

#### Notification
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary Key |
| user | ForeignKey(MeetupUser) | 수신자 |
| title | CharField(200) | 알림 제목 |
| message | TextField | 알림 내용 |
| notification_type | CharField(20) | 알림 유형 |
| meetup | ForeignKey(Meetup) | 관련 모임 (optional) |
| is_read | BooleanField | 읽음 여부 |
| created_at | DateTimeField | 생성일시 |

**Notification Types:**
- `waitlist_promotion`: 대기열 승격
- `meetup_reminder`: 모임 알림
- `general`: 일반 알림

#### Task
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary Key |
| meetup | ForeignKey(Meetup) | 모임 |
| title | CharField(200) | 과제 제목 |
| description | TextField | 과제 설명 (optional) |
| deadline | DateTimeField | 마감일시 |
| created_at | DateTimeField | 생성일시 |
| updated_at | DateTimeField | 수정일시 |

**Properties:**
- `is_deadline_soon`: 마감 3일 이내 여부
- `is_past_deadline`: 마감 지남 여부

#### TaskSubmission
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary Key |
| task | ForeignKey(Task) | 과제 |
| user | ForeignKey(MeetupUser) | 제출자 |
| message | TextField | 제출 메시지 |
| link | URLField | 제출 링크 (optional) |
| file | FileField | 제출 파일 (optional) |
| status | CharField(20) | 검토 상태 |
| submitted_at | DateTimeField | 제출일시 |
| reviewed_at | DateTimeField | 검토일시 (optional) |

**Submission Status:**
- `pending`: 검토 대기
- `approved`: 승인
- `rejected`: 반려

---

## 5. API Design

### 5.1 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/csrf/` | CSRF 토큰 조회 |
| POST | `/api/auth/register/` | 회원가입 |
| POST | `/api/auth/login/` | 로그인 |
| POST | `/api/auth/logout/` | 로그아웃 |
| GET | `/api/auth/lightning-address/` | 내 Lightning Address 조회 |
| PUT | `/api/auth/lightning-address/` | 내 Lightning Address 저장 |
| POST | `/api/auth/lightning-address/test-invoice/` | 1 sats LNURL 인보이스 생성 검증 |
| GET | `/api/auth/check-username/` | 사용자명 중복 확인 |

### 5.2 Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | 사용자 목록 |
| POST | `/api/users/` | 사용자 생성 |

### 5.3 Meetups

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/meetups/` | 모임 목록 |
| POST | `/api/meetups/` | 모임 생성 |
| GET | `/api/meetups/<id>/` | 모임 상세 |
| PUT | `/api/meetups/<id>/` | 모임 수정 |
| DELETE | `/api/meetups/<id>/` | 모임 삭제 |
| GET | `/api/my-meetups/` | 내 모임 목록 |

### 5.4 Registrations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/registrations/` | 등록 목록 |
| POST | `/api/register/` | 참가 신청 |
| GET | `/api/meetups/<id>/registrations/` | 모임 참가자 목록 |
| POST | `/api/meetups/<id>/register/` | 모임 참가 신청 |
| DELETE | `/api/meetups/<id>/unregister/` | 참가 취소 |
| GET | `/api/meetups/<id>/status/` | 참가 상태 확인 |
| POST | `/api/meetups/<id>/add-participant/` | 참가자 수동 추가 |
| DELETE | `/api/meetups/<id>/remove-participant/<reg_id>/` | 참가자 제거 |

### 5.5 Waitlist

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/meetups/<id>/waitlist/` | 대기열 등록 |
| DELETE | `/api/meetups/<id>/waitlist/remove/` | 대기열 취소 |
| GET | `/api/meetups/<id>/waitlist/status/` | 대기 상태 확인 |
| GET | `/api/meetups/<id>/waitlist/list/` | 대기열 목록 |
| GET | `/api/my-waitlists/` | 내 대기열 목록 |

### 5.6 Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications/` | 알림 목록 |
| PUT | `/api/notifications/<id>/read/` | 알림 읽음 처리 |
| PUT | `/api/notifications/mark-all-read/` | 전체 읽음 처리 |
| DELETE | `/api/notifications/<id>/delete/` | 알림 삭제 |
| POST | `/api/meetups/<id>/send-notification/` | 참가자 알림 발송 |

### 5.7 Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/meetups/<id>/tasks/` | 모임 과제 목록 |
| POST | `/api/meetups/<id>/tasks/` | 과제 생성 |
| GET | `/api/tasks/<id>/` | 과제 상세 |
| PUT | `/api/tasks/<id>/` | 과제 수정 |
| DELETE | `/api/tasks/<id>/` | 과제 삭제 |
| GET | `/api/tasks/<id>/submissions/` | 제출물 목록 |
| POST | `/api/tasks/<id>/submit/` | 과제 제출 |
| GET | `/api/submissions/<id>/file/` | 제출 파일 열기/다운로드 |
| PUT | `/api/submissions/<id>/review/` | 제출물 검토 |

### 5.8 Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users/` | 전체 사용자 목록 |
| GET | `/api/admin/meetups/` | 전체 모임 목록 |
| DELETE | `/api/admin/users/<id>/delete/` | 사용자 삭제 |
| DELETE | `/api/admin/meetups/<id>/delete/` | 모임 삭제 |
| PUT | `/api/admin/users/<id>/toggle-admin/` | 관리자 권한 토글 |
| GET | `/api/admin/statistics/` | 통계 조회 |

### 5.9 Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health/` | 서버 상태 확인 |

---

## 6. Frontend Components

### 6.1 Stores (Pinia)

#### auth.js
- `user`: 현재 사용자 정보
- `isLoggedIn`: 로그인 상태
- `isAdmin`: 관리자 여부
- `isGuest`: 게스트 여부
- `login()`: 로그인 처리
- `logout()`: 로그아웃 처리
- `checkAuth()`: 인증 상태 확인

#### meetups.js
- `meetups`: 모임 목록
- `loading`: 로딩 상태
- `error`: 에러 메시지
- `fetchMeetups()`: 모임 목록 조회
- `addMeetup()`: 모임 추가
- `updateMeetup()`: 모임 수정
- `deleteMeetup()`: 모임 삭제
- `addToWaitlist()`: 대기열 등록
- `removeFromWaitlist()`: 대기열 취소
- `checkWaitlistStatus()`: 대기 상태 확인

#### tasks.js
- `tasks`: 과제 목록
- `loading`: 로딩 상태
- `error`: 에러 메시지
- `fetchTasks()`: 과제 목록 조회
- `createTask()`: 과제 생성
- `updateTask()`: 과제 수정
- `deleteTask()`: 과제 삭제
- `submitTask()`: 과제 제출
- `fetchSubmissions()`: 제출물 조회
- `reviewSubmission()`: 제출물 검토

#### theme.js
- 다크모드/라이트모드 테마 관리

### 6.2 Main Components

| Component | Description |
|-----------|-------------|
| CalendarView.vue | 캘린더 뷰 컴포넌트 |
| MeetupTable.vue | 모임 테이블 컴포넌트 |
| MeetupDetailModal.vue | 모임 상세 모달 |
| ThemeToggle.vue | 테마 토글 버튼 |
| PWAInstallPrompt.vue | PWA 설치 프롬프트 |
| AdsBanner.vue | 광고 배너 |
| CustomSelect.vue | 커스텀 셀렉트 |
| CustomDateInput.vue | 날짜 입력 컴포넌트 |
| CustomDateTimeInput.vue | 날짜/시간 입력 컴포넌트 |
| CustomTimeInput.vue | 시간 입력 컴포넌트 |

---

## 7. Business Logic

### 7.1 Registration Flow
1. 사용자가 모임 참가 신청
2. 정원 확인
   - 여유 있음 → Registration 생성, current_participants 증가
   - 정원 초과 → 에러 반환 또는 대기열 안내

### 7.2 Waitlist Promotion Flow
1. 참가자가 참가 취소
2. Registration 삭제, current_participants 감소
3. 대기열 확인
4. 대기열 1순위 자동 승격
   - Registration 생성
   - Waitlist 항목 삭제
   - 알림 발송
5. 대기열 순서 재조정

### 7.3 Task Submission Flow
1. 참가자가 과제 제출 (message, link, file)
2. TaskSubmission 생성 (status: pending)
3. 관리자/생성자가 검토 (approved/rejected)
4. 검토 결과 저장

---

## 8. Deployment

### 8.1 Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

### 8.2 Production (Docker)
```bash
# Multi-stage Docker build
# Stage 1: Frontend build (Node.js)
# Stage 2: Backend run (Python + Gunicorn)
```

### 8.3 Environment Variables
| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL 연결 URL |
| SECRET_KEY | Django 시크릿 키 |
| ENVIRONMENT | production / development |
| LOG_LEVEL | 로그 레벨 (INFO, DEBUG, etc.) |
| REDIS_URL | Redis 연결 URL (캐싱 시) |

---

## 9. Testing

### 9.1 Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### 9.2 Frontend Tests
```bash
cd frontend
npm run test
```

### 9.3 Integrated Tests
```bash
./tests/test.sh all
```

---

## 10. Security Considerations

- CSRF 토큰 필수 (non-GET requests)
- 한글 비밀번호 영문 자동 변환
- 파일 업로드 크기 제한 (5MB)
- 허용 파일 확장자 제한
- 관리자 권한 분리
- 이메일 마스킹 처리
