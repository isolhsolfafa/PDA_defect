# 🏭 GST 공장 불량 예측 시스템 (PDA_ML)

Microsoft Teams 연동 및 머신러닝을 활용한 공장 불량 예측 및 분석 시스템입니다.

## 🚀 **최신 개발 현황 (2026년 1월)**

### 📋 **v2.3.0 업데이트 (2026-01-06)**
- **연도 선택 드롭다운**: 대시보드에서 2025년/2026년 양방향 전환 가능
- **다년도 데이터 분리**: 2025년 아카이브, 2026년 실시간 운영
- **한국 시간대(KST)**: 업데이트 타임스탬프를 KST로 표시
- **주차별 분석 탭**: 주간 트렌드 분석 기능 추가
- **Plotly 스크롤바 개선**: 드롭다운 스크롤 가시성 향상

### 📋 **시스템 전환 완료**
- **실행 파일 변경**: `factory_ML.py` → `main.py`로 통합
- **데이터 소스 현대화**: 정적 CSV → Teams 동적 엑셀 전환
- **CI/CD 자동화**: GitHub Actions 파이프라인 구축 완료
- **보안 강화**: 하드코딩된 인증 정보 → 환경변수 방식 전환

### 🔄 **CI/CD 파이프라인 구축 완료**
```yaml
# 일간 대시보드 자동 업데이트
daily-dashboard.yml:
  - 트리거: 평일 오후 5시 (KST)
  - 실행: run_refactored_dashboard.py
  - 상태: ✅ 정상 작동 중

# 월간 ML 모델 재학습
monthly-ml.yml:
  - 트리거: 매월 1일 오전 8시 (KST)
  - 실행: main.py
  - 상태: ✅ 설정 완료
```

### 🎯 **최근 주요 개선사항 (v2.3)**
- ✨ **연도 선택 드롭다운**: 대시보드 헤더에서 2025년/2026년 전환 가능
- 📊 **다년도 데이터 분리**:
  - 2026년: `public/internal.html` (매일 자동 업데이트)
  - 2025년: `public/2025/internal.html` (아카이브)
- 🕐 **한국 시간대(KST)**: 업데이트 타임스탬프를 KST로 표시
- 📈 **주차별 분석 탭**: 주간 트렌드 분석 기능 추가
- 🔧 **Plotly 스크롤바 개선**: 드롭다운 스크롤 가시성 향상
- ✅ **Teams API 다중 워크시트 지원**: "가압 불량내역" + "제조품질 불량내역" 통합 분석
- ✅ **향상된 호버 정보**: 차트 hover에 "주요 조치내용" + "주요 불량위치" (상위 3개) 추가
- ✅ **UI 개선**: 인터렉티브 메뉴 버튼 위치 조정으로 차트 겹침 해결
- ✅ **보안 강화**: GitHub Push Protection 대응, 모든 하드코딩 제거
- ✅ **모듈화 완성**: 리팩토링된 분석 모듈 안정화
- ✅ **자동화 완성**: 수동 배포 → GitHub Actions 자동 배포

## 🎯 주요 기능

- **📊 Teams 연동**: Microsoft Teams에서 실시간 불량 데이터 자동 로드
- **🤖 ML 기반 예측**: RandomForest + TF-IDF를 활용한 불량 확률 예측
- **⚖️ 생산량 가중치**: Google Sheets와 연동하여 실제 생산량 반영
- **📈 실시간 대시보드**: 웹 대시보드를 통한 실시간 모니터링
- **🔄 월간/일간 운영**: 효율적인 운영 주기 관리
- **☁️ 자동 배포**: GitHub Pages를 통한 대시보드 자동 배포
- **🎯 고도화된 분석**: Pin Point 제안 및 개선 방안 제시

## 🔄 **CI/CD 파이프라인**

### 📦 **배포 전략**
```bash
# 개발 환경 테스트
python -m pytest tests/

# 데이터 정합성 검증
python -m scripts.validate_data

# 스테이징 환경 배포
git push origin develop

# 프로덕션 배포
git push origin main
```

