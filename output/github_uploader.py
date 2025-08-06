import base64
import requests
import json
import numpy as np
from typing import Dict, Any
import os

from config import github_config, TEST_MODE, DISABLE_GITHUB_UPLOAD
from utils.logger import setup_logger, flush_log

logger = setup_logger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    """numpy 타입을 처리하는 커스텀 JSON 인코더"""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class GitHubUploader:
    """GitHub 업로드 클래스"""

    def __init__(self):
        self.config = github_config

    def upload_file(
        self,
        content: str,
        username: str,
        repo: str,
        branch: str,
        token: str,
        filename: str,
        message: str,
    ) -> bool:
        """GitHub에 파일 업로드"""
        logger.info(
            f"GitHub 업로드 시작 - 사용자: {username}, 레포: {repo}, 브랜치: {branch}, 파일: {filename}"
        )
        flush_log(logger)

        try:
            # Base64 인코딩
            b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

            # GitHub API URL
            url = f"https://api.github.com/repos/{username}/{repo}/contents/{filename}"

            # 헤더 설정
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            }

            # 기존 파일 확인
            response = requests.get(url, headers=headers)
            logger.info(f"GitHub GET 응답 상태: {response.status_code}")
            flush_log(logger)

            sha = response.json().get("sha") if response.status_code == 200 else None

            # 업로드 페이로드 구성
            payload = {"message": message, "content": b64_content, "branch": branch}
            if sha:
                payload["sha"] = sha

            # 파일 업로드
            put_response = requests.put(url, headers=headers, json=payload)

            if put_response.status_code in (200, 201):
                logger.info(f"✅ GitHub 업로드 성공: {username}/{repo}/{filename}")
                flush_log(logger)
                return True
            else:
                logger.error(
                    f"❌ GitHub 업로드 실패: {put_response.status_code}, {put_response.json()}"
                )
                flush_log(logger)
                return False

        except Exception as e:
            logger.error(
                f"❌ GitHub 업로드 예외 발생: {username}/{repo}/{filename} - {e}"
            )
            flush_log(logger)
            return False

    def upload_dashboard_files(self, html_content: str, data: Dict[str, Any]) -> bool:
        """대시보드 파일들을 업로드"""

        # GitHub 업로드 완전 비활성화 확인
        if DISABLE_GITHUB_UPLOAD:
            logger.info(
                "🔒 GitHub 업로드가 비활성화되어 있습니다. 로컬에만 저장합니다."
            )
            return self._save_locally_only(html_content, data)

        # TEST_MODE일 때도 로컬 저장만 수행
        if TEST_MODE:
            logger.info("🧪 [TEST MODE] 로컬 저장만 수행합니다.")
            return self._save_locally_only(html_content, data)

        try:
            # 로컬 저장 먼저 수행
            self._save_locally_only(html_content, data)

            # GitHub 업로드 (DISABLE_GITHUB_UPLOAD가 False일 때만)
            success1 = self._upload_to_repository_1(html_content, data)
            success2 = self._upload_to_repository_2(html_content, data)

            if success1 and success2:
                logger.info("✅ 모든 GitHub 업로드가 성공적으로 완료되었습니다!")
                return True
            else:
                logger.warning(
                    "⚠️ 일부 GitHub 업로드가 실패했지만 로컬 저장은 완료되었습니다."
                )
                return False

        except Exception as e:
            logger.error(f"❌ 업로드 중 오류 발생: {e}")
            return False

    def _save_locally_only(self, html_content: str, data: Dict[str, Any]) -> bool:
        """로컬에만 저장"""
        try:
            # public 디렉토리 생성
            os.makedirs("public", exist_ok=True)

            # HTML 파일 로컬 저장
            with open("public/pie_defect.html", "w", encoding="utf-8") as f:
                f.write(html_content)

            # JSON 데이터 로컬 저장 (커스텀 인코더 사용)
            with open("public/data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)

            logger.info("✅ 로컬 저장 완료: public/pie_defect.html, public/data.json")
            return True

        except Exception as e:
            logger.error(f"❌ 로컬 저장 실패: {e}")
            return False

    def _upload_to_repository_1(self, html_content: str, data: Dict[str, Any]) -> bool:
        """첫 번째 저장소에 업로드"""
        try:
            # JSON 데이터를 문자열로 변환
            json_content = json.dumps(
                data, ensure_ascii=False, indent=2, cls=CustomJSONEncoder
            )

            # HTML 파일 업로드
            html_success = self.upload_file(
                content=html_content,
                username=self.config.username_1,
                repo=self.config.repo_1,
                branch=self.config.branch_1,
                token=self.config.token_1,
                filename=self.config.html_filename,
                message="🤖 ML 불량 예측 대시보드 업데이트",
            )

            # JSON 파일 업로드
            json_success = self.upload_file(
                content=json_content,
                username=self.config.username_1,
                repo=self.config.repo_1,
                branch=self.config.branch_1,
                token=self.config.token_1,
                filename=self.config.json_filename,
                message="📊 ML 예측 데이터 업데이트",
            )

            return html_success and json_success

        except Exception as e:
            logger.error(f"❌ Repository 1 업로드 실패: {e}")
            return False

    def _upload_to_repository_2(self, html_content: str, data: Dict[str, Any]) -> bool:
        """두 번째 저장소에 업로드 (백업용)"""
        try:
            # JSON 데이터를 문자열로 변환
            json_content = json.dumps(
                data, ensure_ascii=False, indent=2, cls=CustomJSONEncoder
            )

            # HTML 파일 업로드
            html_success = self.upload_file(
                content=html_content,
                username=self.config.username_2,
                repo=self.config.repo_2,
                branch=self.config.branch_2,
                token=self.config.token_2,
                filename=self.config.html_filename_2,
                message="🤖 ML 불량 예측 대시보드 백업",
            )

            # JSON 파일 업로드
            json_success = self.upload_file(
                content=json_content,
                username=self.config.username_2,
                repo=self.config.repo_2,
                branch=self.config.branch_2,
                token=self.config.token_2,
                filename=self.config.json_filename_2,
                message="📊 ML 예측 데이터 백업",
            )

            return html_success and json_success

        except Exception as e:
            logger.error(f"❌ Repository 2 업로드 실패: {e}")
            return False
