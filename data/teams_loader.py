import requests
import pandas as pd
import io
from typing import Dict, List, Optional
from msal import ConfidentialClientApplication
import json
import urllib.parse

from config import teams_config
from utils.logger import setup_logger, flush_log

logger = setup_logger(__name__)


class TeamsDataLoader:
    """Microsoft Teams에서 엑셀 파일을 가져오는 데이터 로더"""

    def __init__(self):
        self.config = teams_config
        self.access_token = None
        self.app = None
        self._initialize_msal_app()

    def _initialize_msal_app(self):
        """MSAL 앱 초기화"""
        try:
            self.app = ConfidentialClientApplication(
                client_id=self.config.client_id,
                client_credential=self.config.client_secret,
                authority=f"https://login.microsoftonline.com/{self.config.tenant_id}",
            )
            logger.info("✅ MSAL 앱 초기화 성공")
            flush_log(logger)
        except Exception as e:
            logger.error(f"❌ MSAL 앱 초기화 실패: {e}")
            flush_log(logger)
            raise

    def _get_access_token(self) -> str:
        """Microsoft Graph API 액세스 토큰 획득"""
        try:
            # 클라이언트 자격 증명 플로우 사용
            result = self.app.acquire_token_for_client(scopes=self.config.scopes)

            if "access_token" in result:
                self.access_token = result["access_token"]
                logger.info("✅ Microsoft Graph API 토큰 획득 성공")
                flush_log(logger)
                return self.access_token
            else:
                error_msg = result.get("error_description", "토큰 획득 실패")
                logger.error(f"❌ 토큰 획득 실패: {error_msg}")
                flush_log(logger)
                raise Exception(f"토큰 획득 실패: {error_msg}")

        except Exception as e:
            logger.error(f"❌ 액세스 토큰 획득 중 오류: {e}")
            flush_log(logger)
            raise

    def _get_teams_files(self) -> List[Dict]:
        """Teams 채널의 파일 목록 조회 (특정 경로 접근)"""
        try:
            if not self.access_token:
                self._get_access_token()

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            # 특정 경로의 파일에 접근: General/99.개인폴더/박승록/
            file_path = "General/99.개인폴더/박승록"
            target_filename = self.config.excel_file_name

            try:
                # 경로를 URL 인코딩
                encoded_path = urllib.parse.quote(file_path, safe="")

                # 그룹 드라이브의 특정 폴더 접근
                folder_url = f"https://graph.microsoft.com/v1.0/groups/{self.config.team_id}/drive/root:/{encoded_path}:/children"

                logger.info(f"📡 특정 폴더 접근 시도: {folder_url}")
                logger.info(f"📁 대상 경로: {file_path}")
                logger.info(f"📄 대상 파일: {target_filename}")
                flush_log(logger)

                response = requests.get(folder_url, headers=headers)
                response.raise_for_status()

                files_data = response.json()
                files = files_data.get("value", [])

                logger.info(f"✅ 특정 폴더의 파일 목록 조회 성공: {len(files)}개 파일")
                for file in files:
                    logger.info(
                        f"   - {file.get('name', 'Unknown')} ({file.get('size', 0)} bytes)"
                    )
                flush_log(logger)

                return files

            except Exception as specific_error:
                logger.warning(f"⚠️ 특정 폴더 접근 실패: {specific_error}")
                logger.info("📡 단계별 폴더 접근을 시도합니다...")
                flush_log(logger)

                # 백업: 단계별로 폴더 접근
                return self._search_file_step_by_step(headers, target_filename)

        except Exception as e:
            logger.error(f"❌ Teams 파일 목록 조회 실패: {e}")
            flush_log(logger)
            raise

    def _search_file_step_by_step(
        self, headers: Dict, target_filename: str
    ) -> List[Dict]:
        """단계별로 폴더 접근하여 파일 검색"""
        try:
            # 1. 루트 폴더에서 General 폴더 찾기
            root_url = f"https://graph.microsoft.com/v1.0/groups/{self.config.team_id}/drive/root/children"

            logger.info(f"📡 루트 폴더 검색: {root_url}")
            flush_log(logger)

            response = requests.get(root_url, headers=headers)
            response.raise_for_status()

            root_data = response.json()
            root_items = root_data.get("value", [])

            # General 폴더 찾기
            general_folder = None
            for item in root_items:
                if item.get("name") == "General" and item.get("folder"):
                    general_folder = item
                    break

            if not general_folder:
                logger.warning("⚠️ 'General' 폴더를 찾을 수 없습니다")
                return []

            # 2. General 폴더에서 99.개인폴더 찾기
            general_folder_id = general_folder["id"]
            general_url = f"https://graph.microsoft.com/v1.0/groups/{self.config.team_id}/drive/items/{general_folder_id}/children"

            logger.info(f"📡 General 폴더 검색: {general_url}")
            flush_log(logger)

            response = requests.get(general_url, headers=headers)
            response.raise_for_status()

            general_data = response.json()
            general_items = general_data.get("value", [])

            # 99.개인폴더 찾기
            personal_folder = None
            for item in general_items:
                if item.get("name") == "99.개인폴더" and item.get("folder"):
                    personal_folder = item
                    break

            if not personal_folder:
                logger.warning("⚠️ '99.개인폴더' 폴더를 찾을 수 없습니다")
                return []

            # 3. 99.개인폴더에서 박승록 폴더 찾기
            personal_folder_id = personal_folder["id"]
            personal_url = f"https://graph.microsoft.com/v1.0/groups/{self.config.team_id}/drive/items/{personal_folder_id}/children"

            logger.info(f"📡 99.개인폴더 검색: {personal_url}")
            flush_log(logger)

            response = requests.get(personal_url, headers=headers)
            response.raise_for_status()

            personal_data = response.json()
            personal_items = personal_data.get("value", [])

            # 박승록 폴더 찾기
            user_folder = None
            for item in personal_items:
                if item.get("name") == "박승록" and item.get("folder"):
                    user_folder = item
                    break

            if not user_folder:
                logger.warning("⚠️ '박승록' 폴더를 찾을 수 없습니다")
                return []

            # 4. 박승록 폴더 내용 확인
            user_folder_id = user_folder["id"]
            user_url = f"https://graph.microsoft.com/v1.0/groups/{self.config.team_id}/drive/items/{user_folder_id}/children"

            logger.info(f"📡 박승록 폴더 검색: {user_url}")
            flush_log(logger)

            response = requests.get(user_url, headers=headers)
            response.raise_for_status()

            user_data = response.json()
            user_items = user_data.get("value", [])

            logger.info(f"✅ 최종 폴더의 파일 목록 조회 성공: {len(user_items)}개 파일")
            for file in user_items:
                logger.info(
                    f"   - {file.get('name', 'Unknown')} ({file.get('size', 0)} bytes)"
                )
            flush_log(logger)

            return user_items

        except Exception as e:
            logger.error(f"❌ 단계별 파일 검색 실패: {e}")
            flush_log(logger)
            return []

    def _find_excel_file(self, files: List[Dict]) -> Optional[Dict]:
        """엑셀 파일 찾기"""
        try:
            target_file = None
            target_filename = self.config.excel_file_name

            # 1. 우선순위: 정확한 파일명으로 찾기
            for file in files:
                file_name = file.get("name", "")
                if file_name == target_filename:
                    target_file = file
                    logger.info(f"✅ 대상 파일 발견: {file_name}")
                    break

            # 2. 정확한 파일명을 찾지 못한 경우 패턴 매칭
            if not target_file:
                for file in files:
                    file_name = file.get("name", "")
                    if (
                        "검사 통합 Sheet" in file_name or "가압 통합 Sheet" in file_name
                    ) and file_name.endswith((".xlsm", ".xlsx")):
                        target_file = file
                        logger.warning(
                            f"⚠️ 정확한 파일명을 찾지 못하여 패턴 매칭으로 대체 파일 사용: {file_name}"
                        )
                        break

            if target_file:
                logger.info(f"✅ 대상 엑셀 파일 발견: {target_file['name']}")
                flush_log(logger)
                return target_file
            else:
                logger.warning(
                    f"⚠️ 대상 엑셀 파일을 찾을 수 없습니다: {target_filename}"
                )
                logger.info("📋 발견된 파일 목록:")
                for file in files:
                    logger.info(f"   - {file.get('name', 'Unknown')}")
                flush_log(logger)
                return None

        except Exception as e:
            logger.error(f"❌ 엑셀 파일 검색 중 오류: {e}")
            flush_log(logger)
            raise

    def _download_excel_file(self, file_info: Dict) -> bytes:
        """엑셀 파일 다운로드"""
        try:
            if not self.access_token:
                self._get_access_token()

            # 파일 다운로드 URL 생성 (그룹 드라이브용)
            file_id = file_info["id"]
            download_url = f"https://graph.microsoft.com/v1.0/groups/{self.config.team_id}/drive/items/{file_id}/content"

            headers = {"Authorization": f"Bearer {self.access_token}"}

            logger.info(f"📥 파일 다운로드 시작: {download_url}")
            flush_log(logger)

            response = requests.get(download_url, headers=headers)
            response.raise_for_status()

            logger.info(f"✅ 엑셀 파일 다운로드 성공: {len(response.content)} bytes")
            flush_log(logger)

            return response.content

        except Exception as e:
            logger.error(f"❌ 엑셀 파일 다운로드 실패: {e}")
            flush_log(logger)
            raise

    def load_defect_data_from_teams(self) -> pd.DataFrame:
        """Teams에서 불량 데이터 로드 (여러 워크시트 통합)"""
        try:
            logger.info("📊 Teams에서 불량 데이터 로드 시작...")
            flush_log(logger)

            # 1. Teams 파일 목록 조회
            files = self._get_teams_files()

            # 2. 엑셀 파일 찾기
            excel_file = self._find_excel_file(files)
            if not excel_file:
                raise Exception("대상 엑셀 파일을 찾을 수 없습니다")

            # 3. 엑셀 파일 다운로드
            file_content = self._download_excel_file(excel_file)

            # 4. 여러 워크시트에서 데이터 로드 및 통합
            excel_buffer = io.BytesIO(file_content)
            combined_df = pd.DataFrame()

            for worksheet_name in self.config.worksheet_names:
                try:
                    logger.info(f"📋 워크시트 '{worksheet_name}' 로드 중...")
                    flush_log(logger)

                    # 각 워크시트별로 데이터 로드
                    df = pd.read_excel(excel_buffer, sheet_name=worksheet_name)

                    # 데이터 소스 구분을 위한 컬럼 추가
                    df["데이터_소스"] = worksheet_name

                    # 데이터프레임 통합
                    combined_df = pd.concat([combined_df, df], ignore_index=True)

                    logger.info(f"✅ '{worksheet_name}' 로드 완료: {len(df)}건")
                    flush_log(logger)

                except Exception as worksheet_error:
                    logger.warning(
                        f"⚠️ 워크시트 '{worksheet_name}' 로드 실패: {worksheet_error}"
                    )
                    flush_log(logger)
                    continue

            if combined_df.empty:
                raise Exception("모든 워크시트에서 데이터 로드에 실패했습니다")

            logger.info(
                f"✅ Teams에서 불량 데이터 로드 완료: 총 {len(combined_df)}건 (워크시트 {len(self.config.worksheet_names)}개)"
            )
            flush_log(logger)

            return combined_df

        except Exception as e:
            logger.error(f"❌ Teams 데이터 로드 실패: {e}")
            flush_log(logger)
            raise

    def get_latest_file_info(self) -> Dict:
        """최신 파일 정보 조회 (수정일시, 크기 등)"""
        try:
            files = self._get_teams_files()
            excel_file = self._find_excel_file(files)

            if excel_file:
                file_info = {
                    "name": excel_file.get("name"),
                    "size": excel_file.get("size"),
                    "last_modified": excel_file.get("lastModifiedDateTime"),
                    "created": excel_file.get("createdDateTime"),
                    "id": excel_file.get("id"),
                }

                logger.info(f"✅ 최신 파일 정보: {file_info}")
                flush_log(logger)

                return file_info
            else:
                return {}

        except Exception as e:
            logger.error(f"❌ 파일 정보 조회 실패: {e}")
            flush_log(logger)
            return {}

    def _download_sharepoint_file_direct(self, sharepoint_url: str) -> bytes:
        """SharePoint URL에서 직접 파일 다운로드"""
        try:
            if not self.access_token:
                self._get_access_token()

            # SharePoint URL에서 사이트와 파일 정보 추출
            # 예: https://gst365.sharepoint.com/:x:/s/ManufacturingTechTeam1/ESiuRXZj795Kp-HjGfrG-2QB_nZTfeUqoixbsGoP7bj8rg

            # SharePoint 파일 다운로드 URL 구성
            if (
                "gst365.sharepoint.com" in sharepoint_url
                and "ManufacturingTechTeam1" in sharepoint_url
            ):
                # 파일 ID 추출
                file_id = "ESiuRXZj795Kp-HjGfrG-2QB_nZTfeUqoixbsGoP7bj8rg"

                # SharePoint Graph API URL
                download_url = f"https://graph.microsoft.com/v1.0/sites/gst365.sharepoint.com:/sites/ManufacturingTechTeam1/drive/items/{file_id}/content"

                headers = {"Authorization": f"Bearer {self.access_token}"}

                response = requests.get(download_url, headers=headers)
                response.raise_for_status()

                logger.info(
                    f"✅ SharePoint 파일 다운로드 성공: {len(response.content)} bytes"
                )
                flush_log(logger)

                return response.content
            else:
                raise Exception("지원되지 않는 SharePoint URL 형식")

        except Exception as e:
            logger.error(f"❌ SharePoint 파일 다운로드 실패: {e}")
            flush_log(logger)
            raise

    def load_defect_data_from_sharepoint(
        self, sharepoint_url: str = None
    ) -> pd.DataFrame:
        """SharePoint에서 직접 불량 데이터 로드 (여러 워크시트 통합)"""
        try:
            logger.info("📊 SharePoint에서 불량 데이터 로드 시작...")
            flush_log(logger)

            # 기본 SharePoint URL 사용
            if not sharepoint_url:
                sharepoint_url = "https://gst365.sharepoint.com/:x:/s/ManufacturingTechTeam1/ESiuRXZj795Kp-HjGfrG-2QB_nZTfeUqoixbsGoP7bj8rg"

            # SharePoint 파일 다운로드
            file_content = self._download_sharepoint_file_direct(sharepoint_url)

            # 여러 워크시트에서 데이터 로드 및 통합
            excel_buffer = io.BytesIO(file_content)
            combined_df = pd.DataFrame()

            for worksheet_name in self.config.worksheet_names:
                try:
                    logger.info(f"📋 워크시트 '{worksheet_name}' 로드 중...")
                    flush_log(logger)

                    # 각 워크시트별로 데이터 로드
                    df = pd.read_excel(excel_buffer, sheet_name=worksheet_name)

                    # 데이터 소스 구분을 위한 컬럼 추가
                    df["데이터_소스"] = worksheet_name

                    # 데이터프레임 통합
                    combined_df = pd.concat([combined_df, df], ignore_index=True)

                    logger.info(f"✅ '{worksheet_name}' 로드 완료: {len(df)}건")
                    flush_log(logger)

                except Exception as worksheet_error:
                    logger.warning(
                        f"⚠️ 워크시트 '{worksheet_name}' 로드 실패: {worksheet_error}"
                    )
                    flush_log(logger)
                    continue

            if combined_df.empty:
                raise Exception("모든 워크시트에서 데이터 로드에 실패했습니다")

            logger.info(
                f"✅ SharePoint에서 불량 데이터 로드 완료: 총 {len(combined_df)}건 (워크시트 {len(self.config.worksheet_names)}개)"
            )
            flush_log(logger)

            return combined_df

        except Exception as e:
            logger.error(f"❌ SharePoint 데이터 로드 실패: {e}")
            flush_log(logger)
            raise