### 🚀 **GitHub Actions 워크플로우**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest
      - name: Deploy to GitHub Pages
        run: python main.py
```

### 🔍 **품질 관리 (QA)**
- **단위 테스트**: ML 모델 정확도 검증
- **통합 테스트**: Teams API 연동 테스트
- **성능 테스트**: 대용량 데이터 처리 성능
- **보안 테스트**: API 키 및 인증 보안

## 📊 **7월 생산물량 업데이트 현황**

### 📈 **생산량 변화**
| 모델명 | 기존 | 7월 | 변화 | 가중치 |
|--------|------|-----|------|--------|
| GAIA-I | 42대 | 58대 | +16 | 0.315 |
| GAIA-I DUAL | 45대 | 46대 | +1 | 0.250 |
| GAIA-II | - | 25대 | +25 | 0.136 |
| DRAGON | - | 8대 | +8 | 0.043 |
| GAIA ORIGIN | - | 8대 | +8 | 0.043 |
| **총계** | **96대** | **156대** | **+60** | **1.000** |

### 🎯 **베타 테스트 KPI**
- **데이터 정합성**: 99.5% 이상
- **예측 정확도**: 90% 이상
- **응답 시간**: 3초 이내
- **가용성**: 99.9% 이상

## 📁 프로젝트 구조

```
PDA_ML/
├── config.py                    # 전체 시스템 설정 (환경변수 통합)
├── main.py                      # 📊 메인 ML 시스템 (Teams API + ML 통합)
├── run_main.py                  # 🚀 main.py 실행 스크립트 (환경변수 설정)
├── run_refactored_dashboard.py  # 📈 일간 대시보드 실행 (CI/CD 연동)
├── local_only/
│   └── factory_ML.py            # 🏭 레거시 ML (로컬 전용, Git 제외)
├── requirements.txt             # 패키지 의존성
├── README.md                   # 프로젝트 설명서
├── 
├── utils/
│   └── logger.py               # 로깅 유틸리티
├── 
├── data/
│   ├── teams_loader.py         # Teams API 연동 (주요)
│   ├── data_loader.py          # 로컬 CSV 로더
│   └── 통합본.csv              # 백업 데이터
├── 
├── ml/
│   └── defect_predictor.py     # ML 모델 및 예측 엔진
├── 
├── analysis/
│   ├── defect_analyzer.py      # 기본 불량 분석
│   ├── advanced_defect_analyzer.py  # 고도화된 분석 + Pin Point 제안
│   └── defect_visualizer.py    # 일간 실행 (HTML 생성)
├── 
├── refactored_analysis/        # 🔄 리팩토링된 분석 모듈
│   ├── __init__.py            # 모듈 초기화
│   ├── defect_visualizer.py   # 메인 통합 클래스
│   ├── base_visualizer.py     # 공통 기능 기본 클래스
│   ├── pressure_charts.py     # 가압검사 차트 (84KB, 1801줄)
│   ├── quality_charts.py      # 품질분석 차트 (76KB, 1579줄)
│   └── dashboard_builder.py   # 대시보드 구성 (68KB, 1591줄)
├── 
├── output/
│   └── github_uploader.py      # GitHub 자동 업로드
├── 
├── templates/
│   └── dashboard_template.html # 대시보드 템플릿
├── 
├── credentials/
│   └── gst-manegemnet-70faf8ce1bff.json  # Google Sheets 인증
├── 
├── logs/                       # 로그 파일들
├── models/                     # 저장된 ML 모델들
└── cache/                      # 캐시 데이터
```

## 🗓️ 운영 주기

### 📅 **월간 실행 (main.py)**
```bash
# 한 달에 1번 실행
python main.py
```
**목적:**
- ML 모델 재학습
- 월간 생산량 데이터 업데이트
- 전체 시스템 갱신
- 캐시 데이터 생성

### 📊 **일간 실행 (defect_visualizer.py)**
```bash
# 매일 실행
python -m analysis.defect_visualizer
```
**목적:**
- 최신 Teams 데이터 로드
- internal.html 대시보드 생성
- GitHub 자동 업로드
- 빠른 실시간 모니터링

### 📊 **메인 ML 시스템 (main.py)**
```bash
# 현재 메인 시스템 - Teams API 통합 ML 실행
python run_main.py
```
**목적:**
- Teams API 기반 실시간 불량 데이터 분석
- 다중 워크시트 통합 분석 ("가압 불량내역" + "제조품질 불량내역")
- Google Sheets 기반 생산량 가중치 적용
- GitHub Pages 자동 배포

**주요 기능:**
- **ML 엔진**: RandomForest 분류기 + TF-IDF + MeCab 한국어 분석
- **데이터 소스**: 동적 데이터 기반
  - **불량 분석**: Teams Excel 다중 워크시트 (실시간 동적 데이터)
  - **생산 가중치**: Google Sheets `"7월생산물량"` 시트 (백업: `"월생산물량"`)
- **시각화**: 통합 대시보드 + Pie Chart + 회전 카드 UI
- **배포**: GitHub Actions를 통한 자동 배포

### 🏭 **레거시 ML (local_only/factory_ML.py)**
```bash
# 로컬 전용 - Google Sheets 기반 ML 실행 (Git 제외)
python local_only/factory_ML.py
```
**목적:**
- 기존 방식 호환성 유지 (로컬 개발/테스트용)
- 정적 CSV 파일 기반 분석
- 수동 배포 방식

### 🔄 **현재 시스템 실행 흐름**
```bash
# 1. 환경변수 설정 및 main.py 실행
python run_main.py

