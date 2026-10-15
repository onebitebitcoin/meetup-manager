# Meetup Manager - Project Specification

## 1. Overview

### 1.1 Purpose
모임 관리 웹 애플리케이션으로, 사용자가 모임을 생성하고 참가할 수 있으며, 과제 관리 및 알림 기능을 제공합니다.

### 1.2 Key Features
- 사용자 인증 (회원가입, 로그인, 로그아웃)
- 설정 페이지 (계정 정보/비밀번호 통합 수정, Lightning Address 관리)
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
| GET | `/api/auth/account-settings/` | 내 계정 정보 조회 (username/name/email) |
| PUT | `/api/auth/account-settings/` | 내 계정 정보/비밀번호 통합 수정 |
| POST | `/api/auth/change-password/` | 비밀번호 변경 (하위 호환 유지) |
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

---

## 11. LITE (간소화 버전, `/lite`)

### 11.1 목적과 원칙
- 지금보다 훨씬 쉬운 참석 신청 + "이런 모임 열어주세요" 요청 기반 개설 + 1:1 세미나 상시 접수.
- 로그인 없음: 이름만 입력하면 서버가 기기 토큰을 발급한다. 이름은 중복 불가.
- UI 원칙: 텍스트 최소, 화면 깊이 1(홈 → 채팅방). 모임 정보·응답 변경·도착 코드는 채팅방 상단 줄에서 처리한다.
- 기존 `meetups` 앱과 테이블은 수정하지 않는다. 새 `lite` 앱이 별도 테이블을 가진다. 기존 모임은 관리 명령으로 복사만 한다.
- 화면 시안: `docs/lite/prototype.html` (클릭 가능한 프로토타입, v0.4). 화면 구조·문구·테마는 이 파일을 기준으로 한다.
- 시간은 UTC로 저장하고, "오늘" 판단과 표시는 Asia/Seoul 기준이다.

### 11.2 모델 (`backend/lite/models.py`)
| 모델 | 필드 |
|------|------|
| Member | name(CharField 20, unique), token(CharField 64, unique, `secrets.token_urlsafe(32)`), is_host(bool), created_at |
| Meetup | title(80), description(blank), starts_at(DateTime), location(100), capacity(PositiveInt), image_url(500, blank: 썸네일 주소, 기존 모임은 /media/ 경로 또는 외부 URL), checkin_code(CharField 4, 생성 시 랜덤 숫자 4자리), from_request(FK MeetupRequest null), legacy_meetup_id(Int unique null), cancelled_at(DateTime null: 운영자 취소 시각), created_at |
| Rsvp | member FK, meetup FK, status(going/maybe/no), checked_in_at(null), removed_at(DateTime null: 운영자가 내보낸 시각), updated_at · unique(member, meetup) |
| SeminarRequest | member(O2O Member), mode(online/offline, null), topic(Text blank), status(guide/received/confirmed), created_at |
| ChatRoom | kind(meetup/seminar), meetup(O2O null), seminar(O2O SeminarRequest null), pinned_message(FK ChatMessage null, SET_NULL: 방마다 고정 공지 1개) |
| ChatMessage | room FK, member FK null, kind(user/system/guide), body(Text ≤ 1000), created_at · ordering id · 복합 인덱스(room, id) |
| MeetupRequest | title(60), preferred_period(this_month/next_month/any), created_by FK Member, status(open/done), meetup(FK Meetup null), created_at |
| RequestVote | request FK, member FK · unique(request, member) |
| LiteConfig | 싱글턴(pk=1). vote_threshold(기본 5), seminar_guide_1="원하는 주제로 운영자와 1:1로 진행해요.", seminar_guide_2="시간당 50,000원이에요.\n진행 방식을 골라 주세요.", seminar_guide_3="주제와 희망 날짜·시간을 적어 주세요.", seminar_guide_4="접수됐어요. 여기서 일정을 안내해 드릴게요.", join_guide="신청 완료! 공지는 여기서 안내해요." · Django admin에서 수정 |

