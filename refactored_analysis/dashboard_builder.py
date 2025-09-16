"""
Dashboard Builder Module

HTML 대시보드 생성 및 템플릿 관리 기능
- HTML 템플릿 관리
- 차트 HTML 생성
- 대시보드 조립
- GitHub 업로드
"""

import pandas as pd
from typing import Dict, Tuple
import plotly.graph_objects as go

# 직접 실행 시 절대 import 사용
if __name__ == "__main__":
    from base_visualizer import BaseVisualizer
else:
    # 패키지 import 시 상대 import 사용
    from .base_visualizer import BaseVisualizer
# 직접 실행 시 절대 import 사용
if __name__ == "__main__":
    from pressure_charts import PressureCharts
    from quality_charts import QualityCharts
else:
    # 패키지 import 시 상대 import 사용
    from .pressure_charts import PressureCharts
    from .quality_charts import QualityCharts
from utils.logger import setup_logger, flush_log

logger = setup_logger(__name__)


class DashboardBuilder(BaseVisualizer):
    """대시보드 빌더 클래스"""

    def __init__(self):
        super().__init__()
        self.pressure_charts = PressureCharts()
        self.quality_charts = QualityCharts()

    def generate_defect_analysis_html(self) -> str:
        """완전한 HTML 대시보드 생성"""
        try:
            logger.info("📊 HTML 대시보드 생성 시작...")

            # 가압검사 차트들 생성
            monthly_chart = self.pressure_charts.create_monthly_trend_chart()
            action_chart = self.pressure_charts.create_action_type_integrated_chart()
            supplier_chart = self.pressure_charts.create_supplier_integrated_chart()
            part_chart = self.pressure_charts.create_part_monthly_chart()
            part_integrated_chart = self.pressure_charts.create_part_integrated_chart()

            # 제조품질 차트들 생성
            quality_monthly_chart = (
                self.quality_charts.create_quality_monthly_trend_chart()
            )
            quality_action_chart = (
                self.quality_charts.create_quality_action_integrated_chart()
            )
            quality_supplier_chart = (
                self.quality_charts.create_supplier_integrated_chart()
            )
            quality_part_chart = self.quality_charts.create_quality_part_monthly_chart()
            quality_part_integrated_chart = (
                self.quality_charts.create_quality_part_integrated_chart()
            )

            # 통합 비교 차트들 생성
            integrated_monthly_chart = self.create_integrated_monthly_comparison()
            integrated_kpi_chart = self.create_integrated_kpi_comparison()
            integrated_parts_chart, integrated_actions_chart = (
                self.create_integrated_common_charts()
            )

            # 확대/축소 비활성화 config 설정 (모바일 친화적)
            zoom_config = {
                "scrollZoom": False,
                "doubleClick": False,
                "showTips": False,
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtonsToRemove": [
                    "zoom2d",
                    "pan2d",
                    "select2d",
                    "lasso2d",
                    "zoomIn2d",
                    "zoomOut2d",
                    "autoScale2d",
                    "resetScale2d",
                ],
            }

            # 차트를 HTML로 변환 (확대/축소 비활성화)
            monthly_html = monthly_chart.to_html(
                include_plotlyjs="cdn", div_id="monthly-chart", config=zoom_config
            )
            action_integrated_html = action_chart.to_html(
                include_plotlyjs=False,
                div_id="action-integrated-chart",
                config=zoom_config,
            )
            supplier_integrated_html = supplier_chart.to_html(
                include_plotlyjs=False,
                div_id="supplier-integrated-chart",
                config=zoom_config,
            )
            part_monthly_html = part_chart.to_html(
                include_plotlyjs=False, div_id="part-monthly-chart", config=zoom_config
            )
            part_integrated_html = part_integrated_chart.to_html(
                include_plotlyjs=False,
                div_id="part-integrated-chart",
                config=zoom_config,
            )

            quality_monthly_html = quality_monthly_chart.to_html(
                include_plotlyjs=False,
                div_id="quality-monthly-chart",
                config=zoom_config,
            )
            quality_action_html = quality_action_chart.to_html(
                include_plotlyjs=False,
                div_id="quality-action-chart",
                config=zoom_config,
            )
            quality_supplier_html = quality_supplier_chart.to_html(
                include_plotlyjs=False,
                div_id="quality-supplier-chart",
                config=zoom_config,
            )
            quality_part_html = quality_part_chart.to_html(
                include_plotlyjs=False, div_id="quality-part-chart", config=zoom_config
            )
            quality_part_integrated_html = quality_part_integrated_chart.to_html(
                include_plotlyjs=False,
                div_id="quality-part-integrated-chart",
                config=zoom_config,
            )

            # 통합 비교 차트 HTML 변환 (확대/축소 비활성화)
            integrated_monthly_html = integrated_monthly_chart.to_html(
                include_plotlyjs=False,
                div_id="integrated-monthly-chart",
                config=zoom_config,
            )
            integrated_kpi_html = integrated_kpi_chart.to_html(
                include_plotlyjs=False,
                div_id="integrated-kpi-chart",
                config=zoom_config,
            )
            integrated_parts_html = integrated_parts_chart.to_html(
                include_plotlyjs=False,
                div_id="integrated-parts-chart",
                config=zoom_config,
            )
            integrated_actions_html = integrated_actions_chart.to_html(
                include_plotlyjs=False,
                div_id="integrated-actions-chart",
                config=zoom_config,
            )

            # 통계 데이터 생성 (엑셀 기준)
            pressure_kpi = self.pressure_charts.extract_kpi_data()
            quality_kpi = self.quality_charts.extract_quality_kpi_data()

            # 가압검사 KPI 데이터 (엑셀 기준)
            pressure_total_ch = pressure_kpi["total_ch"]
            pressure_total_defects = pressure_kpi["total_defects"]
            pressure_avg_rate = pressure_kpi["avg_rate"]
            supplier_count = 3  # BAT, FNI, TMS (하드코딩)

            # 제조품질 KPI 데이터 (엑셀 기준)
            quality_total_ch = quality_kpi["total_ch"]
            quality_total_defects = quality_kpi["total_defects"]
            quality_avg_rate = quality_kpi["avg_rate"]
            quality_supplier_count = 6  # 6개 외주사 (하드코딩)

            # HTML 템플릿
            html_template = self._get_html_template()

            # 현재 연도 및 타임스탬프 추출
            from datetime import datetime

            now = datetime.now()
            current_year = now.year
            timestamp = now.strftime("%Y년 %m월 %d일 %H:%M:%S")

            # 템플릿에 데이터 삽입
            html_content = html_template.format(
                current_year=current_year,
                timestamp=timestamp,
                pressure_total_defects=pressure_total_defects,
                pressure_total_ch=pressure_total_ch,
                pressure_avg_rate=pressure_avg_rate,
                supplier_count=supplier_count,
                quality_total_defects=quality_total_defects,
                quality_total_ch=quality_total_ch,
                quality_avg_rate=quality_avg_rate,
                quality_supplier_count=quality_supplier_count,
                monthly_html=monthly_html,
                action_integrated_html=action_integrated_html,
                supplier_integrated_html=supplier_integrated_html,
                part_integrated_html=part_integrated_html,
                part_monthly_html=part_monthly_html,
                quality_monthly_html=quality_monthly_html,
                quality_action_html=quality_action_html,
                quality_supplier_html=quality_supplier_html,
                quality_part_integrated_html=quality_part_integrated_html,
                quality_part_html=quality_part_html,
                integrated_monthly_html=integrated_monthly_html,
                integrated_kpi_html=integrated_kpi_html,
                integrated_parts_html=integrated_parts_html,
                integrated_actions_html=integrated_actions_html,
            )

            logger.info("✅ HTML 대시보드 생성 완료")
            return html_content

        except Exception as e:
            logger.error(f"❌ HTML 대시보드 생성 실패: {e}")
            flush_log(logger)
            raise

    def save_html_report(self, filename: str = "defect_analysis_dashboard.html") -> str:
        """HTML 리포트를 파일로 저장"""
        try:
            html_content = self.generate_defect_analysis_html()

            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"✅ HTML 리포트 저장 완료: {filename}")
            return filename

        except Exception as e:
            logger.error(f"❌ HTML 리포트 저장 실패: {e}")
            flush_log(logger)
            raise

    def save_and_upload_internal_report(self) -> bool:
        """내부용 HTML 리포트 생성 및 GitHub 업로드"""
        try:
            logger.info("📋 내부용 대시보드 생성 및 업로드 시작...")

            # 1. HTML 콘텐츠 생성
            html_content = self.generate_defect_analysis_html()

            # 2. 로컬 저장
            local_filename = "internal.html"
            with open(local_filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"✅ 로컬 저장 완료: {local_filename}")

            # 3. GitHub 업로드
            from config import DISABLE_GITHUB_UPLOAD

            if DISABLE_GITHUB_UPLOAD:
                logger.info("🔄 GitHub 업로드 비활성화됨 - 로컬 저장만 완료")
                return True

            logger.info("🚀 GitHub 업로드 중...")
            from output.github_uploader import GitHubUploader
            from config import github_config

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

        except Exception as e:
            logger.error(f"❌ internal.html 업로드 실패: {e}")
            return False

    def create_integrated_monthly_comparison(self) -> go.Figure:
        """월별 불량률 비교 차트 (가압검사 vs 제조품질)"""
        try:
            logger.info("📊 통합 월별 비교 차트 생성 중...")

            # 데이터 추출
            pressure_data = self.pressure_charts.extract_monthly_data()
            quality_data = self.quality_charts.extract_quality_monthly_data()

            # 공통 월 정보 (가압검사 기준)
            months = pressure_data["months"]

            fig = go.Figure()

            # 가압검사 불량률 라인
            fig.add_trace(
                go.Scatter(
                    x=months,
                    y=pressure_data["defect_rates"],
                    mode="lines+markers",
                    name="가압검사",
                    line=dict(color="#45B7D1", width=3),
                    marker=dict(size=8, color="#45B7D1"),
                    text=[f"{rate:.1f}%" for rate in pressure_data["defect_rates"]],
                    textposition="top center",
                    hovertemplate="<b>가압검사</b><br>월: %{x}<br>불량률: %{y:.1f}%<extra></extra>",
                )
            )

            # 제조품질 불량률 라인
            fig.add_trace(
                go.Scatter(
                    x=months,
                    y=quality_data["defect_rates"],
                    mode="lines+markers",
                    name="제조품질",
                    line=dict(color="#E91E63", width=3),
                    marker=dict(size=8, color="#E91E63"),
                    text=[f"{rate:.1f}%" for rate in quality_data["defect_rates"]],
                    textposition="bottom center",
                    hovertemplate="<b>제조품질</b><br>월: %{x}<br>불량률: %{y:.1f}%<extra></extra>",
                )
            )

            fig.update_layout(
                title=dict(
                    text="🔄 가압검사 vs 제조품질 월별 불량률 비교",
                    x=0.5,
                    xanchor="center",
                    font=dict(size=18),
                ),
                xaxis_title="월",
                yaxis_title="불량률 (%)",
                height=500,
                template="plotly_white",
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                hovermode="x unified",
            )

            logger.info("✅ 통합 월별 비교 차트 생성 완료")
            return fig

        except Exception as e:
            logger.error(f"❌ 통합 월별 비교 차트 생성 실패: {e}")
            return go.Figure()

    def create_integrated_kpi_comparison(self) -> go.Figure:
        """KPI 비교 차트 (사이드바이사이드)"""
        try:
            logger.info("📊 통합 KPI 비교 차트 생성 중...")

            # 데이터 추출
            pressure_kpi = self.pressure_charts.extract_kpi_data()
            quality_kpi = self.quality_charts.extract_quality_kpi_data()

            categories = ["총 검사 CH수", "총 불량 건수", "평균 불량률(%)"]
            pressure_values = [
                pressure_kpi["total_ch"],
                pressure_kpi["total_defects"],
                pressure_kpi["avg_rate"],
            ]
            quality_values = [
                quality_kpi["total_ch"],
                quality_kpi["total_defects"],
                quality_kpi["avg_rate"],
            ]

            fig = go.Figure()

            # 가압검사 막대
            fig.add_trace(
                go.Bar(
                    name="가압검사",
                    x=categories,
                    y=pressure_values,
                    marker_color="#45B7D1",
                    text=[
                        f"{val:,}" if i < 2 else f"{val:.1f}%"
                        for i, val in enumerate(pressure_values)
                    ],
                    textposition="outside",
                    hovertemplate="<b>가압검사</b><br>%{x}: %{y}<extra></extra>",
                )
            )

            # 제조품질 막대
            fig.add_trace(
                go.Bar(
                    name="제조품질",
                    x=categories,
                    y=quality_values,
                    marker_color="#E91E63",
                    text=[
                        f"{val:,}" if i < 2 else f"{val:.1f}%"
                        for i, val in enumerate(quality_values)
                    ],
                    textposition="outside",
                    hovertemplate="<b>제조품질</b><br>%{x}: %{y}<extra></extra>",
                )
            )

            fig.update_layout(
                title=dict(
                    text="📊 가압검사 vs 제조품질 주요 KPI 비교",
                    x=0.5,
                    xanchor="center",
                    font=dict(size=18),
                ),
                xaxis_title="항목",
                yaxis_title="값",
                height=500,
                template="plotly_white",
                barmode="group",
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
            )

            logger.info("✅ 통합 KPI 비교 차트 생성 완료")
            return fig

        except Exception as e:
            logger.error(f"❌ 통합 KPI 비교 차트 생성 실패: {e}")
            return go.Figure()

    def create_integrated_common_charts(self) -> Tuple[go.Figure, go.Figure]:
        """통합 공통 분석 차트 생성 (부품별 TOP10, 조치유형별 전체분포)"""
        try:
            logger.info("📊 통합 공통 분석 차트 생성 시작...")

            # 가압검사와 제조품질 불량내역 데이터 로드
            pressure_df = (
                self.pressure_charts.defect_data.copy()
                if self.pressure_charts.defect_data is not None
                else pd.DataFrame()
            )
            quality_df = (
                self.quality_charts.quality_defect_data.copy()
                if self.quality_charts.quality_defect_data is not None
                else pd.DataFrame()
            )

            # 데이터 유효성 검사
            if pressure_df.empty or quality_df.empty:
                logger.warning("⚠️ 가압검사 또는 제조품질 불량내역 데이터가 없음")
                # 빈 차트 반환
                empty_fig = go.Figure()
                empty_fig.add_trace(
                    go.Bar(x=["데이터 없음"], y=[1], text=["실제 데이터 연결 필요"])
                )
                empty_fig.update_layout(title="데이터 준비 중", height=500)
                return empty_fig, empty_fig

            # 1. 공통 부품별 전체 분포 TOP10 차트
            # He미보증 데이터 필터링
            if "비고" in pressure_df.columns:
                pressure_df = pressure_df[
                    ~pressure_df["비고"].str.contains(
                        "제조\\(He미보증\\)", case=False, na=False
                    )
                ]
            if "비고" in quality_df.columns:
                quality_df = quality_df[
                    ~quality_df["비고"].str.contains(
                        "제조\\(He미보증\\)", case=False, na=False
                    )
                ]

            # 가압검사 데이터에 구분 컬럼 추가
            pressure_df["검사구분"] = "가압검사"
            quality_df["검사구분"] = "제조품질"

            # 날짜 컬럼 전처리 (분기, 월 정보 생성)
            if "발생일" in pressure_df.columns:
                pressure_df["발생일_pd"] = pd.to_datetime(
                    pressure_df["발생일"], errors="coerce"
                )
                pressure_df["발생분기"] = pressure_df["발생일_pd"].dt.to_period("Q")
                pressure_df["발생월"] = pressure_df["발생일_pd"].dt.to_period("M")

            if "발생일" in quality_df.columns:
                quality_df["발생일_pd"] = pd.to_datetime(
                    quality_df["발생일"], errors="coerce"
                )
                quality_df["발생분기"] = quality_df["발생일_pd"].dt.to_period("Q")
                quality_df["발생월"] = quality_df["발생일_pd"].dt.to_period("M")

            # 부품명 컬럼 확인
            pressure_parts = (
                pressure_df["부품명"].value_counts()
                if "부품명" in pressure_df.columns
                else pd.Series()
            )
            quality_parts = (
                quality_df["부품명"].value_counts()
                if "부품명" in quality_df.columns
                else pd.Series()
            )

            # 전체 부품별 통합 카운트
            all_parts = (
                pd.concat([pressure_parts, quality_parts])
                .groupby(level=0)
                .sum()
                .sort_values(ascending=False)
            )

            # 전체 부품별 TOP10 데이터
            top10_parts = all_parts.head(10)

            # 부품별 상세 데이터 (검사구분별)
            combined_df = pd.concat([pressure_df, quality_df], ignore_index=True)
            part_detail_data = []

            for part in top10_parts.index:
                pressure_count = pressure_parts.get(part, 0)
                quality_count = quality_parts.get(part, 0)
                total_count = pressure_count + quality_count

                part_detail_data.append(
                    {
                        "부품명": part,
                        "가압검사": pressure_count,
                        "제조품질": quality_count,
                        "전체": total_count,
                    }
                )

            # 부품별 차트 생성
            fig_parts = go.Figure()

            # 1. 전체 분포 막대차트 (사이드바이사이드 - 가압검사 vs 제조품질)

            # 가압검사 데이터
            pressure_values = [
                pressure_parts.get(part, 0) for part in top10_parts.index
            ]
            fig_parts.add_trace(
                go.Bar(
                    name="가압검사",
                    x=list(top10_parts.index),
                    y=pressure_values,
                    marker_color="#FF6B6B",
                    text=[f"{v}건" if v > 0 else "" for v in pressure_values],
                    textposition="outside",
                    textfont=dict(size=10),
                    hovertemplate="<b>%{x}</b><br>가압검사: %{y}건<extra></extra>",
                    visible=True,
                    showlegend=True,
                )
            )

            # 제조품질 데이터
            quality_values = [quality_parts.get(part, 0) for part in top10_parts.index]
            fig_parts.add_trace(
                go.Bar(
                    name="제조품질",
                    x=list(top10_parts.index),
                    y=quality_values,
                    marker_color="#4ECDC4",
                    text=[f"{v}건" if v > 0 else "" for v in quality_values],
                    textposition="outside",
                    textfont=dict(size=10),
                    hovertemplate="<b>%{x}</b><br>제조품질: %{y}건<extra></extra>",
                    visible=True,
                    showlegend=True,
                )
            )

            # 2. 분기별 비교 막대차트 추가
            # 분기별 데이터 계산
            quarterly_parts_data = {}

            # 가압검사 분기별 데이터
            if "발생분기" in pressure_df.columns:
                pressure_quarterly = (
                    pressure_df.groupby(["발생분기", "부품명"])
                    .size()
                    .unstack(fill_value=0)
                )
                for part in top10_parts.index:
                    if part in pressure_quarterly.columns:
                        quarterly_parts_data[f"가압_{part}"] = pressure_quarterly[
                            part
                        ].values
                    else:
                        quarterly_parts_data[f"가압_{part}"] = [0] * len(
                            pressure_quarterly.index
                        )

            # 제조품질 분기별 데이터
            if "발생분기" in quality_df.columns:
                quality_quarterly = (
                    quality_df.groupby(["발생분기", "부품명"])
                    .size()
                    .unstack(fill_value=0)
                )
                quarters = sorted(
                    list(
                        set(
                            list(pressure_df["발생분기"].dropna())
                            + list(quality_df["발생분기"].dropna())
                        )
                    )
                )

                # 분기 이름을 한국어로 변환
                quarter_names = []
                for quarter in quarters:
                    quarter_str = str(quarter)
                    try:
                        year = quarter_str[:4]
                        q_num = quarter_str[-1]
                        quarter_names.append(f"{year}년 {q_num}분기")
                    except:
                        quarter_names.append(quarter_str)

                # 분기별 비교 막대차트 추가 (TOP5만)
                colors_bar = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

                for i, part in enumerate(list(top10_parts.index)[:5]):  # TOP5만
                    # 가압검사 + 제조품질 분기별 합계
                    pressure_quarterly_part = (
                        pressure_df[pressure_df["부품명"] == part]
                        .groupby("발생분기")
                        .size()
                        if "발생분기" in pressure_df.columns
                        else pd.Series()
                    )
                    quality_quarterly_part = (
                        quality_df[quality_df["부품명"] == part]
                        .groupby("발생분기")
                        .size()
                        if "발생분기" in quality_df.columns
                        else pd.Series()
                    )

                    combined_quarterly = (
                        pd.concat([pressure_quarterly_part, quality_quarterly_part])
                        .groupby(level=0)
                        .sum()
                    )

                    # 각 분기별 hover 정보 구성
                    hover_texts = []
                    x_values = []
                    y_values = []

                    for j, quarter in enumerate(quarters):
                        quarter_name = quarter_names[j]
                        x_values.append(quarter_name)

                        quarterly_count = combined_quarterly.get(quarter, 0)
                        y_values.append(quarterly_count)

                        # 해당 분기, 해당 부품의 상세 정보
                        quarter_pressure_df = pressure_df[
                            (pressure_df["발생분기"] == quarter)
                            & (pressure_df["부품명"] == part)
                        ]
                        quarter_quality_df = quality_df[
                            (quality_df["발생분기"] == quarter)
                            & (quality_df["부품명"] == part)
                        ]

                        # 조치내용 상위 3개 추출
                        pressure_actions = (
                            quarter_pressure_df["상세조치내용"].dropna().unique()[:3]
                            if "상세조치내용" in quarter_pressure_df.columns
                            else []
                        )
                        quality_actions = (
                            quarter_quality_df["상세조치내용"].dropna().unique()[:3]
                            if "상세조치내용" in quarter_quality_df.columns
                            else []
                        )
                        combined_actions = list(
                            set(list(pressure_actions) + list(quality_actions))
                        )[:3]

                        # 불량위치 상위 3개 추출
                        pressure_locations = (
                            quarter_pressure_df["불량위치"].dropna().unique()[:3]
                            if "불량위치" in quarter_pressure_df.columns
                            else []
                        )
                        quality_locations = (
                            quarter_quality_df["불량위치"].dropna().unique()[:3]
                            if "불량위치" in quarter_quality_df.columns
                            else []
                        )
                        combined_locations = list(
                            set(list(pressure_locations) + list(quality_locations))
                        )[:3]

                        hover_text = f"<b>{quarter_name}: {part}</b><br>불량 건수: {quarterly_count}건<br><br>"
                        if len(combined_actions) > 0:
                            hover_text += "<b>주요 조치내용:</b><br>"
                            for idx, action in enumerate(combined_actions, 1):
                                hover_text += f"{idx}. {action}<br>"
                            hover_text += "<br>"
                        if len(combined_locations) > 0:
                            hover_text += "<b>주요 불량위치:</b><br>"
                            for idx, location in enumerate(combined_locations, 1):
                                hover_text += f"{idx}. {location}<br>"

                        hover_texts.append(hover_text)

                    fig_parts.add_trace(
                        go.Bar(
                            name=part,
                            x=x_values,
                            y=y_values,
                            marker_color=colors_bar[i % len(colors_bar)],
                            text=[f"{val}건" if val > 0 else "" for val in y_values],
                            textposition="outside",
                            hovertemplate="%{hovertext}<extra></extra>",
                            hovertext=hover_texts,
                            visible=False,  # 기본 숨김
                            showlegend=True,
                        )
                    )

            # 3. 월별 추이 라인차트 추가 (TOP3만)
            if "발생월" in pressure_df.columns and "발생월" in quality_df.columns:
                months = sorted(
                    list(
                        set(
                            list(pressure_df["발생월"].dropna())
                            + list(quality_df["발생월"].dropna())
                        )
                    )
                )

                # 월 이름을 한국어로 변환
                month_names = []
                for month in months:
                    month_str = str(month)
                    try:
                        if "-" in month_str:
                            year, month_num = month_str.split("-")
                            month_names.append(f"{year}년 {month_num}월")
                        else:
                            month_names.append(month_str)
                    except:
                        month_names.append(month_str)

                colors_line = ["#FF6B6B", "#4ECDC4", "#45B7D1"]

                for i, part in enumerate(list(top10_parts.index)[:3]):  # TOP3만
                    # 가압검사 + 제조품질 월별 합계
                    pressure_monthly_part = (
                        pressure_df[pressure_df["부품명"] == part]
                        .groupby("발생월")
                        .size()
                        if "발생월" in pressure_df.columns
                        else pd.Series()
                    )
                    quality_monthly_part = (
                        quality_df[quality_df["부품명"] == part]
                        .groupby("발생월")
                        .size()
                        if "발생월" in quality_df.columns
                        else pd.Series()
                    )

                    combined_monthly = (
                        pd.concat([pressure_monthly_part, quality_monthly_part])
                        .groupby(level=0)
                        .sum()
                    )

                    # 각 월별 hover 정보 구성
                    hover_texts = []
                    x_values = []
                    y_values = []

                    for j, month in enumerate(months):
                        month_name = month_names[j]
                        x_values.append(month_name)

                        monthly_count = combined_monthly.get(month, 0)
                        y_values.append(monthly_count)

                        # 해당 월, 해당 부품의 상세 정보
                        month_pressure_df = pressure_df[
                            (pressure_df["발생월"] == month)
                            & (pressure_df["부품명"] == part)
                        ]
                        month_quality_df = quality_df[
                            (quality_df["발생월"] == month)
                            & (quality_df["부품명"] == part)
                        ]

                        # 조치내용 상위 3개 추출
                        pressure_actions = (
                            month_pressure_df["상세조치내용"].dropna().unique()[:3]
                            if "상세조치내용" in month_pressure_df.columns
                            else []
                        )
                        quality_actions = (
                            month_quality_df["상세조치내용"].dropna().unique()[:3]
                            if "상세조치내용" in month_quality_df.columns
                            else []
                        )
                        combined_actions = list(
                            set(list(pressure_actions) + list(quality_actions))
                        )[:3]

                        # 불량위치 상위 3개 추출
                        pressure_locations = (
                            month_pressure_df["불량위치"].dropna().unique()[:3]
                            if "불량위치" in month_pressure_df.columns
                            else []
                        )
                        quality_locations = (
                            month_quality_df["불량위치"].dropna().unique()[:3]
                            if "불량위치" in month_quality_df.columns
                            else []
                        )
                        combined_locations = list(
                            set(list(pressure_locations) + list(quality_locations))
                        )[:3]

                        hover_text = f"<b>{month_name}: {part}</b><br>불량 건수: {monthly_count}건<br><br>"
                        if len(combined_actions) > 0:
                            hover_text += "<b>주요 조치내용:</b><br>"
                            for idx, action in enumerate(combined_actions, 1):
                                hover_text += f"{idx}. {action}<br>"
                            hover_text += "<br>"
                        if len(combined_locations) > 0:
                            hover_text += "<b>주요 불량위치:</b><br>"
                            for idx, location in enumerate(combined_locations, 1):
                                hover_text += f"{idx}. {location}<br>"

                        hover_texts.append(hover_text)

                    fig_parts.add_trace(
                        go.Scatter(
                            name=part,
                            x=x_values,
                            y=y_values,
                            mode="lines+markers",
                            line=dict(color=colors_line[i % len(colors_line)], width=3),
                            marker=dict(
                                size=8, color=colors_line[i % len(colors_line)]
                            ),
                            text=[f"{val}건" if val > 0 else "" for val in y_values],
                            textposition="top center",
                            hovertemplate="%{hovertext}<extra></extra>",
                            hovertext=hover_texts,
                            visible=False,  # 기본 숨김
                            showlegend=True,
                        )
                    )

            # 4. 부품별 검사공정 비교 차트 추가 (TOP5, 월별)
            # TOP5 부품에 대해 각각 가압검사/제조품질 분리된 월별 추이
            top5_for_comparison = list(top10_parts.index)[:5]  # TOP10에서 상위 5개 선택

            if "발생월" in pressure_df.columns and "발생월" in quality_df.columns:
                months = sorted(
                    list(
                        set(
                            list(pressure_df["발생월"].dropna())
                            + list(quality_df["발생월"].dropna())
                        )
                    )
                )

                # 월 이름을 한국어로 변환
                month_names = []
                for month in months:
                    month_str = str(month)
                    try:
                        year_month = month_str.split("-")
                        if len(year_month) == 2:
                            year, month_num = year_month
                            month_names.append(f"{year}년 {month_num}월")
                        else:
                            month_names.append(month_str)
                    except:
                        month_names.append(month_str)

                # 부품별 색상 팔레트 (분기별 비교와 동일)
                colors_comparison = [
                    "#FF6B6B",
                    "#4ECDC4",
                    "#45B7D1",
                    "#96CEB4",
                    "#FFEAA7",
                ]

                # 각 TOP5 부품별로 가압검사/제조품질 분리된 라인차트 추가
                for i, part in enumerate(top5_for_comparison):
                    base_color = colors_comparison[i % len(colors_comparison)]

                    # 옅은 색상 생성 (RGBA 형식으로 변환)
                    # hex -> rgba 변환
                    hex_color = base_color.lstrip("#")
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    light_color = f"rgba({r},{g},{b},0.5)"  # 50% 투명도

                    # 가압검사 월별 데이터
                    pressure_monthly_part = (
                        pressure_df[pressure_df["부품명"] == part]
                        .groupby("발생월")
                        .size()
                        if "발생월" in pressure_df.columns
                        else pd.Series()
                    )

                    # 제조품질 월별 데이터
                    quality_monthly_part = (
                        quality_df[quality_df["부품명"] == part]
                        .groupby("발생월")
                        .size()
                        if "발생월" in quality_df.columns
                        else pd.Series()
                    )

                    # 가압검사 라인 (기본 색상, 실선)
                    pressure_y_values = []
                    pressure_hover_texts = []

                    for j, month in enumerate(months):
                        month_name = month_names[j]
                        monthly_count = pressure_monthly_part.get(month, 0)
                        pressure_y_values.append(monthly_count)

                        # 해당 월, 해당 부품의 가압검사 상세 정보
                        month_pressure_df = pressure_df[
                            (pressure_df["발생월"] == month)
                            & (pressure_df["부품명"] == part)
                        ]

                        # 불량위치 상위 3개 추출
                        pressure_locations = (
                            month_pressure_df["불량위치"].dropna().unique()[:3]
                            if "불량위치" in month_pressure_df.columns
                            else []
                        )

                        hover_text = f"<b>{month_name}: {part} (가압검사)</b><br>불량 건수: {monthly_count}건<br><br>"
                        if len(pressure_locations) > 0:
                            hover_text += "<b>주요 불량위치:</b><br>"
                            for idx, location in enumerate(pressure_locations, 1):
                                hover_text += f"{idx}. {location}<br>"

                        pressure_hover_texts.append(hover_text)

                    fig_parts.add_trace(
                        go.Scatter(
                            name=f"{part} (가압검사)",
                            x=month_names,
                            y=pressure_y_values,
                            mode="lines+markers",
                            line=dict(color=base_color, width=3, dash="solid"),
                            marker=dict(size=8, symbol="circle"),
                            hovertemplate="%{hovertext}<extra></extra>",
                            hovertext=pressure_hover_texts,
                            visible=False,  # 기본 숨김
                            showlegend=True,
                        )
                    )

                    # 제조품질 라인 (옅은 색상, 점선)
                    quality_y_values = []
                    quality_hover_texts = []

                    for j, month in enumerate(months):
                        month_name = month_names[j]
                        monthly_count = quality_monthly_part.get(month, 0)
                        quality_y_values.append(monthly_count)

                        # 해당 월, 해당 부품의 제조품질 상세 정보
                        month_quality_df = quality_df[
                            (quality_df["발생월"] == month)
                            & (quality_df["부품명"] == part)
                        ]

                        # 불량위치 상위 3개 추출
                        quality_locations = (
                            month_quality_df["불량위치"].dropna().unique()[:3]
                            if "불량위치" in month_quality_df.columns
                            else []
                        )

                        hover_text = f"<b>{month_name}: {part} (제조품질)</b><br>불량 건수: {monthly_count}건<br><br>"
                        if len(quality_locations) > 0:
                            hover_text += "<b>주요 불량위치:</b><br>"
                            for idx, location in enumerate(quality_locations, 1):
                                hover_text += f"{idx}. {location}<br>"

                        quality_hover_texts.append(hover_text)

                    fig_parts.add_trace(
                        go.Scatter(
                            name=f"{part} (제조품질)",
                            x=month_names,
                            y=quality_y_values,
                            mode="lines+markers",
                            line=dict(color=light_color, width=3, dash="dash"),
                            marker=dict(size=8, symbol="diamond"),
                            hovertemplate="%{hovertext}<extra></extra>",
                            hovertext=quality_hover_texts,
                            visible=False,  # 기본 숨김
                            showlegend=True,
                        )
                    )

            # 드롭다운 메뉴 설정
            total_main_traces = 2  # 가압검사 + 제조품질
            total_bar_traces = 5  # TOP5 부품 (분기별)
            total_line_traces = 3  # TOP3 부품 (월별)
            total_comparison_traces = (
                10  # TOP5 부품별 검사공정 비교 (각 부품당 가압검사+제조품질 = 5*2)
            )

            # 가시성 설정
            visibility_main = [True, True] + [False] * (
                total_bar_traces + total_line_traces + total_comparison_traces
            )  # 전체분포: 가압검사 + 제조품질
            visibility_bar = (
                [False, False]
                + [True] * total_bar_traces
                + [False] * total_line_traces
                + [False] * total_comparison_traces
            )  # 분기별
            visibility_line = (
                [False] * (total_main_traces + total_bar_traces)
                + [True] * total_line_traces
                + [False] * total_comparison_traces
            )  # 월별
            visibility_comparison = [False] * (
                total_main_traces + total_bar_traces + total_line_traces
            ) + [
                True
            ] * total_comparison_traces  # 부품별 검사공정 비교

            fig_parts.update_layout(
                title="🔧 공통 부품별 전체 분포 TOP10 (통합분석)",
                height=500,
                template="plotly_white",
                font=dict(family="Malgun Gothic", size=12),
                xaxis=dict(
                    title="부품명", visible=True, showgrid=True, tickangle=45
                ),  # 막대차트가 기본이므로 축 표시
                yaxis=dict(title="불량 건수", visible=True, showgrid=True),
                updatemenus=[
                    {
                        "buttons": [
                            {
                                "label": "전체 분포",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_main},
                                    {
                                        "title": "🔧 공통 부품별 전체 분포 TOP10 (통합분석)",
                                        "xaxis": {
                                            "title": "부품명",
                                            "visible": True,
                                            "showgrid": True,
                                            "tickangle": 45,
                                        },
                                        "yaxis": {
                                            "title": "불량 건수",
                                            "visible": True,
                                            "showgrid": True,
                                        },
                                    },
                                ],
                            },
                            {
                                "label": "분기별 비교 (TOP5)",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_bar},
                                    {
                                        "title": "🔧 공통 부품별 분기별 비교 TOP5 (통합분석)",
                                        "xaxis": {
                                            "title": "분기",
                                            "visible": True,
                                            "showgrid": True,
                                        },
                                        "yaxis": {
                                            "title": "불량 건수",
                                            "visible": True,
                                            "showgrid": True,
                                        },
                                    },
                                ],
                            },
                            {
                                "label": "월별 추이 (TOP3)",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_line},
                                    {
                                        "title": "🔧 공통 부품별 월별 추이 TOP3 (통합분석)",
                                        "xaxis": {
                                            "title": "월",
                                            "visible": True,
                                            "showgrid": True,
                                        },
                                        "yaxis": {
                                            "title": "불량 건수",
                                            "visible": True,
                                            "showgrid": True,
                                        },
                                    },
                                ],
                            },
                            {
                                "label": "부품별 검사공정 비교 (TOP5)",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_comparison},
                                    {
                                        "title": "🔧 부품별 검사공정 비교 TOP5 (월별 추이)",
                                        "xaxis": {
                                            "title": "월",
                                            "visible": True,
                                            "showgrid": True,
                                        },
                                        "yaxis": {
                                            "title": "불량 건수",
                                            "visible": True,
                                            "showgrid": True,
                                        },
                                    },
                                ],
                            },
                        ],
                        "direction": "down",
                        "showactive": True,
                        "x": 0.85,
                        "xanchor": "left",
                        "y": 1.15,
                        "yanchor": "top",
                    }
                ],
                margin=dict(l=50, r=50, t=120, b=50),
            )

            # 2. 공통 조치유형별 전체분포 차트
            pressure_actions = (
                pressure_df["상세조치내용"].value_counts()
                if "상세조치내용" in pressure_df.columns
                else pd.Series()
            )
            quality_actions = (
                quality_df["상세조치내용"].value_counts()
                if "상세조치내용" in quality_df.columns
                else pd.Series()
            )

            # 전체 조치유형별 통합 카운트
            all_actions = (
                pd.concat([pressure_actions, quality_actions])
                .groupby(level=0)
                .sum()
                .sort_values(ascending=False)
            )

            # 조치유형별 상세 데이터
            action_detail_data = []
            for action in all_actions.index:
                pressure_count = pressure_actions.get(action, 0)
                quality_count = quality_actions.get(action, 0)
                total_count = pressure_count + quality_count

                action_detail_data.append(
                    {
                        "조치유형": action,
                        "가압검사": pressure_count,
                        "제조품질": quality_count,
                        "전체": total_count,
                        "비율": (total_count / all_actions.sum()) * 100,
                    }
                )

            # 조치유형별 통합 차트 생성 (드롭다운 메뉴)
            fig_actions = go.Figure()

            # 1. 전체 분포 파이차트 (기존과 동일)
            action_names = [item["조치유형"] for item in action_detail_data]
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

            fig_actions.add_trace(
                go.Pie(
                    labels=action_names,
                    values=[item["전체"] for item in action_detail_data],
                    hole=0.3,
                    marker=dict(colors=colors[: len(action_detail_data)]),
                    textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>"
                    + "전체: %{value}건<br>"
                    + "비율: %{percent}<br>"
                    + "<extra></extra>",
                    visible=True,
                    showlegend=True,
                )
            )

            # 2. 분기별 비교 차트 (TOP5 조치유형)
            top5_actions = action_names[:5]  # TOP5만 선택
            colors_bar = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

            for i, action in enumerate(top5_actions):
                # 가압검사 + 제조품질 분기별 합계
                pressure_quarterly_action = (
                    pressure_df[pressure_df["상세조치내용"] == action]
                    .groupby("발생분기")
                    .size()
                    if "발생분기" in pressure_df.columns
                    else pd.Series()
                )
                quality_quarterly_action = (
                    quality_df[quality_df["상세조치내용"] == action]
                    .groupby("발생분기")
                    .size()
                    if "발생분기" in quality_df.columns
                    else pd.Series()
                )

                combined_quarterly_action = (
                    pd.concat([pressure_quarterly_action, quality_quarterly_action])
                    .groupby(level=0)
                    .sum()
                )

                # 분기 데이터 정렬
                quarters = sorted(
                    list(
                        set(
                            list(pressure_df["발생분기"].dropna())
                            + list(quality_df["발생분기"].dropna())
                        )
                    )
                )
                quarter_names = []
                for quarter in quarters:
                    quarter_str = str(quarter)
                    try:
                        year = quarter_str[:4]
                        q_num = quarter_str[-1]
                        quarter_names.append(f"{year}년 {q_num}분기")
                    except:
                        quarter_names.append(quarter_str)

                quarterly_values = []
                for quarter in quarters:
                    quarterly_values.append(combined_quarterly_action.get(quarter, 0))

                # 각 분기별로 해당 조치유형의 주요부품 TOP5 추출
                hover_texts = []
                for j, quarter in enumerate(quarters):
                    # 해당 분기 + 조치유형의 부품별 데이터
                    pressure_quarter_parts = (
                        pressure_df[
                            (pressure_df["발생분기"] == quarter)
                            & (pressure_df["상세조치내용"] == action)
                        ]["부품명"].value_counts()
                        if "발생분기" in pressure_df.columns
                        else pd.Series()
                    )

                    quality_quarter_parts = (
                        quality_df[
                            (quality_df["발생분기"] == quarter)
                            & (quality_df["상세조치내용"] == action)
                        ]["부품명"].value_counts()
                        if "발생분기" in quality_df.columns
                        else pd.Series()
                    )

                    # 통합 부품 카운트
                    combined_quarter_parts = (
                        pd.concat([pressure_quarter_parts, quality_quarter_parts])
                        .groupby(level=0)
                        .sum()
                        .sort_values(ascending=False)
                    )

                    # TOP5 부품 추출
                    top5_parts = combined_quarter_parts.head(5)
                    if len(top5_parts) > 0:
                        parts_info = "<br>".join(
                            [
                                f"• {part}: {count}건"
                                for part, count in top5_parts.items()
                            ]
                        )
                        hover_text = f"<b>{action}</b><br>{quarter_names[j]}<br>총 {quarterly_values[j]}건<br><br>주요부품 TOP5:<br>{parts_info}"
                    else:
                        hover_text = f"<b>{action}</b><br>{quarter_names[j]}<br>총 {quarterly_values[j]}건<br><br>데이터 없음"

                    hover_texts.append(hover_text)

                fig_actions.add_trace(
                    go.Bar(
                        name=action,
                        x=quarter_names,
                        y=quarterly_values,
                        marker_color=colors_bar[i % len(colors_bar)],
                        text=[
                            f"{val}건" if val > 0 else "" for val in quarterly_values
                        ],
                        textposition="outside",
                        hovertemplate="%{customdata}<extra></extra>",
                        customdata=hover_texts,
                        visible=False,  # 기본 숨김
                        showlegend=True,
                    )
                )

            # 3. 월별 추이 차트 (TOP3 조치유형)
            top3_actions = action_names[:3]  # TOP3만 선택
            colors_line = ["#FF6B6B", "#4ECDC4", "#45B7D1"]

            # 월 데이터 준비
            months = sorted(
                list(
                    set(
                        list(pressure_df["발생월"].dropna())
                        + list(quality_df["발생월"].dropna())
                    )
                )
            )
            month_names = []
            for month in months:
                month_str = str(month)
                try:
                    year = month_str[:4]
                    month_num = month_str[-2:]
                    month_names.append(f"{year}년 {month_num}월")
                except:
                    month_names.append(month_str)

            for i, action in enumerate(top3_actions):
                # 가압검사 + 제조품질 월별 합계
                pressure_monthly_action = (
                    pressure_df[pressure_df["상세조치내용"] == action]
                    .groupby("발생월")
                    .size()
                    if "발생월" in pressure_df.columns
                    else pd.Series()
                )
                quality_monthly_action = (
                    quality_df[quality_df["상세조치내용"] == action]
                    .groupby("발생월")
                    .size()
                    if "발생월" in quality_df.columns
                    else pd.Series()
                )

                combined_monthly_action = (
                    pd.concat([pressure_monthly_action, quality_monthly_action])
                    .groupby(level=0)
                    .sum()
                )

                # 각 월별 hover 정보 구성
                hover_texts = []
                x_values = []
                y_values = []

                for j, month in enumerate(months):
                    month_name = month_names[j]
                    x_values.append(month_name)

                    monthly_count = combined_monthly_action.get(month, 0)
                    y_values.append(monthly_count)

                    # 해당 월, 해당 조치유형의 상세 정보
                    month_pressure_df = pressure_df[
                        (pressure_df["발생월"] == month)
                        & (pressure_df["상세조치내용"] == action)
                    ]
                    month_quality_df = quality_df[
                        (quality_df["발생월"] == month)
                        & (quality_df["상세조치내용"] == action)
                    ]

                    # 부품명 상위 3개 추출
                    pressure_parts = (
                        month_pressure_df["부품명"].dropna().value_counts().head(3)
                        if "부품명" in month_pressure_df.columns
                        else pd.Series()
                    )
                    quality_parts = (
                        month_quality_df["부품명"].dropna().value_counts().head(3)
                        if "부품명" in month_quality_df.columns
                        else pd.Series()
                    )
                    combined_parts = (
                        pd.concat([pressure_parts, quality_parts])
                        .groupby(level=0)
                        .sum()
                        .head(3)
                    )

                    # 불량위치 상위 3개 추출
                    pressure_locations = (
                        month_pressure_df["불량위치"].dropna().unique()[:3]
                        if "불량위치" in month_pressure_df.columns
                        else []
                    )
                    quality_locations = (
                        month_quality_df["불량위치"].dropna().unique()[:3]
                        if "불량위치" in month_quality_df.columns
                        else []
                    )
                    combined_locations = list(
                        set(list(pressure_locations) + list(quality_locations))
                    )[:3]

                    hover_text = f"<b>{month_name}: {action}</b><br>불량 건수: {monthly_count}건<br><br>"
                    if len(combined_parts) > 0:
                        hover_text += "<b>주요 부품명:</b><br>"
                        for idx, (part, count) in enumerate(combined_parts.items(), 1):
                            hover_text += f"{idx}. {part} ({count}건)<br>"
                        hover_text += "<br>"
                    if len(combined_locations) > 0:
                        hover_text += "<b>주요 불량위치:</b><br>"
                        for idx, location in enumerate(combined_locations, 1):
                            hover_text += f"{idx}. {location}<br>"

                    hover_texts.append(hover_text)

                fig_actions.add_trace(
                    go.Scatter(
                        name=action,
                        x=x_values,
                        y=y_values,
                        mode="lines+markers",
                        line=dict(color=colors_line[i % len(colors_line)], width=3),
                        marker=dict(size=8, color=colors_line[i % len(colors_line)]),
                        text=[f"{val}건" if val > 0 else "" for val in y_values],
                        textposition="top center",
                        hovertemplate="%{hovertext}<extra></extra>",
                        hovertext=hover_texts,
                        visible=False,  # 기본 숨김
                        showlegend=True,
                    )
                )

            # 드롭다운 메뉴 설정
            total_pie_traces = 1  # 파이차트
            total_bar_traces = 5  # TOP5 조치유형 (분기별)
            total_line_traces = 3  # TOP3 조치유형 (월별)

            # 가시성 설정
            visibility_pie = [True] + [False] * (
                total_bar_traces + total_line_traces
            )  # 전체분포 파이차트
            visibility_bar = (
                [False] + [True] * total_bar_traces + [False] * total_line_traces
            )  # 분기별
            visibility_line = [False] * (total_pie_traces + total_bar_traces) + [
                True
            ] * total_line_traces  # 월별

            fig_actions.update_layout(
                title="⚙️ 공통 조치유형별 전체분포 (통합분석)",
                height=500,
                template="plotly_white",
                font=dict(family="Malgun Gothic", size=12),
                xaxis=dict(
                    visible=False, showgrid=False, zeroline=False
                ),  # 파이차트가 기본이므로 축 숨김
                yaxis=dict(visible=False, showgrid=False, zeroline=False),
                updatemenus=[
                    {
                        "buttons": [
                            {
                                "label": "전체 분포",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_pie},
                                    {
                                        "title": "⚙️ 공통 조치유형별 전체분포 (통합분석)",
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
                            },
                            {
                                "label": "분기별 비교 (TOP5)",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_bar},
                                    {
                                        "title": "⚙️ 공통 조치유형별 분기별 비교 TOP5 (통합분석)",
                                        "xaxis": {
                                            "title": "분기",
                                            "visible": True,
                                            "showgrid": True,
                                        },
                                        "yaxis": {
                                            "title": "불량 건수",
                                            "visible": True,
                                            "showgrid": True,
                                        },
                                    },
                                ],
                            },
                            {
                                "label": "월별 추이 (TOP3)",
                                "method": "update",
                                "args": [
                                    {"visible": visibility_line},
                                    {
                                        "title": "⚙️ 공통 조치유형별 월별 추이 TOP3 (통합분석)",
                                        "xaxis": {
                                            "title": "월",
                                            "visible": True,
                                            "showgrid": True,
                                        },
                                        "yaxis": {
                                            "title": "불량 건수",
                                            "visible": True,
                                            "showgrid": True,
                                        },
                                    },
                                ],
                            },
                        ],
                        "direction": "down",
                        "showactive": True,
                        "x": 0.85,
                        "xanchor": "left",
                        "y": 1.15,
                        "yanchor": "top",
                    }
                ],
                margin=dict(l=50, r=50, t=120, b=50),
            )

            logger.info(
                f"✅ 통합 공통 분석 차트 생성 완료 - 부품 TOP10: {len(part_detail_data)}개, 조치유형: {len(action_detail_data)}개"
            )

            return fig_parts, fig_actions

        except Exception as e:
            logger.error(f"❌ 통합 공통 분석 차트 생성 실패: {e}")
            # 빈 차트 반환
            empty_fig = go.Figure()
            empty_fig.add_trace(go.Bar(x=["오류"], y=[1], text=["차트 생성 실패"]))
            empty_fig.update_layout(title="차트 생성 오류", height=500)
            return empty_fig, empty_fig

    def _get_html_template(self) -> str:
        """HTML 템플릿 반환 (새로운 디자인)"""
        return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GST 통합 검사 분석 대시보드</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4rem 0;
            text-align: center;
            position: relative;
            overflow: visible;
            min-height: 200px;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(255,255,255,0.1) 25%, transparent 25%), 
                        linear-gradient(-45deg, rgba(255,255,255,0.1) 25%, transparent 25%), 
                        linear-gradient(45deg, transparent 75%, rgba(255,255,255,0.1) 75%), 
                        linear-gradient(-45deg, transparent 75%, rgba(255,255,255,0.1) 75%);
            background-size: 30px 30px;
            background-position: 0 0, 0 15px, 15px -15px, -15px 0px;
            opacity: 0.3;
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
            padding-bottom: 3rem;
        }}
        
        .timestamp {{
            margin-top: 1.5rem;
            font-size: 1rem;
            opacity: 0.9;
            padding: 0.8rem 1.5rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 25px;
            display: inline-block;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .timestamp-label {{
            font-weight: 500;
            margin-right: 0.5rem;
        }}
        
        .timestamp-value {{
            font-weight: 600;
            color: #ffd700;
        }}
        
        .header h1 {{
            font-size: 2.8rem;
            font-weight: 300;
            letter-spacing: 3px;
            margin-bottom: 0.5rem;
            position: relative;
            cursor: pointer;
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .kpi-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: -3rem auto 3rem auto;
            max-width: 1200px;
            padding: 0 20px;
            position: relative;
            z-index: 2;
        }}
        
        .kpi-card {{
            background: white;
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.8);
            position: relative;
        }}
        
        .kpi-card.tooltip-trigger {{
            cursor: help;
        }}
        
        .kpi-card.tooltip-trigger:hover {{
            border-color: rgba(102, 126, 234, 0.5);
        }}
        
        .kpi-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .kpi-value {{
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .kpi-label {{
            font-size: 1.1rem;
            color: #666;
            font-weight: 500;
            letter-spacing: 1px;
        }}
        
        .tabs {{
            display: flex;
            justify-content: center;
            margin: 2rem 0;
            gap: 1rem;
        }}
        
        .tab-button {{
            background: white;
            border: 2px solid #e1e8ed;
            padding: 1rem 2.5rem;
            border-radius: 50px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            color: #666;
            position: relative;
            overflow: hidden;
        }}
        
        .tab-button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transition: left 0.3s ease;
            z-index: 0;
        }}
        
        .tab-button span {{
            position: relative;
            z-index: 1;
        }}
        
        .tab-button:hover {{
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }}
        
        .tab-button:hover::before {{
            left: 0;
        }}
        
        .tab-button:hover {{
            color: white;
        }}
        
        .tab-button.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }}
        
        .tab-button.active::before {{
            left: 0;
        }}
        
        .tab-content {{
            display: none;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 25px;
            padding: 2.5rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.8);
        }}
        
        .tab-content.active {{
            display: block;
            animation: fadeInUp 0.5s ease;
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .chart-container {{
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border: 1px solid rgba(230, 230, 230, 0.8);
            min-height: 500px;
            position: relative;
        }}
        
        .chart-container .plotly-graph-div {{
            width: 100% !important;
            height: auto !important;
        }}
        
        .chart-container:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.12);
            border-color: rgba(102, 126, 234, 0.3);
        }}
        
        .update-time {{
            text-align: center;
            color: #888;
            margin-top: 3rem;
            font-size: 0.95rem;
            padding: 1rem;
            background: rgba(255,255,255,0.6);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(230, 230, 230, 0.8);
            transition: all 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}
        
        .stat-label {{
            color: #666;
            font-weight: 500;
            font-size: 0.95rem;
        }}
        
        h2 {{
            text-align: center;
            color: #333;
            margin-bottom: 2rem;
            font-size: 1.8rem;
            font-weight: 300;
        }}
        
        h3 {{
            text-align: center;
            color: #555;
            margin: 2rem 0 1rem 0;
            font-size: 1.4rem;
            font-weight: 400;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 0.5rem;
        }}
        
        /* 툴팁 스타일 - 최고 우선순위 */
        .tooltip {{
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.95);
            color: white;
            padding: 20px;
            border-radius: 12px;
            font-size: 13px;
            line-height: 1.8;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            z-index: 99999 !important;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            pointer-events: none;
            min-width: 1400px;
            max-width: 1600px;
            width: 90vw;
            white-space: normal;
        }}
        
        .tooltip.show {{
            opacity: 1;
            visibility: visible;
            transform: translateX(-50%) translateY(10px);
            z-index: 99999 !important;
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
            gap: 40px;
            justify-content: center;
            align-items: flex-start;
            width: 100%;
        }}
        
        .tooltip-section {{
            flex: 1;
            max-width: 700px;
            min-width: 600px;
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
            table-layout: fixed;
        }}
        
        .tooltip-table th {{
            background: rgba(135, 206, 235, 0.2);
            color: #87ceeb;
            padding: 10px 8px;
            font-size: 12px;
            font-weight: bold;
            text-align: center;
            border-bottom: 1px solid #555;
        }}
        
        .tooltip-table td {{
            padding: 10px 8px;
            font-size: 12px;
            border-bottom: 1px solid #333;
            vertical-align: top;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        
        .tooltip-table td:first-child {{
            font-weight: bold;
            color: #ffd700;
            text-align: center;
            width: 15%;
            min-width: 80px;
        }}
        
        .tooltip-table td:last-child {{
            color: #ffeaa7;
            font-style: italic;
            width: 35%;
            text-align: center;
            line-height: 1.6;
        }}
        
        .tooltip-table td:nth-child(2) {{
            width: 50%;
            line-height: 1.7;
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

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .kpi-section {{
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1rem;
                margin: -2rem auto 2rem auto;
            }}
            
            .kpi-value {{
                font-size: 2.5rem;
            }}
            
            .tabs {{
                flex-wrap: wrap;
                gap: 0.5rem;
            }}
            
            .tab-button {{
                padding: 0.8rem 1.5rem;
                font-size: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
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
            <p>{current_year}년 통합 검사(가압검사 + 제조품질) 불량 현황 및 분석</p>
            <div class="timestamp">
                <span class="timestamp-label">📅 마지막 업데이트:</span>
                <span class="timestamp-value">{timestamp}</span>
            </div>
        </div>
    </div>
    

    
    <div class="container">
        <div class="tabs">
            <button class="tab-button active" onclick="showTab('pressure')"><span>가압검사</span></button>
            <button class="tab-button" onclick="showTab('quality')"><span>제조품질</span></button>
            <button class="tab-button" onclick="showTab('integrated')"><span>통합비교</span></button>
        </div>
        
        <div id="pressure-tab" class="tab-content active">
            <!-- KPI 카드 섹션 (가압검사용) -->
            <div class="kpi-section">
                <div class="kpi-card">
                    <div class="kpi-value">{pressure_total_defects}</div>
                    <div class="kpi-label">총 불량 건수</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{pressure_total_ch}</div>
                    <div class="kpi-label">총 검사 CH수</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{pressure_avg_rate}%</div>
                    <div class="kpi-label">평균 불량률</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{supplier_count}</div>
                    <div class="kpi-label">주요 외주사</div>
                </div>
            </div>
            
            <div class="chart-container">{monthly_html}</div>
            <div class="chart-container">{action_integrated_html}</div>
            <div class="chart-container">{supplier_integrated_html}</div>
            <div class="chart-container">{part_integrated_html}</div>
            <div class="chart-container">{part_monthly_html}</div>
        </div>
        
        <div id="quality-tab" class="tab-content">
            <!-- KPI 카드 섹션 (제조품질용) -->
            <div class="kpi-section">
                <div class="kpi-card">
                    <div class="kpi-value">{quality_total_defects}</div>
                    <div class="kpi-label">총 불량 건수</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{quality_total_ch}</div>
                    <div class="kpi-label">총 검사 CH수</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{quality_avg_rate:.1f}%</div>
                    <div class="kpi-label">평균 불량률</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{quality_supplier_count}</div>
                    <div class="kpi-label">주요 외주사</div>
                </div>
            </div>
            
            <div class="chart-container">{quality_monthly_html}</div>
            <div class="chart-container">{quality_action_html}</div>
            <div class="chart-container">{quality_supplier_html}</div>
            <div class="chart-container">{quality_part_integrated_html}</div>
            <div class="chart-container">{quality_part_html}</div>
        </div>
        
        <div id="integrated-tab" class="tab-content">
            <h2>🔄 통합 비교 분석</h2>
            
            <div class="chart-container">{integrated_monthly_html}</div>
            <div class="chart-container">{integrated_kpi_html}</div>
            
            <h3>📊 공정 표준화를 위한 통합 분석</h3>
            <div class="chart-container">{integrated_parts_html}</div>
            <div class="chart-container">{integrated_actions_html}</div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // 탭 전환 시 차트 리사이즈
            setTimeout(() => {{
                resizeAllCharts();
            }}, 100);
        }}
        
        function resizeAllCharts() {{
            // 모든 Plotly 차트 리사이즈
            document.querySelectorAll('.plotly-graph-div').forEach(chart => {{
                if (window.Plotly) {{
                    window.Plotly.Plots.resize(chart);
                }}
            }});
        }}
        
        // 페이지 로드 완료 후 차트 리사이즈
        window.addEventListener('load', function() {{
            setTimeout(() => {{
                resizeAllCharts();
            }}, 500);
        }});
        
        // 윈도우 리사이즈 시 차트 리사이즈
        window.addEventListener('resize', function() {{
            setTimeout(() => {{
                resizeAllCharts();
            }}, 100);
        }});
        
        // DOM이 로드된 후에도 한번 더 실행
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(() => {{
                resizeAllCharts();
            }}, 1000);
        }});
        
        // 툴팁 기능 (메인 타이틀에 적용 - 최고 우선순위)
        document.addEventListener('DOMContentLoaded', function() {{
            const title = document.getElementById('dashboard-title');
            const tooltip = document.getElementById('title-tooltip');
            let showTimeout, hideTimeout;
            
            if (title && tooltip) {{
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
            }}
        }});
    </script>
</body>
</html>
"""
