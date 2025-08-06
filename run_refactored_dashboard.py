#!/usr/bin/env python3
"""
GST 불량 분석 대시보드 실행 스크립트 (리팩토링 버전)
환경변수 설정 후 리팩토링된 대시보드 실행
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


def run_refactored_dashboard():
    """리팩토링된 대시보드 실행"""
    try:
        print("🚀 GST 불량 분석 대시보드 (리팩토링 버전) 실행 중...")

        # 환경변수 설정
        set_environment_variables()

        # 리팩토링된 대시보드 실행 (테스트 스크립트 사용)
        result = subprocess.run(
            [sys.executable, "test_refactored.py"], capture_output=False, text=True
        )

        if result.returncode == 0:
            print("✅ 리팩토링된 대시보드 실행 완료!")
        else:
            print(f"❌ 대시보드 실행 실패: {result.returncode}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


def run_comparison_test():
    """기존 버전과 리팩토링 버전 비교 테스트"""
    try:
        print("🔍 기존 버전 vs 리팩토링 버전 비교 테스트 시작...")

        # 환경변수 설정
        set_environment_variables()

        print("\n📊 1. 기존 버전 실행...")
        original_script = (
            "/Users/kdkyu311/Desktop/GST/PDA_ML/analysis/defect_visualizer.py"
        )
        original_result = subprocess.run(
            [sys.executable, original_script], capture_output=True, text=True
        )

        print("\n📊 2. 리팩토링 버전 실행...")
        refactored_result = subprocess.run(
            [sys.executable, "test_refactored.py"], capture_output=True, text=True
        )

        print("\n📋 결과 비교:")
        print(f"기존 버전 종료 코드: {original_result.returncode}")
        print(f"리팩토링 버전 종료 코드: {refactored_result.returncode}")

        if original_result.returncode == refactored_result.returncode == 0:
            print("✅ 두 버전 모두 성공적으로 실행됨!")
        else:
            print("❌ 실행 결과가 다릅니다.")
            if original_result.stderr:
                print(f"기존 버전 오류: {original_result.stderr}")
            if refactored_result.stderr:
                print(f"리팩토링 버전 오류: {refactored_result.stderr}")

    except Exception as e:
        print(f"❌ 비교 테스트 중 오류 발생: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="GST 불량 분석 대시보드 (리팩토링 버전)"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["run", "compare"],
        default="run",
        help="실행 모드: run (리팩토링 버전만 실행), compare (기존 vs 리팩토링 비교)",
    )
    args = parser.parse_args()

    if args.mode == "compare":
        run_comparison_test()
    else:
        run_refactored_dashboard()
