# GitHub Secrets 설정 가이드

## 🔐 GitHub Actions에서 설정해야 할 필수 Secrets

### Teams API 관련 (4개)
```
TEAMS_TENANT_ID=your-tenant-id-here
TEAMS_CLIENT_ID=your-client-id-here
TEAMS_CLIENT_SECRET=your-client-secret-here
TEAMS_TEAM_ID=your-team-id-here
```

### GitHub API 관련 (2개)
```
GH_TOKEN_1=your_github_token_1_here
GH_TOKEN_2=your_github_token_2_here
```

## 📊 총 설정해야 할 Secrets: 6개

1. **TEAMS_TENANT_ID** - Microsoft Teams 테넌트 ID
2. **TEAMS_CLIENT_ID** - Teams API 클라이언트 ID  
3. **TEAMS_CLIENT_SECRET** - Teams API 클라이언트 시크릿
4. **TEAMS_TEAM_ID** - Teams 팀 ID
5. **GH_TOKEN_1** - GitHub 토큰 1 (gst-factory-display 레포용)
6. **GH_TOKEN_2** - GitHub 토큰 2 (gst-factory 레포용)

💡 **참고**: Google Sheets API는 생산량 가중치 계산용으로만 사용되며, 주요 불량 데이터는 Teams에서 가져옵니다.

## 🔑 개발자 참고사항

실제 값들은 로컬 `.env` 파일이나 개발자 문서에서 별도 관리합니다.
보안상 GitHub 저장소에는 예시 값만 포함합니다.

## 📝 설정 방법

1. GitHub Repository → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. 위의 각 항목을 Name/Value로 입력
4. "Add secret" 클릭

## 🔧 로컬 개발용 (.env)

로컬 개발 시에는 `.env` 파일에 동일한 환경변수 설정:
```bash
# Teams API (4개)
TEAMS_TENANT_ID=your-tenant-id-here
TEAMS_CLIENT_ID=your-client-id-here
TEAMS_CLIENT_SECRET=your-client-secret-here
TEAMS_TEAM_ID=your-team-id-here

# GitHub API (2개)
GH_TOKEN_1=your_github_token_1_here
GH_TOKEN_2=your_github_token_2_here
```

💡 **참고**: `.env` 파일은 `.gitignore`에 포함되어 Git에 업로드되지 않습니다.

## ⚠️ 보안 주의사항

- 절대 코드에 하드코딩하지 말 것
- `.env` 파일은 .gitignore에 포함
- GitHub Secrets는 읽기 전용 (수정 시 새로 생성)
- 토큰 만료 시 새로 발급하여 업데이트