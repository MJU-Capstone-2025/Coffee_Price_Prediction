# Baseline audit — 레거시 조사와 로컬 환경 경계

- 조사일: 2026-09-12
- 기준: `develop`, `004ac9760611f658fef140ce617728f3f1e30b49`.
- 방법: notebook JSON의 소스·저장 출력 분리 조사, CSV의 기계적 품질 검사, 파일 SHA-256 비교. 학습·재예측·타깃 관계 EDA·holdout 평가는 실행하지 않았다.
- 재현: `.venv/bin/python tools/audit_baseline.py`. 상세 증거: [baseline-inventory.json](reports/baseline-inventory.json).
- 셀 번호는 markdown을 포함하는 **1-based notebook 위치**이며 execution_count가 아니다.

2026-09-12 후속 사용자 지시로 notebook 4개를 별도 보관했다. 아래 표와 최초 inventory의 경로는 **최초 조사 시점 경로**다. 현재 데이터는 `data/old_data/`, notebook은 `data_code/old_code/{data_code,model_code}/`, 과거 문서는 `docs/old_docs/`에 있다. 최초 [이동 매핑·SHA-256](reports/legacy-notebook-move.json)은 당시 기록으로 보존한다. 최신 [배치·보존 검사](reports/directory-reorganization-2026-09-12.json)에서 과거 17개 파일의 현재 위치를 확인했으며, Attention notebook 하나는 이전 작업에서 이미 수정되어 최초 SHA-256과 다르다. 이번 배치 정리로 그 내용을 바꾸거나 원본으로 되돌리지 않았다. 감사 스크립트는 과거 자료 폴더만 읽고 현재 Probe CSV를 레거시 Date 스키마로 처리하지 않는다.

## 문서·구현·Git 대조

`Context.md`의 초기화 완료와 기존 `.venv` 존재는 확인했다. 다만 작업 시작 시 STATUS, ADR, baseline audit, Core-4 수집기·설정·테스트는 없었다. 새 초기화를 수행하지 않고 사용자 “없으면 만들어” 지시로 STATUS를 생성했다. 루트 AGENTS의 notebook 중심 설명은 레거시에는 맞지만 신규 Core-4 구현 완료를 의미하지 않는다.

작업 시작의 unstaged 삭제: 루트 README와 docs의 PDF 3개. 대응하는 `docs/old_docs/` README·PDF는 모두 HEAD 원본과 byte 단위로 일치했다. 사용자 이동 및 staging 상태를 변경하지 않았다. 데이터 8개, notebook 4개, model README 1개, old_docs 4개 총 **17개**의 해시를 보존한다. PDF 내용 분석이나 보고서 지표의 재현 검증은 수행하지 않았다.

`.gitignore`는 `AGENTS.md`, `Context.md`, `STATUS.md` 및 자기 자신을 무시한다. 이 때문에 문서의 존재 여부를 `git status`만으로 판단할 수 없다. 기존 무시 규칙은 유지했다.

## Colab 의존성 인벤토리

| 파일 | 실행 소스 셀 | 저장 출력·해석 |
|---|---|---|
| `data_code/기후데이터_FeatureSelection.ipynb` | 셀 1: `/content/drive/...` CSV 읽기 | 셀 8 출력에 `google.colab` JS. Python import가 아님 |
| `data_code/기후데이터_수확기_평균값_매핑.ipynb` | 셀 1, 22: `/content/drive/...` CSV 읽기 | Drive mount 소스 없음 |
| `model_code/MultiStepLSTM_거시경제_기후사용.ipynb` | 셀 1, 2: `/content/drive/...`; 셀 18: `cuda` 가능 시 사용, 아니면 `cpu` | 셀 26 출력에 `google.colab` JS |
| `model_code/Attention_LSTM_모델학습_예측결과활용.ipynb` | 셀 1: `pip install entmax`; 셀 4: `/content/drive/...`; 셀 24: `cuda` 가능 시 사용, 아니면 `cpu` | 셀 1 저장 출력에 NVIDIA/CUDA Linux wheel 설치 로그 |

