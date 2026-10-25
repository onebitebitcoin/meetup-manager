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
- 로그인 없음: 이름을 묻지 않는다. 처음 신청·요청·1:1 세미나를 시작할 때 프론트가 "친근한 형용사 + 동물/곤충" 닉네임(예: 느긋한 수달)을 만들어 가입시키고, 서버가 기기 토큰을 발급한다. 이름은 중복 불가이므로 409가 나면 새로 뽑고, 마지막 시도에는 두 자리 숫자를 붙인다.
- UI 원칙: 텍스트 최소, 화면 깊이 1(홈 → 채팅방). 모임 정보·응답 변경은 채팅방 상단 줄에서 처리한다.
- 기존 `meetups` 앱과 테이블은 수정하지 않는다. 새 `lite` 앱이 별도 테이블을 가진다. 기존 모임은 관리 명령으로 복사만 한다.
- 화면 시안: `docs/lite/prototype.html` (클릭 가능한 프로토타입, v0.4). 화면 구조·문구·테마는 이 파일을 기준으로 한다.
- 시간은 UTC로 저장하고, "오늘" 판단과 표시는 Asia/Seoul 기준이다.

### 11.2 모델 (`backend/lite/models.py`)
| 모델 | 필드 |
|------|------|
| Member | name(CharField 20, unique), token(CharField 64, unique, `secrets.token_urlsafe(32)`), is_host(bool), created_at |
| Meetup | title(80), description(blank), audience(100, blank: 대상 한 줄, 예 "비트코인을 처음 접하는 분"), starts_at(DateTime), location(100), capacity(PositiveInt), image_url(500, blank: 썸네일 주소, 기존 모임은 /media/ 경로 또는 외부 URL), from_request(FK MeetupRequest null), legacy_meetup_id(Int unique null), cancelled_at(DateTime null: 운영자 취소 시각), created_at |
| Rsvp | member FK, meetup FK, status(going/maybe/no), removed_at(DateTime null: 운영자가 내보낸 시각), updated_at · unique(member, meetup) |
| SeminarRequest | member(O2O Member), mode(online/offline, null), topic(Text blank), status(guide/received/confirmed), created_at |
| ChatRoom | kind(meetup/seminar), meetup(O2O null), seminar(O2O SeminarRequest null), pinned_message(FK ChatMessage null, SET_NULL: 방마다 고정 공지 1개) |
| ChatMessage | room FK, member FK null, kind(user/system/guide), body(Text ≤ 1000), created_at · ordering id · 복합 인덱스(room, id) |
| MeetupRequest | title(60), preferred_period(this_month/next_month/any), created_by FK Member, status(open/done), meetup(FK Meetup null), created_at |
| RequestVote | request FK, member FK · unique(request, member) |
| LiteConfig | 싱글턴(pk=1). vote_threshold(기본 5), seminar_guide_1="원하는 주제로 운영자와 1:1로 진행해요.", seminar_guide_2="진행 방식을 골라 주세요.", seminar_guide_3="주제와 희망 날짜·시간을 적어 주세요.", seminar_guide_4="접수됐어요. 여기서 일정을 안내해 드릴게요.", join_guide="신청 완료! 공지는 여기서 안내해요." · Django admin에서 수정 |

- Meetup 생성 시 ChatRoom(kind=meetup)을 함께 만든다(뷰·관리 명령·Django admin 어디서 만들어도 보장, 모델 계층에서 처리). ChatRoom은 admin에서 읽기 전용. SeminarRequest 생성 시 ChatRoom(kind=seminar)을 함께 만든다.
- 참석 인원(going_count)은 Rsvp(status=going) 수로 계산한다. 별도 카운터 필드는 두지 않는다.

