# 프로젝트 맥락
- 목표: 커피 가격 수집 → CatBoost 비교 → FastAPI와 차트 화면.
- 환경: uv로 관리하는 프로젝트 외부의 Python 3.12 가상환경 `$HOME/.virtualenvs/coffee-price-prediction`을 사용한다. PyCaret은 4.0.0a8로 고정했다. `.env`의 `COFFEE_VENV`·`UV_PROJECT_ENVIRONMENT`도 이 경로를 사용하며, `.env`는 삭제하거나 출력하지 않는다.
- `configs/`: API 소스 요약과 브라질·콜롬비아의 6개 기상 요청 좌표.
- `data/old_data/`: 학부 프로젝트 원본 CSV. 삭제·덮어쓰기 금지.
- `data/raw/pilot_probe/`: 소스별 파일럿 원응답 한 벌. `data/processed/`: 현재 분석은 2014-07-01~2025-12-31 Core-4·ALFRED Parquet를 사용하며 이전 자료도 보존한다.
- `data_code/`: `01` 파일럿 → `02` 수집 → `03` EDA·기준 비교 → `03_2` 60일 입력 창·피처 그룹·Attention-LSTM 재검증. `04`는 이전 7/30/90일 실험으로 보존한다.
- `docs/architecture.md`, `docs/troubleshooting.md`: 설계 이유와 Yahoo 가격 조사 과정.
- 학부 코드·보고서는 `data_code/old_code/`, `docs/old_docs/`, 환경 검사는 `tests/`에 둔다.
- 최신 상태는 `docs/STATUS.md`에 짧게 기록한다. 새 감사 로그·manifest·중복 스냅샷은 만들지 않는다.
