# Railway Migration Validation Report

## 실행일
- 2026-05-17 KST

## 수행 내용
1. Railway 프로젝트 `meetup` 생성
2. Railway PostgreSQL 서비스 생성
3. Railway backend 서비스 배포 및 Railway 제공 도메인 발급
4. Django 설정을 `DATABASE_URL` 기반으로 보강
4. `backend/db.sqlite3` 기준 source snapshot 생성
5. Railway PostgreSQL로 bulk-copy dry-run 수행
6. source/target snapshot 비교
7. rollback-only smoke transaction 수행
8. backend media volume 연결 및 기존 운영 media 39건 이관

## Dry-run 결과
| 검증 항목 | 결과 |
|---|---|
| 핵심 모델 snapshot 비교 | PASS |
| PostgreSQL migration 적용 | PASS |
| bulk copy 적재 | PASS |
| 신규 User/Meetup/Registration 생성 smoke | PASS |
| media manifest 생성 | PASS |
| Railway media volume 이관 | PASS |

## 핵심 수치
| 모델 | Count |
|---|---:|
| auth.User | 258 |
| meetups.MeetupUser | 314 |
| meetups.Meetup | 56 |
| meetups.Registration | 455 |
| meetups.Waitlist | 7 |
| meetups.Notification | 63 |
| meetups.Task | 9 |
| meetups.TaskSubmission | 21 |
| meetups.Review | 14 |
| meetups.MeetupPaymentLink | 5 |

## 확인된 리스크
1. `backend/db.sqlite3`와 루트 `db.sqlite3`의 데이터량이 다르다. 실제 운영 cutover 전에 반드시 원본 DB를 확정해야 한다.
2. `loaddata` 방식은 Railway 공개 TCP 경유에서 느리다. 실전 경로는 `scripts/sqlite_to_postgres.py` bulk copy를 사용한다.
3. 로컬 `artifacts/media-manifest.txt`는 11개 파일만 담고 있었지만, 실제 DB가 참조하는 운영 media는 39건이었다. 최종 이관은 DB 참조 기준 39건으로 검증해야 한다.
4. Railway backend는 reverse proxy가 없으므로 media volume만 붙여서는 부족하고, `SERVE_MEDIA_FILES=true` 설정이 함께 필요하다.

## 남은 실제 전환 단계
1. 실제 운영 원본 DB freeze
2. 최종 snapshot 재생성
3. bulk copy 재실행
4. smoke test 후 DNS/API endpoint 전환