#### 11.2.1 운영자 관리 동작
- 취소: `Meetup.cancelled_at`을 기록한다. 취소된 모임은 홈에 그대로 남고 카드의 `cancelled`로 표시한다. 참석 응답은 400 "취소된 모임이에요". 채팅방에 시스템 메시지 "모임이 취소됐어요"를 남기고, 되돌리면 "모임이 다시 열렸어요"를 남긴다. 이미 같은 상태면 메시지 없이 200.
- 삭제: 모임, 응답, 채팅방, 메시지를 함께 지운다(CASCADE). 이 모임으로 완료 처리된 요청은 meetup만 NULL이 되고 status는 그대로 둔다.
- 수정: 제목, 시작 시각, 장소, 정원, 설명, 썸네일 URL. 생성과 달리 "현재 이후" 조건이 없다. 정원은 현재 참석(going) 인원보다 작게 줄일 수 없다. 썸네일 URL은 빈 문자열 허용, 500자 이하이며 공백·제어문자는 거부한다. `urlsplit` 결과 scheme이 `http` 또는 `https`(대소문자 무시)이고 netloc이 비어 있지 않거나, `/media/`로 시작하면서 `//`, `..`, `\`가 없어야 한다(`//host/x`, `data:` 등은 400). 시작 시각이나 장소가 실제로 바뀌면 시스템 메시지 "일정이 바뀌었어요 · 10월 18일 (토) 19:00 · 장소"(서울 시간)를 남긴다. 취소된 모임의 일정을 수정해도 이 메시지는 똑같이 남는다.
- 내보내기: 모임 행을 잠근 뒤 해당 회원의 응답을 `no`로 바꾸고 `Rsvp.removed_at`을 기록한다. 내보낸 회원은 그 모임에 다시 응답할 수 없고(403 "운영자가 내보낸 모임이에요"), 응답이 `no`이므로 채팅방에도 들어갈 수 없다. 시스템 메시지는 남기지 않는다.
- 메시지 삭제: DB에서 지운다. 폴링은 새 메시지만 가져오므로 다른 사람 화면에서는 새로고침 후 사라진다.
- 공지 고정: 방마다 1개. 메시지 조회 응답(폴링 포함)에 `pinned`(Message|null)를 담는다. 고정된 메시지를 삭제하면 `pinned`는 null이 된다.

