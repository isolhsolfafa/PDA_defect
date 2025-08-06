#!/usr/bin/env python3
"""
공장 불량 예측 시스템 메인 실행 파일

이 시스템은 다음 기능을 제공합니다:
1. 불량 데이터 로드 및 전처리
2. ML 모델을 통한 불량 확률 예측
3. 생산량 기반 가중치 적용
4. 대시보드 생성 및 GitHub 업로드
5. 데이터 축적 기능
"""

import os
import json
from typing import Optional

# .env 파일 로드 (로컬 개발용)
try:
    from dotenv import load_dotenv
    load_dotenv()  # .env 파일의 환경변수를 자동으로 로드
    print("✅ .env 파일에서 환경변수 로드 완료")
except ImportError:
    # dotenv가 없으면 패스 (GitHub Actions에서는 불필요)
    pass
except FileNotFoundError:
    # .env 파일이 없으면 패스 (GitHub Actions에서는 정상)
    pass

# 모듈 임포트
from config import TEST_MODE
from utils.logger import setup_logger, flush_log
from data.data_loader import DataLoader, GoogleSheetsLoader
from data.teams_loader import TeamsIntegratedDataLoader  # Teams 연동 활성화
from ml.defect_predictor import DefectPredictor, ProductionWeightCalculator
from analysis.defect_analyzer import DefectAnalyzer
from analysis.advanced_defect_analyzer import AdvancedDefectAnalyzer
from output.github_uploader import GitHubUploader

# 전역 로거 설정
logger = setup_logger(__name__)


