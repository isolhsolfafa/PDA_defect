"""
Base Visualizer Module

모든 차트 생성기의 공통 기능을 제공하는 기본 클래스
- 색상 생성
- 로거 설정
- 데이터 로딩 유틸리티
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from typing import Dict
import colorsys

from data.teams_loader import TeamsDataLoader
from utils.logger import setup_logger, flush_log

logger = setup_logger(__name__)


class BaseVisualizer:
    """시각화 기본 클래스"""

    def __init__(self):
        """초기화"""
        try:
            self.teams_loader = TeamsDataLoader()
            self.use_mock_data = False
        except Exception as e:
            logger.warning(f"⚠️ Teams 연동 실패, Mock 데이터 사용: {e}")
            self.teams_loader = None
            self.use_mock_data = True

        self.analysis_data = None
        self.defect_data = None
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
            colors = []
            for i in range(count):
                hue = i / count
                rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
                hex_color = "#{:02x}{:02x}{:02x}".format(
                    int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
                )
                colors.append(hex_color)
            return colors

    def _load_excel_data(self, sheet_name: str) -> pd.DataFrame:
        """엑셀 시트 데이터 로드 공통 함수"""
        try:
            if self.use_mock_data:
                logger.info(f"📊 Mock {sheet_name} 데이터 사용...")
                return self._generate_mock_data(sheet_name)

            logger.info(f"📊 {sheet_name} 워크시트 데이터 로드 시작...")

            # Teams에서 파일 다운로드
            files = self.teams_loader._get_teams_files()
            excel_file = self.teams_loader._find_excel_file(files)
            file_content = self.teams_loader._download_excel_file(excel_file)

            # 시트 로드
            excel_buffer = io.BytesIO(file_content)
            df = pd.read_excel(excel_buffer, sheet_name=sheet_name)

            logger.info(f"✅ {sheet_name} 데이터 로드 완료: {df.shape}")
            flush_log(logger)

            return df

        except Exception as e:
            logger.error(f"❌ {sheet_name} 데이터 로드 실패: {e}")
            flush_log(logger)
            raise

    def _generate_mock_data(self, sheet_name: str) -> pd.DataFrame:
        """Mock 데이터 생성"""
        if sheet_name == "가압 불량분석":
            return self._generate_mock_analysis_data()
        elif sheet_name == "가압 불량내역":
            return self._generate_mock_defect_data()
        elif sheet_name == "제조품질 불량분석":
            return self._generate_mock_quality_analysis_data()
        elif sheet_name == "제조품질 불량내역":
            return self._generate_mock_quality_defect_data()
        else:
            raise ValueError(f"Unknown sheet name: {sheet_name}")

    def _generate_mock_analysis_data(self) -> pd.DataFrame:
        """Mock 불량분석 데이터 생성"""
        # 여기에 Mock 데이터 생성 로직
        return pd.DataFrame()

    def _generate_mock_defect_data(self) -> pd.DataFrame:
        """Mock 불량내역 데이터 생성"""
        # 여기에 Mock 데이터 생성 로직
        return pd.DataFrame()

    def _generate_mock_quality_analysis_data(self) -> pd.DataFrame:
        """Mock 제조품질 불량분석 데이터 생성"""
        # 여기에 Mock 데이터 생성 로직
        return pd.DataFrame()

    def _generate_mock_quality_defect_data(self) -> pd.DataFrame:
        """Mock 제조품질 불량내역 데이터 생성"""
        import random
        from datetime import datetime, timedelta

        # Mock 데이터 생성
        mock_data = []
        actions = ["재작업", "교체", "조정", "검사강화", "공정개선"]
        parts = ["케이스", "커버", "핀", "스위치", "센서"]
        suppliers = ["TMS(기구)", "C&A", "P&S"]

        start_date = datetime(2025, 1, 1)

        for i in range(50):  # 50개 Mock 데이터
            random_days = random.randint(0, 200)  # 올해 기간
            date = start_date + timedelta(days=random_days)

            mock_data.append(
                {
                    "발생일": date.strftime("%Y-%m-%d"),
                    "상세조치내용": random.choice(actions),
                    "부품명": random.choice(parts),
                    "외주사": random.choice(suppliers),
                    "불량내용": f"Mock 불량내용 {i+1}",
                    "조치결과": "Mock 조치결과",
                }
            )

        return pd.DataFrame(mock_data)