### 11.3 인증
- 요청 헤더 `X-Member-Token: <token>`. DRF 인증 클래스 `lite.auth.MemberTokenAuthentication`이 `request.user` 대신 `request.member`를 채운다(`request.auth`=Member도 허용).
- lite 뷰는 `authentication_classes=[MemberTokenAuthentication]`만 사용한다(세션 미사용 → CSRF 불필요).
- 토큰 없음/잘못됨 → 401 `{"error": "이름을 먼저 입력해 주세요"}`. 운영자 전용 → 403 `{"error": "운영자만 할 수 있어요"}`.
- 운영자 승격: 환경 변수 `LITE_HOST_KEY`(비어 있으면 승격 불가, 운영에서는 `secrets.token_urlsafe(32)` 수준의 무작위 값)와 일치하는 key를 `POST host/claim/`으로 보내면 is_host=True.
- 이름 검증: NFKC 정규화 후 앞뒤 공백 제거, 1~20자, 제어문자·줄바꿈·제로폭 문자 거부, 예약어("운영자", "관리자", "admin", "host") 거부.
- 요청 횟수 제한(DRF throttle, 캐시는 워커 간 공유되는 FileBasedCache): 회원 생성 IP당 60/hour, 운영자 승격 회원·IP당 5/hour, 메시지 전송 회원당 30/min, 요청 작성 회원당 10/hour, 세미나 mode 선택 회원당 10/hour. 초과 시 429 `{"error": "잠시 후 다시 시도해 주세요"}`.
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
| GET | home/ | 없음(토큰이 있으면 회원 기준) | - | 200 {meetups: [MeetupCard], my_seminar: SeminarCard\|null (이름 없으면 null), seminars: [SeminarCard] (운영자만, 아니면 []), ready_request_count: int} — meetups는 starts_at가 오늘(서울) 0시 이후인 것, 시간순 |
| POST | meetups/ | host | {title(≤80), starts_at(현재 이후), location(≤100), capacity(2~500), description?(≤1000), audience?(≤100), request_id?} | 201 {meetup: MeetupCard} (request_id가 있으면 해당 요청 status=done, meetup 연결, 시스템 메시지 "요청으로 열린 모임이에요 · N명에게 알림") |
| GET | meetups/<id>/ | 없음(토큰이 있으면 회원 기준, 이름 없으면 my_status는 null) | - | 200 {meetup: MeetupCard, description: str, audience: str (비어 있으면 ""), removed: bool (요청한 회원 본인이 운영자에게 내보내졌는지)} |
| PUT | meetups/<id>/rsvp/ | member | {status} | 200 {meetup: MeetupCard} · 이미 지난 모임(시작 시각 + 12시간 경과)은 400 · 취소된 모임은 400 "취소된 모임이에요" · 운영자가 내보낸 회원은 403 · going인데 정원 초과 409 "정원이 찼어요" · 상태가 바뀌면 시스템 메시지 "<이름>님 참석/미정/불참", 처음 going/maybe가 되면 guide 메시지 join_guide 추가 |
| GET | rooms/<id>/messages/?after=<msg_id> 또는 ?before=<msg_id> | 모임방: going/maybe 또는 host · 세미나방: 본인 또는 host | - | after가 있으면 200 {messages, pinned} (그 이후 최대 200개, 폴링용). after가 없으면 200 {messages, has_more, pinned} — 최신 100개, before가 있으면 그 id보다 오래된 메시지 중 최신 100개(둘 다 id 오름차순). has_more는 더 오래된 메시지가 남았는지. after·before는 0 이상 정수(아니면 400) |
| POST | rooms/<id>/messages/ | 위와 동일 | {body} (1~1000자) | 201 {message: Message} · 세미나방에서 신청자 본인이 보낸 메시지이고 status=guide이며 mode가 정해져 있으면: topic=body, status=received, guide 메시지 seminar_guide_4 추가 |
| POST | seminar/ | member | - | 200 {seminar: SeminarCard} — 내 SeminarRequest get-or-create. 새로 만들 때 guide 메시지 seminar_guide_1, seminar_guide_2 추가 |
| POST | seminar/mode/ | member | {mode} | 200 {seminar} — 사용자 메시지 "온라인"/"오프라인" + guide 메시지 seminar_guide_3 추가 |
| POST | seminars/<id>/confirm/ | host | - | 200 {seminar} — status=confirmed, 시스템 메시지 "일정 확정" |
| GET | requests/ | member | - | 200 {requests: [RequestCard]} (open 먼저, vote_count 내림차순, done 뒤) |
| POST | requests/ | member | {title(1~60), preferred_period} | 201 {request: RequestCard} (작성자 자동 투표) |
| POST | requests/<id>/vote/ | member | - | 200 {request: RequestCard} (토글) |
| GET | admin/meetups/?scope=upcoming\|past | host | - | 200 {meetups: [MeetupCard]} — upcoming(기본)은 starts_at가 오늘(서울) 0시 이후, 시간 오름차순. past는 그 이전, 시간 내림차순. 취소된 모임 포함. 그 외 scope는 400 |
| GET | admin/meetups/<id>/ | host | - | 200 AdminMeetup {meetup: MeetupCard, description, audience, image_url, attendees: [{member: {id,name}, status, removed: bool}]} — attendees는 going, maybe, no 순이고 같은 상태 안에서는 updated_at 순 |
| PATCH | admin/meetups/<id>/ | host | {title?, starts_at?, location?, capacity?, description?, audience?, image_url?} (보낸 필드만 수정) | 200 AdminMeetup · 정원이 현재 참석 인원보다 작으면 400 "정원은 현재 참석 인원(N명)보다 작게 줄일 수 없어요" · image_url 형식 오류 400 |
| DELETE | admin/meetups/<id>/ | host | - | 200 {deleted: true} |
| POST | admin/meetups/<id>/cancel/ | host | {cancelled: bool} | 200 AdminMeetup · bool이 아니면 400 |
| DELETE | admin/meetups/<id>/members/<member_id>/ | host | - | 200 AdminMeetup · 신청 기록이 없으면 404 "참석 신청한 회원이 아니에요" |
| DELETE | rooms/<id>/messages/<msg_id>/ | host | - | 200 {deleted: true} · 그 방의 메시지가 아니면 404 |
| PUT | rooms/<id>/pin/ | host | {message_id: int\|null} (키 필수, 해제는 null을 명시) | 200 {pinned: Message\|null} · 키가 없거나 bool·문자열·실수면 400 · 그 방의 메시지가 아니거나 범위(2^63-1) 초과, 고정 중 삭제되면 404 · kind 제한 없음 |

