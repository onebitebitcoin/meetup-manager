#!/bin/bash
set -e

echo "=== Backend 의존성 설치 ==="
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-test.txt
deactivate

echo ""
echo "=== Frontend 의존성 설치 ==="
cd ../frontend
npm install

echo ""
echo "=== 설치 완료 ==="
echo "Backend: cd backend && source venv/bin/activate"
echo "Frontend: cd frontend && npm run dev"
