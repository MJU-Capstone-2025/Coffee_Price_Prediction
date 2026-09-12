# 프로젝트 맥락
- 목표: 커피 가격 수집 → CatBoost 비교 → FastAPI와 차트 화면.
- 환경: uv로 관리하는 프로젝트 외부의 기존 Python 3.14 가상환경 `$HOME/.virtualenvs/coffee-price-prediction`을 유지한다. `.env`의 `COFFEE_VENV`·`UV_PROJECT_ENVIRONMENT`도 이 경로를 사용하며, `.env`는 삭제하거나 출력하지 않는다.
- `configs/`: API 소스 요약과 브라질·콜롬비아의 6개 기상 요청 좌표.
- `data/old_data/`: 학부 프로젝트 원본 CSV. 삭제·덮어쓰기 금지.
- `data/raw/pilot_probe/`: 소스별 파일럿 원응답 한 벌. `data/processed/`: 10년치 Parquet.
- `data_code/`: `01` 파일럿 확인 → `02` 10년 수집 → `03_eda_and_baseline_models.ipynb` EDA·모델 비교.
- `docs/architecture.md`, `docs/troubleshooting.md`: 설계 이유와 Yahoo 가격 조사 과정.
- 학부 코드·보고서는 `data_code/old_code/`, `docs/old_docs/`, 환경 검사는 `tests/`에 둔다.
- 최신 상태는 `docs/STATUS.md`에 짧게 기록한다. 새 감사 로그·manifest·중복 스냅샷은 만들지 않는다.