- 4개 notebook 실행 소스에 `google.colab` import와 `drive.mount(...)`는 **없다**. mount 셀이 없다고 Drive 의존성이 없는 것은 아니다. 절대경로가 세션 외부 Drive 준비를 전제한다.
- 정확히 `!pip` 또는 `%pip`로 시작하는 설치 셀은 **없다**. Attention의 bare `pip install entmax`는 notebook/IPython 설치 명령이므로 함께 식별했다.
- 두 모델 모두 CPU fallback이 있어 CUDA 필수라고 단정할 수 없다. MPS 선택 분기는 없다. 저장된 CUDA 설치 성공은 현재 Mac 호환성의 증거가 아니다.
- 새 구현은 저장소 기준 경로와 외부 `.venv` 패키지 설치를 사용한다. 원본 셀·출력·기후 피처·모델 설정은 보존했다. notebook의 로컬 실행 이전과 모델·전처리 교정은 후속 별도 작업/commit 대상이다.

## 실제 전처리·모델 확인 사항

| 근거 | 확인 사실 | 영향 및 후속 검증 |
|---|---|---|
| FeatureSelection 셀 3, 6–13 | `train_test_split(..., random_state=42)`에서 시간 순서 분리 옵션 없이 LightGBM 학습·early stopping 후 상위 7개 피처 CSV 저장 | 새 검증에서는 피처 선택·튜닝을 각 학습 경계 안으로 제한해야 한다. 현재 결과를 독립적인 미래 검증으로 채택하지 않음 |
| 수확기 매핑 셀 7, 23 | 전체 프레임에 ffill 다음 bfill | bfill은 미래 행 값을 사용할 수 있다. 실제 어떤 행이 영향을 받았는지는 미추적. 단순 경로 이전과 별도로 교정 필요 |
| 수확기 매핑 셀 14–16 | 수확 블록 전체 평균을 계산하되 `current_date > end_date`인 블록 중 가장 최근 것을 선택 | 미완료 수확기의 평균을 항상 쓴다고 단정하지 않음. 기상 공개일·빈티지 및 선행 bfill의 영향은 별도 미검증 |
| MultiStepLSTM 셀 7–8 | 80% 분할 후 학습 프레임에만 MinMaxScaler fit | 전체 구간 scaler fit 누수는 이 코드에서 확인되지 않음 |
| MultiStepLSTM 셀 9, 11, 15, 19, 21–27 | 100행 창, 14행 예측, 입력 step=6; shuffle=True loader에서 hidden state를 batch 간 전달; 마지막 학습 dataset 입력으로 예측한 값을 학습 종료 다음 14행과 비교 | 입력 시점·평가 날짜의 정렬과 hidden state 연결을 별도 검증해야 함. 14행을 승인된 14거래일 계약으로 해석하지 않음 |
| Attention 셀 9–12 | 80/20 순서 분할 후 StandardScaler를 학습에만 fit. `X_train`은 scaled, `X_test`는 원본 `test_df`에서 생성 | 테스트 입력 스케일 불일치 확인. 전체 구간 scaler fit 누수와 구분 |
| Attention 셀 10, 12, 32, 38, 58, 64 | 타깃 수익률은 scaler 적용 전 값으로 되돌렸지만 예측 수익률에 다시 scaler inverse_transform | 타깃 변환·복원 경로 불일치 확인. 수정 효과나 지표는 재실행 전 미확정 |
| Attention 셀 20–21 | LSTM 출력에 Entmax attention, context와 last hidden의 학습 gate, static 피처 및 FC 사용 | 실제 Attention-LSTM 구현 존재. Attention의 독립적인 성능 기여는 통제 비교 전 미확정 |
| Attention 셀 25, 28 | `test_loader` 손실로 매 epoch scheduler 갱신 | 이 구간은 모델 선택에 사용된 validation 성격. 미사용 최종 holdout으로 주장할 수 없음 |
| Attention 셀 32–40, 50–66 | target date별 여러 예측을 평균; 7·14행 horizon 및 미래 `freq='D'`; 2024–2025 구간 그래프 코드 | 발행 시각·horizon별 예측 이력이 분리되지 않음. 기존 연구에서 본 구간을 새 미사용 holdout이라 부를 수 있는지는 승인 전에 확인 필요 |

표는 정적 코드 조사 결과다. 레거시 버그를 이번에 수정하거나 성능 개선을 검증한 것으로 해석하지 않는다. 두 notebook의 데이터·타깃·평가 구간이 다르므로 기존 README의 수치를 같은 조건 비교로 재사용하지 않는다.

## 데이터 계층과 기계적 품질

현재 `data/`에는 아래 계층이 섞여 있다. **이번에는 분류만 기록했으며 파일 이동·스키마 변경·원값 수정은 없다.**

