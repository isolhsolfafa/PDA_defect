import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score
from typing import Dict, List, Tuple, Any
import pickle
import os
from collections import defaultdict

from config import ml_config
from utils.logger import setup_logger, flush_log

logger = setup_logger(__name__)


class DefectPredictor:
    """불량 예측 머신러닝 모델 클래스"""

    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.tfidf_vectorizer = None
        self.feature_names = None
        self.is_trained = False

        # 제품명 매핑 (CSV 제품명 -> 생산량 데이터 제품명)
        self.product_name_mapping = {
            "DRAGON AB DUAL": "DRAGON DUAL",
            "DRAGON AB": "DRAGON",
            # 필요시 추가 매핑 규칙
        }

    def normalize_product_name(self, product_name: str) -> str:
        """제품명을 생산량 데이터와 매칭되도록 정규화"""
        return self.product_name_mapping.get(product_name, product_name)

    def prepare_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """피처 준비 및 타겟 변수 생성"""
        logger.info("🔧 피처 준비 중...")

        # 제품명 정규화
        if "제품명" in data.columns:
            data["제품명"] = data["제품명"].apply(self.normalize_product_name)
            logger.info(f"제품명 정규화 완료: {data['제품명'].unique()}")

        # 라벨 인코딩
        columns_to_encode = ["제품명", "부품명", "검출단계", "대분류", "중분류"]

        for column in columns_to_encode:
            # NaN 값을 "미분류"로 대체
            data[column] = data[column].fillna("미분류")

            if column not in self.label_encoders:
                self.label_encoders[column] = LabelEncoder()
                data[column] = self.label_encoders[column].fit_transform(data[column])
            else:
                # 새로운 라벨이 있을 경우 처리
                try:
                    data[column] = self.label_encoders[column].transform(data[column])
                except ValueError as e:
                    logger.warning(f"새로운 라벨 발견 ({column}): {e}")
                    # 새로운 라벨을 포함하여 다시 학습
                    self.label_encoders[column] = LabelEncoder()
                    data[column] = self.label_encoders[column].fit_transform(
                        data[column]
                    )

        # TF-IDF 벡터화
        if self.tfidf_vectorizer is None:
            logger.info("📈 TF-IDF 벡터화 중...")
            self.tfidf_vectorizer = TfidfVectorizer(
                max_df=ml_config.max_df, min_df=ml_config.min_df
            )
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(data["keyword_text"])
            self.feature_names = self.tfidf_vectorizer.get_feature_names_out()
        else:
            tfidf_matrix = self.tfidf_vectorizer.transform(data["keyword_text"])

        # 숫자형 피처와 TF-IDF 피처 결합
        X_numeric = data[["제품명", "부품명", "검출단계"]].values
        X_tfidf = tfidf_matrix.toarray()
        X = np.hstack((X_numeric, X_tfidf))

        # 타겟 변수 (부품불량 여부)
        try:
            target_label = self.label_encoders["대분류"].transform(["부품불량"])[0]
            y = (data["대분류"] == target_label).astype(int)
        except ValueError:
            # '부품불량' 라벨이 없는 경우 가장 빈번한 라벨을 타겟으로 설정
            most_common_label = data["대분류"].mode()[0]
            y = (data["대분류"] == most_common_label).astype(int)
            logger.warning(
                f"'부품불량' 라벨을 찾을 수 없어 '{most_common_label}'을 타겟으로 설정했습니다."
            )

        logger.info(f"✅ 피처 준비 완료: {X.shape}, 타겟 분포: {np.bincount(y)}")
        flush_log(logger)

        return X, y

    def train_model(self, data: pd.DataFrame) -> Dict[str, Any]:
        """모델 학습"""
        logger.info("🧠 ML 모델 학습 중...")

        # 피처 준비
        X, y = self.prepare_features(data)

        # 학습/테스트 데이터 분할
        # 동적 random_state: 매번 다른 샘플링으로 다양한 인사이트 확보
        current_random_state = ml_config.random_state
        if current_random_state is None:
            import time

            current_random_state = int(time.time()) % 10000
            logger.info(f"🎲 동적 random_state 사용: {current_random_state}")

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=ml_config.test_size,
            random_state=current_random_state,
            stratify=y if len(np.unique(y)) > 1 else None,
        )

        # 모델 학습
        self.model = RandomForestClassifier(
            random_state=current_random_state, class_weight="balanced", n_estimators=100
        )
        self.model.fit(X_train, y_train)

        # 모델 평가
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        logger.info(f"✅ 모델 학습 완료 - 정확도: {accuracy:.3f}")
        logger.info(f"학습 데이터: {len(X_train)}, 테스트 데이터: {len(X_test)}")

        # 피처 중요도 분석
        feature_importance = self.get_feature_importance()

        self.is_trained = True
        flush_log(logger)

        return {
            "accuracy": accuracy,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "feature_importance": feature_importance,
        }

    def predict_defect_probability(
        self,
        data: pd.DataFrame,
        production_weights: Dict[str, float] = None,
        monthly_production_counts: Dict[str, int] = None,
    ) -> List[Dict]:
        """불량 확률 예측 (월간 생산 모델 전체 표시)"""
        if not self.is_trained:
            raise ValueError(
                "모델이 학습되지 않았습니다. train_model()을 먼저 실행하세요."
            )

        logger.info("🔍 불량 확률 예측 중...")

        # 월간 생산 카운트 설정
        if monthly_production_counts:
            self.monthly_production_counts = monthly_production_counts

        # 기존 코드처럼: 학습된 데이터와 동일한 데이터 사용
        # 즉, 이미 라벨 인코딩된 데이터를 그대로 사용
        data_copy = data.copy()

        # 생산량 가중치 계산 (기존 코드 방식)
        if production_weights:
            # 이미 인코딩된 제품명을 원래 이름으로 복원하여 가중치 매핑
            data_copy["production_weight"] = data_copy["제품명"].apply(
                lambda x: self._get_production_weight(x, production_weights)
            )
        else:
            # 기본 가중치
            data_copy["production_weight"] = 1.0

        # 개선된 샘플링: 월간 생산 모델 전체 표시 (SPEED CONTROLLER 제외)

        # SPEED CONTROLLER 제외 필터링
        speed_controller_encoded = None
        try:
            speed_controller_encoded = self.label_encoders["부품명"].transform(
                ["SPEED CONTROLLER"]
            )[0]
        except (ValueError, KeyError):
            pass

        # 월간 생산 모델별 대표 부품 선별 (SPEED CONTROLLER 제외)
        model_representative_samples = []

        # 월간 생산 모델 목록 가져오기
        monthly_production_models = set()
        if (
            hasattr(self, "monthly_production_counts")
            and self.monthly_production_counts
        ):
            monthly_production_models = set(self.monthly_production_counts.keys())

        # 각 월간 생산 모델별로 부품 선별
        for model_name in monthly_production_models:
            try:
                model_encoded = self.label_encoders["제품명"].transform([model_name])[0]
                model_data = data_copy[data_copy["제품명"] == model_encoded]

                # SPEED CONTROLLER 제외
                if speed_controller_encoded is not None:
                    model_data = model_data[
                        model_data["부품명"] != speed_controller_encoded
                    ]

                if len(model_data) == 0:
                    continue

                # 해당 모델의 부품별 카운트 계산
                model_part_counts = (
                    model_data.groupby("부품명")
                    .size()
                    .reset_index(name="model_part_count")
                )
                model_data_with_counts = model_data.merge(
                    model_part_counts, on="부품명", how="left"
                )

                # 모델별 상위 2개 부품 선별 (다양성 확보를 위해)
                top_parts = (
                    model_data_with_counts.groupby("부품명")["model_part_count"]
                    .first()
                    .nlargest(2)
                    .index
                )

                for part_encoded in top_parts:
                    part_data = model_data_with_counts[
                        model_data_with_counts["부품명"] == part_encoded
                    ]
                    if len(part_data) > 0:
                        # 해당 모델-부품 조합에서 대표 샘플 선택
                        representative_sample = part_data.iloc[0:1].copy()
                        representative_sample["diversity_weight"] = part_data[
                            "model_part_count"
                        ].iloc[0]
                        representative_sample["production_count"] = (
                            self.monthly_production_counts.get(model_name, 0)
                        )
                        model_representative_samples.append(representative_sample)

            except (ValueError, KeyError) as e:
                logger.warning(f"⚠️ 모델 '{model_name}' 인코딩 실패: {e}")
                continue

        # 대표 샘플들 결합 및 생산량 기준 정렬
        if model_representative_samples:
            sample_data = pd.concat(model_representative_samples, ignore_index=True)
            # 생산량 기준으로 내림차순 정렬
            sample_data = sample_data.sort_values(
                "production_count", ascending=False
            ).reset_index(drop=True)
        else:
            # 대체 방안: 기존 방식
            sample_size = min(ml_config.sample_size, len(data_copy))
            # 동적 random_state 사용
            sample_random_state = ml_config.random_state
            if sample_random_state is None:
                import time

                sample_random_state = int(time.time()) % 10000

            sample_data = data_copy.sample(
                n=sample_size,
                weights="production_weight",
                random_state=sample_random_state,
            ).reset_index(drop=True)

        # 로그: 샘플링된 모델 분포
        sampled_models = sample_data["제품명"].apply(
            lambda x: self.label_encoders["제품명"].inverse_transform([x])[0]
        )
        sampled_model_counts = sampled_models.value_counts()

        logger.info(f"샘플링된 모델 분포: {sampled_model_counts.to_dict()}")
        logger.info(f"월간 생산 모델 전체 표시: {len(sampled_model_counts)}개 모델")

        # 피처 준비
        X_sample_numeric = sample_data[["제품명", "부품명", "검출단계"]].values
        X_sample_tfidf = self.tfidf_vectorizer.transform(
            sample_data["keyword_text"]
        ).toarray()
        X_sample = np.hstack((X_sample_numeric, X_sample_tfidf))

        # 예측
        probs = self.model.predict_proba(X_sample)[:, 1] * 100

        # 결과 구성
        predictions = []
        for i, (idx, row) in enumerate(sample_data.iterrows()):
            # 부품명 안전하게 변환 (NaN 처리)
            try:
                part_name = self.label_encoders["부품명"].inverse_transform(
                    [row["부품명"]]
                )[0]
                if pd.isna(part_name) or part_name == "nan":
                    part_name = "미분류"
            except (ValueError, IndexError):
                part_name = "미분류"

            predictions.append(
                {
                    "모델": self.label_encoders["제품명"].inverse_transform(
                        [row["제품명"]]
                    )[0],
                    "검출단계": self.label_encoders["검출단계"].inverse_transform(
                        [row["검출단계"]]
                    )[0],
                    "부품": part_name,
                    "예상불량률": round(float(probs[i]), 1),  # 소수점 1자리로 반올림
                    "키워드": ", ".join(row["keywords"]),
                }
            )

        # 불량률 기준으로 정렬
        top_predictions = sorted(
            predictions, key=lambda x: x["예상불량률"], reverse=True
        )[: ml_config.top_predictions_count]

        for pred in top_predictions:
            logger.info(
                f"- {pred['모델']} ({pred['검출단계']}), 부품: {pred['부품']}, 불량 확률: {pred['예상불량률']:.1f}%"
            )

        flush_log(logger)
        return top_predictions

    def _get_production_weight(
        self, encoded_product: int, production_weights: Dict[str, float]
    ) -> float:
        """인코딩된 제품명을 원래 이름으로 복원하여 생산량 가중치 반환"""
        try:
            product_name = self.label_encoders["제품명"].inverse_transform(
                [encoded_product]
            )[0]
            return production_weights.get(product_name, 0.01)  # 기본값
        except Exception:
            return 0.01

    def get_feature_importance(self) -> List[Tuple[str, float]]:
        """피처 중요도 반환"""
        if not self.is_trained:
            return []

        # 숫자형 피처 이름
        numeric_features = ["제품명", "부품명", "검출단계"]

        # 모든 피처 이름
        all_features = numeric_features + list(self.feature_names)

        # 중요도 계산
        importances = self.model.feature_importances_
        feature_importance = list(zip(all_features, importances))

        # 중요도 기준으로 정렬
        feature_importance.sort(key=lambda x: x[1], reverse=True)

        return feature_importance[:20]  # 상위 20개만 반환

    def get_top_keywords(self) -> List[Tuple[str, float]]:
        """TF-IDF 기준 상위 키워드 반환"""
        if self.tfidf_vectorizer is None:
            return []

        # TF-IDF 점수 계산
        tfidf_scores = np.sum(
            self.tfidf_vectorizer.transform(["dummy"]).toarray(), axis=0
        )
        top_keywords = sorted(
            zip(self.feature_names, tfidf_scores), key=lambda x: x[1], reverse=True
        )[: ml_config.top_keywords_count]

        return top_keywords

    def save_model(self, file_path: str = "models/defect_predictor.pkl"):
        """모델 저장"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        model_data = {
            "model": self.model,
            "label_encoders": self.label_encoders,
            "tfidf_vectorizer": self.tfidf_vectorizer,
            "feature_names": self.feature_names,
            "is_trained": self.is_trained,
        }

        with open(file_path, "wb") as f:
            pickle.dump(model_data, f)

        logger.info(f"✅ 모델 저장 완료: {file_path}")
        flush_log(logger)

    def load_model(self, file_path: str = "models/defect_predictor.pkl"):
        """모델 로드"""
        try:
            with open(file_path, "rb") as f:
                model_data = pickle.load(f)

            self.model = model_data["model"]
            self.label_encoders = model_data["label_encoders"]
            self.tfidf_vectorizer = model_data["tfidf_vectorizer"]
            self.feature_names = model_data["feature_names"]
            self.is_trained = model_data["is_trained"]

            logger.info(f"✅ 모델 로드 완료: {file_path}")
            flush_log(logger)

        except FileNotFoundError:
            logger.warning(f"모델 파일을 찾을 수 없습니다: {file_path}")
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            raise


class ProductionWeightCalculator:
    """생산량 기반 가중치 계산기"""

    @staticmethod
    def calculate_weights(
        monthly_production_counts: Dict[str, int],
    ) -> Dict[str, float]:
        """생산량 기준 가중치 계산"""
        logger.info("📈 가중치 계산 중...")

        if not monthly_production_counts:
            logger.warning("생산량 데이터가 없습니다.")
            return {}

        total_production = sum(monthly_production_counts.values())

        # 원시 가중치 계산
        raw_weights = {
            model: count / total_production
            for model, count in monthly_production_counts.items()
        }

        # 최소/최대 가중치 적용
        production_weights = {
            model: min(max(weight, ml_config.min_weight), ml_config.max_weight)
            for model, weight in raw_weights.items()
        }

        # 정규화
        total_weight = sum(production_weights.values())
        production_weights = {
            model: weight / total_weight for model, weight in production_weights.items()
        }

        logger.info(f"가중치 비율: {production_weights}")
        flush_log(logger)

        return production_weights