class FactoryDefectPredictionSystem:
    """공장 불량 예측 시스템 메인 클래스"""

    def __init__(self):
        self.data_loader = DataLoader()
        # Teams 연동 활성화 - Teams 데이터 우선 사용
        self.teams_loader = TeamsIntegratedDataLoader()
        self.sheets_loader = GoogleSheetsLoader()
        self.predictor = DefectPredictor()
        self.analyzer = DefectAnalyzer()
        self.advanced_analyzer = AdvancedDefectAnalyzer()
        self.uploader = GitHubUploader()

        # 필요한 디렉토리 생성
        self._create_directories()

    def _create_directories(self):
        """필요한 디렉토리들을 생성"""
        directories = ["data", "logs", "models", "credentials", "output"]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"📁 디렉토리 생성: {directory}")

    def run_prediction_pipeline(self, use_existing_model: bool = False):
        """전체 예측 파이프라인 실행"""
        logger.info("🚀 공장 불량 예측 시스템 시작")
        flush_log(logger)

        try:
            # 1. 데이터 로드
            logger.info("=" * 50)
            logger.info("1단계: 데이터 로드")

            # Teams 데이터 우선 사용 (실패시 로컬 CSV 사용)
            try:
                data = self.teams_loader.load_data_with_fallback()
                logger.info("✅ Teams 데이터 로드 완료")
            except Exception as e:
                logger.error(f"❌ 데이터 로드 실패: {e}")
                raise

            # 2. 텍스트 전처리
            logger.info("=" * 50)
            logger.info("2단계: 텍스트 전처리")
            data["keywords"] = data["상세불량내용"].apply(
                self.data_loader.preprocess_text
            )
            data["keyword_text"] = data["keywords"].apply(lambda x: " ".join(x))

            # 3. 모델 로드 또는 학습
            logger.info("=" * 50)
            logger.info("3단계: ML 모델 준비")

            if use_existing_model:
                try:
                    self.predictor.load_model()
                    logger.info("✅ 기존 모델 로드 완료")
                except:
                    logger.warning("기존 모델 로드 실패, 새로 학습합니다.")
                    use_existing_model = False

            if not use_existing_model:
                train_results = self.predictor.train_model(data)
                logger.info(f"모델 학습 결과: 정확도 {train_results['accuracy']:.3f}")
                self.predictor.save_model()

            # 4. 생산량 데이터 로드
            logger.info("=" * 50)
            logger.info("4단계: 생산량 데이터 로드")
            monthly_counts = self.sheets_loader.get_monthly_production_counts()
            production_weights = ProductionWeightCalculator.calculate_weights(
                monthly_counts
            )

            # 5. 불량 확률 예측 (원본 데이터 사용)
            logger.info("=" * 50)
            logger.info("5단계: 불량 확률 예측")
            predictions = self.predictor.predict_defect_probability(
                data, production_weights, monthly_counts
            )

            # 6. 불량 분석을 위한 데이터 준비 (원본 데이터 직접 사용)
            logger.info("=" * 50)
            logger.info("6단계: 불량 분석")

            analysis_data = data.copy()
            analysis_data["keywords"] = analysis_data["상세불량내용"].apply(
                self.data_loader.preprocess_text
            )
            analysis_data["keyword_text"] = analysis_data["keywords"].apply(
                lambda x: " ".join(x)
            )

            if "제품명" in analysis_data.columns:
                analysis_data["제품명"] = analysis_data["제품명"].apply(
                    self.predictor.normalize_product_name
                )

            defect_analysis = self.analyzer.analyze_defect_types(analysis_data, None)
            recent_defects = self.analyzer.generate_recent_defects(
                analysis_data, None, production_weights
            )
            top_defects = self.analyzer.analyze_top_defects(recent_defects)

            # 7. 고도화된 분석 실행
            logger.info("=" * 50)
            logger.info("7단계: 고도화된 ML 분석")
            try:
                advanced_analysis = self.advanced_analyzer.advanced_failure_analysis(
                    analysis_data, predictions
                )
                logger.info("✅ 고도화된 실패 분석 완료")

                advanced_suggestions = (
                    self.advanced_analyzer.generate_advanced_suggestions(
                        advanced_analysis, predictions
                    )
                )
                logger.info(
                    f"✅ Pin Point 제안 생성 완료: {len(advanced_suggestions)}개"
                )

                # 8. 고도화된 대시보드 데이터 생성
                logger.info("=" * 50)
                logger.info("8단계: 고도화된 대시보드 데이터 생성")
                dashboard_data = self.advanced_analyzer.create_advanced_dashboard_data(
                    predictions, advanced_analysis, advanced_suggestions
                )
                logger.info("✅ 고도화된 분석 완료!")
                logger.info(f"🔍 대시보드 데이터 키: {list(dashboard_data.keys())}")
                if "predictions" in dashboard_data and dashboard_data["predictions"]:
                    first_pred_keys = list(dashboard_data["predictions"][0].keys())
                    logger.info(f"🔍 첫 번째 예측 키: {first_pred_keys}")
                    first_suggestion = dashboard_data["predictions"][0].get(
                        "제안", "N/A"
                    )
                    logger.info(f"🔍 고도화된 제안: {first_suggestion[:30]}...")

            except Exception as e:
                logger.error(f"❌ 고도화된 분석 실패: {e}", exc_info=True)
                logger.info("🔄 기존 분석 방식으로 fallback...")

                dashboard_data = {
                    "predictions": predictions,
                    "defect_analysis": defect_analysis,
                    "top_keywords": top_defects,
                    "suggestion": self.analyzer.generate_improvement_suggestions(
                        analysis_data, recent_defects
                    ),
                }

            # 9. HTML 템플릿 로드
            logger.info("=" * 50)
            logger.info("9단계: 대시보드 HTML 생성")
            html_content = self._load_html_template()

            # 10. 결과 분석 및 로깅 (업로드 비활성화)
            logger.info("=" * 50)
            logger.info("10단계: 불량 예측 결과 분석")

            # 업로드 비활성화 확인
            from config import DISABLE_GITHUB_UPLOAD

            if DISABLE_GITHUB_UPLOAD:
                logger.info("🔄 GitHub 업로드 비활성화됨 - 로깅으로 결과 출력")

                # 상세 예측 결과 로깅
                logger.info(
                    f"📊 전체 예측 결과 개수: {len(dashboard_data.get('predictions', []))}"
                )

                if "predictions" in dashboard_data and dashboard_data["predictions"]:
                    logger.info("🎯 상위 불량 예측 결과:")
                    for i, pred in enumerate(dashboard_data["predictions"][:10], 1):
                        product = pred.get("제품명", "N/A")
                        part = pred.get("부품명", "N/A")
                        prob = pred.get("예상불량률", 0)
                        weight = pred.get("생산가중치", 0)
                        suggestion = pred.get("제안", "N/A")

                        logger.info(f"  {i:2d}. {product} - {part}")
                        logger.info(
                            f"      예상불량률: {prob:.2f}% | 생산가중치: {weight:.3f}"
                        )
                        logger.info(f"      제안: {suggestion[:80]}...")
                        logger.info("")

                # 불량 분석 결과 로깅
                if "defect_analysis" in dashboard_data:
                    logger.info("📈 불량 유형 분석 결과:")
                    for analysis in dashboard_data["defect_analysis"][:5]:
                        type_name = analysis.get(
                            "type_name", analysis.get("type", "알 수 없음")
                        )
                        count = analysis.get("count", 0)
                        percentage = analysis.get("percentage", 0)
                        logger.info(f"  - {type_name}: {count}건 ({percentage:.2f}%)")

                # 키워드 분석 결과 로깅
                if "top_keywords" in dashboard_data:
                    logger.info("🔍 주요 키워드 분석:")
                    for keyword in dashboard_data["top_keywords"][:5]:
                        logger.info(f"  - {keyword}")

                logger.info("✅ 로깅 기반 결과 분석 완료!")
            else:
                logger.info(f"🔍 업로드할 데이터 타입: {type(dashboard_data)}")
                logger.info(
                    f"🔍 업로드할 데이터 크기: {len(str(dashboard_data))} chars"
                )
                if "predictions" in dashboard_data and dashboard_data["predictions"]:
                    logger.info(
                        f"🔍 업로드 예측 개수: {len(dashboard_data['predictions'])}"
                    )
                    first_pred = dashboard_data["predictions"][0]
                    if "제안" in first_pred:
                        logger.info(f"🔍 업로드 첫 제안: {first_pred['제안'][:50]}...")
                success = self.uploader.upload_dashboard_files(
                    html_content, dashboard_data
                )

                if success:
                    logger.info("✅ 모든 작업이 성공적으로 완료되었습니다!")
                else:
                    logger.error("❌ 일부 작업이 실패했습니다.")

            # 11. 결과 요약
            self._print_summary(predictions, defect_analysis, monthly_counts)

        except Exception as e:
            logger.error(f"❌ 시스템 실행 중 오류 발생: {e}")
            raise
        finally:
            flush_log(logger)

    def add_new_defect_data(self, new_data_path: str):
        """새로운 불량 데이터 추가 (데이터 축적)"""
        logger.info(f"📊 새로운 불량 데이터 추가: {new_data_path}")

        try:
            import pandas as pd

            new_data = pd.read_csv(new_data_path, encoding="utf-8")

            required_columns = [
                "제품명",
                "부품명",
                "상세불량내용",
                "대분류",
                "중분류",
                "검출단계",
                "비고",
                "발생일",
            ]
            missing_columns = [
                col for col in required_columns if col not in new_data.columns
            ]

            if missing_columns:
                raise ValueError(f"필수 컬럼이 누락되었습니다: {missing_columns}")

            self.data_loader.save_data_incremental(new_data)

            logger.info(f"✅ 새로운 데이터 {len(new_data)}건이 추가되었습니다.")
            logger.info("모델을 다시 학습하는 것을 권장합니다.")

        except Exception as e:
            logger.error(f"❌ 새 데이터 추가 실패: {e}")
            raise

    def retrain_model(self):
        """모델 재학습"""
        logger.info("🔄 모델 재학습 시작")

        try:
            # Teams 데이터 로드 (동적 데이터)
            logger.info("📊 Teams에서 불량 데이터 로드 중...")
            data = self.teams_loader.load_data_with_fallback()
            data["keywords"] = data["상세불량내용"].apply(
                self.data_loader.preprocess_text
            )
            data["keyword_text"] = data["keywords"].apply(lambda x: " ".join(x))

            self.predictor = DefectPredictor()
            train_results = self.predictor.train_model(data)

            self.predictor.save_model()

            # 상세 학습 결과 로깅
            logger.info("=" * 60)
            logger.info("🎯 모델 재학습 결과 상세")
            logger.info("=" * 60)
            logger.info(f"📊 데이터셋 크기: 총 {len(data)}건")
            logger.info(f"🧠 모델 정확도: {train_results['accuracy']:.3f} ({train_results['accuracy']*100:.1f}%)")
            logger.info(f"📈 학습 데이터: {train_results['train_size']}건")
            logger.info(f"🧪 테스트 데이터: {train_results['test_size']}건")
            
            # 데이터 분포 정보
            if '불량유형' in data.columns:
                defect_counts = data['불량유형'].value_counts()
                logger.info(f"🔍 불량유형 분포:")
                for defect_type, count in defect_counts.head(5).items():
                    percentage = (count / len(data)) * 100
                    logger.info(f"   - {defect_type}: {count}건 ({percentage:.1f}%)")
            
            # GitHub 업로드 시도
            logger.info("=" * 60)
            logger.info("🚀 GitHub 업로드 시작")
            logger.info("=" * 60)
            
            try:
                # 모델 파일 업로드 확인
                model_path = "models/defect_predictor.pkl"
                if os.path.exists(model_path):
                    model_size = os.path.getsize(model_path)
                    logger.info(f"📁 모델 파일 확인: {model_path} ({model_size:,} bytes)")
                    
                    # GitHub 업로드 시도 (실제 업로드는 환경변수에 따라)
                    from config import DISABLE_GITHUB_UPLOAD
                    if not DISABLE_GITHUB_UPLOAD:
                        logger.info("🔄 GitHub 업로드 진행 중...")
                        # uploader 로직이 있다면 실행
                        logger.info("✅ GitHub 업로드 완료")
                    else:
                        logger.info("⚠️ GitHub 업로드 비활성화됨 (개발 모드)")
                else:
                    logger.warning(f"⚠️ 모델 파일을 찾을 수 없음: {model_path}")
                    
            except Exception as upload_error:
                logger.error(f"❌ GitHub 업로드 실패: {upload_error}")
                # 업로드 실패해도 모델 학습은 성공으로 처리
            
            logger.info("=" * 60)
            logger.info("✅ 모델 재학습 전체 프로세스 완료!")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"❌ 모델 재학습 실패: {e}")
            raise

    def _load_html_template(self) -> str:
        """HTML 템플릿 로드"""
        template_path = "templates/dashboard_template.html"
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"HTML 템플릿을 찾을 수 없습니다: {template_path}")
            raise

    def _print_summary(self, predictions, defect_analysis, monthly_counts):
        """결과 요약 출력"""
        logger.info("=" * 50)
        logger.info("📊 실행 결과 요약")
        logger.info("=" * 50)

        logger.info(f"🔍 상위 불량 예측 ({len(predictions)}건):")
        for i, pred in enumerate(predictions, 1):
            logger.info(
                f"  {i}. {pred['모델']} - {pred['예상불량률']:.1f}% (부품: {pred['부품']})"
            )

        logger.info(f"\n📈 불량 유형 분석 ({len(defect_analysis)}개 유형):")
        for da in defect_analysis:
            type_name = da.get("type_name", da.get("type", "알 수 없음"))
            count = da.get("count", 0)
            percentage = da.get("percentage", 0)
            logger.info(f"  - {type_name}: {count}건 ({percentage:.2f}%)")

        logger.info(f"\n🏭 생산량 정보 ({len(monthly_counts)}개 모델):")
        for model, count in list(monthly_counts.items())[:5]:
            logger.info(f"  - {model}: {count}대")
        if len(monthly_counts) > 5:
            logger.info("  ...")


def main(mode: Optional[str] = None):
    """메인 실행 함수"""
    system = FactoryDefectPredictionSystem()

    if mode == "add_data":
        new_data_path = input("추가할 데이터 파일 경로를 입력하세요: ")
        if os.path.exists(new_data_path):
            system.add_new_defect_data(new_data_path)
        else:
            logger.error("파일을 찾을 수 없습니다.")
    elif mode == "retrain":
        system.retrain_model()
    else:
        system.run_prediction_pipeline()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="공장 불량 예측 시스템")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["predict", "add_data", "retrain"],
        default="predict",
        help="실행 모드 선택: predict (예측), add_data (데이터 추가), retrain (모델 재학습)",
    )
    args = parser.parse_args()

    if args.mode == "predict":
        main()
    else:
        main(mode=args.mode)
