#!/usr/bin/env python3
"""
일간 실행용 경량화된 대시보드 생성 스크립트
- 기존 ML 모델 사용 (재학습 없음)
- 최신 데이터만 로드
- HTML 생성 + GitHub 업로드
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

from data.teams_loader import TeamsDataLoader
from ml.defect_predictor import DefectPredictor
from analysis.defect_analyzer import DefectAnalyzer
from analysis.advanced_defect_analyzer import AdvancedDefectAnalyzer
from output.github_uploader import GitHubUploader
from utils.logger import setup_logger, flush_log
from config import ml_config


class DailyDashboard:
    """일간 대시보드 생성 클래스"""

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.teams_loader = TeamsDataLoader()
        self.predictor = DefectPredictor()
        self.analyzer = DefectAnalyzer()
        self.advanced_analyzer = AdvancedDefectAnalyzer()
        self.uploader = GitHubUploader()

    def run_daily_update(self):
        """일간 대시보드 업데이트 실행"""
        try:
            self.logger.info("🌅 일간 대시보드 업데이트 시작")

            # 1. 기존 ML 모델 로드
            self.logger.info("📂 기존 ML 모델 로드 중...")
            self.predictor.load_model()

            # 2. 최신 Teams 데이터 로드
            self.logger.info("📊 최신 Teams 데이터 로드 중...")
            data = self.teams_loader.load_defect_data_from_teams()

            # 3. 데이터 전처리 (경량화)
            self.logger.info("🔧 데이터 전처리 중...")
            data["keywords"] = data["상세불량내용"].apply(
                self.teams_loader.preprocess_text
            )
            data["keyword_text"] = data["keywords"].apply(lambda x: " ".join(x))

            # 4. 월간 생산량 데이터 로드 (캐시된 데이터 사용)
            monthly_counts = self._load_cached_production_data()

            # 5. 불량 확률 예측 (기존 모델 사용)
            self.logger.info("🔍 불량 확률 예측 중...")
            production_weights = self._calculate_production_weights(monthly_counts)
            predictions = self.predictor.predict_defect_probability(
                data, production_weights, monthly_counts
            )

            # 6. 기본 불량 분석
            self.logger.info("📈 불량 분석 중...")
            defect_analysis = self.analyzer.analyze_defects(data)

            # 7. 고도화된 분석
            self.logger.info("🎯 고도화된 분석 중...")
            advanced_analysis = self.advanced_analyzer.analyze_advanced_defects(data)
            advanced_suggestions = (
                self.advanced_analyzer.generate_improvement_suggestions(predictions)
            )

            # 8. 대시보드 데이터 구성
            dashboard_data = self.advanced_analyzer.create_dashboard_data(
                predictions, advanced_analysis, advanced_suggestions
            )

            # 9. HTML 템플릿 로드
            self.logger.info("📄 HTML 템플릿 로드 중...")
            html_content = self._load_html_template()

            # 10. GitHub 업로드
            self.logger.info("🚀 GitHub 업로드 중...")
            success = self.uploader.upload_dashboard_files(html_content, dashboard_data)

            if success:
                self.logger.info("✅ 일간 대시보드 업데이트 완료!")
                self._print_daily_summary(predictions, len(data))
            else:
                self.logger.error("❌ 일간 대시보드 업데이트 실패")

        except Exception as e:
            self.logger.error(f"❌ 일간 업데이트 중 오류 발생: {e}")
            raise
        finally:
            flush_log(self.logger)

    def _load_cached_production_data(self) -> Dict[str, int]:
        """캐시된 월간 생산량 데이터 로드"""
        cache_file = "cache/monthly_production.json"

        try:
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.logger.info("📂 캐시된 생산량 데이터 로드 성공")
                    return data
        except Exception as e:
            self.logger.warning(f"⚠️ 캐시 로드 실패: {e}")

        # 캐시 실패 시 기본값 반환
        self.logger.info("🔄 기본 생산량 데이터 사용")
        return {
            "GAIA-I DUAL": 45,
            "GAIA-I": 42,
            "DRAGON": 8,
            "GAIA-II DUAL": 6,
            "SWS-I": 5,
            "GAIA-II": 4,
            "GAIA-P DUAL": 3,
            "DRAGON DUAL": 1,
        }

    def _calculate_production_weights(
        self, monthly_counts: Dict[str, int]
    ) -> Dict[str, float]:
        """생산량 가중치 계산"""
        total_production = sum(monthly_counts.values())
        return {
            model: count / total_production for model, count in monthly_counts.items()
        }

    def _load_html_template(self) -> str:
        """HTML 템플릿 로드"""
        template_path = "templates/dashboard_template.html"
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            self.logger.error(f"HTML 템플릿을 찾을 수 없습니다: {template_path}")
            raise

    def _print_daily_summary(self, predictions, data_count):
        """일간 업데이트 요약 출력"""
        self.logger.info("=" * 50)
        self.logger.info("📊 일간 업데이트 요약")
        self.logger.info("=" * 50)
        self.logger.info(f"📈 처리된 데이터: {data_count}건")
        self.logger.info(f"🔍 상위 불량 예측 ({len(predictions)}건):")

        for i, pred in enumerate(predictions[:3], 1):
            self.logger.info(
                f"  {i}. {pred['모델']} - {pred['예상불량률']:.1f}% (부품: {pred['부품']})"
            )

        self.logger.info(
            f"⏰ 업데이트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )


def main():
    """메인 실행 함수"""
    dashboard = DailyDashboard()
    dashboard.run_daily_update()


if __name__ == "__main__":
    main()
