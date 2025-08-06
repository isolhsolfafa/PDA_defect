#!/usr/bin/env python3
"""
리팩토링된 DefectVisualizer 테스트 스크립트
"""

import os
import sys


def test_refactored_visualizer():
    """리팩토링된 DefectVisualizer 테스트"""
    try:
        # 환경변수 설정
        env_vars = {
            "TEAMS_TENANT_ID": os.getenv("TEAMS_TENANT_ID", ""),
            "TEAMS_CLIENT_ID": os.getenv("TEAMS_CLIENT_ID", ""),
            "TEAMS_CLIENT_SECRET": os.getenv("TEAMS_CLIENT_SECRET", ""),
            "TEAMS_TEAM_ID": os.getenv("TEAMS_TEAM_ID", ""),
        }

        for key, value in env_vars.items():
            os.environ[key] = value

        print("🚀 리팩토링된 DefectVisualizer 테스트 시작...")

        # 리팩토링된 DefectVisualizer import 및 실행
        from refactored_analysis import DefectVisualizer

        print("✅ DefectVisualizer import 성공")

        # 인스턴스 생성
        visualizer = DefectVisualizer()
        print("✅ DefectVisualizer 인스턴스 생성 성공")

        # 메인 함수 실행
        visualizer.main()
        print("✅ 리팩토링된 DefectVisualizer 실행 완료!")

        return True

    except Exception as e:
        print(f"❌ 리팩토링된 버전 실행 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_refactored_visualizer()
    sys.exit(0 if success else 1)
