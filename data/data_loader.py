import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from mecab import MeCab

# from konlpy.tag import Okt # Java 설치 문제로 다시 주석 처리

from config import data_config, sheets_config, KOREAN_STOP_WORDS
from utils.logger import setup_logger, flush_log

logger = setup_logger(__name__)


class DataLoader:
    """데이터 로드 및 전처리 클래스"""

    def __init__(self):
        self.data_config = data_config
        self.mecab = MeCab()
        # self.nlp = Okt() # Java 설치 문제로 다시 주석 처리
        self.korean_stop_words = set(KOREAN_STOP_WORDS)

        # 제품명 매핑 (CSV 제품명 -> 생산량 데이터 제품명)
        self.product_name_mapping = {
            "DRAGON AB DUAL": "DRAGON DUAL",
            "DRAGON AB": "DRAGON",
            "DRAGON AB SINGLE": "DRAGON",  # 맞음!
            "DRAGON LE DUAL": "DRAGON DUAL",
            # GAIA-P, GAIA-P20, GAIA-I SINGLE, WET 1000은 개별 모델로 유지
            # 필요시 추가 매핑 규칙
        }

    def normalize_product_name(self, name: str) -> str:
        """제품명을 생산량 데이터와 매칭되도록 정규화"""
        return self.product_name_mapping.get(name, name)

    def load_defect_data(self) -> pd.DataFrame:
        """불량 데이터 로드"""
        logger.info("📊 불량 데이터 로드 중...")
        try:
            data = pd.read_csv(self.data_config.csv_file_path, encoding="utf-8")

            # 데이터 검증
            missing_cols = [
                col
                for col in self.data_config.required_columns
                if col not in data.columns
            ]
            if missing_cols:
                raise ValueError(f"필수 컬럼 누락: {missing_cols}")

            # 제품명 정규화
            original_product_count = len(data["제품명"].unique())
            data["제품명"] = data["제품명"].apply(self.normalize_product_name)
            new_product_count = len(data["제품명"].unique())
            if original_product_count != new_product_count:
                logger.info(
                    f"제품명 정규화 적용: {original_product_count} -> {new_product_count}개"
                )

            # 제외할 키워드가 포함된 데이터 필터링
            for keyword in self.data_config.exclude_keywords:
                data = data[~data["비고"].str.contains(keyword, case=False, na=False)]

            # 빈 불량내용 제거
            data = data[data["상세불량내용"].str.strip() != ""]

            # NaN 값 처리 - 주요 컬럼들의 NaN을 "미분류"로 대체
            categorical_columns = ["제품명", "부품명", "검출단계", "대분류", "중분류"]
            for col in categorical_columns:
                if col in data.columns:
                    data[col] = data[col].fillna("미분류")

            # 날짜 컬럼 변환
            data["발생일"] = pd.to_datetime(data["발생일"])

            logger.info(f"✅ 처리된 데이터 크기: {len(data)} 건")
            flush_log(logger)

            return data

        except FileNotFoundError:
            logger.error(
                f"❌ 파일을 찾을 수 없습니다: {self.data_config.csv_file_path}"
            )
            flush_log(logger)
            raise
        except Exception as e:
            logger.error(f"데이터 로드 중 예외 발생: {e}")
            flush_log(logger)
            raise

    def preprocess_text(self, text: str) -> List[str]:
        """한국어 텍스트 전처리 (MeCab 형태소 분석)"""
        try:
            if not isinstance(text, str):
                return []
            nouns = self.mecab.nouns(text)
            return [
                noun
                for noun in nouns
                if noun not in self.korean_stop_words and len(noun) > 1
            ]
        except Exception as e:
            logger.warning(f"텍스트 전처리 실패: {text[:20]}... - {e}")
            return []

    def save_data_incremental(
        self, new_data: pd.DataFrame, save_path: str = None
    ) -> None:
        """새로운 데이터를 기존 데이터에 추가 저장 (데이터 축적용)"""
        if save_path is None:
            save_path = self.data_config.csv_file_path

        try:
            # 기존 데이터 로드
            try:
                existing_data = pd.read_csv(save_path, encoding="utf-8")
                logger.info(f"기존 데이터 수: {len(existing_data)} 건")
            except FileNotFoundError:
                existing_data = pd.DataFrame()
                logger.info("새로운 데이터 파일 생성")

            # 데이터 합치기
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)

            # 중복 제거 (필요한 경우)
            combined_data = combined_data.drop_duplicates()

            # 저장
            combined_data.to_csv(save_path, index=False, encoding="utf-8")
            logger.info(
                f"✅ 데이터 저장 완료: {len(combined_data)} 건 (새로 추가: {len(new_data)} 건)"
            )
            flush_log(logger)

        except Exception as e:
            logger.error(f"❌ 데이터 저장 실패: {e}")
            flush_log(logger)
            raise


