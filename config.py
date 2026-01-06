import os
from dataclasses import dataclass
from typing import List

# .env 파일 로드
try:
    from dotenv import load_dotenv

    load_dotenv()  # .env 파일의 환경변수를 자동으로 로드
except ImportError:
    # dotenv가 없으면 패스 (선택적 의존성)
    pass

# GitHub 업로드 비활성화 플래그 (테스트용)
DISABLE_GITHUB_UPLOAD = True


@dataclass
class GitHubConfig:
    """GitHub 업로드 설정"""

    username_1: str = "isolhsolfafa"
    repo_1: str = "gst-factory-display"
    branch_1: str = "main"
    token_1: str = os.getenv("GH_TOKEN_1", "")  # GitHub Token 1 (환경변수 필수)

    username_2: str = "isolhsolfafa"
    repo_2: str = "gst-factory"
    branch_2: str = "main"
    token_2: str = os.getenv("GH_TOKEN_2", "")  # GitHub Token 2 (환경변수 필수)

    html_filename: str = "public/pie_defect.html"  # React public 폴더
    json_filename: str = "public/data.json"  # React public 폴더
    html_filename_2: str = "public/pie_defect.html"  # React public 폴더
    json_filename_2: str = "public/data.json"  # React public 폴더


@dataclass
class GoogleSheetsConfig:
    """Google Sheets 설정"""

    service_account_file: str = (
        "credentials/gst-manegemnet-e6c4e7bd79e2.json"  # 새로운 service key로 변경
    )
    spreadsheet_id: str = "19dkwKNW6VshCg3wTemzmbbQlbATfq6brAWluaps1Rm0"
    sheet_name: str = "월생산물량"
    fallback_sheet_name: str = "8월생산물량"
    scopes: List[str] = None

    def __post_init__(self):
        if self.scopes is None:
            self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]


@dataclass
class TeamsConfig:
    """Microsoft Teams/SharePoint API 설정"""

    tenant_id: str = os.getenv("TEAMS_TENANT_ID", "")  # Azure AD 테넌트 ID
    client_id: str = os.getenv("TEAMS_CLIENT_ID", "")  # 앱 등록 클라이언트 ID
    client_secret: str = os.getenv("TEAMS_CLIENT_SECRET", "")  # 클라이언트 시크릿

    # Teams 채널 정보
    team_id: str = os.getenv("TEAMS_TEAM_ID", "")  # Teams 팀 ID
    channel_id: str = os.getenv("TEAMS_CHANNEL_ID", "")  # 채널 ID

    # SharePoint 정보 (Teams 파일은 SharePoint에 저장됨)
    site_id: str = os.getenv("TEAMS_SITE_ID", "")  # SharePoint 사이트 ID
    drive_id: str = os.getenv("TEAMS_DRIVE_ID", "")  # 드라이브 ID

    # 파일 정보 (연도별 파일명)
    excel_file_name: str = "▶2026年 검사 통합 Sheet.xlsm"  # Teams에서 공유되는 엑셀 파일명
    worksheet_names: List[str] = None  # 워크시트명 리스트

    # API 스코프
    scopes: List[str] = None

    def __post_init__(self):
        if self.worksheet_names is None:
            self.worksheet_names = [
                "가압 불량내역",
                "제조품질 불량내역",
            ]  # 두 개의 워크시트
        if self.scopes is None:
            self.scopes = ["https://graph.microsoft.com/.default"]


@dataclass
class DataConfig:
    """데이터 관련 설정"""

    csv_file_path: str = "data/통합본.csv"  # 상대경로로 변경
    required_columns: List[str] = None
    exclude_keywords: List[str] = None

    def __post_init__(self):
        if self.required_columns is None:
            self.required_columns = [
                "제품명",
                "부품명",
                "상세불량내용",
                "대분류",
                "중분류",
                "검출단계",
                "비고",
                "발생일",
            ]
        if self.exclude_keywords is None:
            self.exclude_keywords = ["He미보증"]


@dataclass
class MLConfig:
    """머신러닝 모델 설정"""

    test_size: float = 0.2
    random_state: int = None  # None = 동적, 42 = 고정
    max_df: float = 0.85
    min_df: int = 2
    top_keywords_count: int = 10
    top_predictions_count: int = 5
    sample_size: int = 10  # 기존 코드와 동일하게 복원
    min_weight: float = 0.05
    max_weight: float = 0.40


@dataclass
class LogConfig:
    """로깅 설정"""

    log_file: str = "logs/factory_ml.log"
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    log_level: str = "INFO"


# 전역 설정 객체들
github_config = GitHubConfig()
sheets_config = GoogleSheetsConfig()
teams_config = TeamsConfig()
data_config = DataConfig()
ml_config = MLConfig()
log_config = LogConfig()

# 테스트 모드 설정
TEST_MODE = False  # 실제 업로드 모드

# GitHub 업로드 완전 비활성화 설정
DISABLE_GITHUB_UPLOAD = False  # GitHub 업로드 활성화

# 한국어 불용어
KOREAN_STOP_WORDS = [
    "이다",
    "있",
    "하",
    "것",
    "들",
    "그",
    "되",
    "수",
    "이",
    "보",
    "않",
    "없",
    "나",
    "사람",
    "주",
    "아",
    "등",
    "같",
    "우리",
    "때",
    "년",
    "가",
    "한",
    "지",
    "대하",
    "오",
    "말",
    "일",
    "그렇",
    "위하",
]
