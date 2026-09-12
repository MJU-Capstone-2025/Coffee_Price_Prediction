# 작업 상태

## 2026-09-13 — 외부 uv 가상환경 안내 정리

- `AGENTS.md`·`Context.md`의 환경 안내를 프로젝트 외부의 `$HOME/.virtualenvs/coffee-price-prediction`으로 맞추고 활성화·uv 패키지 관리 명령을 명시했다.
- `.env`의 `COFFEE_VENV`·`UV_PROJECT_ENVIRONMENT`는 `python-dotenv`에서도 경로가 확장되도록 `$HOME`을 `${HOME}`으로 바꿨다. 다른 설정은 유지했다.
- 검증: uv 생성 정보·CPython 3.14.7, 문서의 셸 활성화 명령, 두 dotenv 경로가 같은 외부 환경을 가리키는지 확인했다. `git diff --check` 통과. 가상환경 재생성·패키지 변경은 없으며 `.env`는 Git 제외 상태다.

## 2026-09-13 — notebook 시각화 한국어 표시

- `01`·`03` 첫 코드 셀에 운영체제별 폰트 분기를 추가했다. Windows/Mac/Linux는 각각 Malgun Gothic/AppleGothic/NanumGothic을 쓰며 Linux/Colab에는 설치 명령을 주석으로 안내한다. Seaborn에도 선택한 폰트를 전달한다. 변경 후 Mac의 새 커널에서 각각 11셀·19셀을 전체 실행했고 글꼴 경고는 없었다. Windows·Linux에서 직접 실행한 것은 아니다.
- 활성 notebook `01`·`03`의 표 항목명, 산지·피처명, 그래프 제목·축·범례를 한국어로 바꿨다. 설치된 한글 폰트를 선택하며 내부 계산용 컬럼은 유지한다.
- 기존 `.venv` 새 커널에서 각각 10셀·18셀을 전체 실행했다. 차트 3개를 확인했고 한글 글꼴 경고는 없었다. 모델 지표는 동일하다. `old_code/`의 학부 원본은 유지했다.

## 2026-09-13 — EDA·베이스라인

- `03_eda_and_baseline_models.ipynb` 전체 17셀을 기존 `.venv`의 새 커널에서 실행했다. 로컬 소켓 권한으로 실행했으며, 표 출력 셀의 괄호 오류 수정 후 전체 재실행을 통과했다.
- Parquet 12개를 공개 지연 가정으로 As-of Join하고 피처 21개를 만들었다. ICE 공지와 달력을 대조해 휴장일 6행은 모델 입력에서 제외하고, 누락 거래일 3개는 빈칸으로 유지했다. 원본 데이터는 수정하지 않았다.
- 2016~2021년 학습 1,422행, 2022~2023년 검증 496행. 경계에 걸친 5일 뒤 정답을 제외했다. Ridge alpha=100, CatBoost depth=4·31 trees를 고른 뒤 2016~2023년 1,923행으로 재학습했다.
- 테스트 498건의 RMSE는 Naive 0.054442, Ridge 0.057085, CatBoost 0.054631. CatBoost 중요도 상위는 Huila 30일 평균 기온(25.6), 20거래일 수익률(11.5), BRL 환율(9.8)이다. 모델 설정에 테스트 구간은 사용하지 않았다.
- CatBoost 1.2.10과 pandas_market_calendars 5.4.0 및 필요한 의존성을 기존 환경에 추가했다. 과거 발표시각·수정 전 값 부재와 소스별 지연 가정은 notebook에 명시했다. 다음은 FastAPI·차트 화면.
- 검증: 30달력일 기상 집계·FRED 휴일 ffill·COT 발표 지연·5거래일 타깃·학습 경계를 확인했다. 차트 2개를 확인했고 `pip check`, `git diff --check`도 통과했다.

## 2026-09-13 — 디렉터리 정리

- 설계는 `architecture.md`, Yahoo 조사는 `troubleshooting.md`로 통합했다. ADR 4개·reports·references·일회성 tools·중복 수집본·과거 실행 notebook 사본을 제거했다. 이전 준비 문서와 긴 컬럼 사전은 소스 YAML·설계 노트로 정리했다.
- `data/raw/pilot_probe/`에 원응답 16개를 보관한다. FRED·NASA·CFTC는 2026-09-12 08:30 UTC 전체 수집본, Yahoo는 08:40 UTC 원응답 대조본이다. CFTC는 파일럿 기간에 해당하는 2024·2025년 ZIP만 남겼다.
- `backfill.py`를 `02_backfill_10y.py`로 이름만 변경했다. 2016~2025년 Parquet 12개, `.env`, 레거시 CSV 8개, 학부 notebook 4개·보고서 5개, 기존 테스트·requirements를 보존했다.
- 파일럿 notebook은 10셀, 출력은 검증 표 2개·가격 그래프 1개다. 기본 실행은 로컬 원응답을 읽으며 `REFRESH=True`일 때만 백필 스크립트로 작은 구간을 수집한다. manifest·run_id 폴더를 만들지 않는다.
- 검증: 기존 `.venv` 새 커널에서 전체 실행 통과. 12개 데이터셋의 날짜·행 수·공통 관측값을 이전 검증 CSV와 대조했다. COT는 날짜순으로 맞춰 비교했고, Yahoo 원응답의 Volume 결측을 유지했다. 커피 OHLC 범위 이탈은 기존과 같은 73행이다.
- 기본 샌드박스의 loopback 제한 때문에 notebook 실행은 로컬 소켓 권한으로 재실행했다. 외부 API 재수집·학습·패키지 변경·commit·push는 하지 않았다.
- 다음: 과거 Close 피처로 CatBoost와 단순 기준 모델 비교 → FastAPI·차트 화면.
