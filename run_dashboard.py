#!/usr/bin/env python3
"""
GST 불량 분석 대시보드 실행 스크립트
환경변수 설정 후 대시보드 실행
"""

import os
import subprocess
import sys


def set_environment_variables():
    """환경변수 설정"""
    env_vars = {
        "TEAMS_TENANT_ID": os.getenv("TEAMS_TENANT_ID", ""),
        "TEAMS_CLIENT_ID": os.getenv("TEAMS_CLIENT_ID", ""),
        "TEAMS_CLIENT_SECRET": os.getenv("TEAMS_CLIENT_SECRET", ""),
        "TEAMS_TEAM_ID": os.getenv("TEAMS_TEAM_ID", ""),
    }

    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ {key} 설정 완료")


def run_dashboard():
    """대시보드 실행"""
    try:
        print("🚀 GST 불량 분석 대시보드 실행 중...")

        # 환경변수 설정
        set_environment_variables()

        # 대시보드 실행
        script_path = "/Users/kdkyu311/Desktop/GST/PDA_ML/analysis/defect_visualizer.py"
        result = subprocess.run(
            [sys.executable, script_path], capture_output=False, text=True
        )

        if result.returncode == 0:
            print("✅ 대시보드 실행 완료!")
        else:
            print(f"❌ 대시보드 실행 실패: {result.returncode}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    run_dashboard()
