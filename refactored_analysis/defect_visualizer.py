"""
Defect Visualizer - Main Module

기존 DefectVisualizer 클래스와 호환성 유지
리팩토링된 모듈들을 통합하는 메인 클래스
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.graph_objects as go
from typing import Dict

# 직접 실행 시 절대 import 사용
if __name__ == "__main__":
    from base_visualizer import BaseVisualizer
    from pressure_charts import PressureCharts
    from quality_charts import QualityCharts
    from dashboard_builder import DashboardBuilder
else:
    # 패키지 import 시 상대 import 사용
    from .base_visualizer import BaseVisualizer
    from .pressure_charts import PressureCharts
    from .quality_charts import QualityCharts
    from .dashboard_builder import DashboardBuilder

from utils.logger import setup_logger, flush_log

logger = setup_logger(__name__)


class DefectVisualizer:
    """
    불량 데이터 시각화 메인 클래스

    기존 analysis/defect_visualizer.py와 동일한 인터페이스 제공
    내부적으로 리팩토링된 모듈들 사용
    """

    def __init__(self):
        """초기화 - 기존 코드와 호환성 유지"""
        try:
            self.base = BaseVisualizer()
            self.pressure_charts = PressureCharts()
            self.quality_charts = QualityCharts()
            self.dashboard_builder = DashboardBuilder()

            # 기존 속성들과 호환성 유지
            self.use_mock_data = self.base.use_mock_data
            self.teams_loader = self.base.teams_loader

            logger.info("✅ DefectVisualizer 초기화 완료 (리팩토링 버전)")

        except Exception as e:
            logger.error(f"❌ DefectVisualizer 초기화 실패: {e}")
            raise

    # =========================================================================
    # 데이터 로딩 메서드들 (기존 API 유지)
    # =========================================================================

    def load_analysis_data(self) -> pd.DataFrame:
        """불량분석 워크시트 데이터 로드"""
        return self.pressure_charts.load_analysis_data()

    def load_defect_data(self) -> pd.DataFrame:
        """불량내역 워크시트 데이터 로드"""
        return self.pressure_charts.load_defect_data()

    def load_quality_analysis_data(self) -> pd.DataFrame:
        """제조품질 불량분석 워크시트 데이터 로드"""
        return self.quality_charts.load_quality_analysis_data()

    def load_quality_defect_data(self) -> pd.DataFrame:
        """제조품질 불량내역 워크시트 데이터 로드"""
        return self.quality_charts.load_quality_defect_data()

    # =========================================================================
    # 유틸리티 메서드들 (기존 API 유지)
    # =========================================================================

    def generate_colors(self, count: int) -> list:
        """동적 색상 생성"""
        return self.base.generate_colors(count)

    # =========================================================================
    # 가압검사 관련 메서드들 (기존 API 유지)
    # =========================================================================

    def extract_monthly_data(self) -> Dict:
        """월별 불량 현황 데이터 추출"""
        return self.pressure_charts.extract_monthly_data()

    def extract_action_type_data(self) -> Dict:
        """불량조치 유형별 데이터 추출"""
        return self.pressure_charts.extract_action_type_data()

    def extract_supplier_data(self) -> Dict:
        """외주사별 불량 데이터 추출"""
        return self.pressure_charts.extract_supplier_data()

    def extract_supplier_monthly_data(self) -> Dict:
        """기구 외주사별 월별 불량률 데이터 추출"""
        return self.pressure_charts.extract_supplier_monthly_data()

    def extract_supplier_quarterly_data(self) -> Dict:
        """기구 외주사별 분기별 불량률 데이터 추출"""
        return self.pressure_charts.extract_supplier_quarterly_data()

    def create_monthly_trend_chart(self) -> go.Figure:
        """월별 불량 트렌드 차트 생성"""
        return self.pressure_charts.create_monthly_trend_chart()

    def create_action_type_integrated_chart(self) -> go.Figure:
        """불량조치 유형별 통합 차트"""
        return self.pressure_charts.create_action_type_integrated_chart()

    def create_supplier_chart(self) -> go.Figure:
        """외주사별 불량 차트 생성"""
        return self.pressure_charts.create_supplier_chart()

    def create_supplier_monthly_chart(self) -> go.Figure:
        """기구 외주사별 월별 불량률 차트 생성"""
        return self.pressure_charts.create_supplier_monthly_chart()

    def create_supplier_quarterly_chart(self) -> go.Figure:
        """기구 외주사별 분기별 불량률 차트 생성"""
        return self.pressure_charts.create_supplier_quarterly_chart()

    def create_supplier_integrated_chart(self) -> go.Figure:
        """기구 외주사별 통합 차트"""
        return self.pressure_charts.create_supplier_integrated_chart()

    def create_action_type_monthly_chart(self) -> go.Figure:
        """조치 유형별 월별 차트"""
        return self.pressure_charts.create_action_type_monthly_chart()

    def create_part_monthly_chart(self) -> go.Figure:
        """부품별 월별 차트"""
        return self.pressure_charts.create_part_monthly_chart()

    def create_part_integrated_chart(self) -> go.Figure:
        """가압검사 부품별 통합 차트 (드롭다운 형태)"""
        return self.pressure_charts.create_part_integrated_chart()

    # =========================================================================
    # 제조품질 관련 메서드들 (기존 API 유지)
    # =========================================================================

    def extract_quality_monthly_data(self) -> Dict:
        """제조품질 월별 데이터 추출"""
        return self.quality_charts.extract_quality_monthly_data()

    def extract_quality_kpi_data(self) -> Dict:
        """제조품질 KPI 데이터 추출 (엑셀 기준)"""
        return self.quality_charts.extract_quality_kpi_data()

    def create_quality_monthly_trend_chart(self) -> go.Figure:
        """제조품질 월별 트렌드 차트 생성"""
        return self.quality_charts.create_quality_monthly_trend_chart()

    def create_quality_action_integrated_chart(self) -> go.Figure:
        """제조품질 조치 유형별 통합 차트 생성"""
        return self.quality_charts.create_quality_action_integrated_chart()

    def create_quality_supplier_integrated_chart(self) -> go.Figure:
        """제조품질 외주사별 통합 차트"""
        return self.quality_charts.create_supplier_integrated_chart()

    def create_quality_part_monthly_chart(self) -> go.Figure:
        """제조품질 부품별 월별 차트"""
        return self.quality_charts.create_quality_part_monthly_chart()

    def create_quality_part_integrated_chart(self) -> go.Figure:
        """제조품질 부품별 통합 차트 (드롭다운 형태)"""
        return self.quality_charts.create_quality_part_integrated_chart()

    # =========================================================================
    # HTML 대시보드 관련 메서드들 (기존 API 유지)
    # =========================================================================

    def generate_defect_analysis_html(self) -> str:
        """완전한 HTML 대시보드 생성"""
        return self.dashboard_builder.generate_defect_analysis_html()

    def save_html_report(self, filename: str = "defect_analysis_dashboard.html") -> str:
        """HTML 리포트를 파일로 저장"""
        return self.dashboard_builder.save_html_report(filename)

    def save_and_upload_internal_report(self) -> bool:
        """내부용 HTML 리포트 생성 및 GitHub 업로드"""
        return self.dashboard_builder.save_and_upload_internal_report()

    def main(self):
        """데일리 실행용 메인 함수 (기존 API 호환)"""
        try:
            logger.info("🌅 데일리 internal.html 대시보드 업데이트 시작")

            # internal.html 생성 및 GitHub 업로드
            success = self.save_and_upload_internal_report()

            if success:
                logger.info("✅ 데일리 internal.html 업데이트 완료!")
                print("✅ internal.html 대시보드가 성공적으로 업데이트되었습니다!")

                # config에서 URL 동적 생성
                from config import github_config

                print(
                    f"🌐 접속 URL: https://{github_config.username_2}.github.io/{github_config.repo_2}/public/internal.html"
                )
            else:
                logger.error("❌ 데일리 업데이트 실패")
                print("❌ 업데이트 중 오류가 발생했습니다.")

        except Exception as e:
            logger.error(f"❌ 데일리 실행 중 오류 발생: {e}")
            print(f"❌ 오류 발생: {e}")
        finally:
            flush_log(logger)


def main():
    """메인 실행 함수"""
    try:
        logger.info("🚀 리팩토링된 DefectVisualizer 실행 시작...")

        # DefectVisualizer 인스턴스 생성
        visualizer = DefectVisualizer()

        # HTML 대시보드 생성 및 업로드
        success = visualizer.save_and_upload_internal_report()

        if success:
            logger.info("✅ 대시보드 생성 및 업로드 완료!")
            from config import github_config

            print(
                f"🌐 접속 URL: https://{github_config.username_2}.github.io/{github_config.repo_2}/public/internal.html"
            )
        else:
            logger.error("❌ 대시보드 업로드 실패")

    except Exception as e:
        logger.error(f"❌ 메인 실행 실패: {e}")
        flush_log(logger)
        raise


if __name__ == "__main__":
    main()