# 2. 모델 재학습 (월간)
python run_main.py --mode retrain

# 3. 데이터 추가
python run_main.py --mode add_data
```
**실행 흐름:**
1. `run_main.py`: 환경변수 설정 및 Teams API 인증 준비
2. `main.py`: 실제 ML 분석 및 대시보드 생성 실행
3. GitHub Actions: 자동 배포 및 모니터링

**통합 데이터 소스:**
- **불량 분석**: Teams Excel `"가압 불량내역"` + `"제조품질 불량내역"` (실시간)
- **생산 가중치**: Google Sheets `"7월생산물량"` 시트
- **배포**: `gst-factory` + `gst-factory-display` 저장소 자동 업로드

### 🔄 **리팩토링 대시보드 실행 (run_refactored_dashboard.py)**
```bash
# 매일 실행 (리팩토링 버전)
python run_refactored_dashboard.py

# 기존 버전과 비교 테스트
python run_refactored_dashboard.py --mode compare
```
**목적:**
- 리팩토링된 대시보드 시스템 실행
- 환경변수 자동 설정 및 실행
- 기존 버전과 비교 검증
- 시스템 안정성 확보

**리팩토링 구조:**
- **기존**: `analysis/defect_visualizer.py` (3897줄 단일 파일)
- **신규**: `refactored_analysis/` (5개 모듈로 분할)
  - `pressure_charts.py`: 가압검사 분석 (1801줄)
  - `quality_charts.py`: 품질분석 차트 (1579줄)
  - `dashboard_builder.py`: 대시보드 통합 (1591줄)
  - `base_visualizer.py`: 공통 기능 (149줄)
  - `defect_visualizer.py`: 메인 클래스 (247줄)

## 🚀 설치 및 설정

### 1. 환경 설정

```bash
# Python 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 2. Microsoft Teams API 연동 설정

