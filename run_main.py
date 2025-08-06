#!/usr/bin/env python3
"""
GST ML 시스템 실행 스크립트 (월간 실행용)
환경변수 설정 후 main.py 실행
"""

import os
import subprocess
import sys
import argparse


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


def run_main_system(mode=None):
    """ML 시스템 실행"""
    try:
        print("🚀 GST ML 시스템 실행 중...")

        # 환경변수 설정
        set_environment_variables()

        # 실행 명령어 구성
        script_path = "/Users/kdkyu311/Desktop/GST/PDA_ML/main.py"
        cmd = [sys.executable, script_path]

        if mode == "retrain":
            print("🔄 모델 재학습 모드")
            cmd.extend(["--mode", "retrain"])
        elif mode == "add_data":
            print("📊 데이터 추가 모드")
            cmd.extend(["--mode", "add_data"])
        else:
            print("🤖 기본 예측 모드")

        # ML 시스템 실행
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode == 0:
            print("✅ ML 시스템 실행 완료!")
        else:
            print(f"❌ ML 시스템 실행 실패: {result.returncode}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


def main():
    parser = argparse.ArgumentParser(description="GST ML 시스템 실행")
    parser.add_argument(
        "--mode", choices=["retrain", "add_data"], help="실행 모드 선택"
    )

    args = parser.parse_args()
    run_main_system(args.mode)


if __name__ == "__main__":
    main()
