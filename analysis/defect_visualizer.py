"""
불량 데이터 시각화 모듈
Teams 엑셀 데이터를 기반으로 HTML 차트 생성
"""

# VS Code "Run Code" 지원을 위한 경로 설정
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.graph_objects as go

# import plotly.express as px  # 사용안함
from plotly.subplots import make_subplots

# import json  # 사용안함
import os

# from datetime import datetime  # 사용안함
from typing import Dict  # List, Tuple 사용안함
import io

# import numpy as np  # 사용안함

from data.teams_loader import TeamsDataLoader
from utils.logger import setup_logger, flush_log

logger = setup_logger(__name__)


class DefectVisualizer:
    """불량 데이터 시각화 클래스"""

    def __init__(self):
        try:
            self.teams_loader = TeamsDataLoader()
            self.use_mock_data = False
        except Exception as e:
            logger.warning(f"⚠️ Teams 연동 실패, Mock 데이터 사용: {e}")
            self.teams_loader = None
            self.use_mock_data = True

        self.analysis_data = None
        self.defect_data = None

    def generate_colors(self, count: int) -> list:
        """동적 색상 생성"""
        base_colors = [
            "#FF6B6B",
            "#4ECDC4",
            "#45B7D1",
            "#96CEB4",
            "#FFEAA7",
            "#DDA0DD",
            "#FF8A80",
            "#81C784",
            "#64B5F6",
            "#FFB74D",
            "#F06292",
            "#9575CD",
            "#4DB6AC",
            "#AED581",
            "#FFD54F",
            "#FF8A65",
            "#A1887F",
            "#90A4AE",
        ]

        if count <= len(base_colors):
            return base_colors[:count]
        else:
            # 색상이 부족하면 HSV 색상 공간에서 균등하게 생성
            import colorsys

            colors = []
            for i in range(count):
                hue = i / count
                rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
                hex_color = "#{:02x}{:02x}{:02x}".format(
                    int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
                )
                colors.append(hex_color)
            return colors

    def load_analysis_data(self) -> pd.DataFrame:
        """불량분석 워크시트 데이터 로드"""
        try:
            logger.info("📊 불량분석 워크시트 데이터 로드 시작...")

            # Teams에서 파일 다운로드
            files = self.teams_loader._get_teams_files()
            excel_file = self.teams_loader._find_excel_file(files)
            file_content = self.teams_loader._download_excel_file(excel_file)

            # 불량분석 워크시트 로드
            excel_buffer = io.BytesIO(file_content)
            df = pd.read_excel(excel_buffer, sheet_name="가압 불량분석")

            self.analysis_data = df
            logger.info(f"✅ 불량분석 데이터 로드 완료: {df.shape}")
            flush_log(logger)

            return df

        except Exception as e:
            logger.error(f"❌ 불량분석 데이터 로드 실패: {e}")
            flush_log(logger)
            raise

    def load_defect_data(self) -> pd.DataFrame:
        """불량내역 워크시트 데이터 로드"""
        try:
            if self.use_mock_data:
                logger.info("📊 Mock 불량내역 데이터 사용...")

                # Mock 불량내역 데이터 생성
                mock_data = {
                    "모델": ["Model-A", "Model-B", "Model-C"] * 20,
                    "부품명": ["HEATING JACKET", "LEAK SENSOR", "TOUCH SCREEN"] * 20,
                    "외주사": ["업체A", "업체B", "업체C"] * 20,
                    "조치": ["재체결", "재작업", "재조립", "Teflon 작업", "파트교체"]
                    * 12,
                    "대분류": ["기구작업불량", "전장작업불량", "부품불량"] * 20,
                    "중분류": ["조립불량", "배선불량", "품질불량"] * 20,
                }
                df = pd.DataFrame(mock_data)
                self.defect_data = df
                logger.info(f"✅ Mock 불량내역 데이터 로드 완료: {df.shape}")
                flush_log(logger)
                return df

            logger.info("📊 불량내역 데이터 로드 시작...")

            df = self.teams_loader.load_defect_data_from_teams()
            self.defect_data = df

            logger.info(f"✅ 불량내역 데이터 로드 완료: {df.shape}")
            flush_log(logger)

            return df

        except Exception as e:
            logger.error(f"❌ 불량내역 데이터 로드 실패: {e}")
            flush_log(logger)
            raise

    def extract_monthly_data(self) -> Dict:
        """월별 불량 현황 데이터 추출 (동적)"""
        try:
            if self.analysis_data is None:
                self.load_analysis_data()

            # 동적으로 월별 데이터 추출
            months = []
            ch_counts = []
            defect_counts = []
            defect_rates = []

            # 헤더 행 찾기 (구분, 1월, 2월, ... 형태)
            header_row = None
            for idx, row in self.analysis_data.iterrows():
                if pd.notna(row.iloc[1]) and "구분" in str(row.iloc[1]):
                    header_row = idx
                    break

            if header_row is not None:
                # 월별 컬럼 찾기 (1월, 2월, ... 형태)
                month_indices = []
                for col_idx in range(2, len(self.analysis_data.columns)):
                    cell_value = self.analysis_data.iloc[header_row, col_idx]
                    if pd.notna(cell_value) and "월" in str(cell_value):
                        months.append(str(cell_value))
                        month_indices.append(col_idx)

                # 각 월별 데이터 추출
                for month_idx in month_indices:
                    # 검사 CH수 찾기
                    ch_count = 0
                    for idx, row in self.analysis_data.iterrows():
                        if pd.notna(row.iloc[1]) and "검사 Ch수" in str(row.iloc[1]):
                            ch_count = (
                                row.iloc[month_idx]
                                if pd.notna(row.iloc[month_idx])
                                else 0
                            )
                            break
                    ch_counts.append(int(ch_count) if ch_count != 0 else 0)

                    # 불량 건수 찾기
                    defect_count = 0
                    for idx, row in self.analysis_data.iterrows():
                        if pd.notna(row.iloc[1]) and "불량 건수" in str(row.iloc[1]):
                            defect_count = (
                                row.iloc[month_idx]
                                if pd.notna(row.iloc[month_idx])
                                else 0
                            )
                            break
                    defect_counts.append(int(defect_count) if defect_count != 0 else 0)

                    # CH당 불량률 찾기
                    defect_rate = 0
                    for idx, row in self.analysis_data.iterrows():
                        if pd.notna(row.iloc[1]) and "CH당 불량률" in str(row.iloc[1]):
                            defect_rate = (
                                row.iloc[month_idx]
                                if pd.notna(row.iloc[month_idx])
                                else 0
                            )
                            break
                    # 소수점 형태를 백분율로 변환 (0.318 -> 31.8)
                    defect_rates.append(
                        float(defect_rate) * 100 if defect_rate != 0 else 0
                    )

            logger.info(f"📊 동적 월별 데이터 추출 완료: {len(months)}개월")

            return {
                "months": months,
                "ch_counts": ch_counts,
                "defect_counts": defect_counts,
                "defect_rates": defect_rates,
            }

        except Exception as e:
            logger.error(f"❌ 월별 데이터 추출 실패: {e}")
            flush_log(logger)
            raise

    def extract_action_type_data(self) -> Dict:
        """불량조치 유형별 데이터 추출 (동적)"""
        try:
            if self.analysis_data is None:
                self.load_analysis_data()

            action_types = []
            action_counts = []

            # "불량조치 유형별" 섹션 찾기 (두 번째 컬럼에서)
            action_section_start = None
            for idx, row in self.analysis_data.iterrows():
                if pd.notna(row.iloc[1]) and "불량조치 유형별" in str(row.iloc[1]):
                    action_section_start = idx
                    break

            if action_section_start is not None:
                # 불량조치 유형별 데이터 추출 (다음 행부터 시작)
                for idx in range(action_section_start + 1, len(self.analysis_data)):
                    row = self.analysis_data.iloc[idx]

                    # 두 번째 컬럼이 비어있거나 다른 섹션이 시작되면 종료
                    if pd.isna(row.iloc[1]) or "기구" in str(row.iloc[1]):
                        break

                    action_type = str(row.iloc[1]).strip()

                    # O열(누적값) 데이터 찾기 - 14번째 컬럼 (O열)
                    count = 0
                    if len(self.analysis_data.columns) > 14:  # O열이 존재하는 경우
                        cell_value = row.iloc[14]  # O열 (0-based index: 14)
                        if (
                            pd.notna(cell_value)
                            and str(cell_value).replace(".", "").isdigit()
                        ):
                            count = int(float(cell_value))

                    # O열에 데이터가 없으면 마지막 컬럼에서 역순으로 찾기
                    if count == 0:
                        for col_idx in range(
                            len(self.analysis_data.columns) - 1, 1, -1
                        ):
                            cell_value = row.iloc[col_idx]
                            if (
                                pd.notna(cell_value)
                                and str(cell_value).replace(".", "").isdigit()
                            ):
                                count = int(float(cell_value))
                                break

                    if action_type and count > 0:
                        action_types.append(action_type)
                        action_counts.append(count)

            # 데이터가 없으면 더 정확한 검색으로 재시도
            if not action_types:
                logger.warning("⚠️ 첫 번째 시도 실패, 더 넓은 범위에서 재검색...")

                # 전체 시트에서 "재체결", "재작업" 등의 키워드가 포함된 행 찾기
                action_keywords = [
                    "재체결",
                    "재작업",
                    "재조립",
                    "Teflon",
                    "파트교체",
                    "교체",
                    "체결",
                    "클램프",
                ]

                for idx, row in self.analysis_data.iterrows():
                    for col_idx in range(len(self.analysis_data.columns)):
                        cell_value = (
                            str(row.iloc[col_idx])
                            if pd.notna(row.iloc[col_idx])
                            else ""
                        )

                        # 조치 관련 키워드가 포함되어 있고, 숫자 데이터가 있는지 확인
                        for keyword in action_keywords:
                            if (
                                keyword in cell_value and len(cell_value.strip()) < 20
                            ):  # 너무 긴 텍스트 제외
                                # O열(14번째 컬럼) 우선 확인
                                count = 0
                                if len(self.analysis_data.columns) > 14:
                                    o_col_value = row.iloc[14]  # O열
                                    if (
                                        pd.notna(o_col_value)
                                        and str(o_col_value).replace(".", "").isdigit()
                                    ):
                                        count = int(float(o_col_value))

                                # O열에 없으면 같은 행에서 숫자 찾기
                                if count == 0:
                                    for count_col in range(
                                        col_idx + 1, len(self.analysis_data.columns)
                                    ):
                                        count_value = row.iloc[count_col]
                                        if (
                                            pd.notna(count_value)
                                            and str(count_value)
                                            .replace(".", "")
                                            .isdigit()
                                        ):
                                            count = int(float(count_value))
                                            break

                                if count > 0 and cell_value.strip() not in action_types:
                                    action_types.append(cell_value.strip())
                                    action_counts.append(count)
                                break

                # 여전히 데이터가 없으면 기본값 사용
                if not action_types:
                    logger.warning("⚠️ 동적 데이터 추출 완전 실패, 기본값 사용")
                    action_types = [
                        "재체결",
                        "재체결(클램프)",
                        "재작업",
                        "재조립",
                        "Teflon 작업",
                        "파트교체",
                    ]
                    action_counts = [86, 11, 35, 13, 23, 124]

            logger.info(
                f"📊 동적 불량조치 유형 데이터 추출 완료: {len(action_types)}개 유형"
            )

            return {"action_types": action_types, "action_counts": action_counts}

        except Exception as e:
            logger.error(f"❌ 조치유형 데이터 추출 실패: {e}")
            flush_log(logger)
            raise

    def extract_supplier_data(self) -> Dict:
        """외주사별 불량 데이터 추출 (동적)"""
        try:
            if self.analysis_data is None:
                self.load_analysis_data()

            suppliers = []
            supplier_counts = []
            supplier_rates = []

            # "기구 외주사별 불량률" 섹션 찾기
            supplier_section_start = None
            for idx, row in self.analysis_data.iterrows():
                if pd.notna(row.iloc[1]) and "기구 외주사별 불량률" in str(row.iloc[1]):
                    supplier_section_start = idx
                    break

            if supplier_section_start is not None:
                # 외주사별 데이터 추출 (다음 행부터 시작)
                idx = supplier_section_start + 1
                while idx < len(self.analysis_data):
                    row = self.analysis_data.iloc[idx]

                    # 두 번째 컬럼이 비어있으면 종료
                    if pd.isna(row.iloc[1]):
                        break

                    supplier_name = str(row.iloc[1]).strip()

                    # 외주사 이름이 유효한지 확인 (BAT, FNI, TMS 등)
                    if (
                        supplier_name
                        and len(supplier_name) <= 5
                        and supplier_name.isalpha()
                    ):
                        # 월별 데이터 합계 계산
                        total_count = 0
                        for col_idx in range(
                            2, min(len(self.analysis_data.columns), 9)
                        ):  # 1월~7월 데이터
                            cell_value = row.iloc[col_idx]
                            if (
                                pd.notna(cell_value)
                                and str(cell_value).replace(".", "").isdigit()
                            ):
                                total_count += int(float(cell_value))

                        # 다음 행에서 비율 정보 추출
                        rate = 0
                        if idx + 1 < len(self.analysis_data):
                            rate_row = self.analysis_data.iloc[idx + 1]
                            # 비율 행에서 평균 계산
                            rate_values = []
                            for col_idx in range(
                                2, min(len(self.analysis_data.columns), 9)
                            ):
                                cell_value = rate_row.iloc[col_idx]
                                if pd.notna(cell_value) and isinstance(
                                    cell_value, (int, float)
                                ):
                                    rate_values.append(
                                        float(cell_value) * 100
                                    )  # 백분율로 변환
                            if rate_values:
                                rate = sum(rate_values) / len(rate_values)

                        if total_count > 0:
                            suppliers.append(supplier_name)
                            supplier_counts.append(total_count)
                            supplier_rates.append(round(rate, 1))

                        # 다음 외주사로 이동 (비율 행 건너뛰기)
                        idx += 2
                    else:
                        idx += 1

            # 데이터가 없으면 기본값 사용
            if not suppliers:
                logger.warning("⚠️ 동적 외주사 데이터 추출 실패, 기본값 사용")
                suppliers = ["BAT", "FNI", "TMS"]
                supplier_counts = [79, 58, 26]
                supplier_rates = [48.2, 35.4, 15.9]

            logger.info(f"📊 동적 외주사 데이터 추출 완료: {len(suppliers)}개 업체")

            return {
                "suppliers": suppliers,
                "supplier_counts": supplier_counts,
                "supplier_rates": supplier_rates,
            }

        except Exception as e:
            logger.error(f"❌ 외주사 데이터 추출 실패: {e}")
            flush_log(logger)
            raise

    def extract_supplier_monthly_data(self) -> Dict:
        """기구 외주사별 월별 불량률 데이터 추출"""
        try:
            if self.analysis_data is None:
                self.load_analysis_data()

            # 월별 컬럼 찾기
            months = []
            header_row = None
            for idx, row in self.analysis_data.iterrows():
                if pd.notna(row.iloc[1]) and "구분" in str(row.iloc[1]):
                    header_row = idx
                    break

            month_indices = []
            if header_row is not None:
                for col_idx in range(2, len(self.analysis_data.columns)):
                    cell_value = self.analysis_data.iloc[header_row, col_idx]
                    if pd.notna(cell_value) and "월" in str(cell_value):
                        months.append(str(cell_value))
                        month_indices.append(col_idx)

            # 기구 외주사별 불량률 섹션 찾기
            supplier_section_start = None
            for idx, row in self.analysis_data.iterrows():
                if pd.notna(row.iloc[1]) and "기구 외주사별 불량률" in str(row.iloc[1]):
                    supplier_section_start = idx
                    break

            suppliers_monthly = {}

            if supplier_section_start is not None:
                idx = supplier_section_start + 1
                while idx < len(self.analysis_data):
                    row = self.analysis_data.iloc[idx]

                    # 두 번째 컬럼이 비어있으면 종료
                    if pd.isna(row.iloc[1]):
                        break

                    supplier_name = str(row.iloc[1]).strip()

                    # 외주사 이름이 유효한지 확인 (BAT, FNI, TMS 등)
                    if (
                        supplier_name
                        and len(supplier_name) <= 5
                        and supplier_name.isalpha()
                    ):
                        # 다음 행에서 월별 비율 데이터 추출
                        if idx + 1 < len(self.analysis_data):
                            rate_row = self.analysis_data.iloc[idx + 1]
                            monthly_rates = []

                            for month_idx in month_indices:
                                cell_value = rate_row.iloc[month_idx]
                                if pd.notna(cell_value) and isinstance(
                                    cell_value, (int, float)
                                ):
                                    monthly_rates.append(
                                        float(cell_value) * 100
                                    )  # 백분율로 변환
                                else:
                                    monthly_rates.append(0)

                            suppliers_monthly[supplier_name] = monthly_rates

                        # 다음 외주사로 이동 (비율 행 건너뛰기)
                        idx += 2
                    else:
                        idx += 1

            logger.info(
                f"📊 외주사별 월별 데이터 추출 완료: {len(suppliers_monthly)}개 업체"
            )

            return {"months": months, "suppliers_monthly": suppliers_monthly}

        except Exception as e:
            logger.error(f"❌ 외주사별 월별 데이터 추출 실패: {e}")
            flush_log(logger)
            raise

    def extract_supplier_quarterly_data(self) -> Dict:
        """기구 외주사별 분기별 불량률 데이터 추출"""
        try:
            # 월별 데이터를 분기별로 그룹화
            monthly_data = self.extract_supplier_monthly_data()

            # 분기별 그룹화 (1-3월: 1분기, 4-6월: 2분기, 7-9월: 3분기, 10-12월: 4분기)
            quarters = []
            suppliers_quarterly = {}

            # 월별 데이터를 분기별로 변환
            months = monthly_data["months"]
            month_to_quarter = {}

            for month in months:
                month_num = int(month.replace("월", ""))
                if month_num in [1, 2, 3]:
                    quarter = "1분기"
                elif month_num in [4, 5, 6]:
                    quarter = "2분기"
                elif month_num in [7, 8, 9]:
                    quarter = "3분기"
                else:
                    quarter = "4분기"

                month_to_quarter[month] = quarter
                if quarter not in quarters:
                    quarters.append(quarter)

            # 각 외주사별로 분기별 데이터 계산
            for supplier, monthly_rates in monthly_data["suppliers_monthly"].items():
                quarterly_rates = []

                for quarter in quarters:
                    # 해당 분기의 월별 데이터 평균 계산
                    quarter_months = [
                        i
                        for i, month in enumerate(months)
                        if month_to_quarter[month] == quarter
                    ]
                    if quarter_months:
                        quarter_avg = sum(
                            monthly_rates[i] for i in quarter_months
                        ) / len(quarter_months)
                        quarterly_rates.append(round(quarter_avg, 1))
                    else:
                        quarterly_rates.append(0)

                suppliers_quarterly[supplier] = quarterly_rates

            logger.info(
                f"📊 외주사별 분기별 데이터 추출 완료: {len(suppliers_quarterly)}개 업체, {len(quarters)}개 분기"
            )

            return {"quarters": quarters, "suppliers_quarterly": suppliers_quarterly}

        except Exception as e:
            logger.error(f"❌ 외주사별 분기별 데이터 추출 실패: {e}")
            flush_log(logger)
            raise

    def create_monthly_trend_chart(self) -> go.Figure:
        """월별 불량 트렌드 차트 생성"""
        try:
            monthly_data = self.extract_monthly_data()

            # 이중 축 차트 생성
            fig = make_subplots(
                rows=1,
                cols=1,
                specs=[[{"secondary_y": True}]],
            )

            # 검사 CH수 (막대 차트)
            fig.add_trace(
                go.Bar(
                    x=monthly_data["months"],
                    y=monthly_data["ch_counts"],
                    name="검사 CH수",
                    marker_color="rgba(54, 162, 235, 0.6)",
                    text=monthly_data["ch_counts"],
                    textposition="auto",
                ),
                secondary_y=False,
            )

            # 불량 건수 (막대 차트)
            fig.add_trace(
                go.Bar(
                    x=monthly_data["months"],
                    y=monthly_data["defect_counts"],
                    name="불량 건수",
                    marker_color="rgba(255, 99, 132, 0.8)",
                    text=monthly_data["defect_counts"],
                    textposition="auto",
                ),
                secondary_y=False,
            )

            # 불량률 (선 차트)
            fig.add_trace(
                go.Scatter(
                    x=monthly_data["months"],
                    y=monthly_data["defect_rates"],
                    mode="lines+markers",
                    name="CH당 불량률 (%)",
                    line=dict(color="rgba(54, 162, 235, 1)", width=3),
                    marker=dict(size=8),
                    text=[f"{rate:.1f}%" for rate in monthly_data["defect_rates"]],
                    textposition="top center",
                ),
                secondary_y=True,
            )

            # 축 제목 설정
            fig.update_xaxes(title_text="월")
            fig.update_yaxes(
                title_text="건수 (검사 CH수 / 불량 건수)", secondary_y=False
            )
            fig.update_yaxes(title_text="CH당 불량률 (%)", secondary_y=True)

            # 레이아웃 설정
            fig.update_layout(
                title={
                    "text": "2025년 가압검사 불량 월별 트렌드",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 20, "family": "Arial, sans-serif"},
                },
                xaxis=dict(tickangle=0, tickfont=dict(size=12)),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                height=500,
                template="plotly_white",
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 월별 트렌드 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_action_type_integrated_chart_OLD_DISABLED(self) -> go.Figure:
        """불량조치 유형별 통합 차트 (불량내역 기반, 드롭다운 메뉴 포함)"""
        try:
            logger.info("📊 가압검사 조치유형별 통합 차트 생성 (불량내역 기반)")

            # 불량내역 데이터 로드
            if self.defect_data is None:
                self.load_defect_data()

            df = self.defect_data.copy()
            df["발생일_pd"] = pd.to_datetime(df["발생일"], errors="coerce")
            df["발생월"] = df["발생일_pd"].dt.to_period("M")
            df["발생분기"] = df["발생일_pd"].dt.to_period("Q")

            # 유효한 데이터만 필터링
            df_valid = df.dropna(subset=["상세조치내용", "발생일_pd"])
            logger.info(f"📊 유효한 불량내역 데이터: {len(df_valid)}건")

            # 1. 전체분포용 데이터 (상세조치내용 카운트)
            action_counts = df_valid["상세조치내용"].value_counts()
            logger.info(f"📊 조치유형별 카운트: {dict(action_counts.head())}")

            # 2. TOP3 조치유형 추출
            top_actions = action_counts.head(3).index.tolist()
            df_top3 = df_valid[df_valid["상세조치내용"].isin(top_actions)]
            logger.info(f"📊 TOP3 조치유형: {top_actions}")

            # 메인 차트 생성
            fig = go.Figure()

            # 색상 정의
            colors = [
                "#FF6B6B",
                "#4ECDC4",
                "#45B7D1",
                "#96CEB4",
                "#FFEAA7",
                "#DDA0DD",
                "#FF8A80",
                "#81C784",
            ]

            # 1. 전체 분포 파이차트 (상세조치내용 카운트)
            fig.add_trace(
                go.Pie(
                    labels=action_counts.index.tolist(),
                    values=action_counts.values.tolist(),
                    hole=0.4,
                    textinfo="label+percent+value",
                    textposition="outside",
                    textfont=dict(size=12),
                    marker_colors=colors[: len(action_counts)],
                    pull=[0.05, 0, 0, 0, 0, 0.1],
                    texttemplate="%{label}<br>%{value}건 (%{percent})",
                    hovertemplate="<b>%{label}</b><br>건수: %{value}<br>비율: %{percent}<extra></extra>",
                    visible=True,  # 기본 표시
                    showlegend=True,
                    name="전체분포",
                )
            )

            # 월별 조치 유형별 집계
            monthly_action = (
                df_filtered.groupby(["발생월", "상세조치내용"])
                .size()
                .unstack(fill_value=0)
            )

            # 월 이름을 한국어로 변환
            month_names = []
            for month in monthly_action.index:
                month_str = str(month)
                if "2025-01" in month_str:
                    month_names.append("1월")
                elif "2025-02" in month_str:
                    month_names.append("2월")
                elif "2025-03" in month_str:
                    month_names.append("3월")
                elif "2025-04" in month_str:
                    month_names.append("4월")
                elif "2025-05" in month_str:
                    month_names.append("5월")
                elif "2025-06" in month_str:
                    month_names.append("6월")
                elif "2025-07" in month_str:
                    month_names.append("7월")
                elif "2025-08" in month_str:
                    month_names.append("8월")
                elif "2025-09" in month_str:
                    month_names.append("9월")
                elif "2025-10" in month_str:
                    month_names.append("10월")
                elif "2025-11" in month_str:
                    month_names.append("11월")
                elif "2025-12" in month_str:
                    month_names.append("12월")
                else:
                    month_names.append(month_str)

            # 3. 분기별 데이터 추가
            df["발생분기"] = df["발생일_pd"].dt.to_period("Q")
            df_filtered_quarterly = df[df["상세조치내용"].isin(top_actions)]
            df_filtered_quarterly = df_filtered_quarterly.dropna(subset=["발생분기"])

            # 분기별 조치 유형별 집계
            quarterly_action = (
                df_filtered_quarterly.groupby(["발생분기", "상세조치내용"])
                .size()
                .unstack(fill_value=0)
            )

            # 분기 이름을 한국어로 변환 (동적으로 처리)
            quarter_names = []
            for quarter in quarterly_action.index:
                quarter_str = str(quarter)
                # Q1, Q2, Q3, Q4를 감지하여 변환
                if "Q1" in quarter_str:
                    quarter_names.append("1분기")
                elif "Q2" in quarter_str:
                    quarter_names.append("2분기")
                elif "Q3" in quarter_str:
                    quarter_names.append("3분기")
                elif "Q4" in quarter_str:
                    quarter_names.append("4분기")
                else:
                    quarter_names.append(quarter_str)

            # 메인 차트 생성
            fig = go.Figure()

            # 색상 정의
            colors = self.generate_colors(len(action_data["action_types"]))
            monthly_colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]

            # 1. 전체 분포 도넛차트 (기본 표시, 전체 공간 활용)
            fig.add_trace(
                go.Pie(
                    labels=action_data["action_types"],
                    values=action_data["action_counts"],
                    hole=0.4,
                    textinfo="label+percent+value",
                    textposition="outside",
                    textfont=dict(size=12),
                    marker_colors=colors,
                    pull=[0.05, 0, 0, 0, 0, 0.1],
                    texttemplate="%{label}<br>%{value}건 (%{percent})",
                    hovertemplate="<b>%{label}</b><br>건수: %{value}<br>비율: %{percent}<extra></extra>",
                    visible=True,
                    showlegend=True,
                )
            )

            # 2. 월별 TOP3 라인차트 (숨김)
            for i, action in enumerate(top_actions):
                if action in monthly_action.columns:
                    # 해당 조치 유형의 부품별 정보 수집
                    action_parts_info = []
                    for j, month in enumerate(monthly_action.index):
                        month_name = month_names[j]
                        month_count = monthly_action.loc[month, action]

                        if month_count > 0:
                            # 해당 월, 해당 조치 유형의 부품들 추출
                            month_action_df = df_filtered[
                                (df_filtered["발생월"] == month)
                                & (df_filtered["상세조치내용"] == action)
                            ]

                            # 부품별 건수 집계
                            part_counts = month_action_df["부품명"].value_counts()

                            # hover text 생성
                            hover_text = f"<b>{month_name}: {action}</b><br>"
                            hover_text += f"총 {month_count}건<br><br>"

                            if len(part_counts) > 0:
                                hover_text += "<b>주요 부품:</b><br>"
                                for k, (part, count) in enumerate(
                                    part_counts.head(5).items(), 1
                                ):
                                    hover_text += f"{k}. {part}: {count}건<br>"

                            action_parts_info.append(hover_text)
                        else:
                            action_parts_info.append(
                                f"<b>{month_names[j]}: {action}</b><br>0건"
                            )

                    fig.add_trace(
                        go.Scatter(
                            x=month_names,
                            y=monthly_action[action],
                            mode="lines+markers",
                            name=action,
                            line=dict(
                                color=monthly_colors[i % len(monthly_colors)], width=3
                            ),
                            marker=dict(
                                size=8, color=monthly_colors[i % len(monthly_colors)]
                            ),
                            text=[
                                f"{count}건" if count > 0 else ""
                                for count in monthly_action[action]
                            ],
                            textposition="top center",
                            textfont=dict(size=10),
                            hovertemplate="%{hovertext}<extra></extra>",
                            hovertext=action_parts_info,
                            visible=False,  # 기본 숨김
                        )
                    )

            # 3. 분기별 TOP3 막대차트 (숨김)
            for i, action in enumerate(top_actions):
                if action in quarterly_action.columns:
                    # 해당 조치 유형의 부품별 정보 수집
                    action_parts_info = []
                    for j, quarter in enumerate(quarterly_action.index):
                        quarter_name = quarter_names[j]
                        quarter_count = quarterly_action.loc[quarter, action]

                        if quarter_count > 0:
                            # 해당 분기, 해당 조치 유형의 부품들 추출
                            quarter_action_df = df_filtered_quarterly[
                                (df_filtered_quarterly["발생분기"] == quarter)
                                & (df_filtered_quarterly["상세조치내용"] == action)
                            ]

                            # 부품별 건수 집계
                            part_counts = quarter_action_df["부품명"].value_counts()

                            # hover text 생성
                            hover_text = f"<b>{quarter_name}: {action}</b><br>"
                            hover_text += f"총 {quarter_count}건<br><br>"

                            if len(part_counts) > 0:
                                hover_text += "<b>주요 부품:</b><br>"
                                for k, (part, count) in enumerate(
                                    part_counts.head(5).items(), 1
                                ):
                                    hover_text += f"{k}. {part}: {count}건<br>"

                            action_parts_info.append(hover_text)
                        else:
                            action_parts_info.append(
                                f"<b>{quarter_names[j]}: {action}</b><br>0건"
                            )

                    fig.add_trace(
                        go.Bar(
                            x=quarter_names,
                            y=quarterly_action[action],
                            name=action,
                            marker_color=monthly_colors[i % len(monthly_colors)],
                            text=quarterly_action[action],
                            textposition="auto",
                            textfont=dict(size=10),
                            hovertemplate="%{hovertext}<extra></extra>",
                            hovertext=action_parts_info,
                            visible=False,  # 기본 숨김
                        )
                    )

            # 드롭다운 메뉴 설정
            pie_traces = 1  # 도넛차트 1개
            monthly_bar_traces = len(top_actions)  # 월별 막대차트 개수
            quarterly_bar_traces = len(top_actions)  # 분기별 막대차트 개수

            # 가시성 설정
            visibility_pie = [True] + [False] * (
                monthly_bar_traces + quarterly_bar_traces
            )
            visibility_monthly = (
                [False] + [True] * monthly_bar_traces + [False] * quarterly_bar_traces
            )
            visibility_quarterly = (
                [False] + [False] * monthly_bar_traces + [True] * quarterly_bar_traces
            )

            # 드롭다운 메뉴 구성
            fig.update_layout(
                updatemenus=[
                    {
                        "buttons": [
                            {
                                "label": "전체 분포",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_pie},
                                    {
                                        "title": {
                                            "text": "불량조치 유형별 분포",
                                            "x": 0.5,
                                            "xanchor": "center",
                                        },
                                        "xaxis": {"visible": False},
                                        "yaxis": {"visible": False},
                                    },
                                ],
                            },
                            {
                                "label": "분기별 비교 (TOP3)",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_quarterly},
                                    {
                                        "title": {
                                            "text": "조치 유형별 TOP3 분기별 비교",
                                            "x": 0.5,
                                            "xanchor": "center",
                                        },
                                        "xaxis": {"visible": True, "title": "분기"},
                                        "yaxis": {
                                            "visible": True,
                                            "title": "불량 건수",
                                        },
                                    },
                                ],
                            },
                            {
                                "label": "월별 추이 (TOP3)",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_monthly},
                                    {
                                        "title": {
                                            "text": "조치 유형별 TOP3 월별 추이",
                                            "x": 0.5,
                                            "xanchor": "center",
                                        },
                                        "xaxis": {"visible": True, "title": "월"},
                                        "yaxis": {
                                            "visible": True,
                                            "title": "불량 건수",
                                        },
                                    },
                                ],
                            },
                        ],
                        "direction": "down",
                        "showactive": True,
                        "x": 0.1,
                        "xanchor": "left",
                        "y": 1.15,
                        "yanchor": "top",
                    }
                ]
            )

            # 기본 레이아웃 설정
            fig.update_layout(
                title={
                    "text": "불량조치 유형별 분포",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 18, "family": "Arial, sans-serif"},
                },
                height=500,
                margin=dict(l=50, r=50, t=120, b=50),
                template="plotly_white",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                legend=dict(
                    orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05
                ),
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 조치유형 통합 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_action_type_integrated_chart(self) -> go.Figure:
        """불량조치 유형별 통합 차트 (불량내역 기반, 드롭다운 메뉴 포함)"""
        try:
            logger.info("📊 가압검사 조치유형별 통합 차트 생성 (불량내역 기반)")

            # 불량내역 데이터 로드
            if self.defect_data is None:
                self.load_defect_data()

            df = self.defect_data.copy()
            df["발생일_pd"] = pd.to_datetime(df["발생일"], errors="coerce")
            df["발생월"] = df["발생일_pd"].dt.to_period("M")
            df["발생분기"] = df["발생일_pd"].dt.to_period("Q")

            # 유효한 데이터만 필터링
            df_valid = df.dropna(subset=["상세조치내용", "발생일_pd"])
            logger.info(f"📊 유효한 불량내역 데이터: {len(df_valid)}건")

            # 전체분포용 데이터 (상세조치내용 카운트)
            action_counts = df_valid["상세조치내용"].value_counts()
            logger.info(f"📊 조치유형별 카운트: {dict(action_counts.head())}")

            # TOP3 조치유형 추출
            top_actions = action_counts.head(3).index.tolist()
            df_top3 = df_valid[df_valid["상세조치내용"].isin(top_actions)]
            logger.info(f"📊 TOP3 조치유형: {top_actions}")

            # 메인 차트 생성
            fig = go.Figure()

            # 색상 정의
            colors = [
                "#FF6B6B",
                "#4ECDC4",
                "#45B7D1",
                "#96CEB4",
                "#FFEAA7",
                "#DDA0DD",
                "#FF8A80",
                "#81C784",
            ]

            # 1. 전체 분포 파이차트 (기본 표시)
            fig.add_trace(
                go.Pie(
                    labels=action_counts.index.tolist(),
                    values=action_counts.values.tolist(),
                    hole=0.4,
                    textinfo="label+percent+value",
                    textposition="outside",
                    textfont=dict(size=12),
                    marker_colors=colors[: len(action_counts)],
                    pull=[0.05, 0, 0, 0, 0, 0.1],
                    texttemplate="%{label}<br>%{value}건 (%{percent})",
                    hovertemplate="<b>%{label}</b><br>건수: %{value}<br>비율: %{percent}<extra></extra>",
                    visible=True,
                    showlegend=True,
                    name="전체분포",
                )
            )

            # 2. 분기별 비교 (TOP3) - 막대 차트
            quarterly_data = (
                df_top3.groupby(["발생분기", "상세조치내용"])
                .size()
                .unstack(fill_value=0)
            )

            # 분기 이름을 한국어로 변환
            quarter_names = []
            for quarter in quarterly_data.index:
                quarter_str = str(quarter)
                try:
                    year = quarter_str[:4]
                    q_num = quarter_str[-1]
                    quarter_names.append(f"{year}년 {q_num}분기")
                except:
                    quarter_names.append(quarter_str)

            # 분기별 비교용 막대 차트 추가
            for i, action in enumerate(top_actions):
                if action in quarterly_data.columns:
                    # 각 분기+조치유형 조합의 주요 부품명 추출 (hover용)
                    hover_texts = []
                    for quarter_period in quarterly_data.index:
                        quarter_data_filtered = df_top3[
                            (df_top3["발생분기"] == quarter_period)
                            & (df_top3["상세조치내용"] == action)
                        ]
                        top_parts = (
                            quarter_data_filtered["부품명"]
                            .value_counts()
                            .head(5)
                            .index.tolist()
                        )
                        hover_text = (
                            f"주요부품: {', '.join(top_parts[:3])}"
                            if top_parts
                            else "데이터 없음"
                        )
                        hover_texts.append(hover_text)

                    fig.add_trace(
                        go.Bar(
                            x=quarter_names,
                            y=quarterly_data[action].values,
                            name=action,
                            marker_color=colors[i % len(colors)],
                            hovertemplate=f"<b>{action}</b><br>"
                            + "분기: %{x}<br>"
                            + "건수: %{y}<br>"
                            + "%{customdata}<extra></extra>",
                            customdata=hover_texts,
                            visible=False,  # 기본 숨김
                        )
                    )

            # 3. 월별 추이 (TOP3) - 라인 차트
            monthly_data = (
                df_top3.groupby(["발생월", "상세조치내용"]).size().unstack(fill_value=0)
            )

            # 월 이름을 한국어로 변환
            month_names = []
            for month in monthly_data.index:
                month_str = str(month)
                try:
                    month_num = int(month_str.split("-")[1])
                    month_names.append(f"{month_num}월")
                except:
                    month_names.append(month_str)

            # 월별 추이용 라인 차트 추가
            for i, action in enumerate(top_actions):
                if action in monthly_data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=month_names,
                            y=monthly_data[action].values,
                            mode="lines+markers",
                            name=action,
                            line=dict(color=colors[i % len(colors)], width=3),
                            marker=dict(size=8),
                            hovertemplate=f"<b>{action}</b><br>"
                            + "월: %{x}<br>"
                            + "건수: %{y}<extra></extra>",
                            visible=False,  # 기본 숨김
                        )
                    )

            # 드롭다운 메뉴 구성
            dropdown_buttons = []

            # 전체 분포 버튼
            pie_visibility = [True] + [False] * (len(fig.data) - 1)
            dropdown_buttons.append(
                dict(
                    label="전체 분포",
                    method="update",
                    args=[
                        {"visible": pie_visibility},
                        {
                            "title": "가압검사 조치유형별 전체 분포",
                            "xaxis": {
                                "visible": False,
                                "showgrid": False,
                                "zeroline": False,
                            },
                            "yaxis": {
                                "visible": False,
                                "showgrid": False,
                                "zeroline": False,
                            },
                        },
                    ],
                )
            )

            # 분기별 비교 버튼
            quarterly_visibility = [False] + [
                True if i < len(top_actions) else False
                for i in range(len(fig.data) - 1)
            ]
            dropdown_buttons.append(
                dict(
                    label="분기별 비교 (TOP3)",
                    method="update",
                    args=[
                        {"visible": quarterly_visibility},
                        {
                            "title": "가압검사 조치유형별 분기별 비교 (TOP3)",
                            "xaxis": {"title": "분기", "visible": True},
                            "yaxis": {"title": "건수", "visible": True},
                        },
                    ],
                )
            )

            # 월별 추이 버튼
            monthly_visibility = [False] * (1 + len(top_actions)) + [True] * len(
                top_actions
            )
            dropdown_buttons.append(
                dict(
                    label="월별 추이 (TOP3)",
                    method="update",
                    args=[
                        {"visible": monthly_visibility},
                        {
                            "title": "가압검사 조치유형별 월별 추이 (TOP3)",
                            "xaxis": {"title": "월", "visible": True},
                            "yaxis": {"title": "건수", "visible": True},
                        },
                    ],
                )
            )

            # 레이아웃 설정
            fig.update_layout(
                updatemenus=[
                    {
                        "buttons": dropdown_buttons,
                        "direction": "down",
                        "showactive": True,
                        "x": 0.1,
                        "xanchor": "left",
                        "y": 1.15,
                        "yanchor": "top",
                    }
                ],
                title={
                    "text": "가압검사 조치유형별 전체 분포",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 18, "family": "Arial, sans-serif"},
                },
                height=500,
                margin=dict(l=50, r=50, t=120, b=50),
                template="plotly_white",
                xaxis=dict(visible=False, showgrid=False, zeroline=False),
                yaxis=dict(visible=False, showgrid=False, zeroline=False),
                legend=dict(
                    orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05
                ),
            )

            logger.info("✅ 가압검사 조치유형별 통합 차트 생성 완료 (불량내역 기반)")
            return fig

        except Exception as e:
            logger.error(f"❌ 가압검사 조치유형별 통합 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_supplier_chart(self) -> go.Figure:
        """외주사별 불량 차트 생성"""
        try:
            supplier_data = self.extract_supplier_data()

            # 막대 차트 생성
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=supplier_data["suppliers"],
                        y=supplier_data["supplier_counts"],
                        text=[
                            f"{count}건<br>({rate:.1f}%)"
                            for count, rate in zip(
                                supplier_data["supplier_counts"],
                                supplier_data["supplier_rates"],
                            )
                        ],
                        textposition="auto",
                        textfont=dict(size=14, color="white"),
                        marker_color=self.generate_colors(
                            len(supplier_data["suppliers"])
                        ),
                        marker_line=dict(width=1, color="rgba(0,0,0,0.3)"),
                    )
                ]
            )

            fig.update_layout(
                title={
                    "text": "기구 외주사별 불량 현황",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 18, "family": "Arial, sans-serif"},
                },
                xaxis_title="외주사",
                yaxis_title="불량 건수",
                xaxis=dict(tickfont=dict(size=12), title_font=dict(size=14)),
                yaxis=dict(tickfont=dict(size=12), title_font=dict(size=14)),
                height=450,
                margin=dict(l=50, r=50, t=80, b=50),
                template="plotly_white",
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 외주사 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_supplier_monthly_chart(self) -> go.Figure:
        """기구 외주사별 월별 불량률 차트 생성"""
        try:
            monthly_data = self.extract_supplier_monthly_data()

            # 막대 차트 생성
            fig = go.Figure()

            # 외주사별 색상 정의
            colors = [
                "#4CAF50",
                "#2196F3",
                "#FF9800",
            ]  # BAT: 초록, FNI: 파랑, TMS: 주황

            # 각 외주사별로 막대 추가
            for i, (supplier, rates) in enumerate(
                monthly_data["suppliers_monthly"].items()
            ):
                fig.add_trace(
                    go.Bar(
                        x=monthly_data["months"],
                        y=rates,
                        name=supplier,
                        marker_color=colors[i % len(colors)],
                        text=[f"{rate:.1f}%" if rate > 0 else "" for rate in rates],
                        textposition="auto",
                        textfont=dict(size=10),
                        marker_line=dict(width=1, color="rgba(0,0,0,0.3)"),
                    )
                )

            fig.update_layout(
                title={
                    "text": "기구 외주사별 월별 불량률",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 18, "family": "Arial, sans-serif"},
                },
                xaxis_title="월",
                yaxis_title="불량률 (%)",
                xaxis=dict(tickfont=dict(size=12), title_font=dict(size=14)),
                yaxis=dict(
                    tickfont=dict(size=12),
                    title_font=dict(size=14),
                    range=[
                        0,
                        max(
                            [
                                max(rates)
                                for rates in monthly_data["suppliers_monthly"].values()
                            ]
                        )
                        * 1.1,
                    ],
                ),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                height=450,
                margin=dict(l=50, r=50, t=80, b=50),
                template="plotly_white",
                barmode="group",
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 외주사별 월별 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_supplier_quarterly_chart(self) -> go.Figure:
        """기구 외주사별 분기별 불량률 차트 생성"""
        try:
            quarterly_data = self.extract_supplier_quarterly_data()

            if not quarterly_data["suppliers_quarterly"]:
                raise ValueError("외주사별 분기별 데이터가 없습니다")

            fig = go.Figure()

            # 외주사별 색상 정의
            colors = [
                "#4CAF50",
                "#2196F3",
                "#FF9800",
            ]  # BAT: 초록, FNI: 파랑, TMS: 주황

            # 각 외주사별로 막대 추가
            for i, (supplier, rates) in enumerate(
                quarterly_data["suppliers_quarterly"].items()
            ):
                fig.add_trace(
                    go.Bar(
                        x=quarterly_data["quarters"],
                        y=rates,
                        name=supplier,
                        marker_color=colors[i % len(colors)],
                        text=[f"{rate}%" if rate > 0 else "" for rate in rates],
                        textposition="outside",
                        textfont=dict(size=10),
                        marker_line=dict(width=1, color="rgba(0,0,0,0.3)"),
                    )
                )

            # 레이아웃 설정
            fig.update_layout(
                title={
                    "text": "기구 외주사별 분기별 불량률",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 18, "family": "Arial, sans-serif"},
                },
                xaxis_title="분기",
                yaxis_title="불량률 (%)",
                xaxis=dict(tickfont=dict(size=12), title_font=dict(size=14)),
                yaxis=dict(
                    tickfont=dict(size=12),
                    title_font=dict(size=14),
                    range=[
                        0,
                        max(
                            [
                                max(rates)
                                for rates in quarterly_data[
                                    "suppliers_quarterly"
                                ].values()
                            ]
                        )
                        * 1.1,
                    ],
                ),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                height=450,
                margin=dict(l=50, r=50, t=80, b=50),
                template="plotly_white",
                barmode="group",
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 외주사별 분기별 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_supplier_integrated_chart(self) -> go.Figure:
        """기구 외주사별 통합 차트 (드롭다운 메뉴 포함)"""
        try:
            # 1. 전체 현황 차트
            supplier_data = self.extract_supplier_data()

            # 2. 분기별 차트 데이터
            quarterly_data = self.extract_supplier_quarterly_data()

            # 3. 월별 차트 데이터
            monthly_data = self.extract_supplier_monthly_data()

            # 메인 차트 생성 (기본: 전체 현황)
            fig = go.Figure()

            # 색상 정의
            colors = [
                "#4CAF50",
                "#2196F3",
                "#FF9800",
            ]  # BAT: 초록, FNI: 파랑, TMS: 주황

            # 1. 전체 현황 차트 (기본 표시)
            for i, (supplier, count, rate) in enumerate(
                zip(
                    supplier_data["suppliers"],
                    supplier_data["supplier_counts"],
                    supplier_data["supplier_rates"],
                )
            ):
                fig.add_trace(
                    go.Bar(
                        x=[supplier],
                        y=[count],
                        name=supplier,
                        marker_color=colors[i % len(colors)],
                        text=[f"{count}건<br>({rate}%)"],
                        textposition="outside",
                        textfont=dict(size=10),
                        visible=True,  # 기본 표시
                    )
                )

            # 2. 분기별 차트 (숨김)
            for i, (supplier, rates) in enumerate(
                quarterly_data["suppliers_quarterly"].items()
            ):
                for j, (quarter, rate) in enumerate(
                    zip(quarterly_data["quarters"], rates)
                ):
                    fig.add_trace(
                        go.Bar(
                            x=[quarter],
                            y=[rate],
                            name=supplier,
                            marker_color=colors[i % len(colors)],
                            text=[f"{rate}%" if rate > 0 else ""],
                            textposition="outside",
                            textfont=dict(size=10),
                            visible=False,  # 기본 숨김
                            showlegend=False if j > 0 else True,  # 첫 번째만 범례 표시
                        )
                    )

            # 3. 월별 차트 (선 그래프로 변경)
            for i, (supplier, rates) in enumerate(
                monthly_data["suppliers_monthly"].items()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=monthly_data["months"],
                        y=rates,
                        mode="lines+markers",
                        name=supplier,
                        line=dict(color=colors[i % len(colors)], width=3),
                        marker=dict(size=8, color=colors[i % len(colors)]),
                        text=[f"{rate:.1f}%" if rate > 0 else "" for rate in rates],
                        textposition="top center",
                        textfont=dict(size=10),
                        visible=False,  # 기본 숨김
                        showlegend=True,
                    )
                )

            # 드롭다운 메뉴 설정
            total_suppliers = len(supplier_data["suppliers"])
            quarterly_traces = len(quarterly_data["suppliers_quarterly"]) * len(
                quarterly_data["quarters"]
            )
            monthly_traces = len(
                monthly_data["suppliers_monthly"]
            )  # 선 그래프로 변경되어 외주사별 1개씩

            # 가시성 설정
            visibility_overall = [True] * total_suppliers + [False] * (
                quarterly_traces + monthly_traces
            )
            visibility_quarterly = (
                [False] * total_suppliers
                + [True] * quarterly_traces
                + [False] * monthly_traces
            )
            visibility_monthly = (
                [False] * total_suppliers
                + [False] * quarterly_traces
                + [True] * monthly_traces
            )

            # 드롭다운 메뉴 구성
            fig.update_layout(
                updatemenus=[
                    {
                        "buttons": [
                            {
                                "label": "전체 현황 (누적)",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_overall},
                                    {
                                        "title": {
                                            "text": "기구 외주사별 불량 현황 (누적)",
                                            "x": 0.5,
                                            "xanchor": "center",
                                        },
                                        "xaxis": {"title": "외주사"},
                                        "yaxis": {"title": "불량 건수"},
                                    },
                                ],
                            },
                            {
                                "label": "분기별 비교",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_quarterly},
                                    {
                                        "title": {
                                            "text": "기구 외주사별 분기별 불량률",
                                            "x": 0.5,
                                            "xanchor": "center",
                                        },
                                        "xaxis": {"title": "분기"},
                                        "yaxis": {"title": "불량률 (%)"},
                                    },
                                ],
                            },
                            {
                                "label": "월별 추이",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_monthly},
                                    {
                                        "title": {
                                            "text": "기구 외주사별 월별 불량률",
                                            "x": 0.5,
                                            "xanchor": "center",
                                        },
                                        "xaxis": {"title": "월"},
                                        "yaxis": {"title": "불량률 (%)"},
                                    },
                                ],
                            },
                        ],
                        "direction": "down",
                        "showactive": True,
                        "x": 0.1,
                        "xanchor": "left",
                        "y": 1.15,
                        "yanchor": "top",
                    }
                ]
            )

            # 기본 레이아웃 설정
            fig.update_layout(
                title={
                    "text": "기구 외주사별 불량 현황 (누적)",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 18, "family": "Arial, sans-serif"},
                },
                xaxis_title="외주사",
                yaxis_title="불량 건수",
                xaxis=dict(tickfont=dict(size=12), title_font=dict(size=14)),
                yaxis=dict(tickfont=dict(size=12), title_font=dict(size=14)),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                height=500,
                margin=dict(l=50, r=50, t=120, b=50),
                template="plotly_white",
                barmode="group",
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 외주사별 통합 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_defect_category_chart(self) -> go.Figure:
        """불량 카테고리별 차트 생성 (불량내역 데이터 기반)"""
        try:
            if self.defect_data is None:
                self.load_defect_data()

            # 대분류별 불량 건수 집계
            category_counts = self.defect_data["대분류"].value_counts()

            # 상위 10개 카테고리만 표시
            top_categories = category_counts.head(10)

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=top_categories.index,
                        y=top_categories.values,
                        text=top_categories.values,
                        textposition="auto",
                        marker_color="rgba(255, 99, 132, 0.8)",
                    )
                ]
            )

            fig.update_layout(
                title={
                    "text": "불량 대분류별 현황 (상위 10개)",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 18, "family": "Arial, sans-serif"},
                },
                xaxis_title="불량 대분류",
                yaxis_title="불량 건수",
                xaxis=dict(tickangle=45),
                height=400,
                template="plotly_white",
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 불량 카테고리 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_action_type_monthly_chart(self) -> go.Figure:
        """조치 유형별 TOP3 월별 시각화"""
        try:
            if self.defect_data is None:
                self.load_defect_data()

            # 데이터 전처리
            df = self.defect_data.copy()
            df["발생일_pd"] = pd.to_datetime(df["발생일"], errors="coerce")
            df["발생월"] = df["발생일_pd"].dt.to_period("M")

            # 조치 유형별 TOP3 추출
            top_actions = df["상세조치내용"].value_counts().head(3).index.tolist()

            # 월별 데이터 필터링
            df_filtered = df[df["상세조치내용"].isin(top_actions)]
            df_filtered = df_filtered.dropna(subset=["발생월"])

            # 월별 조치 유형별 집계
            monthly_action = (
                df_filtered.groupby(["발생월", "상세조치내용"])
                .size()
                .unstack(fill_value=0)
            )

            # 월 이름을 한국어로 변환
            month_names = []
            for month in monthly_action.index:
                month_str = str(month)
                if "2025-01" in month_str:
                    month_names.append("1월")
                elif "2025-02" in month_str:
                    month_names.append("2월")
                elif "2025-03" in month_str:
                    month_names.append("3월")
                elif "2025-04" in month_str:
                    month_names.append("4월")
                elif "2025-05" in month_str:
                    month_names.append("5월")
                elif "2025-06" in month_str:
                    month_names.append("6월")
                elif "2025-07" in month_str:
                    month_names.append("7월")
                elif "2025-08" in month_str:
                    month_names.append("8월")
                elif "2025-09" in month_str:
                    month_names.append("9월")
                elif "2025-10" in month_str:
                    month_names.append("10월")
                elif "2025-11" in month_str:
                    month_names.append("11월")
                elif "2025-12" in month_str:
                    month_names.append("12월")
                else:
                    month_names.append(month_str)

            # subplot을 사용하여 왼쪽에 배치
            from plotly.subplots import make_subplots

            fig = make_subplots(
                rows=1,
                cols=2,
                column_widths=[0.7, 0.3],  # 첫 번째 컬럼을 더 크게
                specs=[[{"type": "xy"}, {"type": "xy"}]],
                subplot_titles=[
                    "조치 유형별 TOP3 월별 현황",
                    "",
                ],  # 첫 번째 컬럼에만 제목
                horizontal_spacing=0.05,
            )

            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]

            # 첫 번째 컬럼에 막대 차트 추가 (왼쪽 정렬)
            for i, action in enumerate(top_actions):
                if action in monthly_action.columns:
                    # 해당 조치 유형의 부품별 정보 수집
                    action_parts_info = []
                    for j, month in enumerate(monthly_action.index):
                        month_name = month_names[j]
                        month_count = monthly_action.loc[month, action]

                        if month_count > 0:
                            # 해당 월, 해당 조치 유형의 부품들 추출
                            month_action_df = df_filtered[
                                (df_filtered["발생월"] == month)
                                & (df_filtered["상세조치내용"] == action)
                            ]

                            # 부품별 건수 집계
                            part_counts = month_action_df["부품명"].value_counts()

                            # hover text 생성
                            hover_text = f"<b>{month_name}: {action}</b><br>"
                            hover_text += f"총 {month_count}건<br><br>"

                            if len(part_counts) > 0:
                                hover_text += "<b>주요 부품:</b><br>"
                                for k, (part, count) in enumerate(
                                    part_counts.head(5).items(), 1
                                ):
                                    hover_text += f"{k}. {part}: {count}건<br>"

                            action_parts_info.append(hover_text)
                        else:
                            action_parts_info.append(
                                f"<b>{month_names[j]}: {action}</b><br>0건"
                            )

                    fig.add_trace(
                        go.Bar(
                            x=month_names,
                            y=monthly_action[action],
                            name=action,
                            marker_color=colors[i % len(colors)],
                            text=monthly_action[action],
                            textposition="auto",
                            textfont=dict(size=10),
                            hovertemplate="%{hovertext}<extra></extra>",
                            hovertext=action_parts_info,
                            showlegend=False,
                        ),
                        row=1,
                        col=1,
                    )

            # 두 번째 컬럼에는 범례 정보를 텍스트로 표시
            legend_text = []
            total_counts = df["상세조치내용"].value_counts()
            for i, action in enumerate(top_actions):
                count = total_counts[action] if action in total_counts else 0
                legend_text.append(
                    f"<span style='color: {colors[i % len(colors)]}; font-size: 16px;'>●</span> {action}: {count}건"
                )

            # 빈 scatter plot으로 범례 영역 생성
            fig.add_trace(
                go.Scatter(
                    x=[0],
                    y=[0.5],
                    mode="text",
                    text="<br>".join(legend_text),
                    textfont=dict(size=14, family="Arial"),
                    textposition="middle left",
                    showlegend=False,
                ),
                row=1,
                col=2,
            )

            # 첫 번째 subplot 축 설정
            fig.update_xaxes(
                title_text="월",
                tickfont=dict(size=10),
                title_font=dict(size=12),
                row=1,
                col=1,
            )
            fig.update_yaxes(
                title_text="불량 건수",
                tickfont=dict(size=10),
                title_font=dict(size=12),
                row=1,
                col=1,
            )

            # 두 번째 subplot의 축 숨기기
            fig.update_xaxes(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                visible=False,
                row=1,
                col=2,
            )
            fig.update_yaxes(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                visible=False,
                row=1,
                col=2,
            )

            fig.update_layout(
                height=450,
                margin=dict(l=10, r=10, t=80, b=50),
                template="plotly_white",
                barmode="group",
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 조치 유형별 월별 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_part_monthly_chart(self) -> go.Figure:
        """드롭다운 형태 부품 분석 차트"""
        try:
            if self.defect_data is None:
                self.load_defect_data()

            # 데이터 전처리 - He미보증 제외
            df = self.defect_data.copy()
            df["발생일_pd"] = pd.to_datetime(df["발생일"], errors="coerce")
            df["발생월"] = df["발생일_pd"].dt.to_period("M")
            df["발생분기"] = df["발생일_pd"].dt.to_period("Q")

            # He미보증 데이터 제외
            df_filtered_he = df[
                ~df["비고"].str.contains("He미보증", case=False, na=False)
            ]
            df_filtered_he = df_filtered_he.dropna(subset=["발생분기"])

            # 분기별 TOP5 데이터 추출
            quarters = sorted(df_filtered_he["발생분기"].unique())
            quarterly_top5_data = {}

            for quarter in quarters:
                quarter_df = df_filtered_he[df_filtered_he["발생분기"] == quarter]
                quarter_top5 = quarter_df["부품명"].value_counts().head(5)
                quarterly_top5_data[quarter] = quarter_top5

            # 전체 기간 TOP3 부품의 월별 추이
            overall_top3_parts = (
                df_filtered_he["부품명"].value_counts().head(3).index.tolist()
            )

            # 월별 데이터 추출
            months = sorted(df_filtered_he["발생월"].unique())
            monthly_top3_data = {}

            for month in months:
                month_df = df_filtered_he[df_filtered_he["발생월"] == month]
                month_part_counts = month_df["부품명"].value_counts()
                monthly_top3_data[month] = month_part_counts

            # 분기 이름을 한국어로 동적 변환
            quarter_names = []
            for quarter in quarters:
                quarter_str = str(quarter)
                # 년도와 분기를 동적으로 추출
                if "Q1" in quarter_str:
                    quarter_names.append("1분기")
                elif "Q2" in quarter_str:
                    quarter_names.append("2분기")
                elif "Q3" in quarter_str:
                    quarter_names.append("3분기")
                elif "Q4" in quarter_str:
                    quarter_names.append("4분기")
                else:
                    quarter_names.append(quarter_str)

            # 월 이름을 한국어로 변환
            month_names = []
            for month in months:
                month_str = str(month)
                if "2025-01" in month_str:
                    month_names.append("1월")
                elif "2025-02" in month_str:
                    month_names.append("2월")
                elif "2025-03" in month_str:
                    month_names.append("3월")
                elif "2025-04" in month_str:
                    month_names.append("4월")
                elif "2025-05" in month_str:
                    month_names.append("5월")
                elif "2025-06" in month_str:
                    month_names.append("6월")
                elif "2025-07" in month_str:
                    month_names.append("7월")
                elif "2025-08" in month_str:
                    month_names.append("8월")
                elif "2025-09" in month_str:
                    month_names.append("9월")
                elif "2025-10" in month_str:
                    month_names.append("10월")
                elif "2025-11" in month_str:
                    month_names.append("11월")
                elif "2025-12" in month_str:
                    month_names.append("12월")
                else:
                    month_names.append(month_str)

            # 차트 생성
            fig = go.Figure()

            # 색상 정의
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

            # 0. 전체 분포 파이차트 (TOP10 + 기타)
            part_counts = df_filtered_he["부품명"].value_counts()

            # TOP10 추출
            top10_parts = part_counts.head(10)
            other_count = part_counts.iloc[10:].sum() if len(part_counts) > 10 else 0

            # TOP10 + 기타로 구성
            if other_count > 0:
                pie_labels = list(top10_parts.index) + ["기타"]
                pie_values = list(top10_parts.values) + [other_count]
            else:
                pie_labels = list(top10_parts.index)
                pie_values = list(top10_parts.values)

            fig.add_trace(
                go.Pie(
                    labels=pie_labels,
                    values=pie_values,
                    hole=0.4,
                    textinfo="label+percent+value",
                    textposition="outside",
                    textfont=dict(size=12),
                    marker_colors=colors[: len(pie_labels)],
                    pull=[
                        0.05,
                        0,
                        0,
                        0,
                        0,
                        0.1,
                        0,
                        0,
                        0,
                        0,
                        0.05,
                    ],  # 첫 번째와 마지막(기타) 강조
                    texttemplate="%{label}<br>%{value}건 (%{percent})",
                    hovertemplate="<b>%{label}</b><br>건수: %{value}<br>비율: %{percent}<extra></extra>",
                    visible=True,  # 기본 표시
                    showlegend=True,
                )
            )

            # 각 분기별 TOP5 차트 데이터 추가
            for q_idx, quarter in enumerate(quarters):
                quarter_name = quarter_names[q_idx]
                top5_parts = quarterly_top5_data[quarter]

                # 각 부품별 막대 추가
                for p_idx, (part, count) in enumerate(top5_parts.items()):
                    # 해당 분기, 해당 부품의 상세 정보 추출
                    quarter_part_df = df_filtered_he[
                        (df_filtered_he["발생분기"] == quarter)
                        & (df_filtered_he["부품명"] == part)
                    ]

                    # 상세조치내용과 불량위치 정보 수집
                    action_details = (
                        quarter_part_df["상세조치내용"].dropna().unique()[:5]
                    )  # 최대 5개
                    location_details = (
                        quarter_part_df["불량위치"].dropna().unique()[:5]
                    )  # 최대 5개

                    # hover text 생성
                    hover_text = f"<b>{part}</b><br>"
                    hover_text += f"불량 건수: {count}건<br><br>"

                    if len(action_details) > 0:
                        hover_text += "<b>주요 조치내용:</b><br>"
                        for i, action in enumerate(action_details, 1):
                            hover_text += f"{i}. {action}<br>"
                        hover_text += "<br>"

                    if len(location_details) > 0:
                        hover_text += "<b>주요 불량위치:</b><br>"
                        for i, location in enumerate(location_details, 1):
                            hover_text += f"{i}. {location}<br>"

                    fig.add_trace(
                        go.Bar(
                            x=[part],
                            y=[count],
                            name=part,
                            marker_color=colors[p_idx % len(colors)],
                            text=[count],
                            textposition="auto",
                            textfont=dict(size=12),
                            hovertemplate=f"{hover_text}<extra></extra>",
                            visible=False,  # 파이차트가 기본이므로 모든 막대차트는 숨김
                            legendgroup=f"quarter_{q_idx}",
                            showlegend=False,
                        )
                    )

            # 월별 추이 차트 데이터 추가
            for p_idx, part in enumerate(overall_top3_parts):
                x_values = []
                y_values = []
                hover_texts = []

                for j, month in enumerate(months):
                    month_name = month_names[j]
                    x_values.append(month_name)

                    if part in monthly_top3_data[month]:
                        y_values.append(monthly_top3_data[month][part])
                    else:
                        y_values.append(0)

                    # 해당 월, 해당 부품의 상세 정보 추출
                    month_part_df = df_filtered_he[
                        (df_filtered_he["발생월"] == month)
                        & (df_filtered_he["부품명"] == part)
                    ]

                    # 상세조치내용과 불량위치 정보 수집
                    action_details = (
                        month_part_df["상세조치내용"].dropna().unique()[:3]
                    )  # 최대 3개
                    location_details = (
                        month_part_df["불량위치"].dropna().unique()[:3]
                    )  # 최대 3개

                    # hover text 생성
                    hover_text = f"<b>{month_name}: {part}</b><br>"
                    hover_text += f"불량 건수: {y_values[-1]}건<br><br>"

                    if len(action_details) > 0:
                        hover_text += "<b>주요 조치내용:</b><br>"
                        for i, action in enumerate(action_details, 1):
                            hover_text += f"{i}. {action}<br>"
                        hover_text += "<br>"

                    if len(location_details) > 0:
                        hover_text += "<b>주요 불량위치:</b><br>"
                        for i, location in enumerate(location_details, 1):
                            hover_text += f"{i}. {location}<br>"

                    hover_texts.append(hover_text)

                fig.add_trace(
                    go.Scatter(
                        x=x_values,
                        y=y_values,
                        mode="lines+markers",
                        name=part,
                        line=dict(color=colors[p_idx % len(colors)], width=3),
                        marker=dict(size=8),
                        text=y_values,
                        textposition="top center",
                        textfont=dict(size=10),
                        hovertemplate="%{hovertext}<extra></extra>",
                        hovertext=hover_texts,
                        visible=False,  # 기본적으로 숨김
                        legendgroup="trend",
                        showlegend=False,
                    )
                )

            # 드롭다운 메뉴 버튼 구성
            dropdown_buttons = []

            # 전체 분포 버튼 (첫 번째)
            pie_visibility = [True] + [False] * (len(fig.data) - 1)  # 파이차트만 표시
            dropdown_buttons.append(
                dict(
                    label="전체 분포",
                    method="update",
                    args=[
                        {"visible": pie_visibility},
                        {
                            "title": "가압검사 부품별 전체 분포 (TOP10)",
                            "xaxis": {
                                "visible": False,
                                "showgrid": False,
                                "zeroline": False,
                            },
                            "yaxis": {
                                "visible": False,
                                "showgrid": False,
                                "zeroline": False,
                            },
                        },
                    ],
                )
            )

            # 각 분기별 버튼
            for q_idx, quarter in enumerate(quarters):
                quarter_name = quarter_names[q_idx]

                # 해당 분기의 trace만 보이도록 설정
                visibility = [False] * len(fig.data)
                start_idx = 1 + q_idx * 5  # 파이차트(1개) + 각 분기당 5개 부품
                end_idx = start_idx + len(quarterly_top5_data[quarter])

                for i in range(start_idx, min(end_idx, len(fig.data))):
                    if i < len(fig.data):
                        visibility[i] = True

                dropdown_buttons.append(
                    dict(
                        label=f"{quarter_name} TOP5",
                        method="update",
                        args=[
                            {"visible": visibility},
                            {
                                "title": f"{quarter_name} TOP5 부품 불량 현황",
                                "xaxis": {"title": "부품명", "visible": True},
                                "yaxis": {"title": "불량 건수", "visible": True},
                            },
                        ],
                    )
                )

            # 월별 추이 버튼
            trend_visibility = [False] * len(fig.data)
            trend_start_idx = (
                1 + len(quarters) * 5
            )  # 파이차트(1개) + 분기별 데이터 이후
            for i in range(trend_start_idx, len(fig.data)):
                trend_visibility[i] = True

            dropdown_buttons.append(
                dict(
                    label="월별 추이 (TOP3)",
                    method="update",
                    args=[
                        {"visible": trend_visibility},
                        {
                            "title": "전체 기간 TOP3 부품 월별 추이",
                            "xaxis": {"title": "월", "visible": True},
                            "yaxis": {"title": "불량 건수", "visible": True},
                        },
                    ],
                )
            )

            # 기본 제목 설정 (전체 분포가 기본)
            default_title = "가압검사 부품별 전체 분포 (TOP10)"

            # 레이아웃 설정
            fig.update_layout(
                title=dict(text=default_title, x=0.5, xanchor="center"),
                xaxis=dict(
                    visible=False, showgrid=False, zeroline=False
                ),  # 파이차트가 기본이므로 축 숨김
                yaxis=dict(visible=False, showgrid=False, zeroline=False),
                height=500,
                margin=dict(l=50, r=50, t=100, b=50),
                template="plotly_white",
                updatemenus=[
                    dict(
                        buttons=dropdown_buttons,
                        direction="down",
                        pad={"r": 10, "t": 10},
                        showactive=True,
                        x=0.1,
                        xanchor="left",
                        y=1.15,
                        yanchor="top",
                    )
                ],
                showlegend=False,
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 드롭다운 부품 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def generate_defect_analysis_html(self) -> str:
        """불량 분석 HTML 페이지 생성 - 탭 기반 통합 대시보드"""
        try:
            logger.info("🎨 통합 불량 분석 HTML 생성 시작...")

            # 실제 데이터 기반 통계 계산
            monthly_data = self.extract_monthly_data()
            supplier_data = self.extract_supplier_data()

            # 총 불량 건수 (월별 불량 건수 합계)
            total_defects = sum(monthly_data["defect_counts"])

            # 총 검사 CH수 (월별 검사 CH수 합계)
            total_ch_count = sum(monthly_data["ch_counts"])

            # 평균 불량률 계산
            avg_defect_rate = (
                (total_defects / total_ch_count * 100) if total_ch_count > 0 else 0
            )

            # 주요 외주사 수
            supplier_count = len(supplier_data["suppliers"])

            logger.info(
                f"📊 실제 통계 - 총 불량: {total_defects}건, 총 CH수: {total_ch_count}, 평균 불량률: {avg_defect_rate:.1f}%, 외주사: {supplier_count}개"
            )

            # 가압검사 차트들 생성 (기존 로직 그대로)
            monthly_chart = self.create_monthly_trend_chart()
            action_integrated_chart = self.create_action_type_integrated_chart()
            supplier_integrated_chart = self.create_supplier_integrated_chart()
            part_monthly_chart = self.create_part_monthly_chart()

            # 제조품질 차트들 생성 (가압검사와 동일한 4개 차트)
            quality_monthly_chart = self.create_quality_monthly_trend_chart()
            quality_action_chart = self.create_quality_action_integrated_chart()
            quality_supplier_chart = self.create_quality_supplier_integrated_chart()
            quality_part_chart = self.create_quality_part_monthly_chart()

            # 제조품질 차트를 HTML로 변환
            quality_monthly_html = quality_monthly_chart.to_html(
                include_plotlyjs=False, div_id="quality-monthly-chart"
            )
            quality_action_html = quality_action_chart.to_html(
                include_plotlyjs=False, div_id="quality-action-chart"
            )
            quality_supplier_html = quality_supplier_chart.to_html(
                include_plotlyjs=False, div_id="quality-supplier-chart"
            )
            quality_part_html = quality_part_chart.to_html(
                include_plotlyjs=False, div_id="quality-part-chart"
            )

            # 제조품질 실제 통계 계산
            quality_monthly_data = self.extract_quality_monthly_data()
            quality_supplier_data = self.extract_quality_supplier_data()

            quality_total_defects = sum(quality_monthly_data["defect_counts"])
            quality_total_ch = sum(quality_monthly_data["ch_counts"])
            quality_avg_rate = (
                (quality_total_defects / quality_total_ch * 100)
                if quality_total_ch > 0
                else 0
            )
            quality_supplier_count = len(quality_supplier_data["suppliers"])

            logger.info(
                f"📊 제조품질 실제 통계 - 총 불량: {quality_total_defects}건, 총 CH수: {quality_total_ch}, 평균 불량률: {quality_avg_rate:.1f}%, 외주사: {quality_supplier_count}개"
            )

            # 차트를 HTML로 변환
            monthly_html = monthly_chart.to_html(
                include_plotlyjs="cdn", div_id="monthly-chart"
            )
            action_integrated_html = action_integrated_chart.to_html(
                include_plotlyjs=False, div_id="action-integrated-chart"
            )
            supplier_integrated_html = supplier_integrated_chart.to_html(
                include_plotlyjs=False, div_id="supplier-integrated-chart"
            )
            part_monthly_html = part_monthly_chart.to_html(
                include_plotlyjs=False, div_id="part-monthly-chart"
            )

            # 통합 통계
            integrated_total_defects = total_defects + quality_total_defects
            integrated_total_ch = total_ch_count + quality_total_ch
            integrated_avg_rate = (
                (integrated_total_defects / integrated_total_ch * 100)
                if integrated_total_ch > 0
                else 0
            )

            # 전체 HTML 템플릿 (탭 기반)
            html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GST 통합 검사 분석 대시보드</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
            position: relative;
            cursor: pointer;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        /* 탭 스타일 */
        .tab-container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .tab-nav {{
            display: flex;
            border-bottom: 1px solid #e0e0e0;
            border-radius: 10px 10px 0 0;
            overflow: hidden;
        }}
        .tab-button {{
            flex: 1;
            padding: 15px 20px;
            background: #f8f9fa;
            border: none;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }}
        .tab-button.active {{
            background: white;
            color: #667eea;
            border-bottom-color: #667eea;
        }}
        .tab-button:hover {{
            background: #e9ecef;
        }}
        .tab-button.active:hover {{
            background: white;
        }}
        
        /* 탭 콘텐츠 */
        .tab-content {{
            display: none;
            padding: 20px;
            animation: fadeIn 0.3s ease-in;
        }}
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        /* 툴팁 스타일 */
        .tooltip {{
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.95);
            color: white;
            padding: 20px;
            border-radius: 12px;
            font-size: 11px;
            line-height: 1.6;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            pointer-events: none;
            min-width: 1000px;
            max-width: 1200px;
            white-space: nowrap;
        }}
        
        .tooltip.show {{
            opacity: 1;
            visibility: visible;
            transform: translateX(-50%) translateY(10px);
        }}
        
        .tooltip-content {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .tooltip-title {{
            font-size: 14px;
            font-weight: bold;
            color: #ffd700;
            text-align: center;
            margin-bottom: 10px;
            border-bottom: 1px solid #444;
            padding-bottom: 8px;
        }}
        
        .tooltip-tables-container {{
            display: flex;
            gap: 30px;
            justify-content: space-between;
        }}
        
        .tooltip-section {{
            flex: 1;
        }}
        
        .tooltip-section-title {{
            font-size: 12px;
            font-weight: bold;
            color: #87ceeb;
            margin-bottom: 10px;
            text-align: center;
            padding: 5px;
            background: rgba(135, 206, 235, 0.1);
            border-radius: 5px;
        }}
        
        .tooltip-table {{
            width: 100%;
        }}
        
        .tooltip-table table {{
            width: 100%;
            border-collapse: collapse;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            overflow: hidden;
        }}
        
        .tooltip-table th {{
            background: rgba(135, 206, 235, 0.2);
            color: #87ceeb;
            padding: 8px 6px;
            font-size: 10px;
            font-weight: bold;
            text-align: center;
            border-bottom: 1px solid #555;
        }}
        
        .tooltip-table td {{
            padding: 6px;
            font-size: 10px;
            border-bottom: 1px solid #333;
            vertical-align: top;
        }}
        
        .tooltip-table td:first-child {{
            font-weight: bold;
            color: #ffd700;
            text-align: center;
            width: 80px;
        }}
        
        .tooltip-table td:last-child {{
            color: #ffeaa7;
            font-style: italic;
        }}
        
        .tooltip::before {{
            content: '';
            position: absolute;
            top: -8px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-bottom: 8px solid rgba(0, 0, 0, 0.95);
        }}
        
        /* 기존 스타일들 */
        .chart-wrapper {{
            margin-bottom: 30px;
        }}
        .custom-select {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            font-size: 14px;
            margin-bottom: 15px;
            cursor: pointer;
        }}
        .section-title {{
            color: #333;
            font-size: 1.2em;
            margin: 20px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 2px solid #667eea;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 id="dashboard-title">GST 통합 검사 분석 대시보드
            <div class="tooltip" id="title-tooltip">
                <div class="tooltip-content">
                    <div class="tooltip-title">🔧 불량 조치 정의 가이드</div>
                    
                    <div class="tooltip-tables-container">
                        <div class="tooltip-section tooltip-section-left">
                            <div class="tooltip-section-title">📋 가압 불량 조치 정의</div>
                            <div class="tooltip-table">
                                <table>
                                    <tr>
                                        <th>조치</th>
                                        <th>정의</th>
                                        <th>예시</th>
                                    </tr>
                                    <tr>
                                        <td><strong>① 재체결</strong></td>
                                        <td>단순한 조임 불량, 미완체결 등 재체결시 LEAK가 잡히는 경우<br>기존 ASSY나 부품을 유지한 채 풀었다 다시 조이는 작업</td>
                                        <td class="example-text">클램프, 너트 등 체결이 제대로 되어있지 않은경우</td>
                                    </tr>
                                    <tr>
                                        <td><strong>② 재작업</strong></td>
                                        <td>LEAK가 재체결만으로 잡히지 않는 경우<br>부품이나 ASSY를 분해 후 다시 조립하는 작업</td>
                                        <td class="example-text">Union, Elbow 등 이음 부위에서 누설이 계속 발생하는 경우</td>
                                    </tr>
                                    <tr>
                                        <td><strong>③ 재조립</strong></td>
                                        <td>파트가 파손되는 경우<br>파손된 부품을 새것으로 교체 후 재조립</td>
                                        <td class="example-text">조립 과정에서 O-ring, 가스켓 등이 손상된 경우</td>
                                    </tr>
                                    <tr>
                                        <td><strong>④ Teflon 작업</strong></td>
                                        <td>자체 Sealing으로 LEAK가 잡히지 않는 경우<br>Teflon 테이프나 실런트 추가 적용</td>
                                        <td class="example-text">나사산 부위에서 미세한 누설이 지속되는 경우</td>
                                    </tr>
                                    <tr>
                                        <td><strong>⑤ 파트교체</strong></td>
                                        <td>품질 불량으로 지속적 발생<br>해당 부품 자체를 새것으로 완전 교체</td>
                                        <td class="example-text">부품 자체의 치수 불량이나 재질 문제가 있는 경우</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                        
                        <div class="tooltip-section tooltip-section-right">
                            <div class="tooltip-section-title">🏭 제조품질 불량 조치 정의</div>
                            <div class="tooltip-table">
                                <table>
                                    <tr>
                                        <th>조치</th>
                                        <th>정의</th>
                                        <th>예시</th>
                                    </tr>
                                    <tr>
                                        <td><strong>① 재체결</strong></td>
                                        <td>단순한 체결 불량<br>볼트, 나사 등의 조임이 부족하거나 과다한 경우</td>
                                        <td class="example-text">커버, 브라켓 등의 체결 토크 부족</td>
                                    </tr>
                                    <tr>
                                        <td><strong>② 재작업</strong></td>
                                        <td>잘못된 작업으로 인한 기능 이상<br>작업 순서나 방법을 다시 수행</td>
                                        <td class="example-text">배선 연결 오류, 부품 장착 위치 오류</td>
                                    </tr>
                                    <tr>
                                        <td><strong>③ 식별 조치</strong></td>
                                        <td>외관상 구분되는 불량<br>라벨링, 마킹 등의 식별 관련 조치</td>
                                        <td class="example-text">제품 라벨 부착 누락, 모델명 표시 오류</td>
                                    </tr>
                                    <tr>
                                        <td><strong>④ Teflon 작업</strong></td>
                                        <td>밀봉 관련 보완 작업<br>가압 공정과 동일한 실링 보강</td>
                                        <td class="example-text">연결부 누설 방지를 위한 추가 실링</td>
                                    </tr>
                                    <tr>
                                        <td><strong>⑤ 파트교체</strong></td>
                                        <td>파트 자체 문제<br>불량 부품을 정상 부품으로 교체</td>
                                        <td class="example-text">센서, 커넥터 등 전자 부품의 기능 불량</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </h1>
        <p>2025년 통합 검사(가압검사 + 제조품질) 불량 현황 및 분석</p>
    </div>
    
    <div class="tab-container">
        <div class="tab-nav">
            <button class="tab-button active" onclick="showTab('pressure')">가압검사</button>
            <button class="tab-button" onclick="showTab('quality')">제조품질</button>
            <button class="tab-button" onclick="showTab('integrated')">통합비교</button>
        </div>
        
        <div id="pressure-tab" class="tab-content active">
            
            <!-- 가압검사 개별 통계 -->
            <div class="summary-stats" style="margin-bottom: 30px;">
                <div class="stat-card">
                    <div class="stat-number">{total_defects}</div>
                    <div class="stat-label">총 불량 건수</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_ch_count}</div>
                    <div class="stat-label">총 검사 CH수</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{avg_defect_rate:.1f}%</div>
                    <div class="stat-label">평균 불량률</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{supplier_count}</div>
                    <div class="stat-label">주요 외주사</div>
                </div>
            </div>
            
            <div class="chart-container">
                {monthly_html}
            </div>
            
            <div class="chart-container">
                {action_integrated_html}
            </div>
            
            <div class="chart-container">
                {supplier_integrated_html}
            </div>
            
            <div class="chart-container">
                {part_monthly_html}
            </div>
        </div>
        
        <div id="quality-tab" class="tab-content">
            
            <!-- 제조품질 개별 통계 -->
            <div class="summary-stats" style="margin-bottom: 30px;">
                <div class="stat-card">
                    <div class="stat-number">{quality_total_defects}</div>
                    <div class="stat-label">총 불량 건수</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{quality_total_ch}</div>
                    <div class="stat-label">총 검사 CH수</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{quality_avg_rate:.1f}%</div>
                    <div class="stat-label">평균 불량률</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{quality_supplier_count}</div>
                    <div class="stat-label">주요 외주사</div>
                </div>
            </div>
            
            <div class="chart-container">
                {quality_monthly_html}
            </div>
            
            <div class="chart-container">
                {quality_action_html}
            </div>
            
            <div class="chart-container">
                {quality_supplier_html}
            </div>
            
            <div class="chart-container">
                {quality_part_html}
            </div>
        </div>
        
        <div id="integrated-tab" class="tab-content">
            <h2>🔄 통합 비교 분석</h2>
            <div class="chart-container">
                <p style="text-align: center; color: #666; font-size: 1.1em; padding: 50px;">
                    📊 가압검사와 제조품질 공정의 통합 비교 분석입니다.<br>
                    <small>통합 분석 차트 준비 중...</small>
                </p>
            </div>
        </div>
    </div>
    
    <script>
        // 탭 전환 기능
        function showTab(tabName) {{
            // 모든 탭 버튼과 콘텐츠 비활성화
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            // 선택된 탭 활성화
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // 탭 전환 후 차트 리사이즈
            resizeCharts();
        }}
        
        // Plotly 차트 초기화 함수
        function initializeCharts() {{
            // 모든 Plotly 차트 컨테이너를 찾아서 강제 렌더링
            const chartDivs = document.querySelectorAll('div[id*="chart"]');
            chartDivs.forEach(function(div) {{
                if (window.Plotly && div.data) {{
                    Plotly.redraw(div);
                }}
            }});
        }}
        
        // 차트 강제 리사이즈 함수
        function resizeCharts() {{
            setTimeout(function() {{
                const chartDivs = document.querySelectorAll('div[id*="chart"]');
                chartDivs.forEach(function(div) {{
                    if (window.Plotly && div.data) {{
                        Plotly.Plots.resize(div);
                    }}
                }});
            }}, 100);
        }}
        
        // 툴팁 기능
        document.addEventListener('DOMContentLoaded', function() {{
            const title = document.getElementById('dashboard-title');
            const tooltip = document.getElementById('title-tooltip');
            let showTimeout, hideTimeout;
            
            title.addEventListener('mouseenter', function() {{
                clearTimeout(hideTimeout);
                showTimeout = setTimeout(() => {{
                    tooltip.classList.add('show');
                }}, 300);
            }});
            
            title.addEventListener('mouseleave', function() {{
                clearTimeout(showTimeout);
                hideTimeout = setTimeout(() => {{
                    tooltip.classList.remove('show');
                }}, 300);
            }});
            
            // 페이지 로드 완료 후 차트 초기화
            setTimeout(function() {{
                initializeCharts();
                resizeCharts();
            }}, 500);
            
            // 윈도우 리사이즈 시 차트 리사이즈
            window.addEventListener('resize', resizeCharts);
        }});
    </script>
</body>
</html>
"""

            logger.info("✅ 통합 불량 분석 HTML 생성 완료")
            flush_log(logger)

            return html_template

        except Exception as e:
            logger.error(f"❌ 통합 불량 분석 HTML 생성 실패: {e}")
            flush_log(logger)
            raise

    def save_html_report(self, filename: str = "defect_analysis_dashboard.html") -> str:
        """HTML 리포트 파일 저장"""
        try:
            html_content = self.generate_defect_analysis_html()

            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"✅ HTML 리포트 저장 완료: {filename}")
            flush_log(logger)

            return filename

        except Exception as e:
            logger.error(f"❌ HTML 리포트 저장 실패: {e}")
            flush_log(logger)
            raise

    def save_and_upload_internal_report(self) -> bool:
        """internal.html로 저장하고 GitHub에 업로드"""
        try:
            from output.github_uploader import GitHubUploader
            from config import github_config

            # 1. HTML 생성
            logger.info("🔄 internal.html 생성 중...")
            html_content = self.generate_defect_analysis_html()

            # 2. 로컬 저장
            local_filename = "internal.html"
            with open(local_filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"✅ 로컬 저장 완료: {local_filename}")

            # 3. GitHub 업로드
            logger.info("🚀 GitHub 업로드 중...")
            uploader = GitHubUploader()

            # config.py의 GitHubConfig 사용
            upload_success = uploader.upload_file(
                content=html_content,
                username=github_config.username_2,
                repo=github_config.repo_2,
                branch=github_config.branch_2,
                token=github_config.token_2,
                filename="public/internal.html",
                message="Daily internal dashboard update",
            )

            if upload_success:
                logger.info("✅ internal.html GitHub 업로드 성공!")
                logger.info(
                    f"🌐 접속 URL: https://{github_config.username_2}.github.io/{github_config.repo_2}/public/internal.html"
                )
                return True
            else:
                logger.error("❌ GitHub 업로드 실패")
                return False
            return True

        except Exception as e:
            logger.error(f"❌ internal.html 업로드 실패: {e}")
            return False

    def load_quality_analysis_data(self) -> pd.DataFrame:
        """제조품질 불량분석 워크시트 데이터 로드"""
        try:
            if self.use_mock_data:
                logger.info("📊 Mock 제조품질 불량분석 데이터 사용...")

                # Mock 제조품질 불량분석 데이터 생성
                analysis_data = [
                    ["", "", "구분", "1월", "2월", "3월", "4월", "5월", "6월", "7월"],
                    ["", "", "검사 Ch수", 95, 105, 88, 98, 112, 90, 102],
                    ["", "", "불량 건수", 15, 18, 12, 20, 22, 14, 25],
                    [
                        "",
                        "",
                        "CH당 불량률",
                        0.158,
                        0.171,
                        0.136,
                        0.204,
                        0.196,
                        0.156,
                        0.245,
                    ],
                ]
                df = pd.DataFrame(analysis_data)
                logger.info(f"✅ Mock 제조품질 불량분석 데이터 로드 완료: {df.shape}")
                flush_log(logger)
                return df

            logger.info("📊 제조품질 불량분석 워크시트 데이터 로드 시작...")

            # Teams에서 파일 다운로드
            files = self.teams_loader._get_teams_files()
            excel_file = self.teams_loader._find_excel_file(files)
            file_content = self.teams_loader._download_excel_file(excel_file)

            # 제조품질 불량분석 워크시트 로드
            excel_buffer = io.BytesIO(file_content)
            df = pd.read_excel(excel_buffer, sheet_name="제조품질 불량분석")

            logger.info(f"✅ 제조품질 불량분석 데이터 로드 완료: {df.shape}")
            flush_log(logger)

            return df

        except Exception as e:
            logger.error(f"❌ 제조품질 불량분석 데이터 로드 실패: {e}")
            flush_log(logger)
            raise

    def load_quality_defect_data(self) -> pd.DataFrame:
        """제조품질 불량내역 워크시트 데이터 로드"""
        try:
            if self.use_mock_data:
                logger.info("📊 Mock 제조품질 불량내역 데이터 사용...")

                # Mock 제조품질 불량내역 데이터 생성 (가압검사와 동일한 구조)
                mock_data = {
                    "모델": ["Model-X", "Model-Y", "Model-Z"] * 15,
                    "부품명": ["SPEED CONTROLLER", "FEMALE CONNECTOR", "MALE CONNECTOR"]
                    * 15,
                    "외주사": ["제조업체A", "제조업체B", "제조업체C"] * 15,
                    "조치": ["재체결", "재작업", "재조립", "Teflon 작업", "파트교체"]
                    * 9,
                    "대분류": ["전장작업불량", "기구작업불량", "검사품질불량"] * 15,
                    "중분류": ["배선불량", "조립불량", "식별불량"] * 15,
                }
                df = pd.DataFrame(mock_data)
                logger.info(f"✅ Mock 제조품질 불량내역 데이터 로드 완료: {df.shape}")
                flush_log(logger)
                return df

            logger.info("📊 제조품질 불량내역 데이터 로드 시작...")

            # Teams에서 파일 다운로드
            files = self.teams_loader._get_teams_files()
            excel_file = self.teams_loader._find_excel_file(files)
            file_content = self.teams_loader._download_excel_file(excel_file)

            # 제조품질 불량내역 워크시트 로드
            excel_buffer = io.BytesIO(file_content)
            df = pd.read_excel(excel_buffer, sheet_name="제조품질 불량내역")

            # 컬럼명 확인 및 O열(불량위치), P열(상세조치내용) 컬럼명 설정
            if df.shape[1] >= 16:  # P열까지 있는지 확인 (P는 16번째 컬럼)
                # O열 (15번째, 인덱스 14) - 불량위치
                if df.shape[1] > 14:
                    df.columns.values[14] = "불량위치"
                # P열 (16번째, 인덱스 15) - 상세조치내용
                if df.shape[1] > 15:
                    df.columns.values[15] = "상세조치내용"

            logger.info(f"✅ 제조품질 불량내역 데이터 로드 완료: {df.shape}")
            logger.info(f"📊 컬럼명들: {list(df.columns)}")
            flush_log(logger)

            return df

        except Exception as e:
            logger.error(f"❌ 제조품질 불량내역 데이터 로드 실패: {e}")
            flush_log(logger)
            raise

    def extract_quality_monthly_data(self) -> Dict:
        """제조품질 월별 데이터 추출"""
        try:
            logger.info("📊 제조품질 월별 데이터 추출 시작...")

            if (
                not hasattr(self, "quality_analysis_data")
                or self.quality_analysis_data is None
            ):
                self.quality_analysis_data = self.load_quality_analysis_data()

            months = []
            ch_counts = []
            defect_counts = []
            defect_rates = []

            # 헤더 행 찾기 (가압검사와 동일한 구조)
            header_row = None
            for idx, row in self.quality_analysis_data.iterrows():
                if pd.notna(row.iloc[1]) and "구분" in str(row.iloc[1]):
                    header_row = idx
                    break

            if header_row is not None:
                # 월별 컬럼 찾기 (가압검사와 동일하게 2번째 컬럼부터)
                month_indices = []
                for col_idx in range(2, len(self.quality_analysis_data.columns)):
                    cell_value = self.quality_analysis_data.iloc[header_row, col_idx]
                    if pd.notna(cell_value) and "월" in str(cell_value):
                        months.append(str(cell_value))
                        month_indices.append(col_idx)

                # 각 월별 데이터 추출
                for month_idx in month_indices:
                    # 검사 CH수 찾기 (동일한 위치)
                    ch_count = 0
                    for idx, row in self.quality_analysis_data.iterrows():
                        if pd.notna(row.iloc[1]) and "검사 Ch수" in str(row.iloc[1]):
                            ch_count = (
                                row.iloc[month_idx]
                                if pd.notna(row.iloc[month_idx])
                                else 0
                            )
                            break
                    ch_counts.append(int(ch_count) if ch_count != 0 else 0)

                    # 불량 건수 찾기 (정확한 키워드 매칭)
                    defect_count = 0
                    for idx, row in self.quality_analysis_data.iterrows():
                        cell_value = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
                        if cell_value == "불량 건수":  # 정확한 문자열 매칭
                            defect_count = (
                                row.iloc[month_idx]
                                if pd.notna(row.iloc[month_idx])
                                else 0
                            )
                            break
                    defect_counts.append(int(defect_count) if defect_count != 0 else 0)

                    # CH당 불량률 찾기 (정확한 키워드 매칭)
                    defect_rate = 0
                    for idx, row in self.quality_analysis_data.iterrows():
                        cell_value = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
                        if "CH당 불량률" in cell_value:  # CH당 불량률이 포함된 셀
                            defect_rate = (
                                row.iloc[month_idx]
                                if pd.notna(row.iloc[month_idx])
                                else 0
                            )
                            break
                    defect_rates.append(
                        float(defect_rate) * 100 if defect_rate != 0 else 0
                    )

            logger.info(f"📊 제조품질 월별 데이터 추출 완료: {len(months)}개월")

            return {
                "months": months,
                "ch_counts": ch_counts,
                "defect_counts": defect_counts,
                "defect_rates": defect_rates,
            }

        except Exception as e:
            logger.error(f"❌ 제조품질 월별 데이터 추출 실패: {e}")
            flush_log(logger)
            raise

    def extract_quality_supplier_data(self) -> Dict:
        """제조품질 외주사별 데이터 추출 (불량분석 시트에서 동적 추출)"""
        try:
            logger.info("📊 제조품질 외주사별 데이터 추출 시작...")

            if (
                not hasattr(self, "quality_analysis_data")
                or self.quality_analysis_data is None
            ):
                self.quality_analysis_data = self.load_quality_analysis_data()

            suppliers = []
            supplier_counts = []
            supplier_rates = []

            # "외주사별 불량률" 섹션 찾기
            supplier_section_start = None
            for idx, row in self.quality_analysis_data.iterrows():
                if pd.notna(row.iloc[1]) and "외주사별 불량률" in str(row.iloc[1]):
                    supplier_section_start = idx
                    break

            if supplier_section_start is not None:
                # 외주사별 데이터 추출 (다음 행부터 시작)
                idx = supplier_section_start + 1
                while idx < len(self.quality_analysis_data):
                    row = self.quality_analysis_data.iloc[idx]

                    # 두 번째 컬럼이 비어있으면 종료
                    if pd.isna(row.iloc[1]):
                        break

                    supplier_name = str(row.iloc[1]).strip()

                    # 외주사 이름이 유효한지 확인 (BAT, FNI, TMS(기구), C&A, P&S, TMS(전장) 등)
                    if supplier_name and supplier_name not in ["NaN", ""]:
                        # 월별 데이터 합계 계산
                        total_count = 0
                        for col_idx in range(
                            2, min(len(self.quality_analysis_data.columns), 9)
                        ):  # 1월~7월 데이터
                            cell_value = row.iloc[col_idx]
                            if (
                                pd.notna(cell_value)
                                and str(cell_value).replace(".", "").isdigit()
                            ):
                                total_count += int(float(cell_value))

                        # 다음 행에서 비율 정보 추출 (제조품질 전용 - 누계 컬럼 사용)
                        rate = 0
                        if idx + 1 < len(self.quality_analysis_data):
                            rate_row = self.quality_analysis_data.iloc[idx + 1]
                            # 누계 컬럼에서 비율 추출 (맨 오른쪽 컬럼)
                            for col_idx in range(
                                len(self.quality_analysis_data.columns) - 1, 1, -1
                            ):
                                cell_value = rate_row.iloc[col_idx]
                                if pd.notna(cell_value):
                                    # 백분율 형태(25.0%) 또는 소수 형태(0.25) 처리
                                    if isinstance(cell_value, str) and "%" in str(
                                        cell_value
                                    ):
                                        rate = float(str(cell_value).replace("%", ""))
                                    elif isinstance(cell_value, (int, float)):
                                        # 1보다 작으면 소수형태로 판단하여 백분율로 변환
                                        rate = (
                                            float(cell_value) * 100
                                            if float(cell_value) <= 1
                                            else float(cell_value)
                                        )
                                    break

                        if total_count > 0:
                            suppliers.append(supplier_name)
                            supplier_counts.append(total_count)
                            supplier_rates.append(round(rate, 1))

                        # 다음 외주사로 이동 (비율 행 건너뛰기)
                        idx += 2
                    else:
                        idx += 1

            # 데이터가 없으면 기본값 사용
            if not suppliers:
                logger.warning("⚠️ 제조품질 동적 외주사 데이터 추출 실패, 기본값 사용")
                suppliers = ["TMS(기구)", "C&A", "P&S"]
                supplier_counts = [5, 1, 1]
                supplier_rates = [1.0, 0.17, 0.17]

            logger.info(
                f"📊 제조품질 외주사별 데이터 추출 완료: {len(suppliers)}개 업체"
            )

            return {
                "suppliers": suppliers,
                "supplier_counts": supplier_counts,
                "supplier_rates": supplier_rates,
            }

        except Exception as e:
            logger.error(f"❌ 제조품질 외주사별 데이터 추출 실패: {e}")
            flush_log(logger)
            # 실패 시 기본값 반환
            return {
                "suppliers": ["TMS(기구)", "C&A", "P&S"],
                "supplier_counts": [5, 1, 1],
                "supplier_rates": [1.0, 0.17, 0.17],
            }

    def extract_quality_supplier_monthly_data(self) -> Dict:
        """제조품질 외주사별 월별 불량률 데이터 추출"""
        try:
            logger.info("📊 제조품질 외주사별 월별 데이터 추출 시작...")

            if (
                not hasattr(self, "quality_analysis_data")
                or self.quality_analysis_data is None
            ):
                self.quality_analysis_data = self.load_quality_analysis_data()

            # 월별 컬럼 찾기
            months = []
            header_row = None
            for idx, row in self.quality_analysis_data.iterrows():
                if pd.notna(row.iloc[1]) and "구분" in str(row.iloc[1]):
                    header_row = idx
                    break

            month_indices = []
            if header_row is not None:
                for col_idx in range(2, len(self.quality_analysis_data.columns)):
                    cell_value = self.quality_analysis_data.iloc[header_row, col_idx]
                    if pd.notna(cell_value) and "월" in str(cell_value):
                        months.append(str(cell_value))
                        month_indices.append(col_idx)

            # 외주사별 불량률 섹션 찾기
            supplier_section_start = None
            for idx, row in self.quality_analysis_data.iterrows():
                if pd.notna(row.iloc[1]) and "외주사별 불량률" in str(row.iloc[1]):
                    supplier_section_start = idx
                    break

            suppliers_monthly = {}

            if supplier_section_start is not None:
                idx = supplier_section_start + 1
                while idx < len(self.quality_analysis_data):
                    row = self.quality_analysis_data.iloc[idx]

                    # 두 번째 컬럼이 비어있으면 종료
                    if pd.isna(row.iloc[1]):
                        break

                    supplier_name = str(row.iloc[1]).strip()

                    # 외주사 이름이 유효한지 확인
                    if supplier_name and supplier_name not in ["NaN", ""]:
                        # 다음 행에서 월별 비율 데이터 추출
                        if idx + 1 < len(self.quality_analysis_data):
                            rate_row = self.quality_analysis_data.iloc[idx + 1]
                            monthly_rates = []

                            for month_idx in month_indices:
                                cell_value = rate_row.iloc[month_idx]
                                if pd.notna(cell_value):
                                    # 백분율 형태(25.0%) 또는 소수 형태(0.25) 처리
                                    if isinstance(cell_value, str) and "%" in str(
                                        cell_value
                                    ):
                                        monthly_rates.append(
                                            float(str(cell_value).replace("%", ""))
                                        )
                                    elif isinstance(cell_value, (int, float)):
                                        # 1보다 작으면 소수형태로 판단하여 백분율로 변환
                                        rate_val = (
                                            float(cell_value) * 100
                                            if float(cell_value) <= 1
                                            else float(cell_value)
                                        )
                                        monthly_rates.append(rate_val)
                                    else:
                                        monthly_rates.append(0)
                                else:
                                    monthly_rates.append(0)

                            suppliers_monthly[supplier_name] = monthly_rates

                        # 다음 외주사로 이동 (비율 행 건너뛰기)
                        idx += 2
                    else:
                        idx += 1

            logger.info(
                f"📊 제조품질 외주사별 월별 데이터 추출 완료: {len(suppliers_monthly)}개 업체"
            )

            return {"months": months, "suppliers_monthly": suppliers_monthly}

        except Exception as e:
            logger.error(f"❌ 제조품질 외주사별 월별 데이터 추출 실패: {e}")
            flush_log(logger)
            raise

    def extract_quality_supplier_quarterly_data(self) -> Dict:
        """제조품질 외주사별 분기별 불량률 데이터 추출"""
        try:
            logger.info("📊 제조품질 외주사별 분기별 데이터 추출 시작...")

            # 월별 데이터를 분기별로 그룹화
            monthly_data = self.extract_quality_supplier_monthly_data()

            # 분기별 그룹화 (1-3월: 1분기, 4-6월: 2분기, 7-9월: 3분기, 10-12월: 4분기)
            quarters = []
            suppliers_quarterly = {}

            # 월별 데이터를 분기별로 변환
            months = monthly_data["months"]
            month_to_quarter = {}

            for month in months:
                month_num = int(month.replace("월", ""))
                if month_num in [1, 2, 3]:
                    quarter = "1분기"
                elif month_num in [4, 5, 6]:
                    quarter = "2분기"
                elif month_num in [7, 8, 9]:
                    quarter = "3분기"
                else:
                    quarter = "4분기"

                month_to_quarter[month] = quarter
                if quarter not in quarters:
                    quarters.append(quarter)

            # 각 외주사별로 분기별 데이터 계산
            for supplier, monthly_rates in monthly_data["suppliers_monthly"].items():
                quarterly_rates = []

                for quarter in quarters:
                    # 해당 분기의 월별 데이터 평균 계산
                    quarter_months = [
                        i
                        for i, month in enumerate(months)
                        if month_to_quarter[month] == quarter
                    ]
                    if quarter_months:
                        quarter_avg = sum(
                            monthly_rates[i] for i in quarter_months
                        ) / len(quarter_months)
                        quarterly_rates.append(round(quarter_avg, 1))
                    else:
                        quarterly_rates.append(0)

                suppliers_quarterly[supplier] = quarterly_rates

            logger.info(
                f"📊 제조품질 외주사별 분기별 데이터 추출 완료: {len(suppliers_quarterly)}개 업체, {len(quarters)}개 분기"
            )

            return {"quarters": quarters, "suppliers_quarterly": suppliers_quarterly}

        except Exception as e:
            logger.error(f"❌ 제조품질 외주사별 분기별 데이터 추출 실패: {e}")
            flush_log(logger)
            raise

    def create_quality_monthly_trend_chart(self) -> go.Figure:
        """제조품질 월별 트렌드 차트 생성 (가압검사와 완전히 동일한 구조)"""
        try:
            logger.info("📊 제조품질 월별 트렌드 차트 생성 중...")

            monthly_data = self.extract_quality_monthly_data()

            # 이중 축 차트 생성 (가압검사와 완전히 동일한 구조)
            fig = make_subplots(
                rows=1,
                cols=1,
                specs=[[{"secondary_y": True}]],
            )

            # 검사 CH수 (막대 차트)
            fig.add_trace(
                go.Bar(
                    x=monthly_data["months"],
                    y=monthly_data["ch_counts"],
                    name="검사 CH수",
                    marker_color="rgba(54, 162, 235, 0.6)",
                    text=monthly_data["ch_counts"],
                    textposition="auto",
                ),
                secondary_y=False,
            )

            # 불량 건수 (막대 차트)
            fig.add_trace(
                go.Bar(
                    x=monthly_data["months"],
                    y=monthly_data["defect_counts"],
                    name="불량 건수",
                    marker_color="rgba(255, 99, 132, 0.8)",
                    text=monthly_data["defect_counts"],
                    textposition="auto",
                ),
                secondary_y=False,
            )

            # 불량률 (선 차트)
            fig.add_trace(
                go.Scatter(
                    x=monthly_data["months"],
                    y=monthly_data["defect_rates"],
                    mode="lines+markers",
                    name="CH당 불량률 (%)",
                    line=dict(color="rgba(54, 162, 235, 1)", width=3),
                    marker=dict(size=8),
                    text=[f"{rate:.1f}%" for rate in monthly_data["defect_rates"]],
                    textposition="top center",
                ),
                secondary_y=True,
            )

            # 축 제목 설정
            fig.update_xaxes(title_text="월")
            fig.update_yaxes(
                title_text="건수 (검사 CH수 / 불량 건수)", secondary_y=False
            )
            fig.update_yaxes(title_text="CH당 불량률 (%)", secondary_y=True)

            # 레이아웃 설정
            fig.update_layout(
                title={
                    "text": "2025년 제조품질 불량 월별 트렌드",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 20, "family": "Arial, sans-serif"},
                },
                xaxis=dict(tickangle=0, tickfont=dict(size=12)),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                height=500,
                template="plotly_white",
            )

            logger.info("✅ 제조품질 월별 트렌드 차트 생성 완료")
            flush_log(logger)

            return fig

        except Exception as e:
            logger.error(f"❌ 제조품질 월별 트렌드 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_quality_action_integrated_chart(self) -> go.Figure:
        """제조품질 조치 유형별 통합 차트 생성 (불량내역 기반, 가압검사와 동일한 방식)"""
        try:
            logger.info("📊 제조품질 조치유형별 통합 차트 생성 (불량내역 기반)")

            # 제조품질 불량내역 데이터 로드
            if (
                not hasattr(self, "quality_defect_data")
                or self.quality_defect_data is None
            ):
                self.quality_defect_data = self.load_quality_defect_data()

            df = self.quality_defect_data.copy()
            df["발생일_pd"] = pd.to_datetime(df["발생일"], errors="coerce")
            df["발생월"] = df["발생일_pd"].dt.to_period("M")
            df["발생분기"] = df["발생일_pd"].dt.to_period("Q")

            # 유효한 데이터만 필터링
            df_valid = df.dropna(subset=["상세조치내용", "발생일_pd"])
            logger.info(f"📊 제조품질 유효한 불량내역 데이터: {len(df_valid)}건")

            # 전체분포용 데이터 (상세조치내용 카운트)
            action_counts = df_valid["상세조치내용"].value_counts()
            logger.info(f"📊 제조품질 조치유형별 카운트: {dict(action_counts.head())}")

            # TOP3 조치유형 추출
            top_actions = action_counts.head(3).index.tolist()
            df_top3 = df_valid[df_valid["상세조치내용"].isin(top_actions)]
            logger.info(f"📊 제조품질 TOP3 조치유형: {top_actions}")

            # 메인 차트 생성
            fig = go.Figure()

            # 색상 정의
            colors = [
                "#FF6B6B",
                "#4ECDC4",
                "#45B7D1",
                "#96CEB4",
                "#FFEAA7",
                "#DDA0DD",
                "#FF8A80",
                "#81C784",
            ]

            # 1. 전체 분포 파이차트 (기본 표시)
            fig.add_trace(
                go.Pie(
                    labels=action_counts.index.tolist(),
                    values=action_counts.values.tolist(),
                    hole=0.4,
                    textinfo="label+percent+value",
                    textposition="outside",
                    textfont=dict(size=12),
                    marker_colors=colors[: len(action_counts)],
                    pull=[0.05, 0, 0, 0, 0, 0.1],
                    texttemplate="%{label}<br>%{value}건 (%{percent})",
                    hovertemplate="<b>%{label}</b><br>건수: %{value}<br>비율: %{percent}<extra></extra>",
                    visible=True,
                    showlegend=True,
                    name="전체분포",
                )
            )

            # 2. 분기별 비교 (TOP3) - 막대 차트
            quarterly_data = (
                df_top3.groupby(["발생분기", "상세조치내용"])
                .size()
                .unstack(fill_value=0)
            )

            # 분기 이름을 한국어로 변환
            quarter_names = []
            for quarter in quarterly_data.index:
                quarter_str = str(quarter)
                try:
                    year = quarter_str[:4]
                    q_num = quarter_str[-1]
                    quarter_names.append(f"{year}년 {q_num}분기")
                except:
                    quarter_names.append(quarter_str)

            # 분기별 비교용 막대 차트 추가
            for i, action in enumerate(top_actions):
                if action in quarterly_data.columns:
                    # 각 분기+조치유형 조합의 주요 부품명 추출 (hover용)
                    hover_texts = []
                    for quarter_period in quarterly_data.index:
                        quarter_data_filtered = df_top3[
                            (df_top3["발생분기"] == quarter_period)
                            & (df_top3["상세조치내용"] == action)
                        ]
                        top_parts = (
                            quarter_data_filtered["부품명"]
                            .value_counts()
                            .head(5)
                            .index.tolist()
                        )
                        hover_text = (
                            f"주요부품: {', '.join(top_parts[:3])}"
                            if top_parts
                            else "데이터 없음"
                        )
                        hover_texts.append(hover_text)

                    fig.add_trace(
                        go.Bar(
                            x=quarter_names,
                            y=quarterly_data[action].values,
                            name=action,
                            marker_color=colors[i % len(colors)],
                            hovertemplate=f"<b>{action}</b><br>"
                            + "분기: %{x}<br>"
                            + "건수: %{y}<br>"
                            + "%{customdata}<extra></extra>",
                            customdata=hover_texts,
                            visible=False,  # 기본 숨김
                        )
                    )

            # 3. 월별 추이 (TOP3) - 라인 차트
            monthly_data = (
                df_top3.groupby(["발생월", "상세조치내용"]).size().unstack(fill_value=0)
            )

            # 월 이름을 한국어로 변환
            month_names = []
            for month in monthly_data.index:
                month_str = str(month)
                try:
                    month_num = int(month_str.split("-")[1])
                    month_names.append(f"{month_num}월")
                except:
                    month_names.append(month_str)

            # 월별 추이용 라인 차트 추가
            for i, action in enumerate(top_actions):
                if action in monthly_data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=month_names,
                            y=monthly_data[action].values,
                            mode="lines+markers",
                            name=action,
                            line=dict(color=colors[i % len(colors)], width=3),
                            marker=dict(size=8),
                            hovertemplate=f"<b>{action}</b><br>"
                            + "월: %{x}<br>"
                            + "건수: %{y}<extra></extra>",
                            visible=False,  # 기본 숨김
                        )
                    )

            # 드롭다운 메뉴 구성
            dropdown_buttons = []

            # 전체 분포 버튼
            pie_visibility = [True] + [False] * (len(fig.data) - 1)
            dropdown_buttons.append(
                dict(
                    label="전체 분포",
                    method="update",
                    args=[
                        {"visible": pie_visibility},
                        {
                            "title": "제조품질 조치유형별 전체 분포",
                            "xaxis": {
                                "visible": False,
                                "showgrid": False,
                                "zeroline": False,
                            },
                            "yaxis": {
                                "visible": False,
                                "showgrid": False,
                                "zeroline": False,
                            },
                        },
                    ],
                )
            )

            # 분기별 비교 버튼
            quarterly_visibility = [False] + [
                True if i < len(top_actions) else False
                for i in range(len(fig.data) - 1)
            ]
            dropdown_buttons.append(
                dict(
                    label="분기별 비교 (TOP3)",
                    method="update",
                    args=[
                        {"visible": quarterly_visibility},
                        {
                            "title": "제조품질 조치유형별 분기별 비교 (TOP3)",
                            "xaxis": {"title": "분기", "visible": True},
                            "yaxis": {"title": "건수", "visible": True},
                        },
                    ],
                )
            )

            # 월별 추이 버튼
            monthly_visibility = [False] * (1 + len(top_actions)) + [True] * len(
                top_actions
            )
            dropdown_buttons.append(
                dict(
                    label="월별 추이 (TOP3)",
                    method="update",
                    args=[
                        {"visible": monthly_visibility},
                        {
                            "title": "제조품질 조치유형별 월별 추이 (TOP3)",
                            "xaxis": {"title": "월", "visible": True},
                            "yaxis": {"title": "건수", "visible": True},
                        },
                    ],
                )
            )

            # 레이아웃 설정
            fig.update_layout(
                updatemenus=[
                    {
                        "buttons": dropdown_buttons,
                        "direction": "down",
                        "showactive": True,
                        "x": 0.1,
                        "xanchor": "left",
                        "y": 1.15,
                        "yanchor": "top",
                    }
                ],
                title={
                    "text": "제조품질 조치유형별 전체 분포",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 18, "family": "Arial, sans-serif"},
                },
                height=500,
                margin=dict(l=50, r=50, t=120, b=50),
                template="plotly_white",
                xaxis=dict(visible=False, showgrid=False, zeroline=False),
                yaxis=dict(visible=False, showgrid=False, zeroline=False),
                legend=dict(
                    orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05
                ),
            )

            logger.info("✅ 제조품질 조치유형별 통합 차트 생성 완료 (불량내역 기반)")
            return fig

        except Exception as e:
            logger.error(f"❌ 제조품질 조치 유형별 통합 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_quality_supplier_integrated_chart(self) -> go.Figure:
        """제조품질 외주사별 통합 차트 생성 (가압검사와 동일한 드롭다운 방식)"""
        try:
            logger.info("📊 제조품질 외주사별 통합 차트 생성 중...")

            # 1. 전체 현황 차트
            supplier_data = self.extract_quality_supplier_data()

            # 2. 분기별 차트 데이터
            quarterly_data = self.extract_quality_supplier_quarterly_data()

            # 3. 월별 차트 데이터
            monthly_data = self.extract_quality_supplier_monthly_data()

            # 메인 차트 생성 (기본: 전체 현황)
            fig = go.Figure()

            # 색상 정의 (6개 외주사용)
            colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336", "#607D8B"]

            # 1. 전체 현황 차트 (기본 표시)
            for i, (supplier, count, rate) in enumerate(
                zip(
                    supplier_data["suppliers"],
                    supplier_data["supplier_counts"],
                    supplier_data["supplier_rates"],
                )
            ):
                fig.add_trace(
                    go.Bar(
                        x=[supplier],
                        y=[count],
                        name=supplier,
                        marker_color=colors[i % len(colors)],
                        text=[f"{count}건<br>({rate:.1f}%)"],
                        textposition="outside",
                        textfont=dict(size=10),
                        visible=True,  # 기본 표시
                    )
                )

            # 2. 분기별 차트 (숨김)
            for i, (supplier, rates) in enumerate(
                quarterly_data["suppliers_quarterly"].items()
            ):
                for j, (quarter, rate) in enumerate(
                    zip(quarterly_data["quarters"], rates)
                ):
                    fig.add_trace(
                        go.Bar(
                            x=[quarter],
                            y=[rate],
                            name=supplier,
                            marker_color=colors[i % len(colors)],
                            text=[f"{rate}%" if rate > 0 else ""],
                            textposition="outside",
                            textfont=dict(size=10),
                            visible=False,  # 기본 숨김
                            showlegend=False if j > 0 else True,  # 첫 번째만 범례 표시
                        )
                    )

            # 3. 월별 차트 (선 그래프로 변경)
            for i, (supplier, rates) in enumerate(
                monthly_data["suppliers_monthly"].items()
            ):
                fig.add_trace(
                    go.Scatter(
                        x=monthly_data["months"],
                        y=rates,
                        mode="lines+markers",
                        name=supplier,
                        line=dict(color=colors[i % len(colors)], width=3),
                        marker=dict(size=8, color=colors[i % len(colors)]),
                        text=[f"{rate:.1f}%" if rate > 0 else "" for rate in rates],
                        textposition="top center",
                        textfont=dict(size=10),
                        visible=False,  # 기본 숨김
                        showlegend=True,
                    )
                )

            # 드롭다운 메뉴 설정
            total_suppliers = len(supplier_data["suppliers"])
            quarterly_traces = len(quarterly_data["suppliers_quarterly"]) * len(
                quarterly_data["quarters"]
            )
            monthly_traces = len(
                monthly_data["suppliers_monthly"]
            )  # 선 그래프로 변경되어 외주사별 1개씩

            # 가시성 설정
            visibility_overall = [True] * total_suppliers + [False] * (
                quarterly_traces + monthly_traces
            )
            visibility_quarterly = (
                [False] * total_suppliers
                + [True] * quarterly_traces
                + [False] * monthly_traces
            )
            visibility_monthly = (
                [False] * total_suppliers
                + [False] * quarterly_traces
                + [True] * monthly_traces
            )

            # 드롭다운 메뉴 구성
            fig.update_layout(
                updatemenus=[
                    {
                        "buttons": [
                            {
                                "label": "전체 현황",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_overall},
                                    {
                                        "title": {
                                            "text": "제조품질 외주사별 불량 현황",
                                            "x": 0.5,
                                            "xanchor": "center",
                                        },
                                        "xaxis": {"title": "외주사", "visible": True},
                                        "yaxis": {
                                            "title": "불량 건수",
                                            "visible": True,
                                        },
                                    },
                                ],
                            },
                            {
                                "label": "분기별 불량률",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_quarterly},
                                    {
                                        "title": {
                                            "text": "제조품질 외주사별 분기별 불량률",
                                            "x": 0.5,
                                            "xanchor": "center",
                                        },
                                        "xaxis": {"title": "분기", "visible": True},
                                        "yaxis": {
                                            "title": "불량률 (%)",
                                            "visible": True,
                                        },
                                    },
                                ],
                            },
                            {
                                "label": "월별 트렌드",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_monthly},
                                    {
                                        "title": {
                                            "text": "제조품질 외주사별 월별 불량률 트렌드",
                                            "x": 0.5,
                                            "xanchor": "center",
                                        },
                                        "xaxis": {"title": "월", "visible": True},
                                        "yaxis": {
                                            "title": "불량률 (%)",
                                            "visible": True,
                                        },
                                    },
                                ],
                            },
                        ],
                        "direction": "down",
                        "showactive": True,
                        "x": 0.02,
                        "xanchor": "left",
                        "y": 1.15,
                        "yanchor": "top",
                        "bgcolor": "rgba(255, 255, 255, 0.9)",
                        "bordercolor": "rgba(0, 0, 0, 0.2)",
                        "borderwidth": 1,
                        "font": {"size": 12},
                    }
                ],
                title={
                    "text": "제조품질 외주사별 불량 현황",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 20, "family": "Arial, sans-serif"},
                },
                xaxis_title="외주사",
                yaxis_title="불량 건수",
                height=500,
                template="plotly_white",
                font=dict(family="Arial, sans-serif", size=12),
                legend=dict(
                    orientation="v", yanchor="top", y=1, xanchor="left", x=1.02
                ),
                margin=dict(t=100, b=50, l=50, r=120),
            )

            logger.info("✅ 제조품질 외주사별 통합 차트 생성 완료")
            flush_log(logger)

            return fig

        except Exception as e:
            logger.error(f"❌ 제조품질 외주사별 통합 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_quality_part_monthly_chart(self) -> go.Figure:
        """제조품질 부품별 상세 분석 차트 생성 (가압검사와 완전히 동일한 구조)"""
        try:
            logger.info("📊 제조품질 부품별 상세 분석 차트 생성 중...")

            if (
                not hasattr(self, "quality_defect_data")
                or self.quality_defect_data is None
            ):
                self.quality_defect_data = self.load_quality_defect_data()

            df = self.quality_defect_data.copy()

            # 발생일을 날짜 형식으로 변환
            df["발생일_pd"] = pd.to_datetime(df["발생일"], errors="coerce")
            df["발생분기"] = df["발생일_pd"].dt.to_period("Q")
            df["발생월"] = df["발생일_pd"].dt.to_period("M")

            # 각 분기별 상위 5개 부품 추출
            quarters = df["발생분기"].dropna().unique()
            quarterly_top5_data = {}

            for quarter in quarters:
                quarter_data = df[df["발생분기"] == quarter]
                part_counts = quarter_data["부품명"].value_counts().head(5)
                quarterly_top5_data[quarter] = part_counts

            # 전체 기간 상위 3개 부품 (월별 추이용)
            top3_parts = df["부품명"].value_counts().head(3).index.tolist()

            # 월별 데이터 필터링 (TOP3)
            df_top3 = df[df["부품명"].isin(top3_parts)]
            df_top3 = df_top3.dropna(subset=["발생월"])

            # 월별 부품별 집계
            monthly_top3 = (
                df_top3.groupby(["발생월", "부품명"]).size().unstack(fill_value=0)
            )
            months = monthly_top3.index  # months 변수 추가

            # 월 이름을 한국어로 변환
            month_names = []
            for month in monthly_top3.index:
                month_str = str(month)
                try:
                    month_num = int(month_str.split("-")[1])
                    month_names.append(f"{month_num}월")
                except:
                    month_names.append(month_str)

            # 분기 이름을 한국어로 변환
            quarter_names = []
            for quarter in quarters:
                quarter_str = str(quarter)
                if "Q1" in quarter_str:
                    quarter_names.append("1분기")
                elif "Q2" in quarter_str:
                    quarter_names.append("2분기")
                elif "Q3" in quarter_str:
                    quarter_names.append("3분기")
                elif "Q4" in quarter_str:
                    quarter_names.append("4분기")
                else:
                    quarter_names.append(quarter_str)

            # 메인 차트 생성
            fig = go.Figure()

            # 색상 정의
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

            # 0. 전체 분포 파이차트 (TOP10 + 기타)
            part_counts = df["부품명"].value_counts()

            # TOP10 추출
            top10_parts = part_counts.head(10)
            other_count = part_counts.iloc[10:].sum() if len(part_counts) > 10 else 0

            # TOP10 + 기타로 구성
            if other_count > 0:
                pie_labels = list(top10_parts.index) + ["기타"]
                pie_values = list(top10_parts.values) + [other_count]
            else:
                pie_labels = list(top10_parts.index)
                pie_values = list(top10_parts.values)

            fig.add_trace(
                go.Pie(
                    labels=pie_labels,
                    values=pie_values,
                    hole=0.4,
                    textinfo="label+percent+value",
                    textposition="outside",
                    textfont=dict(size=12),
                    marker_colors=colors[: len(pie_labels)],
                    pull=[
                        0.05,
                        0,
                        0,
                        0,
                        0,
                        0.1,
                        0,
                        0,
                        0,
                        0,
                        0.05,
                    ],  # 첫 번째와 마지막(기타) 강조
                    texttemplate="%{label}<br>%{value}건 (%{percent})",
                    hovertemplate="<b>%{label}</b><br>건수: %{value}<br>비율: %{percent}<extra></extra>",
                    visible=True,  # 기본 표시
                    showlegend=True,
                )
            )

            # 1. 각 분기별 TOP5 부품 막대 차트
            for q_idx, quarter in enumerate(quarters):
                top5_data = quarterly_top5_data[quarter]

                for p_idx, (part, count) in enumerate(top5_data.items()):
                    # 해당 분기, 해당 부품의 상세 정보 추출
                    quarter_part_df = df[
                        (df["발생분기"] == quarter) & (df["부품명"] == part)
                    ]

                    # 상세조치내용과 불량위치 정보 수집
                    action_details = (
                        quarter_part_df["상세조치내용"].dropna().unique()[:5]
                    )  # 최대 5개
                    location_details = (
                        quarter_part_df["불량위치"].dropna().unique()[:5]
                    )  # 최대 5개

                    # hover text 생성
                    hover_text = f"<b>{part}</b><br>"
                    hover_text += f"불량 건수: {count}건<br><br>"

                    if len(action_details) > 0:
                        hover_text += "<b>주요 조치내용:</b><br>"
                        for i, action in enumerate(action_details, 1):
                            hover_text += f"{i}. {action}<br>"
                        hover_text += "<br>"

                    if len(location_details) > 0:
                        hover_text += "<b>주요 불량위치:</b><br>"
                        for i, location in enumerate(location_details, 1):
                            hover_text += f"{i}. {location}<br>"

                    fig.add_trace(
                        go.Bar(
                            x=[part],
                            y=[count],
                            name=part,
                            marker_color=colors[p_idx % len(colors)],
                            text=[count],
                            textposition="outside",
                            textfont=dict(size=12),
                            hovertemplate=f"{hover_text}<extra></extra>",
                            visible=False,  # 파이차트가 기본이므로 모든 막대차트는 숨김
                            showlegend=False,
                        )
                    )

            # 2. 월별 추이 (선 그래프, 숨김)
            for p_idx, part in enumerate(top3_parts):
                if part in monthly_top3.columns:
                    # 각 월별로 hover 정보 생성
                    hover_texts = []
                    for m_idx, month in enumerate(months):
                        month_name = month_names[m_idx]
                        month_count = monthly_top3[part].values[m_idx]

                        # 해당 월, 해당 부품의 상세 정보 추출
                        month_part_df = df[
                            (df["발생월"] == month) & (df["부품명"] == part)
                        ]

                        # 상세조치내용과 불량위치 정보 수집
                        action_details = (
                            month_part_df["상세조치내용"].dropna().unique()[:3]
                        )  # 최대 3개
                        location_details = (
                            month_part_df["불량위치"].dropna().unique()[:3]
                        )  # 최대 3개

                        # hover text 생성
                        hover_text = f"<b>{month_name}: {part}</b><br>"
                        hover_text += f"불량 건수: {month_count}건<br><br>"

                        if len(action_details) > 0:
                            hover_text += "<b>주요 조치내용:</b><br>"
                            for i, action in enumerate(action_details, 1):
                                hover_text += f"{i}. {action}<br>"
                            hover_text += "<br>"

                        if len(location_details) > 0:
                            hover_text += "<b>주요 불량위치:</b><br>"
                            for i, location in enumerate(location_details, 1):
                                hover_text += f"{i}. {location}<br>"

                        hover_texts.append(hover_text)

                    fig.add_trace(
                        go.Scatter(
                            x=month_names,
                            y=monthly_top3[part].values,
                            mode="lines+markers",
                            name=part,
                            line=dict(color=colors[p_idx % len(colors)], width=3),
                            marker=dict(size=8),
                            text=monthly_top3[part].values,
                            textposition="top center",
                            textfont=dict(size=10),
                            customdata=hover_texts,
                            hovertemplate="%{customdata}<extra></extra>",
                            visible=False,  # 기본적으로 숨김
                            showlegend=False,
                        )
                    )

            # 드롭다운 메뉴 버튼 구성
            dropdown_buttons = []

            # 전체 분포 버튼 (첫 번째)
            pie_visibility = [True] + [False] * (len(fig.data) - 1)  # 파이차트만 표시
            dropdown_buttons.append(
                dict(
                    label="전체 분포",
                    method="update",
                    args=[
                        {"visible": pie_visibility},
                        {
                            "title": "제조품질 부품별 전체 분포 (TOP10)",
                            "xaxis": {
                                "visible": False,
                                "showgrid": False,
                                "zeroline": False,
                            },
                            "yaxis": {
                                "visible": False,
                                "showgrid": False,
                                "zeroline": False,
                            },
                        },
                    ],
                )
            )

            # 각 분기별 버튼
            for q_idx, quarter in enumerate(quarters):
                quarter_name = quarter_names[q_idx]

                # 해당 분기의 trace만 보이도록 설정
                visibility = [False] * len(fig.data)
                start_idx = 1 + q_idx * 5  # 파이차트(1개) + 각 분기당 5개 부품
                end_idx = start_idx + len(quarterly_top5_data[quarter])

                for i in range(start_idx, min(end_idx, len(fig.data))):
                    if i < len(fig.data):
                        visibility[i] = True

                dropdown_buttons.append(
                    dict(
                        label=f"{quarter_name} TOP5",
                        method="update",
                        args=[
                            {"visible": visibility},
                            {
                                "title": f"{quarter_name} TOP5 부품 불량 현황",
                                "xaxis": {"title": "부품명", "visible": True},
                                "yaxis": {"title": "불량 건수", "visible": True},
                            },
                        ],
                    )
                )

            # 월별 추이 버튼
            trend_visibility = [False] * len(fig.data)
            trend_start_idx = (
                1 + len(quarters) * 5
            )  # 파이차트(1개) + 분기별 데이터 이후
            for i in range(trend_start_idx, len(fig.data)):
                trend_visibility[i] = True

            dropdown_buttons.append(
                dict(
                    label="월별 추이 (TOP3)",
                    method="update",
                    args=[
                        {"visible": trend_visibility},
                        {
                            "title": "전체 기간 TOP3 부품 월별 추이",
                            "xaxis": {"title": "월", "visible": True},
                            "yaxis": {"title": "불량 건수", "visible": True},
                        },
                    ],
                )
            )

            # 기본 제목 설정 (전체 분포가 기본)
            default_title = "제조품질 부품별 전체 분포 (TOP10)"

            # 레이아웃 설정
            fig.update_layout(
                title=dict(text=default_title, x=0.5, xanchor="center"),
                xaxis=dict(
                    visible=False, showgrid=False, zeroline=False
                ),  # 파이차트가 기본이므로 축 숨김
                yaxis=dict(visible=False, showgrid=False, zeroline=False),
                height=500,
                margin=dict(l=50, r=50, t=100, b=50),
                template="plotly_white",
                updatemenus=[
                    dict(
                        buttons=dropdown_buttons,
                        direction="down",
                        pad={"r": 10, "t": 10},
                        showactive=True,
                        x=0.1,
                        xanchor="left",
                        y=1.15,
                        yanchor="top",
                    )
                ],
                showlegend=False,
            )

            logger.info("✅ 제조품질 부품별 상세 분석 차트 생성 완료")
            flush_log(logger)

            return fig

        except Exception as e:
            logger.error(f"❌ 제조품질 부품별 상세 분석 차트 생성 실패: {e}")
            flush_log(logger)
            raise


def main():
    """데일리 실행용 메인 함수"""
    from utils.logger import setup_logger, flush_log

    logger = setup_logger(__name__)

    try:
        logger.info("🌅 데일리 internal.html 대시보드 업데이트 시작")

        # DefectVisualizer 인스턴스 생성
        visualizer = DefectVisualizer()

        # internal.html 생성 및 GitHub 업로드
        success = visualizer.save_and_upload_internal_report()

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


if __name__ == "__main__":
    main()
