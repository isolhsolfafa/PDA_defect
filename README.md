# 🏭 GST 공장 불량 예측 시스템 (PDA_ML)

Microsoft Teams 연동 및 머신러닝을 활용한 공장 불량 예측 및 분석 시스템입니다.

## 🚀 **2025년 7월 베타 서비스 준비**

### 📋 **베타 테스트 계획**
- **기간**: 2025년 7월 1일 - 7월 31일
- **목표**: 프로덕션 환경에서 데이터 정합성 검증 및 시스템 안정성 확보
- **범위**: 7월 생산물량 데이터 기반 실시간 불량 예측 서비스

### 🔍 **데이터 정합성 검증 (Data Integrity Validation)**
```bash
# 데이터 정합성 검증 스크립트 실행
python -m scripts.data_validation

# 7월 생산물량 vs 실제 불량 데이터 매칭 검증
python -m scripts.production_validation
```

### 🎯 **베타 서비스 주요 개선사항**
- ✅ **7월 생산물량 데이터 마이그레이션**: 96대 → 156대 (+62.5%)
- ✅ **모델 다양성 확대**: 5개 → 10개 모델 (GAIA-II, DRAGON 계열 추가)
- ✅ **동적 분기별 차트**: 7월 데이터 자동 3분기 분류
- ✅ **실시간 대시보드**: 외주사별/조치유형별 통합 분석
- ✅ **가중치 최적화**: 새로운 생산량 비율 자동 반영

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
├── config.py                    # 전체 시스템 설정
├── main.py                      # 📊 Teams API 기반 ML 시스템
├── run_main.py                  # 🚀 신규 실행 스크립트 (Teams API)
├── factory_ML.py                # 🏭 기존 ML 실행 파일 (Google Sheets)
├── run_refactored_dashboard.py  # 일간 실행 (리팩토링 버전)
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

### 🏭 **기존 ML 실행 (factory_ML.py)**
```bash
# 기존 방식 - Google Sheets 기반 ML 실행
python factory_ML.py
```
**목적:**
- RandomForest + TF-IDF 기반 불량 예측
- Google Sheets 연동 생산량 가중치 적용 (기존 방식)
- Pie Chart 기반 대시보드 생성
- GitHub Pages 자동 배포 (2개 저장소)

**주요 기능:**
- **ML 엔진**: RandomForest 분류기 + 한국어 형태소 분석
- **데이터 소스**: 정적 데이터 기반
  - **불량 분석**: 로컬 CSV 파일 (`data/통합본.csv`) - 수동 정리된 정적 데이터
  - **생산 가중치**: Google Sheets `"6월생산물량"` 시트 (백업: `"월생산물량"`)
- **시각화**: 모델별 불량률 Pie Chart + 회전 카드 UI
- **배포**: `gst-factory-display` + `gst-factory` 저장소 업로드

### 🚀 **신규 ML 실행 (run_main.py → main.py)**
```bash
# 신규 방식 - Teams API 연동 실행
python run_main.py

# 모델 재학습
python run_main.py --mode retrain

# 데이터 추가
python run_main.py --mode add_data
```
**목적:**
- Teams API를 통한 실시간 불량 데이터 분석
- Google Sheets를 통한 생산모델 비율/가중치 계산
- 환경변수 자동 설정 후 main.py 실행
- 향상된 데이터 정합성 및 신뢰성

**주요 기능:**
- **데이터 소스**: 동적 데이터 기반 (실시간 업데이트)
  - **분석용 불량 데이터**: Teams 엑셀 `"가압 불량내역"` 워크시트 (동적 관리)
  - **시각화용 생산 가중치**: Google Sheets `"7월생산물량"` 시트 (백업: `"월생산물량"`)
- **실행 스크립트**: `run_main.py`가 환경변수 설정 후 `main.py` 호출
- **모드 지원**: 기본 예측 / 모델 재학습 / 데이터 추가
- **완전성**: `TeamsIntegratedDataLoader` 통합 데이터 로더 사용

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

### 🎯 **정기 운영 (추천)**

#### 🚀 신규 ML 실행 (Teams API 기반)
```bash
# Teams API 연동 ML 시스템 실행
python run_main.py
```

#### 🏭 기존 ML 실행 (Google Sheets 기반)
```bash
# 기존 방식 - Google Sheets 기반 ML 실행
python factory_ML.py
```

#### 월간 실행 (모델 학습)
```bash
# 매월 1일 실행 (생산량 변경 시) - Teams API 방식
python run_main.py --mode retrain
```

#### 일간 실행 (대시보드 업데이트)
```bash
# 매일 오전 9시 실행 (cron job 설정) - 리팩토링 버전
python run_refactored_dashboard.py

# 또는 기존 버전
python -m analysis.defect_visualizer
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
- **`main.py`**: Teams API 기반 ML 시스템 (336줄)
- **`factory_ML.py`**: 기존 Google Sheets 기반 ML (527줄) - Pie Chart 생성
- **동적 random_state**: 매번 다른 인사이트 발견
- **생산량 가중치**: Teams API + Google Sheets 실제 생산량 반영
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

## 🌐 접속 URL

- **메인 대시보드**: https://isolhsolfafa.github.io/gst-factory/public/pie_defect.html
- **내부 대시보드**: https://isolhsolfafa.github.io/gst-factory/public/internal.html

## 📝 로그 및 모니터링

- **로그 파일**: `logs/factory_ml.log`
- **모델 저장**: `models/defect_predictor.pkl`
- **캐시 데이터**: `cache/monthly_production.json`

## 🔄 자동화 설정 (Cron Job)

```bash
# crontab -e
# 매일 오전 9시 대시보드 업데이트 (리팩토링 버전)
0 9 * * * cd /path/to/PDA_ML && python run_refactored_dashboard.py

# 매월 1일 오전 8시 모델 재학습
0 8 1 * * cd /path/to/PDA_ML && python main.py

# 백업: 기존 버전 대시보드 업데이트 (필요시)
# 0 9 * * * cd /path/to/PDA_ML && python -m analysis.defect_visualizer
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

**최종 업데이트**: 2025년 7월 12일  
**버전**: v2.1 (7월 베타 서비스 준비)  
**다음 마일스톤**: 프로덕션 배포 (2025년 8월 1일)