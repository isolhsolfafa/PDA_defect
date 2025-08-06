#!/bin/bash

# GST ML 시스템 실행 스크립트 (월간 실행용)
echo "🚀 GST ML 시스템 실행 중..."

# 환경변수 설정
export TEAMS_TENANT_ID="bed54eb6-6d05-4a6c-a7cd-c7b1cba1a040"
export TEAMS_CLIENT_ID="4acb1453-4982-4bdf-8bde-cb766516c89f"
export TEAMS_CLIENT_SECRET="WoK8Q~FByB7znqpHXWbxrr9lFG4ay5UjForZYbE9"
export TEAMS_TEAM_ID="ccffe771-2ae7-43e9-8159-291425184304"

# 실행 모드 확인
if [ "$1" = "retrain" ]; then
    echo "🔄 모델 재학습 모드"
    python3 /Users/kdkyu311/Desktop/GST/PDA_ML/main.py --mode retrain
elif [ "$1" = "add_data" ]; then
    echo "📊 데이터 추가 모드"
    python3 /Users/kdkyu311/Desktop/GST/PDA_ML/main.py --mode add_data
else
    echo "🤖 기본 예측 모드"
    python3 /Users/kdkyu311/Desktop/GST/PDA_ML/main.py
fi

echo "✅ ML 시스템 실행 완료!" 