### 11.4.1 채팅 첨부·링크
- 모델: `ChatMessage`에 `attachment`(FileField, `upload_to='lite/chat/%Y/%m/'`, blank), `attachment_name`(CharField 120, blank: 원래 파일 이름), `attachment_size`(PositiveInteger null), `attachment_kind`(`image`/`file`, blank) 추가. 저장 파일 이름은 `uuid4().hex + 소문자 확장자`로 바꿔서 추측할 수 없게 한다. 메시지를 삭제하면(운영자 삭제·모임 삭제 CASCADE 모두) 저장된 파일도 지운다(post_delete 시그널).
- Message 객체에 `attachment: {url, name, size, kind: "image"|"file"}|null` 추가. `url`은 `/media/...` 경로. 첨부만 있는 메시지는 `body`가 빈 문자열이다. 폴링·이전 메시지·공지(`pinned`) 응답 모두 같은 형태.
- 업로드: `POST rooms/<id>/files/` (multipart/form-data, 필드 `file` 필수, `body` 선택 0~1000자). 권한·throttle은 메시지 전송과 같다(MessageSendThrottle 공유). 201 {message: Message}. 세미나 접수 전환(topic=body)은 텍스트 메시지 전송에서만 일어난다.
  - 최대 10MB(10 * 1024 * 1024 바이트). 초과 시 413 "파일은 10MB까지 올릴 수 있어요". `file`이 없거나 0바이트면 400 "파일을 선택해 주세요".
  - 이미지: 확장자 jpg/jpeg/png/gif/webp이고 Pillow `verify()`를 통과하면 kind=image. 확장자는 이미지인데 검증에 실패하면 400 "이미지 파일이 올바르지 않아요".
  - 그 밖의 파일: kind=file. 실행·스크립트 위험 확장자(html, htm, xhtml, svg, svgz, xml, js, mjs, exe, bat, cmd, sh, php, jsp, asp, aspx)와 확장자 없는 파일은 400 "올릴 수 없는 파일 형식이에요". `/media/`는 nginx가 같은 출처에서 그대로 서빙하므로 브라우저가 실행할 수 있는 형식은 받지 않는다.
  - `attachment_name`은 NFKC 정규화, 경로 구분자·제어문자 제거, 120자로 자른다.
  - 운영 nginx `location /media/lite/chat/`에 `add_header X-Content-Type-Options nosniff` 와 `Content-Disposition attachment`(이미지 제외)를 둔다.
- 링크 미리보기: `GET link-preview/?url=<http(s) URL>` (member, 회원당 60/min throttle). 200 {preview: {url, title, description, image, site_name}|null}. 서버가 대상 페이지를 받아 `og:title`/`og:description`/`og:image`/`og:site_name`(없으면 `<title>`, `meta[name=description]`)을 읽는다. 결과(null 포함)는 Django 캐시에 URL 기준 24시간 저장한다.
  - SSRF 방지: scheme http/https만, 포트 80/443만, 호스트를 DNS 조회한 모든 IP가 공인 IP여야 한다(`ipaddress`의 is_private/is_loopback/is_link_local/is_reserved/is_multicast/is_unspecified 거부). 리다이렉트는 직접 따라가며 최대 3회, 매번 같은 검사를 한다. 타임아웃 3초, 본문 최대 512KB, `text/html`만 파싱한다. 실패·비HTML·검사 거부는 모두 200 {preview: null}로 돌려준다(URL 형식 자체가 틀리면 400 "링크 주소가 올바르지 않아요").
  - 표준 라이브러리(`urllib`, `html.parser`)만 쓴다. `og:image`는 http(s) 절대 URL로 정규화하고 아니면 null.
