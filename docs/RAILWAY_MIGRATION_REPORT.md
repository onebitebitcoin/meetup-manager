# Railway Migration Validation Report

## 실행일
- 2026-05-17 KST

## 수행 내용
1. Railway 프로젝트 `meetup` 생성
2. Railway PostgreSQL 서비스 생성
3. Django 설정을 `DATABASE_URL` 기반으로 보강
4. `backend/db.sqlite3` 기준 source snapshot 생성
5. Railway PostgreSQL로 bulk-copy dry-run 수행
6. source/target snapshot 비교
7. rollback-only smoke transaction 수행

## Dry-run 결과
| 검증 항목 | 결과 |
|---|---|
| 핵심 모델 snapshot 비교 | PASS |
| PostgreSQL migration 적용 | PASS |
| bulk copy 적재 | PASS |
| 신규 User/Meetup/Registration 생성 smoke | PASS |
| media manifest 생성 | PASS |

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
3. media 파일은 DB와 별도 이관 대상이다. 현재 manifest 기준 11개 파일을 별도 검증해야 한다.

## 남은 실제 전환 단계
1. 실제 운영 원본 DB freeze
2. 최종 snapshot 재생성
3. bulk copy 재실행
4. media 이관
5. Railway backend 공개 도메인/최종 secret 설정
6. smoke test 후 DNS/API endpoint 전환