- Meetup 생성 시 ChatRoom(kind=meetup)을 함께 만든다(뷰·관리 명령·Django admin 어디서 만들어도 보장, 모델 계층에서 처리). ChatRoom은 admin에서 읽기 전용. SeminarRequest 생성 시 ChatRoom(kind=seminar)을 함께 만든다.
- 참석 인원(going_count)은 Rsvp(status=going) 수로 계산한다. 별도 카운터 필드는 두지 않는다.

#### 11.2.1 운영자 관리 동작
- 취소: `Meetup.cancelled_at`을 기록한다. 취소된 모임은 홈에 그대로 남고 카드의 `cancelled`로 표시한다. 참석 응답·도착 체크는 400 "취소된 모임이에요". 채팅방에 시스템 메시지 "모임이 취소됐어요"를 남기고, 되돌리면 "모임이 다시 열렸어요"를 남긴다. 이미 같은 상태면 메시지 없이 200.
- 삭제: 모임, 응답, 채팅방, 메시지를 함께 지운다(CASCADE). 이 모임으로 완료 처리된 요청은 meetup만 NULL이 되고 status는 그대로 둔다.
- 수정: 제목, 시작 시각, 장소, 정원, 설명, 썸네일 URL. 생성과 달리 "현재 이후" 조건이 없다. 정원은 현재 참석(going) 인원보다 작게 줄일 수 없다. 썸네일 URL은 빈 문자열 허용, 500자 이하이며 공백·제어문자는 거부한다. `urlsplit` 결과 scheme이 `http` 또는 `https`(대소문자 무시)이고 netloc이 비어 있지 않거나, `/media/`로 시작하면서 `//`, `..`, `\`가 없어야 한다(`//host/x`, `data:` 등은 400). 시작 시각이나 장소가 실제로 바뀌면 시스템 메시지 "일정이 바뀌었어요 · 10월 18일 (토) 19:00 · 장소"(서울 시간)를 남긴다. 취소된 모임의 일정을 수정해도 이 메시지는 똑같이 남는다.
- 내보내기: 모임 행을 잠근 뒤 해당 회원의 응답을 `no`로 바꾸고 `checked_in_at`을 비우고 `Rsvp.removed_at`을 기록한다. 도착 인원(`checked_in_count`)은 `removed_at`이 없는 응답만 센다. 내보낸 회원은 그 모임에 다시 응답할 수 없고(403 "운영자가 내보낸 모임이에요"), 응답이 `no`이므로 채팅방에도 들어갈 수 없다. 시스템 메시지는 남기지 않는다.
- 메시지 삭제: DB에서 지운다. 폴링은 새 메시지만 가져오므로 다른 사람 화면에서는 새로고침 후 사라진다.
- 공지 고정: 방마다 1개. 메시지 조회 응답(폴링 포함)에 `pinned`(Message|null)를 담는다. 고정된 메시지를 삭제하면 `pinned`는 null이 된다.

### 11.3 인증
- 요청 헤더 `X-Member-Token: <token>`. DRF 인증 클래스 `lite.auth.MemberTokenAuthentication`이 `request.user` 대신 `request.member`를 채운다(`request.auth`=Member도 허용).
- lite 뷰는 `authentication_classes=[MemberTokenAuthentication]`만 사용한다(세션 미사용 → CSRF 불필요).
- 토큰 없음/잘못됨 → 401 `{"error": "이름을 먼저 입력해 주세요"}`. 운영자 전용 → 403 `{"error": "운영자만 할 수 있어요"}`.
- 운영자 승격: 환경 변수 `LITE_HOST_KEY`(비어 있으면 승격 불가, 운영에서는 `secrets.token_urlsafe(32)` 수준의 무작위 값)와 일치하는 key를 `POST host/claim/`으로 보내면 is_host=True.
- 이름 검증: NFKC 정규화 후 앞뒤 공백 제거, 1~20자, 제어문자·줄바꿈·제로폭 문자 거부, 예약어("운영자", "관리자", "admin", "host") 거부.
- 요청 횟수 제한(DRF throttle, 캐시는 워커 간 공유되는 FileBasedCache): 회원 생성 IP당 60/hour, 운영자 승격 회원·IP당 5/hour, 도착 코드 확인 회원·모임당 5회/10분, 메시지 전송 회원당 30/min, 요청 작성 회원당 10/hour, 세미나 mode 선택 회원당 10/hour. 초과 시 429 `{"error": "잠시 후 다시 시도해 주세요"}`.
- 프록시 뒤 클라이언트 IP: 운영 설정에서 `REST_FRAMEWORK['NUM_PROXIES'] = 1`(nginx 1단).