#### 1. Azure AD 앱 등록
1. [Azure Portal](https://portal.azure.com)에 로그인
2. **Azure Active Directory** → **앱 등록** → **새 등록**
3. 앱 이름: `GST-Factory-ML-Bot`
4. 지원되는 계정 유형: **이 조직 디렉터리의 계정만**
5. 리디렉션 URI: 생략 (데몬 앱이므로)

#### 2. API 권한 설정
앱 등록 후 **API 권한**에서 다음 권한 추가:
- `Microsoft Graph` → `Application permissions`:
  - `Sites.Read.All` (SharePoint 사이트 읽기)
  - `Files.Read.All` (파일 읽기)
  - `Group.Read.All` (그룹 읽기)

#### 3. 클라이언트 시크릿 생성
1. **인증서 및 비밀** → **새 클라이언트 비밀**
2. 설명: `GST-Factory-Secret`
3. 만료: **24개월**
4. 생성된 **값**을 복사 (한 번만 표시됨)

#### 4. 환경변수 설정 (.env_teams)
```bash
# Teams API 설정
TEAMS_TENANT_ID=your-tenant-id
TEAMS_CLIENT_ID=your-client-id
TEAMS_CLIENT_SECRET=your-client-secret
TEAMS_GROUP_ID=your-group-id
TEAMS_FOLDER_PATH=General/99.개인폴더/박승록
TEAMS_FILE_NAME=▶2025年 가압 통합 Sheet [DAILY UPDATE].xlsm

# GitHub 토큰 설정
GITHUB_TOKEN_1=your_github_token_here
GITHUB_TOKEN_2=your_github_token_here
```

### 3. Google Sheets 인증 설정
`credentials/` 폴더에 Google Service Account JSON 파일을 배치합니다.

## 📖 사용법

### 🎯 **정기 운영 (현재 권장 방식)**

#### 📊 **메인 ML 시스템 실행**
```bash
# 현재 메인 시스템 - Teams API 기반 ML 분석
python run_main.py
```

#### 📈 **일간 대시보드 업데이트 (자동화)**
```bash
# GitHub Actions 자동 실행 (평일 오후 5시)
# 수동 실행시:
python run_refactored_dashboard.py
```

#### 🔄 **월간 모델 재학습 (자동화)**
```bash
# GitHub Actions 자동 실행 (매월 1일 오전 8시)
# 수동 실행시:
python run_main.py --mode retrain
```

#### 🏭 **레거시 시스템 (로컬 전용)**
```bash
# 로컬 개발/테스트용 (Git 제외)
python local_only/factory_ML.py
```

### 🔧 **개발/테스트 모드**

#### 로컬 테스트
```bash
# 로컬 CSV 데이터 사용
python main.py --use-local-data

# 기존 모델 사용 (재학습 없음)
python main.py --use-existing-model
```

#### 새 데이터 추가
```bash
# 새로운 불량 데이터 추가
python main.py --mode add_data

# 모델 재학습
python main.py --mode retrain
```

## 📊 데이터 형식

Teams에서 로드되는 데이터는 다음 컬럼을 포함해야 합니다:

| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| 제품명 | 제품 모델명 | "GAIA-I DUAL" |
| 부품명 | 불량 발생 부품 | "SPEED CONTROLLER" |
| 상세불량내용 | 불량 상세 설명 | "He 가압검사 불합격" |
| 대분류 | 불량 대분류 | "부품불량" |
| 중분류 | 불량 중분류 | "기구작업불량" |
| 검출단계 | 불량 검출 단계 | "가압검사" |
| 비고 | 추가 정보 | "파트교체 완료" |
| 발생일 | 불량 발생일 | "2024-01-15" |

## 🔧 주요 모듈 설명

### 📊 **데이터 로드**
- **`TeamsDataLoader`**: Microsoft Teams API 연동 (주요)
- **`DataLoader`**: 로컬 CSV 백업 데이터 로드

### 🤖 **ML 엔진**
- **`DefectPredictor`**: RandomForest + TF-IDF 기반 예측 (ml/defect_predictor.py)
- **`main.py`**: Teams API 기반 통합 ML 시스템 (398줄) - 현재 메인
- **`local_only/factory_ML.py`**: 레거시 Google Sheets 기반 ML (Git 제외)
- **동적 random_state**: 매번 다른 인사이트 발견
- **다중 워크시트**: Teams Excel "가압 불량내역" + "제조품질 불량내역" 통합
- **생산량 가중치**: Google Sheets 실제 생산량 반영
- **한국어 처리**: MeCab 형태소 분석기 + TF-IDF

### 📈 **분석 엔진**
- **`DefectAnalyzer`**: 기본 불량 분석
- **`AdvancedDefectAnalyzer`**: 고도화된 분석 + Pin Point 제안
- **`DefectVisualizer`**: HTML 대시보드 생성

### 🔄 **리팩토링 분석 모듈 (refactored_analysis/)**
- **`DefectVisualizer`**: 메인 통합 클래스 (기존 호환성 유지)
- **`BaseVisualizer`**: 공통 기능 제공 (색상 생성, 데이터 로딩)
- **`PressureCharts`**: 가압검사 관련 차트 생성 (1801줄)
- **`QualityCharts`**: 품질분석 차트 생성 (1579줄) 
- **`DashboardBuilder`**: 대시보드 구성 및 통합 (1591줄)

### 🌐 **출력 및 배포**
- **`GitHubUploader`**: GitHub Pages 자동 배포
- **HTML 대시보드**: 실시간 웹 모니터링

## 🎯 주요 개선사항

### ✅ **하드코딩 제거**
- 동적 불량유형 매핑
- 실제 Teams 데이터 기반 분석
- 실시간 누적 카운트

### ✅ **SPEED CONTROLLER 문제 해결**
- 제외 옵션으로 다양한 부품 발견
- 숨겨진 불량 패턴 식별

### ✅ **Pin Point 제안**
- 부품별 맞춤형 개선 방안
- 실제 현장 상황 반영
- 구체적인 조치 방법 제시

### ✅ **운영 효율성**
- 월간/일간 실행 주기 분리
- API 호출 최소화
- 캐시 시스템 도입

### 🔄 **코드 리팩토링 (2025년 추가)**
- **모듈화**: 기존 3897줄 단일 파일을 5개 모듈로 분할
- **관심사 분리**: 가압검사, 품질분석, 대시보드 구성으로 역할 분담
- **유지보수성**: 각 모듈별 독립적 수정 및 테스트 가능
- **호환성 보장**: 기존 `DefectVisualizer` 인터페이스 100% 유지
- **성능 최적화**: 메모리 사용량 감소 및 실행 속도 향상

### 📊 **데이터 소스 진화 (핵심 개선)**
- **기존**: 정적 CSV 파일 (수동 정리) → **신규**: Teams 동적 엑셀 (실시간 관리)
- **데이터 품질**: 수동 업데이트 → 실시간 자동 동기화
- **운영 효율성**: 파일 업로드 불필요, Teams에서 직접 관리
- **다중 워크시트**: "가압 불량내역" + "제조품질 불량내역" 통합 분석

### 🔧 **시스템 아키텍처 변화**
- **실행 파일**: `factory_ML.py` → `main.py` 통합
- **CI/CD**: 수동 배포 → GitHub Actions 자동화
- **보안**: 하드코딩 → 환경변수 + GitHub Secrets
- **모니터링**: 로컬 실행 → 클라우드 기반 자동 모니터링

## 🌐 접속 URL

- **메인 대시보드**: https://isolhsolfafa.github.io/gst-factory/public/pie_defect.html
- **내부 대시보드**: https://isolhsolfafa.github.io/gst-factory/public/internal.html

## 📝 로그 및 모니터링

- **로그 파일**: `logs/factory_ml.log`
- **모델 저장**: `models/defect_predictor.pkl`
- **캐시 데이터**: `cache/monthly_production.json`

## 🔄 자동화 설정

### 🚀 **GitHub Actions CI/CD (현재 적용)**
```yaml
# .github/workflows/daily-dashboard.yml
# 평일 오후 5시 (KST) 자동 실행
schedule:
  - cron: '0 8 * * 1-5'  # UTC 08:00 = KST 17:00

# .github/workflows/monthly-ml.yml  
# 매월 1일 오전 8시 (KST) 자동 실행
schedule:
  - cron: '0 23 * * *'  # UTC 23:00 = KST 08:00 (다음날)
```

### 🔧 **로컬 Cron Job (백업 옵션)**
```bash
# crontab -e
# 매일 오후 5시 대시보드 업데이트
0 17 * * * cd /path/to/PDA_ML && python run_refactored_dashboard.py

# 매월 1일 오전 8시 모델 재학습  
0 8 1 * * cd /path/to/PDA_ML && python run_main.py --mode retrain
```

## 🛠️ 트러블슈팅

### Teams API 연동 문제
- Azure AD 권한 확인
- 토큰 만료 확인
- 파일 경로 확인

### ML 모델 문제
- 데이터 품질 확인
- 피처 인코딩 문제
- 메모리 부족 문제

### GitHub 업로드 문제
- 토큰 권한 확인
- 레포지토리 접근 권한
- 파일 크기 제한

## 📞 문의 및 지원

시스템 관련 문의사항이나 개선 제안이 있으시면 개발팀에 연락해주세요.

---

## 📋 **개발 히스토리**

### 🔄 **주요 마일스톤**
- **v1.0 (2024년 Q4)**: 기본 ML 시스템 구축 (`factory_ML.py`)
- **v2.0 (2025년 1월)**: Teams API 연동 및 시스템 통합 (`main.py`)
- **v2.1 (2025년 1월)**: CI/CD 자동화 및 보안 강화
- **v2.2 (2025년 9월)**: 부품별 검사공정 비교 분석 기능
- **v2.3 (2026년 1월)**: 연도별 데이터 분리 및 드롭다운 전환

### 📈 **최근 변경사항 (2026년 1월)**
- ✅ **연도 선택 드롭다운**: 2025년/2026년 데이터 전환 UI 추가
- ✅ **다년도 데이터 분리**: 2025년 아카이브, 2026년 실시간 운영
- ✅ **KST 타임스탬프**: 업데이트 시간을 한국 시간으로 표시
- ✅ **주차별 분석 탭**: 주간 트렌드 분석 기능 추가
- ✅ **Plotly 스크롤바 개선**: 드롭다운 스크롤 가시성 향상
- ✅ **Teams 경로 수정**: `General/99.개인폴더/박승록/0. 불량&TIME`

### 📈 **변경사항 (2025년 1월)**
- ✅ **실행 파일 통합**: `factory_ML.py` → `main.py`로 메인 시스템 변경
- ✅ **데이터 소스 현대화**: 정적 CSV → Teams 동적 Excel 전환
- ✅ **CI/CD 파이프라인**: GitHub Actions 기반 자동 배포 구축
- ✅ **보안 강화**: 모든 하드코딩 제거, 환경변수 + GitHub Secrets 적용
- ✅ **다중 워크시트 지원**: "가압 불량내역" + "제조품질 불량내역" 통합
- ✅ **UI/UX 개선**: 차트 hover 정보 향상, 메뉴 겹침 해결
- ✅ **모듈화 완성**: 리팩토링 분석 모듈 안정화

### 🚧 **진행 중인 작업**
- 🔄 **레거시 시스템 정리**: `local_only/factory_ML.py` 환경변수 리팩토링 (보류)

---

## 🔍 **2025년 8월 27일 시스템 분석 결과**

## 🚀 **2025년 8월 28일 시스템 고도화 완료**

### **📊 주요 개선 성과**

#### **1. 전처리 시스템 고도화**
- **영어+한국어 통합 키워드 추출**: 대소문자 구분 없이 모든 영어 단어 포함
- **키워드 수 대폭 증가**: 1.81개 → 5.34개 (+195.2%)
- **TF-IDF 차원 확장**: 59개 → 173개 (+193.2%)
- **모델 정확도 향상**: 92.59% → 96.30% (+3.71%p)

#### **2. 실제 데이터 기반 분석 시스템**
- **실제 불량 데이터 반영**: 540건 실제 데이터 기반 부품별 맞춤 분석
- **빈도 기반 우선순위**: 데이터 빈도에 따른 자동 우선순위 조정
- **다국어 키워드 분류**: 영어 9개, 한국어 11개 키워드 분류
- **트렌드 정보 추가**: 각 부품별 전체 대비 비율 및 트렌드 방향

#### **3. Advanced Defect Analyzer 고도화**

**🔧 주요 부품별 우선순위 업데이트:**
| 부품명 | 이전 우선순위 | **새 우선순위** | 실제 데이터 기반 개선 |
|--------|---------------|----------------|---------------------|
| **SPEED CONTROLLER** | HIGH | **CRITICAL** | 92건 누수 → 최다발생 |
| **MALE ELBOW** | MEDIUM | **HIGH** | 62건 → 40건 Fitting nut 누수 |
| **MALE CONNECTOR** | MEDIUM | **HIGH** | 40건 → 17건 누수 |
| **REDUCER DOUBLE Y UNION** | MEDIUM | **HIGH** | 28건 → 41건 삽입부 불량 |

**🎯 실제 키워드 기반 개선 제안:**
- **SPEED CONTROLLER**: "전체 교체 (미보증 부품 우선)" - 92건 누수
- **MALE ELBOW**: "Fitting nut 누수 패턴 분석 및 대책" - 40건 누수
- **REDUCER DOUBLE Y UNION**: "삽입부 설계 및 가공 정밀도 개선" - 41건 삽입부

#### **4. 키워드 분석 고도화**
**📈 상위 키워드 (실제 빈도순):**
1. `Speed Controller Leak` (92건)
2. `PFA` (72건)
3. `체결` (67건)
4. `불량` (56건)
5. `Leak` (51건)

**🔍 키워드 분류 결과:**
- **누수 관련**: 5개 키워드 (Speed Controller Leak, PFA, Leak 등)
- **체결 관련**: 3개 키워드 (체결, Fitting nut 등)
- **재질 관련**: 4개 키워드 (PFA, TEFLON, 우레탄, Ring 등)

#### **5. 시스템 성능 지표**
- **모델 정확도**: 94.4% (지속적 개선)
- **고도화된 제안**: "삽입부 설계 및 가공 정밀도 개선"
- **데이터 크기**: 9,364 chars (기존 대비 거의 2배)
- **분석 차원**: 176개 피처 (기존 62개 대비 183.9% 증가)

#### **6. 기술적 개선사항**
- **Document ID 개념 도입**: 인코딩이 카운트가 아닌 고유 식별자임을 명확화
- **MeCab + TF-IDF 시각화**: 트리맵으로 전처리 과정 시각화
- **RandomForest 의사결정 시각화**: 실제 값 기반 트리맵 생성
- **한글 폰트 문제 해결**: NanumGothic 폰트 적용으로 시각화 개선

#### **7. 실용적 개선사항**
- **회사 공용어 보존**: BCW, PFA 등 약어 그대로 유지
- **다양한 표현 방식**: 대소문자 구분 없이 모든 영어 표현 포함
- **실제 불량 패턴**: 누수, 체결, 삽입, 부품누락 등 실제 패턴 반영
- **우선순위 자동 조정**: 데이터 빈도에 따른 동적 우선순위 설정

### **💡 핵심 인사이트**
1. **영어 기술 용어 포함이 성능 향상에 크게 기여**
2. **실제 데이터 기반 분석이 더 정확한 제안 제공**
3. **다국어 키워드 통합으로 풍부한 특징 추출**
4. **빈도 기반 우선순위가 실용적인 개선 방향 제시**

### 📊 **실제 데이터 기반 분석**

#### **1. GAIA-II DUAL REDUCER 100% 불량률 분석**
- **실제 생산량**: 6대 (매우 적음)
- **실제 불량 건수**: 5건
- **실제 불량률**: **83.3%** (5건/6대)
- **ML 예측**: 100% (패턴 학습 결과)
- **분석 결과**: 생산량이 적지만 불량률이 매우 높아 ML이 패턴을 학습하여 100% 예측

#### **2. REDUCER DOUBLE Y UNION 전체 현황**
```
전체 불량: 28건
모델별 분포:
- GAIA-I DUAL: 10건 (가장 많음)
- WET 1000: 5건
- GAIA-II DUAL: 5건 (3번째)
- GAIA-P: 3건
- DRAGON AB: 2건
- 기타: 3건
```

#### **3. 불량 분류 현황**
```
대분류별 분포:
- 기구작업불량: 322건 (59.6%)
- 부품불량: 168건 (31.1%)
- 전장작업불량: 28건 (5.2%)
- 미분류(NaN): 22건 (4.1%)
```

### 🤖 **ML 모델 상세 분석**

#### **ML이 학습하는 것:**
1. **타겟(Y)**: "부품불량" 여부 예측 (이진 분류)
2. **피처(X)**: 
   - 제품명 (라벨 인코딩)
   - 부품명 (라벨 인코딩)
   - 검출단계 (라벨 인코딩)
   - 상세불량내용 (TF-IDF 텍스트 분석)

#### **텍스트 분석 과정:**
```python
# MeCab 한국어 형태소 분석
원본: "CENTRIFUGAL PUMP 볼트 체결불량"
분석: ['볼트', '체결', '불량']

# TF-IDF 벡터화
텍스트 → 540×62 매트릭스로 변환
```

#### **ML vs 엑셀 피봇 차이점:**

| 구분 | 엑셀 피봇 | ML 모델 |
|------|-----------|---------|
| **분석 방식** | 단순 집계/카운트 | 패턴 학습 + 예측 |
| **사용 데이터** | 숫자만 | 숫자 + 텍스트 조합 |
| **결과** | 과거 통계 | 미래 확률 예측 |
| **정확도** | 100% (과거 사실) | 97.2% (예측) |
| **인사이트** | "REDUCER가 28건 불량났다" | "GAIA-II DUAL + REDUCER 조합은 100% 불량 예상" |

### 🔧 **시스템 설정 업데이트**

#### **Google Service Key 변경:**
```python
# config.py 업데이트
service_account_file: str = "credentials/gst-manegemnet-e6c4e7bd79e2.json"
```

#### **생산량 데이터 소스:**
- **주 시트**: "월생산물량"
- **대체 시트**: "8월생산물량"
- **현재 생산량**: GAIA-I DUAL(69대), GAIA-I(45대), GAIA-II(17대), GAIA-II DUAL(6대)

### 📈 **핵심 인사이트**

#### **1. GAIA-II DUAL REDUCER 문제**
- **원인**: 생산량 대비 불량률이 매우 높음 (83.3%)
- **대응**: 체결 토크 표준화, 실링 재료 개선 필요
- **우선순위**: IMMEDIATE (즉시 조치 필요)

#### **2. ML 모델의 예측 능력**
- **패턴 발견**: 단순 통계가 아닌 복합 요인 분석
- **텍스트 분석**: 불량 내용에서 키워드 추출 및 패턴 학습
- **미래 예측**: 과거 데이터 기반으로 새로운 조합의 불량 확률 예측

#### **3. 데이터 품질 개선점**
- **NaN 처리**: 22건의 미분류 데이터 존재
- **제외 키워드**: "He미보증" 키워드만 필터링
- **실시간 업데이트**: Teams API를 통한 실시간 데이터 동기화

### 🎯 **실무 적용 방안**

#### **품질 관리 개선:**
1. **GAIA-II DUAL 생산 시**: REDUCER DOUBLE Y UNION 특별 점검
2. **가압검사 강화**: 해당 부품의 체결 상태 집중 검사
3. **공정 개선**: 체결 토크 표준화 및 작업자 교육

#### **ML 모델 활용:**
1. **신제품 개발**: 새로운 제품-부품 조합의 불량 위험 사전 평가
2. **공급업체 관리**: 특정 부품의 불량 패턴 분석
3. **예방 정비**: 불량 확률이 높은 부품의 사전 점검

---

**최종 업데이트**: 2026년 1월 6일
**현재 버전**: v2.3.0 (연도별 데이터 분리 및 드롭다운 전환 기능)
**다음 목표**: ML 모델 정확도 향상 및 실시간 예측 시스템 구축
