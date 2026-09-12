# Coffee Price Prediction

아라비카 커피 가격 연구를 위한 Core-4 데이터 접근·정합성 검증 프로젝트입니다. 현재 단계는 로컬 Notebook 하나에서 소량 데이터를 수집하고 원응답과 검증 결과를 보존하는 것입니다. 새 모델의 학습·채택이나 서비스 구현은 아직 이 단계에 포함하지 않습니다.

## 디렉터리 역할

| 폴더 | 역할 |
|---|---|
| `data/` | 실제 데이터: 원응답, 수집 테이블, 검증·전처리 CSV, 출처·요청·해시 메타데이터. 코드와 참고 문서는 제외 |
| `data_code/` | 데이터 수집·EDA·전처리 코드. 현재 활성 Notebook은 `01_small_batch_probe.ipynb` 하나 |
| `docs/` | 사람이 읽는 설계·의사결정·분석·포트폴리오 문서 |
| `model_code/` | 향후 모델 실험·학습·평가 코드. 현재 비어 있음 |
| `tests/` | 기능·회귀·환경 검증 코드와 fixture |
| `tools/` | 프로젝트 작업을 돕는 보조 도구. 실제 수집은 Notebook에서 실행 |

`tools/`는 모든 Python 코드를 넣는 폴더가 아닙니다. 데이터 수집·전처리 로직은 `data_code/`, 모델 로직은 `model_code/`, 테스트는 `tests/`처럼 역할을 기준으로 구분합니다. 필요해질 때 파일을 추가하며 빈 기능·프레임워크를 미리 만들지 않습니다.

## 현재 실행 방법

저장소 루트에서 기존 `.venv`의 CPython 3.14 커널로 [01_small_batch_probe.ipynb](data_code/01_small_batch_probe.ipynb)를 엽니다. 저장소의 `.env`에 있는 `FRED_API_KEY`를 사용하며 키 값은 출력하지 않습니다.

Notebook을 실행하면 실제 외부 요청이 발생합니다. 승인 구간은 `2023-12-31`–`2025-12-31`이며, 실행마다 고유한 `data/raw/probes/<run_id>/`에 저장합니다.

- `raw/`: requests 원응답 JSON·ZIP·텍스트.
- `library_return/`: yfinance 반환 표 CSV/PKL과 메타데이터. HTTP 원문과 구분합니다.
- `validation/`: 정규화·기간 필터 후 검증용 CSV. 학습용 전처리 완료 데이터라는 뜻은 아닙니다.
- `system/`: 요청 이력·manifest·검증 요약 등 데이터 추적용 메타데이터.

기존 수집분을 확인하기 위해 Notebook 전체를 다시 실행할 필요는 없습니다. 현재 상태와 데이터 해석은 [STATUS](docs/STATUS.md), [Core-4 데이터 사전](docs/data-dictionary-core4-probe.md), [Yahoo OHLC 기술 메모](docs/reports/yahoo-ohlc-technical-memo.md)를 먼저 확인합니다. 과거 진단 스크립트는 현재 실행 과정의 필수 단계가 아닙니다.

향후 전처리 산출물은 `data/processed/`처럼 raw와 분리해 저장합니다. 현재 이 위치에 새 학습 데이터셋을 만들지는 않았습니다.

## 보관 자료

| 위치 | 내용 |
|---|---|
| `data/old_data/` | 과거 프로젝트 CSV 8개 |
| `data_code/old_code/data_code/` | 과거 데이터 처리 Notebook 2개 |
| `data_code/old_code/model_code/` | 과거 모델 Notebook 2개. Attention 보관본에는 이전 작업의 수정이 있으므로 최초 원본과 동일하다고 주장하지 않음 |
| `data_code/old_code/probe_runs/` | 과거 Probe 실행 Notebook 사본. 활성 수집 Notebook과 구분 |
| `docs/old_docs/` | 과거 프로젝트 README·모델 결과 설명·PDF 보고서 |
| `docs/references/` | 조사에 사용한 외부 공식 참고 문서 |
| `docs/reports/evidence/` | 실행·코드 검토·보존 검사 등 상세 증거 |
| `tools/archive/` | 이미 끝난 일회성 진단 스크립트의 당시 버전 |

과거 manifest와 로그의 경로는 수집·실행 당시 기록입니다. 이번에 이동한 파일은 [경로 매핑·보존 검증](docs/reports/directory-reorganization-2026-09-12.json)으로 현재 위치를 찾을 수 있습니다. 폴더 정리는 수집값·가격 정의·검증 정책·모델 결과를 변경하지 않습니다.