### 11.4 API 계약 (prefix `/api/lite/`, trailing slash 유지)
에러는 항상 `{"error": "<사용자에게 보여줄 한국어 메시지>"}` + 적절한 상태 코드.

공통 객체:
```
Member      {id, name, is_host}
MeetupCard  {id, title, starts_at(ISO8601), location, capacity, image_url: string|null, going_count, maybe_count,
             my_status: "going"|"maybe"|"no"|null, from_request: bool, is_today: bool, cancelled: bool, room_id}
Message     {id, kind: "user"|"system"|"guide", member: {id,name}|null, body, created_at}
SeminarCard {id, member: {id,name}, mode: "online"|"offline"|null, status: "guide"|"received"|"confirmed",
             room_id, last_message: string|null}
RequestCard {id, title, preferred_period, created_by: {id,name}, vote_count, voted: bool,
             status: "open"|"done", meetup_id: int|null, threshold}
```

| Method | Path | 권한 | Body | 응답 |
|---|---|---|---|---|
| POST | members/ | 없음(AnonRateThrottle 10/hour) | {name} (1~20자, 앞뒤 공백 제거) | 201 {token, member: Member} · 이름 중복 409 |
| GET | me/ | member | - | 200 {member: Member} |
| POST | host/claim/ | member | {key} | 200 {member} · 키 불일치 403 |
| GET | home/ | member | - | 200 {meetups: [MeetupCard], my_seminar: SeminarCard\|null, seminars: [SeminarCard] (운영자만, 아니면 []), ready_request_count: int} — meetups는 starts_at가 오늘(서울) 0시 이후인 것, 시간순 |
| POST | meetups/ | host | {title(≤80), starts_at(현재 이후), location(≤100), capacity(2~500), description?(≤1000), request_id?} | 201 {meetup: MeetupCard} (request_id가 있으면 해당 요청 status=done, meetup 연결, 시스템 메시지 "요청으로 열린 모임이에요 · N명에게 알림") |
| GET | meetups/<id>/ | member | - | 200 {meetup: MeetupCard, checkin_code: str\|null (운영자 + 오늘만), checked_in: bool, checked_in_count: int (내보낸 회원 제외), removed: bool (요청한 회원 본인이 운영자에게 내보내졌는지)} |
| PUT | meetups/<id>/rsvp/ | member | {status} | 200 {meetup: MeetupCard} · 이미 지난 모임(시작 시각 + 12시간 경과)은 400 · 취소된 모임은 400 "취소된 모임이에요" · 운영자가 내보낸 회원은 403 · going인데 정원 초과 409 "정원이 찼어요" · 상태가 바뀌면 시스템 메시지 "<이름>님 참석/미정/불참", 처음 going/maybe가 되면 guide 메시지 join_guide 추가 |
| POST | meetups/<id>/checkin/ | member(going/maybe) | {code} | 200 {checked_in: true} · 취소된 모임이면 400 · 내보낸 회원이면 403 "운영자가 내보낸 모임이에요" · 오늘이 아니면 400 · 코드 불일치 400 "코드가 달라요" · 시스템 메시지 "<이름>님 도착" |
| GET | rooms/<id>/messages/?after=<msg_id> 또는 ?before=<msg_id> | 모임방: going/maybe 또는 host · 세미나방: 본인 또는 host | - | after가 있으면 200 {messages, pinned} (그 이후 최대 200개, 폴링용). after가 없으면 200 {messages, has_more, pinned} — 최신 100개, before가 있으면 그 id보다 오래된 메시지 중 최신 100개(둘 다 id 오름차순). has_more는 더 오래된 메시지가 남았는지. after·before는 0 이상 정수(아니면 400) |
| POST | rooms/<id>/messages/ | 위와 동일 | {body} (1~1000자) | 201 {message: Message} · 세미나방에서 신청자 본인이 보낸 메시지이고 status=guide이며 mode가 정해져 있으면: topic=body, status=received, guide 메시지 seminar_guide_4 추가 |
| POST | seminar/ | member | - | 200 {seminar: SeminarCard} — 내 SeminarRequest get-or-create. 새로 만들 때 guide 메시지 seminar_guide_1, seminar_guide_2 추가 |
| POST | seminar/mode/ | member | {mode} | 200 {seminar} — 사용자 메시지 "온라인"/"오프라인" + guide 메시지 seminar_guide_3 추가 |
| POST | seminars/<id>/confirm/ | host | - | 200 {seminar} — status=confirmed, 시스템 메시지 "일정 확정" |
| GET | requests/ | member | - | 200 {requests: [RequestCard]} (open 먼저, vote_count 내림차순, done 뒤) |
| POST | requests/ | member | {title(1~60), preferred_period} | 201 {request: RequestCard} (작성자 자동 투표) |
| POST | requests/<id>/vote/ | member | - | 200 {request: RequestCard} (토글) |
| GET | admin/meetups/?scope=upcoming\|past | host | - | 200 {meetups: [MeetupCard]} — upcoming(기본)은 starts_at가 오늘(서울) 0시 이후, 시간 오름차순. past는 그 이전, 시간 내림차순. 취소된 모임 포함. 그 외 scope는 400 |
| GET | admin/meetups/<id>/ | host | - | 200 AdminMeetup {meetup: MeetupCard, description, image_url, checkin_code, attendees: [{member: {id,name}, status, checked_in_at: ISO\|null, removed: bool}]} — attendees는 going, maybe, no 순이고 같은 상태 안에서는 updated_at 순 |
| PATCH | admin/meetups/<id>/ | host | {title?, starts_at?, location?, capacity?, description?, image_url?} (보낸 필드만 수정) | 200 AdminMeetup · 정원이 현재 참석 인원보다 작으면 400 "정원은 현재 참석 인원(N명)보다 작게 줄일 수 없어요" · image_url 형식 오류 400 |
| DELETE | admin/meetups/<id>/ | host | - | 200 {deleted: true} |
| POST | admin/meetups/<id>/cancel/ | host | {cancelled: bool} | 200 AdminMeetup · bool이 아니면 400 |
| DELETE | admin/meetups/<id>/members/<member_id>/ | host | - | 200 AdminMeetup · 신청 기록이 없으면 404 "참석 신청한 회원이 아니에요" |
| DELETE | rooms/<id>/messages/<msg_id>/ | host | - | 200 {deleted: true} · 그 방의 메시지가 아니면 404 |
| PUT | rooms/<id>/pin/ | host | {message_id: int\|null} (키 필수, 해제는 null을 명시) | 200 {pinned: Message\|null} · 키가 없거나 bool·문자열·실수면 400 · 그 방의 메시지가 아니거나 범위(2^63-1) 초과, 고정 중 삭제되면 404 · kind 제한 없음 |