class TeamsIntegratedDataLoader:
    """Teams와 기존 데이터 소스를 통합하는 데이터 로더"""

    def __init__(self):
        self.teams_loader = TeamsDataLoader()

    def load_data_with_fallback(self) -> pd.DataFrame:
        """Teams 우선, 실패시 로컬 CSV 사용"""
        try:
            # 1. Teams에서 데이터 로드 시도
            logger.info("🔄 Teams에서 데이터 로드 시도...")
            flush_log(logger)

            df = self.teams_loader.load_defect_data_from_teams()

            logger.info("✅ Teams 데이터 로드 성공")
            flush_log(logger)

            return df

        except Exception as e:
            logger.warning(f"⚠️ Teams 데이터 로드 실패, 로컬 CSV 사용: {e}")
            flush_log(logger)

            # 2. 로컬 CSV 파일 사용 (기존 방식)
            from data.data_loader import DataLoader

            local_loader = DataLoader()
            return local_loader.load_defect_data()

    def check_teams_file_updates(self) -> bool:
        """Teams 파일이 업데이트되었는지 확인"""
        try:
            file_info = self.teams_loader.get_latest_file_info()

            if not file_info:
                return False

            # 마지막 수정 시간을 기준으로 업데이트 확인
            # (실제 구현에서는 로컬에 마지막 확인 시간을 저장해야 함)
            last_modified = file_info.get("last_modified")

            logger.info(f"📅 Teams 파일 마지막 수정: {last_modified}")
            flush_log(logger)

            return True  # 임시로 항상 True 반환

        except Exception as e:
            logger.error(f"❌ Teams 파일 업데이트 확인 실패: {e}")
            flush_log(logger)
            return False