class GoogleSheetsLoader:
    """Google Sheets 데이터 로더"""

    def __init__(self):
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Google Sheets 서비스 초기화"""
        try:
            credentials = Credentials.from_service_account_file(
                sheets_config.service_account_file, scopes=sheets_config.scopes
            )
            self.service = build("sheets", "v4", credentials=credentials)
            logger.info("✅ Google Sheets 인증 성공")
            flush_log(logger)
        except Exception as e:
            logger.error(f"❌ Google Sheets 인증 실패: {e}")
            flush_log(logger)
            raise

    def get_sheet_names(self, spreadsheet_id: str) -> List[str]:
        """스프레드시트의 시트 이름 목록 조회"""
        try:
            spreadsheet = (
                self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            )
            sheets = [
                sheet["properties"]["title"] for sheet in spreadsheet.get("sheets", [])
            ]
            logger.info(f"✅ 스프레드시트 시트 이름 목록: {sheets}")
            flush_log(logger)
            return sheets
        except Exception as e:
            logger.error(f"❌ 시트 이름 조회 실패: {e}")
            flush_log(logger)
            return []

    def count_models_from_sheet(
        self, spreadsheet_id: str, sheet_name: str, col_index: int = 3
    ) -> Counter:
        """시트에서 모델 카운트 추출"""
        try:
            # 시트 존재 확인
            sheet_names = self.get_sheet_names(spreadsheet_id)
            if sheet_name not in sheet_names:
                logger.error(
                    f"❌ 시트 이름 '{sheet_name}'이 존재하지 않습니다. 사용 가능한 시트: {sheet_names}"
                )
                flush_log(logger)
                raise ValueError(f"시트 '{sheet_name}'이 존재하지 않습니다.")

            # 데이터 범위 설정 (D열, 3행부터 1000행까지)
            sheet_range = f"{sheet_name}!D3:D1000"
            logger.info(f"✅ 시트 범위: {sheet_range}")
            flush_log(logger)

            # 데이터 조회
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=sheet_range)
                .execute()
            )

            values = result.get("values", [])
            if not values:
                logger.warning(f"⚠️ 시트 '{sheet_name}'에서 데이터가 없습니다.")
                flush_log(logger)
                raise ValueError(f"시트 '{sheet_name}'에 데이터가 없습니다.")

            # 모델명 추출 및 카운트
            models = [row[0].strip() for row in values if row and row[0].strip()]
            model_counts = Counter(models)

            logger.info(f"✅ 모델 카운트 완료: {dict(model_counts)}")
            logger.info(f"데이터 샘플 (최대 5개): {models[:5]}")
            flush_log(logger)

            return model_counts

        except Exception as e:
            logger.error(f"❌ 모델 카운트 실패 (시트: {sheet_name}): {e}")
            flush_log(logger)
            raise

    def get_monthly_production_counts(self) -> Dict[str, int]:
        """월간 생산 모델 카운트 가져오기"""
        try:
            logger.info("📊 월간 생산 모델 카운트 로드 중...")
            flush_log(logger)

            # 기본 시트에서 시도
            try:
                monthly_counts = dict(
                    self.count_models_from_sheet(
                        sheets_config.spreadsheet_id,
                        sheets_config.sheet_name,
                        col_index=3,
                    )
                )
                if monthly_counts:
                    return monthly_counts
            except Exception as e:
                logger.warning(f"기본 시트 '{sheets_config.sheet_name}' 로드 실패: {e}")

            # 대체 시트에서 시도
            logger.warning(
                f"⚠️ 시트 '{sheets_config.sheet_name}'에서 실패. 대체 시트 '{sheets_config.fallback_sheet_name}' 시도."
            )
            flush_log(logger)

            monthly_counts = dict(
                self.count_models_from_sheet(
                    sheets_config.spreadsheet_id,
                    sheets_config.fallback_sheet_name,
                    col_index=3,
                )
            )

            if not monthly_counts:
                logger.error(
                    f"⚠️ 대체 시트 '{sheets_config.fallback_sheet_name}'에서도 모델 카운트가 없습니다."
                )
                flush_log(logger)
                raise ValueError("모델 카운트를 가져올 수 없습니다.")

            return monthly_counts

        except Exception as e:
            logger.error(f"❌ 모델 카운트 로드 실패: {e}")
            flush_log(logger)
            raise