- 프론트엔드:
  - 메시지 본문 안의 `http://`, `https://`, `www.` 링크를 눌러서 새 탭으로 여는 링크로 바꾼다(`target="_blank" rel="noopener noreferrer"`, `v-html` 금지, 텍스트/링크 조각으로 나눠 렌더링). 끝에 붙은 `.,)!?` 같은 문장부호는 링크에서 뺀다.
  - 본문의 첫 번째 링크로 미리보기 카드(이미지·제목·설명·사이트)를 말풍선 아래에 보여준다. 결과는 URL별로 메모리에 캐시하고, null이면 카드를 그리지 않는다.
  - 첨부 버튼(클립 아이콘)으로 파일을 고른다. 이미지(`image/*`)는 보내기 전 미리보기와 취소 버튼을 보여준다. 10MB를 넘으면 보내기 전에 에러 토스트를 띄운다. 업로드 중에는 보내기 버튼을 막는다.
  - 이미지 첨부는 말풍선 안 썸네일(최대 너비 240px, `loading="lazy"`)로, 누르면 전체 화면 뷰어(닫기·다운로드 버튼)를 연다. 파일 첨부는 파일 아이콘·이름·크기(KB/MB)가 있는 행이고 누르면 `download` 속성으로 내려받는다.
  - 공지 바에서 첨부만 있는 메시지는 "사진" 또는 "파일 · <이름>"으로 보여준다.

### 11.5 관리 명령
- `python manage.py import_legacy_meetups [--all]`: 기존 `meetups.Meetup` → `lite.Meetup`. 기본은 starts_at가 현재 이후인 모임만, `--all`이면 전부. name→title, description, date_time→starts_at, location, max_participants→capacity, legacy_meetup_id=원래 id. image가 있으면 그 /media/ 경로, 없으면 image_url을 썸네일로 쓴다. 이미 있는 legacy_meetup_id는 다시 만들지 않고, lite 쪽 썸네일이 비어 있을 때만 채운다(재실행 안전). 결과 개수를 출력한다.