### 11.5 관리 명령
- `python manage.py import_legacy_meetups [--all]`: 기존 `meetups.Meetup` → `lite.Meetup`. 기본은 starts_at가 현재 이후인 모임만, `--all`이면 전부. name→title, description, date_time→starts_at, location, max_participants→capacity, legacy_meetup_id=원래 id. image가 있으면 그 /media/ 경로, 없으면 image_url을 썸네일로 쓴다. 이미 있는 legacy_meetup_id는 다시 만들지 않고, lite 쪽 썸네일이 비어 있을 때만 채운다(재실행 안전). 결과 개수를 출력한다.

### 11.6 프론트엔드 라우트 (`frontend/src/lite/`)
| 경로 | 화면 |
|---|---|
| /lite | 홈(제목 "한입 모임"). 토큰이 없으면 이름 입력. 하단 탭 없음. 맨 위 1:1 세미나 카드(운영자는 세미나 대화별 카드), 그 아래 "이런 모임 열어주세요" 항목(운영자에게는 개설 가능 수), 그 아래 모임 카드. 모임 카드는 "오늘/내일/N일 후"(서울 날짜 기준)와 썸네일(image_url이 있을 때)을 보여준다 |
| /lite/requests | 모임 요청 목록과 "이런 모임 열어주세요" 작성 버튼 |
| /lite/m/:id | 모임 채팅방. 상단 줄: 일정·장소, 내 응답 칩(누르면 참석/미정/불참 펼침), 당일 도착 코드 입력(운영자는 코드와 도착 인원). 미신청자는 메시지 대신 신청하기/못 가요 |
| /lite/admin | 운영자 전용. 다가오는/지난 탭 모임 목록(날짜·제목·참석/정원·취소됨 칩)과 모임 만들기 버튼. 운영자가 아니면 홈으로 이동 |
| /lite/admin/m/:id | 운영자 전용 모임 관리. 수정 폼(썸네일 URL 포함), 참석자 명단과 내보내기, 채팅방 링크, 취소/되돌리기, 삭제. 내보내기·삭제는 화면 안에서 한 번 더 확인 |
| /lite/seminar | 내 1:1 세미나 채팅방. 마지막 안내 메시지 아래 온라인/오프라인 선택 버튼 |
| /lite/seminar/:id | 운영자용 1:1 세미나 채팅방 + 확정 버튼 |
| /lite/new-request | 요청 작성(주제 + 시기 세그먼트) |
| /lite/new-meetup | 운영자 모임 만들기. `?request=<id>`면 요청 제목을 채운다 |
| /lite/r#<token> | 복구 링크: fragment의 토큰으로 `GET me/`를 확인한 뒤에만 저장, 실패하면 기존 토큰 유지. 읽은 즉시 `history.replaceState`로 fragment 제거 후 /lite로 이동 |
| /lite/host#<key> | 운영자 링크: fragment의 key로 host/claim 호출(이름이 없으면 먼저 이름 입력), 읽은 즉시 fragment 제거 후 /lite로 이동 |
- 토큰과 운영자 키는 URL 경로나 쿼리에 넣지 않는다(서버 접속 로그·방문 기록 노출 방지). fragment는 서버로 전송되지 않는다.
- 채팅방은 처음에 최신 100개를 보여 주고, 더 오래된 메시지가 있으면 맨 위의 "이전 메시지 보기"로 100개씩 더 불러온다(`?before=`). 새 메시지는 3초 간격으로 `?after=`를 사용해 가져온다. after 기준은 폴링으로 받은 마지막 id만 사용한다(내가 보낸 메시지 응답으로 기준을 앞당기지 않는다, id로 중복 제거). 화면을 벗어나거나 탭이 숨겨지면 멈추고, 401/403이면 중단한다.
- 홈에 예정된 모임이 없으면 "예정된 모임이 없어요" 한 줄을 표시한다.
- 테마: 원장(Ledger) 구조 + 한입 로고 팔레트. 글자 IBM Plex Sans KR, 숫자 IBM Plex Mono. 배경 크림 #FFF8EC, 글자 초코 #2B1A17, 주요 버튼·오늘 날짜·내 말풍선 머스타드 #F5C431, 참석 민트 #2FBF8A, 1:1 세미나·안내 메시지 자두 #8E3A59, 요청 진행 막대 쿠키 #E2A55A. 1px 옅은 테두리, 그림자 없음, 모서리 10~12px. 다크 모드: 배경 #1C1311, 표면 #281B18, 글자 #FFF1DC. 미신청 모임에는 "신청하기"만 두고 불참 버튼은 두지 않는다(참석 인원만 표시).
