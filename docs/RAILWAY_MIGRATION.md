# Railway Migration Runbook

## 1. 목표 아키텍처
- Railway Project: `meetup`
- App Service: Django backend (`backend/` root)
- Database Service: Railway PostgreSQL
- Frontend: 별도 Railway 서비스 또는 후속 정적 호스팅 전환
- Media: DB와 별개로 이관. 초기에는 manifest 검증 후 별도 저장소 전략 확정

## 2. 왜 PostgreSQL인가
`SPEC.md`는 프로덕션 DB를 PostgreSQL로 정의하고 있다. Railway는 PostgreSQL 템플릿과 백업 기능을 제공하므로, 운영 타깃은 SQLite 유지가 아니라 PostgreSQL 전환으로 잡는다.

## 3. 전환 전 필수 점검
1. 실제 운영 원본 DB를 확정한다.
2. 아래 명령으로 snapshot을 남긴다.
   ```bash
   cd backend
   python scripts/db_snapshot.py > ../artifacts/source-db-snapshot.json
   ```
3. `media/` 파일 manifest를 남긴다.
   ```bash
   find media -type f | sort > artifacts/media-manifest.txt
   ```
4. 서비스 점검 시간을 공지하고, cutover 직전 쓰기 작업을 멈춘다.

## 4. Railway 환경 변수
Backend service에 최소 아래 값을 설정한다.

```bash
DJANGO_SETTINGS_MODULE=meetup_backend.settings_production
SECRET_KEY=<strong secret>
DATABASE_URL=${{Postgres.DATABASE_URL}}
DATABASE_SSL_REQUIRE=true
ALLOWED_HOSTS=<railway-domain>,meet.onebitebitcoin.com
SITE_URL=https://<railway-domain>
CSRF_TRUSTED_ORIGINS=https://<railway-domain>,https://meet.onebitebitcoin.com
```

## 5. DB 이관 절차
### 5.1 Dry-run
1. 빈 PostgreSQL 대상 DB 준비
2. Django migration 실행
3. bulk copy 스크립트로 SQLite 데이터를 PostgreSQL에 적재
4. snapshot 비교 + smoke test

권장 적재 순서:
```bash
cd backend
python manage.py migrate --noinput
cd ..
python scripts/sqlite_to_postgres.py \
  --sqlite-path backend/db.sqlite3 \
  --database-url "$DATABASE_URL"
cd backend
python scripts/db_snapshot.py > ../artifacts/target-db-snapshot.json
```

`loaddata`는 공개 TCP 경유에서 단건 ORM 저장이 많아 느릴 수 있으므로, 실제 cutover 경로에서는 사용하지 않는다.

### 5.2 Cutover
1. 기존 서비스 쓰기 중단
2. 최종 snapshot 생성
3. 최종 export 수행
4. Railway PostgreSQL import 수행
5. snapshot 비교
6. 로그인 / 모임 목록 / 참가 신청 / 후기 / 과제 smoke test
7. 이상 없으면 DNS 또는 frontend API endpoint 전환

## 6. 검증 기준
| 항목 | 기준 |
|---|---|
| 핵심 모델 count | 소스와 타깃 일치 |
| max id | 주요 모델별 일치 |
| 최신 timestamp | 주요 모델별 일치 |
| FK 조회 | 오류 없음 |
| 신규 생성 | User/Meetup/Registration smoke 성공 |
| media manifest | 파일 수 및 샘플 파일 일치 |

## 7. 롤백 기준
아래 중 하나라도 발생하면 전환을 중단하고 기존 서비스로 되돌린다.
- row count mismatch
- FK 오류
- 신규 생성 실패
- media 파일 누락
- Railway startup failure

롤백 시:
1. frontend/API endpoint를 기존 서비스로 복구
2. Railway import DB는 유지하되 쓰기 중단
3. 원본 DB snapshot과 오류 로그를 보존
4. 원인 수정 후 dry-run부터 재실행

## 8. 주의 사항
- `backend/db.sqlite3`와 루트 `db.sqlite3`는 데이터량이 다르다. 실제 운영 원본을 확정하기 전까지 임의 선택 금지
- DB 이관과 media 이관은 별도 검증 대상
- 자동 start command에서 migration은 허용하되, 실제 데이터 import는 수동 검증 후 수행
