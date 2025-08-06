"""
통합 불량 데이터 시각화 모듈
가압검사와 제조품질 공정을 통합 분석하는 탭 기반 대시보드
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import io

from data.teams_loader import TeamsDataLoader
from utils.logger import setup_logger, flush_log

logger = setup_logger(__name__)


class IntegratedDefectVisualizer:
    """통합 불량 데이터 시각화 클래스 (가압검사 + 제조품질)"""

    def __init__(self):
        # Teams 로더는 실제 데이터 로드 시에만 초기화
        self.teams_loader = None

        # 가압검사 데이터
        self.pressure_analysis_data = None
        self.pressure_defect_data = None

        # 제조품질 데이터
        self.quality_analysis_data = None
        self.quality_defect_data = None

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

    def load_all_data(self):
        """모든 시트의 데이터 로드 (Mock 데이터 사용)"""
        try:
            logger.info("📊 통합 데이터 로드 시작 (Mock 데이터)...")

            # Mock 데이터 생성 - 가압검사 분석 데이터 (DataFrame을 행 기준으로 생성)
            pressure_analysis_data = [
                ["", "", "구분", "1월", "2월", "3월", "4월", "5월", "6월", "7월"],
                ["", "", "검사 Ch수", 120, 135, 110, 125, 140, 115, 130],
                ["", "", "불량 건수", 25, 28, 22, 30, 32, 20, 35],
                [
                    "",
                    "",
                    "CH당 불량률",
                    0.208,
                    0.207,
                    0.200,
                    0.240,
                    0.229,
                    0.174,
                    0.269,
                ],
            ]
            pressure_analysis_mock = pd.DataFrame(pressure_analysis_data)
            self.pressure_analysis_data = pressure_analysis_mock
            logger.info(
                f"✅ 가압 불량분석 Mock 데이터 생성: {pressure_analysis_mock.shape}"
            )

            # Mock 데이터 생성 - 제조품질 분석 데이터 (DataFrame을 행 기준으로 생성)
            quality_analysis_data = [
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
            quality_analysis_mock = pd.DataFrame(quality_analysis_data)
            self.quality_analysis_data = quality_analysis_mock
            logger.info(
                f"✅ 제조품질 불량분석 Mock 데이터 생성: {quality_analysis_mock.shape}"
            )

            # Mock 불량내역 데이터는 차트에서 직접 사용하지 않으므로 간단히 생성
            self.pressure_defect_data = pd.DataFrame({"dummy": [1, 2, 3]})
            self.quality_defect_data = pd.DataFrame({"dummy": [1, 2, 3]})

            flush_log(logger)

        except Exception as e:
            logger.error(f"❌ Mock 데이터 생성 실패: {e}")
            flush_log(logger)
            raise

    def extract_monthly_data(
        self, analysis_data: pd.DataFrame, process_name: str
    ) -> Dict:
        """월별 불량 현황 데이터 추출 (공통 로직)"""
        try:
            if analysis_data is None:
                logger.warning(f"⚠️ {process_name} 분석 데이터가 없습니다")
                return {
                    "months": [],
                    "ch_counts": [],
                    "defect_counts": [],
                    "defect_rates": [],
                }

            months = []
            ch_counts = []
            defect_counts = []
            defect_rates = []

            # 헤더 행 찾기 (구분, 1월, 2월, ... 형태)
            header_row = None
            for idx, row in analysis_data.iterrows():
                if pd.notna(row.iloc[2]) and "구분" in str(row.iloc[2]):
                    header_row = idx
                    break

            if header_row is not None:
                # 월별 컬럼 찾기
                month_indices = []
                for col_idx in range(
                    3, len(analysis_data.columns)
                ):  # 3번째 컬럼부터 시작
                    cell_value = analysis_data.iloc[header_row, col_idx]
                    if pd.notna(cell_value) and "월" in str(cell_value):
                        months.append(str(cell_value))
                        month_indices.append(col_idx)

                # 각 월별 데이터 추출
                for month_idx in month_indices:
                    # 검사 CH수 찾기
                    ch_count = 0
                    for idx, row in analysis_data.iterrows():
                        if pd.notna(row.iloc[2]) and "검사 Ch수" in str(row.iloc[2]):
                            ch_count = (
                                row.iloc[month_idx]
                                if pd.notna(row.iloc[month_idx])
                                else 0
                            )
                            break
                    ch_counts.append(int(ch_count) if ch_count != 0 else 0)

                    # 불량 건수 찾기
                    defect_count = 0
                    for idx, row in analysis_data.iterrows():
                        if pd.notna(row.iloc[2]) and "불량 건수" in str(row.iloc[2]):
                            defect_count = (
                                row.iloc[month_idx]
                                if pd.notna(row.iloc[month_idx])
                                else 0
                            )
                            break
                    defect_counts.append(int(defect_count) if defect_count != 0 else 0)

                    # CH당 불량률 찾기
                    defect_rate = 0
                    for idx, row in analysis_data.iterrows():
                        if pd.notna(row.iloc[2]) and "CH당 불량률" in str(row.iloc[2]):
                            defect_rate = (
                                row.iloc[month_idx]
                                if pd.notna(row.iloc[month_idx])
                                else 0
                            )
                            break
                    defect_rates.append(
                        float(defect_rate) * 100 if defect_rate != 0 else 0
                    )

            logger.info(f"📊 {process_name} 월별 데이터 추출 완료: {len(months)}개월")

            return {
                "months": months,
                "ch_counts": ch_counts,
                "defect_counts": defect_counts,
                "defect_rates": defect_rates,
            }

        except Exception as e:
            logger.error(f"❌ {process_name} 월별 데이터 추출 실패: {e}")
            return {
                "months": [],
                "ch_counts": [],
                "defect_counts": [],
                "defect_rates": [],
            }

    def create_integrated_monthly_comparison_chart(self) -> go.Figure:
        """통합 월별 비교 차트 생성"""
        try:
            # 가압검사와 제조품질 월별 데이터 추출
            pressure_data = self.extract_monthly_data(
                self.pressure_analysis_data, "가압검사"
            )
            quality_data = self.extract_monthly_data(
                self.quality_analysis_data, "제조품질"
            )

            # 공통 월 정보 사용 (가압검사 기준)
            months = (
                pressure_data["months"]
                if pressure_data["months"]
                else quality_data["months"]
            )

            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=(
                    "월별 불량 건수 비교",
                    "월별 불량률 비교",
                    "월별 검사 CH수 비교",
                    "누적 불량 현황",
                ),
                specs=[
                    [{"secondary_y": False}, {"secondary_y": False}],
                    [{"secondary_y": False}, {"type": "pie"}],
                ],
            )

            # 1. 월별 불량 건수 비교
            fig.add_trace(
                go.Bar(
                    x=months,
                    y=pressure_data["defect_counts"],
                    name="가압검사",
                    marker_color="#45B7D1",
                    opacity=0.8,
                ),
                row=1,
                col=1,
            )

            if quality_data["defect_counts"]:
                fig.add_trace(
                    go.Bar(
                        x=months,
                        y=quality_data["defect_counts"],
                        name="제조품질",
                        marker_color="#96CEB4",
                        opacity=0.8,
                    ),
                    row=1,
                    col=1,
                )

            # 2. 월별 불량률 비교
            fig.add_trace(
                go.Scatter(
                    x=months,
                    y=pressure_data["defect_rates"],
                    mode="lines+markers",
                    name="가압검사 불량률",
                    line=dict(color="#FF6B6B", width=3),
                    marker=dict(size=8),
                ),
                row=1,
                col=2,
            )

            if quality_data["defect_rates"]:
                fig.add_trace(
                    go.Scatter(
                        x=months,
                        y=quality_data["defect_rates"],
                        mode="lines+markers",
                        name="제조품질 불량률",
                        line=dict(color="#FFEAA7", width=3),
                        marker=dict(size=8),
                    ),
                    row=1,
                    col=2,
                )

            # 3. 월별 검사 CH수 비교
            fig.add_trace(
                go.Bar(
                    x=months,
                    y=pressure_data["ch_counts"],
                    name="가압검사 CH수",
                    marker_color="#4ECDC4",
                    opacity=0.7,
                ),
                row=2,
                col=1,
            )

            if quality_data["ch_counts"]:
                fig.add_trace(
                    go.Bar(
                        x=months,
                        y=quality_data["ch_counts"],
                        name="제조품질 CH수",
                        marker_color="#DDA0DD",
                        opacity=0.7,
                    ),
                    row=2,
                    col=1,
                )

            # 4. 누적 불량 현황 (파이 차트)
            total_pressure = sum(pressure_data["defect_counts"])
            total_quality = (
                sum(quality_data["defect_counts"])
                if quality_data["defect_counts"]
                else 0
            )

            if total_pressure > 0 or total_quality > 0:
                fig.add_trace(
                    go.Pie(
                        labels=["가압검사", "제조품질"],
                        values=[total_pressure, total_quality],
                        marker=dict(colors=["#45B7D1", "#96CEB4"]),
                        textinfo="label+percent+value",
                        hole=0.4,
                    ),
                    row=2,
                    col=2,
                )

            # 레이아웃 설정
            fig.update_layout(
                title={
                    "text": "🔄 가압검사 vs 제조품질 통합 비교 분석",
                    "x": 0.5,
                    "font": {"size": 20, "color": "#2c3e50"},
                },
                height=800,
                showlegend=True,
                template="plotly_white",
                font=dict(family="Arial, sans-serif", size=12),
            )

            # 축 제목 설정
            fig.update_xaxes(title_text="월", row=1, col=1)
            fig.update_xaxes(title_text="월", row=1, col=2)
            fig.update_xaxes(title_text="월", row=2, col=1)

            fig.update_yaxes(title_text="불량 건수", row=1, col=1)
            fig.update_yaxes(title_text="불량률 (%)", row=1, col=2)
            fig.update_yaxes(title_text="검사 CH수", row=2, col=1)

            logger.info("✅ 통합 월별 비교 차트 생성 완료")
            return fig

        except Exception as e:
            logger.error(f"❌ 통합 월별 비교 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_pressure_monthly_trend_chart(self) -> go.Figure:
        """가압검사 월별 트렌드 차트"""
        try:
            pressure_data = self.extract_monthly_data(
                self.pressure_analysis_data, "가압검사"
            )
            months = pressure_data["months"]
            ch_counts = pressure_data["ch_counts"]
            defect_counts = pressure_data["defect_counts"]
            defect_rates = pressure_data["defect_rates"]

            # 서브플롯 생성
            fig = make_subplots(
                rows=2,
                cols=1,
                subplot_titles=("월별 불량 건수 및 검사 CH수", "월별 불량률 추이"),
                specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
            )

            # 상단: 불량 건수 (막대) + 검사 CH수 (선)
            fig.add_trace(
                go.Bar(
                    x=months,
                    y=defect_counts,
                    name="불량 건수",
                    marker_color="#FF6B6B",
                    opacity=0.8,
                    yaxis="y",
                ),
                row=1,
                col=1,
            )

            fig.add_trace(
                go.Scatter(
                    x=months,
                    y=ch_counts,
                    mode="lines+markers",
                    name="검사 CH수",
                    line=dict(color="#4ECDC4", width=3),
                    marker=dict(size=8),
                    yaxis="y2",
                ),
                row=1,
                col=1,
                secondary_y=True,
            )

            # 하단: 불량률 추이
            fig.add_trace(
                go.Scatter(
                    x=months,
                    y=defect_rates,
                    mode="lines+markers",
                    name="불량률 (%)",
                    line=dict(color="#45B7D1", width=4),
                    marker=dict(size=10),
                    fill="tonexty",
                ),
                row=2,
                col=1,
            )

            # 축 설정
            fig.update_xaxes(title_text="월", row=1, col=1)
            fig.update_xaxes(title_text="월", row=2, col=1)
            fig.update_yaxes(title_text="불량 건수", row=1, col=1)
            fig.update_yaxes(title_text="검사 CH수", secondary_y=True, row=1, col=1)
            fig.update_yaxes(title_text="불량률 (%)", row=2, col=1)

            fig.update_layout(
                title={
                    "text": "🔧 가압검사 월별 불량 현황 분석",
                    "x": 0.5,
                    "font": {"size": 18, "color": "#2c3e50"},
                },
                height=700,
                showlegend=True,
                template="plotly_white",
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 가압검사 월별 트렌드 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_pressure_action_chart(self) -> go.Figure:
        """가압검사 조치 유형별 차트 (Mock 데이터)"""
        try:
            # Mock 조치 유형 데이터
            action_types = ["재체결", "재작업", "재조립", "Teflon 작업", "파트교체"]
            action_counts = [45, 25, 18, 15, 35]

            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

            fig = make_subplots(
                rows=1,
                cols=2,
                subplot_titles=("조치 유형별 분포", "월별 조치 추이"),
                specs=[[{"type": "pie"}, {"type": "bar"}]],
            )

            # 파이 차트
            fig.add_trace(
                go.Pie(
                    labels=action_types,
                    values=action_counts,
                    marker=dict(colors=colors),
                    textinfo="label+percent+value",
                    hole=0.4,
                ),
                row=1,
                col=1,
            )

            # 월별 조치 막대 차트 (Mock)
            months = ["1월", "2월", "3월", "4월", "5월", "6월", "7월"]
            for i, action in enumerate(action_types):
                # 각 조치별 월별 데이터 생성 (Mock)
                monthly_values = [action_counts[i] // 7 + (j % 3) for j in range(7)]
                fig.add_trace(
                    go.Bar(
                        x=months,
                        y=monthly_values,
                        name=action,
                        marker_color=colors[i],
                        opacity=0.8,
                    ),
                    row=1,
                    col=2,
                )

            fig.update_layout(
                title={
                    "text": "🛠️ 가압검사 조치 유형별 분석",
                    "x": 0.5,
                    "font": {"size": 18, "color": "#2c3e50"},
                },
                height=500,
                showlegend=True,
                template="plotly_white",
                barmode="stack",
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 가압검사 조치 유형별 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def create_pressure_supplier_chart(self) -> go.Figure:
        """가압검사 외주사별 차트 (Mock 데이터)"""
        try:
            # Mock 외주사 데이터
            suppliers = ["BAT", "FNI", "TMS"]
            supplier_counts = [52, 38, 20]
            supplier_rates = [37.7, 27.5, 14.5]

            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]

            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=(
                    "외주사별 불량 건수",
                    "외주사별 불량률",
                    "월별 외주사 트렌드",
                    "분기별 비교",
                ),
                specs=[[{"type": "bar"}, {"type": "bar"}], [{"colspan": 2}, None]],
            )

            # 외주사별 불량 건수
            fig.add_trace(
                go.Bar(
                    x=suppliers,
                    y=supplier_counts,
                    name="불량 건수",
                    marker_color=colors,
                    text=supplier_counts,
                    textposition="auto",
                ),
                row=1,
                col=1,
            )

            # 외주사별 불량률
            fig.add_trace(
                go.Bar(
                    x=suppliers,
                    y=supplier_rates,
                    name="불량률 (%)",
                    marker_color=colors,
                    text=[f"{rate}%" for rate in supplier_rates],
                    textposition="auto",
                ),
                row=1,
                col=2,
            )

            # 월별 외주사 트렌드
            months = ["1월", "2월", "3월", "4월", "5월", "6월", "7월"]
            for i, supplier in enumerate(suppliers):
                monthly_values = [supplier_counts[i] // 7 + (j % 4) for j in range(7)]
                fig.add_trace(
                    go.Scatter(
                        x=months,
                        y=monthly_values,
                        mode="lines+markers",
                        name=f"{supplier} 트렌드",
                        line=dict(color=colors[i], width=3),
                        marker=dict(size=8),
                    ),
                    row=2,
                    col=1,
                )

            fig.update_layout(
                title={
                    "text": "🏭 가압검사 외주사별 불량 현황",
                    "x": 0.5,
                    "font": {"size": 18, "color": "#2c3e50"},
                },
                height=700,
                showlegend=True,
                template="plotly_white",
            )

            return fig

        except Exception as e:
            logger.error(f"❌ 가압검사 외주사별 차트 생성 실패: {e}")
            flush_log(logger)
            raise

    def generate_integrated_html(self) -> str:
        """통합 대시보드 HTML 생성"""
        try:
            logger.info("🎨 통합 대시보드 HTML 생성 시작...")

            # 모든 데이터 로드
            self.load_all_data()

            # 가압검사 차트들 생성
            pressure_monthly_chart = self.create_pressure_monthly_trend_chart()
            pressure_action_chart = self.create_pressure_action_chart()
            pressure_supplier_chart = self.create_pressure_supplier_chart()

            # 통합 비교 차트 생성
            integrated_chart = self.create_integrated_monthly_comparison_chart()

            # 차트들을 HTML로 변환
            pressure_monthly_html = pressure_monthly_chart.to_html(
                include_plotlyjs=False, div_id="pressure-monthly-chart"
            )
            pressure_action_html = pressure_action_chart.to_html(
                include_plotlyjs=False, div_id="pressure-action-chart"
            )
            pressure_supplier_html = pressure_supplier_chart.to_html(
                include_plotlyjs=False, div_id="pressure-supplier-chart"
            )
            integrated_chart_html = integrated_chart.to_html(
                include_plotlyjs="cdn", div_id="integrated-chart"
            )

            # 기본 통계 계산
            pressure_monthly = self.extract_monthly_data(
                self.pressure_analysis_data, "가압검사"
            )
            quality_monthly = self.extract_monthly_data(
                self.quality_analysis_data, "제조품질"
            )

            total_pressure_defects = sum(pressure_monthly["defect_counts"])
            total_quality_defects = (
                sum(quality_monthly["defect_counts"])
                if quality_monthly["defect_counts"]
                else 0
            )
            total_defects = total_pressure_defects + total_quality_defects

            total_pressure_ch = sum(pressure_monthly["ch_counts"])
            total_quality_ch = (
                sum(quality_monthly["ch_counts"]) if quality_monthly["ch_counts"] else 0
            )
            total_ch = total_pressure_ch + total_quality_ch

            avg_defect_rate = (total_defects / total_ch * 100) if total_ch > 0 else 0

            # HTML 템플릿
            html_content = f"""
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
    
    <div class="summary-stats">
        <div class="stat-card">
            <div class="stat-number">{total_defects}</div>
            <div class="stat-label">총 불량 건수</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{total_ch}</div>
            <div class="stat-label">총 검사 CH수</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{avg_defect_rate:.1f}%</div>
            <div class="stat-label">평균 불량률</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">2</div>
            <div class="stat-label">검사 공정</div>
        </div>
    </div>
    
    <div class="tab-container">
        <div class="tab-nav">
            <button class="tab-button active" onclick="showTab('pressure')">가압검사</button>
            <button class="tab-button" onclick="showTab('quality')">제조품질</button>
            <button class="tab-button" onclick="showTab('integrated')">통합비교</button>
        </div>
        
        <div id="pressure-tab" class="tab-content active">
            <h2>🔧 가압검사 분석</h2>
            
            <div class="chart-container">
                {pressure_monthly_html}
            </div>
            
            <div class="chart-container">
                {pressure_action_html}
            </div>
            
            <div class="chart-container">
                {pressure_supplier_html}
            </div>
        </div>
        
        <div id="quality-tab" class="tab-content">
            <h2>🏭 제조품질 분석</h2>
            <p>제조품질 공정의 불량 현황 및 분석 결과입니다.</p>
            <!-- 제조품질 차트들이 여기에 들어갈 예정 -->
        </div>
        
        <div id="integrated-tab" class="tab-content">
            <h2>🔄 통합 비교 분석</h2>
            <div class="chart-container">
                {integrated_chart_html}
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
        }});
    </script>
</body>
</html>
"""

            logger.info("✅ 통합 대시보드 HTML 생성 완료")
            flush_log(logger)
            return html_content

        except Exception as e:
            logger.error(f"❌ 통합 대시보드 HTML 생성 실패: {e}")
            flush_log(logger)
            raise

    def save_integrated_html(self) -> bool:
        """통합 대시보드 HTML 파일 저장"""
        try:
            html_content = self.generate_integrated_html()

            # 로컬 저장
            local_filename = "internal.html"
            with open(local_filename, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"✅ 통합 대시보드 로컬 저장 완료: {local_filename}")
            flush_log(logger)
            return True

        except Exception as e:
            logger.error(f"❌ 통합 대시보드 저장 실패: {e}")
            flush_log(logger)
            return False


if __name__ == "__main__":
    # 테스트 실행
    visualizer = IntegratedDefectVisualizer()
    success = visualizer.save_integrated_html()
    if success:
        print("✅ 통합 대시보드 생성 성공!")
        print("📁 로컬 파일: internal.html")
    else:
        print("❌ 통합 대시보드 생성 실패")
