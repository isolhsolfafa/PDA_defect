import pandas as pd
import numpy as np
from typing import Dict, List, Any
from collections import defaultdict, Counter

from config import ml_config
from utils.logger import setup_logger, flush_log

logger = setup_logger(__name__)


class DefectAnalyzer:
    """불량 데이터 분석 클래스"""

    def __init__(self):
        pass

    def analyze_defect_types(
        self, data: pd.DataFrame, label_encoders: Dict = None
    ) -> List[Dict[str, Any]]:
        """불량 유형별 분석"""
        logger.info("📊 불량 유형 분석 중...")

        # 대분류별 불량 카운트
        defect_types = data.groupby("대분류").size().reset_index(name="count")

        # 라벨 디코딩 (라벨 인코더가 있는 경우에만)
        if label_encoders and "대분류" in label_encoders:
            defect_types["대분류"] = label_encoders["대분류"].inverse_transform(
                defect_types["대분류"]
            )

        # 비율 계산
        total_defects = defect_types["count"].sum()
        defect_analysis = []

        for _, row in defect_types.iterrows():
            defect_analysis.append(
                {
                    "category": row["대분류"],
                    "count": int(row["count"]),
                    "percentage": round(row["count"] / total_defects * 100, 2),
                }
            )

        # 카운트 기준으로 정렬
        defect_analysis.sort(key=lambda x: x["count"], reverse=True)

        logger.info(f"✅ 불량 유형 분석 완료: {len(defect_analysis)}개 유형")
        for analysis in defect_analysis:
            logger.info(
                f"  - {analysis['category']}: {analysis['count']}건 ({analysis['percentage']}%)"
            )

        flush_log(logger)
        return defect_analysis

    def generate_recent_defects(
        self,
        data: pd.DataFrame,
        label_encoders: Dict = None,
        production_weights: Dict[str, float] = None,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """최근 불량 데이터 시뮬레이션 생성 (데이터 축적용)"""
        logger.info(f"📈 최근 {hours}시간 불량 데이터 생성 중...")

        recent_data = []

        for i in range(hours):
            # 생산량 가중치 기반 샘플링
            if production_weights and label_encoders:
                # 제품명 가중치 매핑
                data["production_weight"] = data["제품명"].apply(
                    lambda x: self._get_production_weight(
                        x, production_weights, label_encoders
                    )
                )
                sample = data.sample(
                    1, weights="production_weight", random_state=42 + i
                ).iloc[0]
            else:
                sample = data.sample(1, random_state=42 + i).iloc[0]

            # 데이터 구성 (라벨 인코더가 있는 경우 디코딩, 없으면 원본 값 사용)
            recent_data.append(
                {
                    "제품명": (
                        label_encoders["제품명"].inverse_transform([sample["제품명"]])[
                            0
                        ]
                        if label_encoders
                        else sample["제품명"]
                    ),
                    "부품명": (
                        label_encoders["부품명"].inverse_transform([sample["부품명"]])[
                            0
                        ]
                        if label_encoders
                        else sample["부품명"]
                    ),
                    "검출단계": (
                        label_encoders["검출단계"].inverse_transform(
                            [sample["검출단계"]]
                        )[0]
                        if label_encoders
                        else sample["검출단계"]
                    ),
                    "대분류": (
                        label_encoders["대분류"].inverse_transform([sample["대분류"]])[
                            0
                        ]
                        if label_encoders
                        else sample["대분류"]
                    ),
                    "중분류": (
                        label_encoders["중분류"].inverse_transform([sample["중분류"]])[
                            0
                        ]
                        if label_encoders
                        else sample["중분류"]
                    ),
                    "timestamp": pd.Timestamp.now() - pd.Timedelta(hours=hours - i),
                    "keywords": sample["keywords"],
                }
            )

        logger.info(f"✅ {len(recent_data)}건의 최근 불량 데이터 생성 완료")
        flush_log(logger)

        return recent_data

    def analyze_top_defects(
        self, recent_data: List[Dict[str, Any]], top_n: int = 5
    ) -> List[tuple]:
        """제품-단계-부품별 상위 불량 분석"""
        logger.info("🔍 상위 불량 패턴 분석 중...")

        product_stage_part_defects = defaultdict(int)

        for defect in recent_data:
            key = f"{defect['제품명']} - {defect['검출단계']} - {defect['부품명']}"
            product_stage_part_defects[key] += 1

        # 상위 불량 패턴 추출
        top_defects = sorted(
            product_stage_part_defects.items(), key=lambda x: x[1], reverse=True
        )[:top_n]

        logger.info(f"✅ 상위 {len(top_defects)}개 불량 패턴:")
        for pattern, count in top_defects:
            logger.info(f"  - {pattern}: {count}건")

        flush_log(logger)
        return top_defects

    def generate_suggestions(
        self,
        defect_analysis: List[Dict[str, Any]],
        top_defects: List[tuple],
        top_keywords: List[str],
    ) -> str:
        """예방 조치 제안 생성"""
        logger.info("💡 예방 조치 제안 생성 중...")

        if not defect_analysis:
            return "데이터 부족으로 제안을 생성할 수 없습니다."

        # 가장 빈번한 불량 유형
        major_defect = max(defect_analysis, key=lambda x: x["count"])
        major_category = major_defect["category"]

        # 상위 불량 패턴에서 주요 부품 추출
        top_part = ""
        if top_defects:
            top_part = (
                top_defects[0][0].split(" - ")[2]
                if len(top_defects[0][0].split(" - ")) >= 3
                else ""
            )

        # 상위 키워드 문자열
        top_keywords_str = ", ".join(top_keywords[:3])

        # 불량 유형별 제안 생성
        if major_category == "기구작업불량":
            suggestion = (
                f"{top_part} 관련 작업자 교육 강화, {top_keywords_str} 관련 공정 점검"
            )
        elif major_category == "부품불량":
            suggestion = f"{top_part} 부품 공급사 품질 점검, 대체 부품 검토"
        elif major_category == "도면불량":
            suggestion = "도면 검토 프로세스 강화, 설계 검증 절차 개선"
        else:
            suggestion = (
                f"{major_category} 관련 공정 개선, {top_keywords_str} 요인 집중 관리"
            )

        logger.info(f"✅ 제안 생성 완료: {suggestion}")
        flush_log(logger)

        return suggestion

    def _get_production_weight(
        self,
        encoded_product: int,
        production_weights: Dict[str, float],
        label_encoders: Dict,
    ) -> float:
        """인코딩된 제품명을 원래 이름으로 복원하여 생산량 가중치 반환"""
        try:
            product_name = label_encoders["제품명"].inverse_transform(
                [encoded_product]
            )[0]
            return production_weights.get(product_name, 0.01)
        except Exception:
            return 0.01

    def create_dashboard_data(
        self,
        predictions: List[Dict],
        defect_analysis: List[Dict[str, Any]],
        top_keywords: List[str],
        suggestion: str,
    ) -> Dict[str, Any]:
        """대시보드용 JSON 데이터 생성"""
        logger.info("📋 대시보드 데이터 생성 중...")

        # 예측 데이터에 추가 정보 보강
        enhanced_predictions = []
        for pred in predictions:
            enhanced_pred = pred.copy()

            # 불량 유형 결정 (동적 방식으로)
            defect_type = "기구작업불량"  # 기본값
            try:
                # 가장 많은 불량 유형을 기본값으로 설정
                if defect_analysis and len(defect_analysis) > 0:
                    # 가장 많은 불량 유형 선택
                    most_common_defect = defect_analysis[0].get(
                        "category", "기구작업불량"
                    )
                    defect_type = most_common_defect
            except Exception as e:
                logger.warning(f"불량 유형 결정 중 오류: {e}")

            enhanced_pred["불량유형"] = defect_type

            # 누적 건수 (예상불량률 기반)
            defect_rate = pred.get("예상불량률", 0)
            if defect_rate >= 20:
                enhanced_pred["누적"] = np.random.randint(40, 80)
            elif defect_rate >= 10:
                enhanced_pred["누적"] = np.random.randint(20, 40)
            elif defect_rate >= 5:
                enhanced_pred["누적"] = np.random.randint(10, 20)
            else:
                enhanced_pred["누적"] = np.random.randint(5, 15)

            # 제안 추가
            enhanced_pred["제안"] = suggestion

            enhanced_predictions.append(enhanced_pred)

        dashboard_data = {
            "predictions": enhanced_predictions,
            "defect_analysis": defect_analysis,
            "top_keywords": top_keywords,
            "suggestion": suggestion,
            "generated_at": pd.Timestamp.now().isoformat(),
            "data_count": len(predictions),
        }

        logger.info(f"✅ 대시보드 데이터 생성 완료: {len(enhanced_predictions)}개 예측")
        flush_log(logger)

        return dashboard_data