| 파일 | 행 × 열 | 계층 해석 | 날짜 범위 |
|---|---:|---|---|
| `coffee_oil_exchange_daily.csv` | 2,905 × 6 | 공급원 필드에 가까운 가격·환율 통합본. 원응답으로 입증되지 않음 | 2015-03-23–2025-03-21 |
| `weather.csv` | 33,602 × 11 | 기상 관측형 값 + `season_tag`, `days_until_harvest` 파생값 혼재 | 2015-01-01–2025-03-23 |
| `커피가격데이터통합.csv` | 2,905 × 7 | 가공 통합본 + 수익률 파생값 | 2015-03-23–2025-03-21 |
| `거시경제및커피가격통합데이터.csv` | 2,556 × 51 | 가공 거시·가격·파생값 통합본 | 2015-03-23–2023-12-29 |
| `기후평균커피가격통합데이터.csv` | 2,742 × 70 | 가격 + 수확 평균 파생 피처 | 2015-10-01–2025-03-21 |
| `기후데이터피쳐선택.csv` | 2,742 × 9 | 타깃 기반으로 선택된 파생 피처 | 2015-10-01–2025-03-21 |
| `비수확기평균커피가격통합데이터.csv` | 2,742 × 16 | 이름은 비수확기이나 컬럼은 `_harvest_mean`; 생성 의미 미확인 | 2015-10-01–2025-03-21 |
| `Coffee_Price_Weather.csv` | 2,742 × 13 | 가격·유가·환율 + 9지역 강수 수확 평균. Attention 입력 | 2015-10-01–2025-03-21 |

- `Date`는 모든 행에서 ISO 날짜 파싱에 성공했다. 비기상 파일은 날짜 순서이며 검사 키 `Date` 중복 0건. 기상 파일은 전체 날짜 순서는 아니지만 9개 `locationName`별 날짜 순서이고 `(Date, locationName)` 중복 0건이다. 이는 조사용 키이며 신규 스키마 채택이 아니다.
- CSV 전체 행 중복은 모두 0건이다. 빈 문자열 셀은 `coffee_oil_exchange_daily.csv`에 1,674개, 다른 파일은 0개다. 이 검사는 sentinel, 잘못된 값, 공급원별 예정 관측 대비 coverage까지 검증하지 않는다.
- 새 6지역 후보와 기존 9지역(에티오피아 포함)은 다르다. 기존 좌표·지역 피처를 Core-4 대표성 정책으로 자동 채택하지 않는다.
- 원자료: 원응답 payload·공급원 요청·필드 정의·원단위가 함께 보존된 자료는 확인되지 않았다.
- 정규화: 단위·시간대·가격 Close/Settlement·계약 연결 규칙을 입증하는 설정이 없다. 컬럼명만으로 USD/lb, 환율 방향 등을 확정하지 않는다.
- 파생 피처: 수익률·수확 평균·선택 피처·계절 태그는 수집값과 구분한다.
- 시스템 메타데이터: raw snapshot hash, 요청 이력, parser version, 발행 시각별 forecast/evaluation 원장은 현재 구현에서 확인되지 않았다. 이번 파일 해시는 보존 감사용이며 과거 공급원 snapshot hash가 아니다.

## 관측·공개·수집·이용 가능 시점

8개 CSV에는 `Date`만 있고 `published_at`, `ingested_at`, `available_at`, `availability_basis`, `vintage` 컬럼은 없다. `Date`는 레거시 행의 날짜이지 검증된 공개 시각이 아니다. 파일 수정 시각 또는 이번 조사 시각을 과거 수집 시각으로 대입하지 않는다.

원응답 및 과거 수정 이력이 없으므로 이 저장소만으로 당시 빈티지를 복원할 수 없다. 공개·이용 가능 시점은 **unknown**이고, 기존 기상·거시 값의 사후 수정 여부도 미확인이다. 임의 shift나 지연 가정만으로 당시 이용 가능 데이터를 재현했다고 주장하지 않는다. 새 데이터 계약은 관측 기간, 공개 시각, 수집 시각, 이용 가능 시각과 근거를 분리하고 승인 후 구현해야 한다.

## 다음 작업 경계

환경 선택의 근거는 [ADR-001](adr/ADR-001-local-development-environment.md), 환경 smoke test 결과는 [STATUS](STATUS.md)와 [환경 보고서](reports/local-environment-validation.md)에 기록한다. 이 감사 당시에는 라이브 Core-4 수집·정규화 구현이 없었으며 fixture 결과를 API 수집 성공으로 세지 않는다. 당시 다음 작업은 Phase 0 데이터·평가 계약 초안과 중요 결정 승인이었다. 이후 구현·검증 결과와 현재 작업 범위는 STATUS를 따른다.