### 11.6 프론트엔드 라우트 (`frontend/src/lite/`)
| 경로 | 화면 |
|---|---|
| /lite | 홈(제목 "한입 모임"). 이름 없이도 모임 목록을 본다(이름은 신청할 때 받는다). 이름이 있으면 오른쪽 위 이름을 눌러 "이 기기에서 이름 지우기"를 할 수 있다(한 번 더 확인, 브라우저의 토큰만 지우고 서버의 회원·기록은 남긴다). 하단 탭 없음. 운영자가 아닌 방문자: 목록에는 모임 카드만 두고, 오른쪽 아래 "문의" 플로팅 버튼을 누르면 "1:1 세미나"(내 세미나 상태 칩)와 "이런 모임 열어주세요"(요청 입력 화면으로 바로 이동) 메뉴가 펼쳐진다. 운영자: 플로팅 버튼 없이 맨 위에 세미나 대화별 카드, 그 아래 "이런 모임 열어주세요" 항목(개설 가능 수), 그 아래 모임 카드. 모임 카드는 "오늘/내일/N일 후"(서울 날짜 기준)와 썸네일(image_url이 있을 때)을 보여준다. 다음 모임 카드는 모임마다 왼쪽에 머스타드 원형 배지(첫 줄 "11/8 (일)", 둘째 줄 "오후 2시")를 두고 오른쪽에 모임 제목을 굵게 쓴다. 남은 날 문구, 장소, 정원은 홈 카드에 적지 않는다(모임 화면 "자세히"에서 본다). 모임마다 아래 줄에 응답 버튼과 "자세히" 버튼을 둔다. 다음 모임 카드와 다가오는 모임 목록의 모든 모임에 참석 스위치를 둔다(운영자 제외, 취소된 모임 제외). 기본은 꺼진 "불참" 상태이고(아직 응답하지 않은 모임 포함), 켜면 참석·끄면 불참으로 `PUT meetups/<id>/rsvp/`를 보낸 뒤 홈을 다시 불러온다. 이름이 없는 방문자는 스위치를 켤 때 자동 닉네임으로 가입한 뒤 신청한다. 스위치 옆에 참석/불참 글자를 함께 쓴다. 홈 카드에는 "신청하기" 버튼을 두지 않는다. "자세히"와 모임 제목은 모임 정보 화면 /lite/m/:id/info로 이동한다(신청하기 직후에는 채팅방 /lite/m/:id로 바로 간다) |
| /lite/requests | 모임 요청 목록과 "이런 모임 열어주세요" 작성 버튼. 이름이 없으면 자동 닉네임으로 가입한 뒤 보여 준다 |
| /lite/m/:id/info | 모임 정보 화면(홈의 "자세히"). 모임 안내 패널(언제·어디서·정원·대상·내용) 아래에, 신청한 회원과 운영자에게는 "공지 확인하기" 버튼(누르면 채팅방 /lite/m/:id), 아직 신청하지 않은 방문자에게는 "신청하기"(가입·신청 후 채팅방)를 둔다. 취소된 모임이나 내보내진 회원에게는 버튼 없이 안내 문구만 보인다 |
| /lite/m/:id | 모임 채팅방. 이름이 없어도 이름을 묻지 않는다. "신청하기"를 누르면 자동 닉네임으로 가입하고 참석 신청까지 마친 뒤 채팅방을 연다. 홈 카드의 "신청하기"도 같은 방식으로 가입·신청한 뒤 이 화면으로 보낸다. 상단 줄: 썸네일(image_url이 있으면 40px, 없으면 달력 아이콘)·일정·장소와 "안내" 버튼(누르면 모임 안내 패널을 펼치고 접는다). 신청한 회원은 그 아래 "내 참석" 줄에서 [참석] [불참] 두 버튼으로 바로 응답을 바꾼다(미정은 고를 수 없고, 예전에 미정으로 응답한 회원은 두 버튼 모두 눌리지 않은 상태로 보인다). 미신청자는 메시지 대신 모임 안내 패널과 큰 신청하기 버튼을 보고, 상단 요약 줄은 취소·내보냄 안내가 있을 때만 보인다. 모임 안내 패널은 어르신도 읽기 쉽게 항목 이름(언제·어디서·정원·대상·내용)을 왼쪽에 두고 값을 크게 쓴다. 언제는 "11월 8일 일요일 오후 2시"와 남은 날, 정원은 "15명"과 "지금 N명 참석", 대상·내용은 운영자가 적었을 때만 보인다 |
| /lite/admin | 운영자 전용. 다가오는/지난 탭 모임 목록(날짜·제목·참석/정원·취소됨 칩)과 모임 만들기 버튼. 운영자가 아니면 홈으로 이동 |
| /lite/admin/m/:id | 운영자 전용 모임 관리. 수정 폼(대상, 내용, 썸네일 URL 포함), 참석자 명단과 내보내기, 채팅방 링크, 취소/되돌리기, 삭제. 내보내기·삭제는 화면 안에서 한 번 더 확인 |
| /lite/seminar | 내 1:1 세미나 채팅방. 이름이 없으면 자동 닉네임으로 가입한 뒤 바로 시작한다. 마지막 안내 메시지 아래 온라인/오프라인 선택 버튼 |
| /lite/seminar/:id | 운영자용 1:1 세미나 채팅방 + 확정 버튼 |
| /lite/new-request | 요청 작성(주제 + 시기 세그먼트). 방문자는 홈 "문의" 메뉴의 "이런 모임 열어주세요"에서 목록을 거치지 않고 이 화면으로 바로 온다. 이름이 없어도 열리고, "올리기"를 누를 때 자동 닉네임으로 가입한 뒤 요청을 올린다. 올린 뒤와 뒤로 가기는 방문자는 홈, 운영자는 /lite/requests로 간다 |
| /lite/new-meetup | 운영자 모임 만들기(제목, 일시, 장소, 정원, 대상, 내용). `?request=<id>`면 요청 제목을 채운다 |
| /lite/r#<token> | 복구 링크: fragment의 토큰으로 `GET me/`를 확인한 뒤에만 저장, 실패하면 기존 토큰 유지. 읽은 즉시 `history.replaceState`로 fragment 제거 후 /lite로 이동 |
| /lite/host#<key> | 운영자 링크: fragment의 key로 host/claim 호출(이름이 없으면 먼저 자동 닉네임으로 가입), 읽은 즉시 fragment 제거 후 /lite로 이동 |
- 토큰과 운영자 키는 URL 경로나 쿼리에 넣지 않는다(서버 접속 로그·방문 기록 노출 방지). fragment는 서버로 전송되지 않는다.
- 채팅방은 처음에 최신 100개를 보여 주고, 더 오래된 메시지가 있으면 맨 위의 "이전 메시지 보기"로 100개씩 더 불러온다(`?before=`). 새 메시지는 3초 간격으로 `?after=`를 사용해 가져온다. after 기준은 폴링으로 받은 마지막 id만 사용한다(내가 보낸 메시지 응답으로 기준을 앞당기지 않는다, id로 중복 제거). 화면을 벗어나거나 탭이 숨겨지면 멈추고, 401/403이면 중단한다.
- 홈에 예정된 모임이 없으면 "예정된 모임이 없어요" 한 줄을 표시한다.
- 레이아웃 폭: 모든 LITE 화면은 최대 480px 칼럼을 쓴다. 홈(/lite)만 화면 폭 1024px 이상에서 칼럼을 1040px로 넓히고, 다음 모임 카드는 왼쪽에 날짜·장소, 오른쪽에 모임 행을 두는 가로 배치로, 다가오는 모임은 위쪽에 이미지가 붙은 카드 그리드(최소 220px 칸)로 보여 준다. image_url이 없는 모임은 그리드에서 빈 이미지 영역을 두고, 모바일 목록에서는 썸네일을 그리지 않는다. 채팅방 등 다른 화면은 PC에서도 480px 칼럼을 유지한다.
- 상단 바는 배경과 같은 색이고, 스크롤해서 내용이 그 밑을 지나갈 때만 아래 구분선을 보인다. 상단 바 아래의 정보 줄(일정·세미나 상태)은 칼럼 끝까지 깔지 않고 본문 여백 안쪽의 둥근 상자로 둔다.
- 채팅(모임방·세미나방)은 테두리가 있는 창 하나로 보인다. 창은 화면 높이에 맞춰 고정되고 메시지만 창 안에서 스크롤한다. 창 맨 위에 고정 공지, 맨 아래에 입력창을 둔다. 같은 사람이 같은 분(서울 시간)에 보낸 메시지는 묶어서 이름·아바타는 첫 메시지에만, 시각(HH:mm)은 마지막 말풍선 옆에만 표시한다. 말풍선 글자는 길게 눌러 선택·복사할 수 있다(전역 `user-select: none`을 말풍선에서만 푼다). 날짜가 바뀌는 자리에는 "10월 19일 월요일" 구분 문구를 넣는다.
- 테마: 흑백 화면 틀 + 머스타드 강조 하나(Luma·Meetup처럼 색은 모임 사진이 낸다). 바탕 따뜻한 회색 #F1EFEA, 카드·채팅창 표면 #FFFFFF(바탕과 구분), 글자 #111111, 흐린 글자 #4A4A4A(바탕 대비 7.7:1, 어르신 권장 7:1 충족), 선 #E0DCD5, 강조 머스타드 #F5C431(신청하기·참석·내 말풍선에만), 다음 모임 머리글 #6E5000. 글자는 Pretendard(jsDelivr CDN의 가변 글꼴 dynamic subset), 본문 16px, 제목 800 굵기, 숫자는 tabular-nums. 버튼 높이 50px 이상. 다음 모임 카드는 흰 카드이고, 같은 날 모임이 여럿이어도 모임 줄마다 자기 썸네일(image_url, 휴대폰 64px·PC 88px 둥근 사각형)을 날짜 배지 왼쪽에 둔다. 사진이 없는 모임은 썸네일 자리를 두지 않는다. 다가오는 모임 목록은 56px 썸네일과 17px 제목을 쓴다. 참석은 초록(누른 버튼 #15803D, 칩 #E3F4EA 바탕에 #166534 글자), 불참은 빨강(누른 버튼 #C62828, 칩 #FBE4E4 바탕에 #B91C1C 글자)으로 칠한다. 누르지 않은 버튼에도 체크(초록)·X(빨강) 아이콘과 글자 라벨을 함께 두어 색만으로 구분하지 않는다. PC 홈 다음 모임 카드는 배지·제목·응답·자세히를 한 줄에 둔다. "문의" 버튼은 검정 알약 모양에 말풍선 아이콘과 글자를 함께 쓴다. html.dark와 관계없이 밝은 테마 하나만 쓴다. 미신청 모임에는 "신청하기"만 두고 불참 버튼은 두지 않는다(참석 인원만 표시).
