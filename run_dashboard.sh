#!/bin/bash

# GST 불량 분석 대시보드 실행 스크립트
echo "🚀 GST 불량 분석 대시보드 실행 중..."

# 환경변수 설정
export TEAMS_TENANT_ID="bed54eb6-6d05-4a6c-a7cd-c7b1cba1a040"
export TEAMS_CLIENT_ID="4acb1453-4982-4bdf-8bde-cb766516c89f"
export TEAMS_CLIENT_SECRET="WoK8Q~FByB7znqpHXWbxrr9lFG4ay5UjForZYbE9"
export TEAMS_TEAM_ID="ccffe771-2ae7-43e9-8159-291425184304"

# 대시보드 실행
python3 /Users/kdkyu311/Desktop/GST/PDA_ML/analysis/defect_visualizer.py

echo "✅ 대시보드 실행 완료!" 