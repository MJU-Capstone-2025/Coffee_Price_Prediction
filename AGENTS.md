# Repository Guidelines

## 작업 방향

취업 준비용 학생 프로젝트입니다. 읽기 쉬운 코드와 실행되는 결과를 먼저 만드세요. 작업 시작 시 `Context.md`, `docs/STATUS.md`의 최신 항목과 현재 Git diff를 확인하고 기존 변경을 보존하세요.

- 수집은 `data_code/02_backfill_10y.py` 하나를 중심으로 구현합니다. 소스별 함수와 짧은 주석이면 충분합니다. 추상화·설정·보조 스크립트를 먼저 늘리지 마세요.
- 새 ADR, JSON manifest, 해시 목록, 별도 검증 보고서는 요청받지 않는 한 만들지 마세요. 필요한 근거는 위 통합 문서와 원응답으로 확인합니다.
- README는 프로젝트 소개, 실행법, 결과, Troubleshooting & 배운 점을 중심으로 씁니다. 실제로 겪은 문제와 선택 이유를 3~4줄로 설명하세요.
- 정기 배치·복구·모니터링은 기본 수집 → CatBoost 비교 → FastAPI와 차트 화면이 동작한 뒤 필요한 만큼 추가합니다.
- 확인하지 않은 원인·성과·개선율을 쓰지 마세요. 코드와 결과를 직접 설명할 수 있는 수준을 유지하세요.

## 파일 배치

- `data_code/`: 수집·EDA·전처리 코드. notebook은 저장된 파일럿의 표·그래프를 확인하며 요청할 때만 재수집합니다.
- `data/`: 수집 데이터와 전처리 테이블. 새 수집 결과는 `data/processed/<시작일>_<종료일>/`에 Parquet로 저장합니다. 코드·문서는 넣지 마세요.
- `configs/regions.yaml`: 기존 기상 요청 좌표. `configs/sources.yaml`은 간결한 API 소스 요약입니다.
- `tests/`: 필요한 기능·회귀 검사. 실제 수집 진입점으로 사용하지 마세요.
- `docs/STATUS.md`: 실제 변경·검증 결과·다음 작업을 짧게 기록합니다. 새 보고서로 내용을 중복하지 마세요.
- `data/raw/pilot_probe/`: 소스별 원응답 한 벌. run_id·manifest·요청 로그를 다시 생성하지 마세요.
- `docs/architecture.md`, `docs/troubleshooting.md`: 통합 설계·조사 문서.
- `data/old_data/`, `data_code/old_code/`, `docs/old_docs/`: 학부 원본 자료를 보존합니다. `.env`와 `data/old_data/`는 삭제하지 마세요.

## 환경과 코드

Apple Silicon Mac에서 uv로 관리하는 프로젝트 폴더 외부의 기존 가상환경 `$HOME/.virtualenvs/coffee-price-prediction`과 CPython 3.14를 사용합니다. 프로젝트 내부에 `.venv`를 만들거나 기존 가상환경을 재생성하지 마세요.

`.env`의 `COFFEE_VENV`와 `UV_PROJECT_ENVIRONMENT`는 이 외부 경로를 가리킵니다. `.env`에서는 `python-dotenv`도 홈 경로를 확장하도록 `${HOME}` 표기를 사용합니다. 셸에서 실행할 때는 다음과 같이 설정합니다.

```sh
export COFFEE_VENV="$HOME/.virtualenvs/coffee-price-prediction"
export UV_PROJECT_ENVIRONMENT="$COFFEE_VENV"
source "$COFFEE_VENV/bin/activate"
python data_code/02_backfill_10y.py
```

패키지는 `uv pip install --python "$COFFEE_VENV/bin/python" -r requirements.txt`처럼 대상 환경을 명시해 관리합니다.

Python은 공백 4칸, 함수·변수는 `snake_case`를 사용합니다. 패키지는 설치·검증 후에만 `requirements.txt`에 추가하세요. `.env`의 키는 환경변수로 읽고 출력·URL 로그·예외에 노출하지 마세요.

`data_code/` notebook의 표 항목명·그래프 제목·축 이름·범례·범주명은 한국어로 표시하세요. 첫 코드 셀에서 `platform.system()`에 따라 Windows는 Malgun Gothic, macOS는 AppleGothic, Linux/Colab은 NanumGothic을 설정하고 Linux 폰트 설치 방법을 안내하세요. Seaborn 테마에서도 선택한 폰트를 유지합니다. 데이터 컬럼은 표시할 때만 이름을 바꾸고, 저장된 차트의 글자 표시를 확인하세요. 모델명·티커·지표 약어는 필요하면 함께 적습니다.

## 필요한 검증

수집 코드를 바꾸면 작은 구간 또는 저장된 응답으로 확인하고 실제 실행 결과를 점검하세요. 날짜 정렬·중복·결측·빈 응답, 조인 전후 행 수를 확인합니다. 문서만 바꿨다면 관련 없는 테스트를 반복하지 마세요.

가격 결측이나 OHLC 범위 이탈을 임의 보정하지 않습니다. FRED의 `.`와 NASA의 결측 표시는 결측값으로 바꿉니다. 주말·휴장일을 가격 행으로 만들거나 미래 값으로 채우지 마세요.

모델은 시간 순서로 분할하고 학습 구간 뒤의 정답·전처리 통계가 유입되지 않게 합니다. 같은 기간의 단순 기준 모델과 MAE·RMSE를 비교하며 기간·horizon·seed를 함께 남깁니다. 실행하지 않은 단계는 완료라고 쓰지 마세요.

## 변경과 기록

현재 요청에 포함된 가역적 구현은 매번 승인이나 ADR을 요구하지 않고 진행하세요. 타깃 등 요청 범위를 벗어난 변경, 기존 자료 삭제, 유료 서비스·외부 공개는 필요한 경우에만 확인합니다.

작업이 끝나면 `git status`와 staged·unstaged diff를 확인하세요. 새 파일도 내용을 확인합니다. 서로 독립적인 변경은 섞지 말고 파일 또는 변경 목적별로 논리적인 커밋 단위를 나누세요. 최종 응답에는 단위별 대상 파일과 커밋 메시지를 작성합니다. 커밋은 사용자가 수동으로 하므로 직접 실행하지 마세요.

제목은 `<type>(<scope>)/<summary>` 형식으로 짧고 명확한 명령형으로 작성합니다. scope를 생략하면 `feat/10년 데이터 EDA 및 베이스라인 모델 비교 추가`처럼 씁니다. 제목만으로 변경 목적을 알 수 있어야 합니다.

- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `refactor`: 코드 리팩토링
- `style`: 동작 변경 없는 코드 포맷팅
- `docs`: 문서 수정
- `test`: 테스트 코드 추가·수정
- `chore`: 빌드·설정·패키지 관리 등

단순하지 않은 변경은 제목 다음에 빈 줄을 두고 본문에 변경 이유, 달라진 내용, 주요 영향 또는 주의점, 수행한 테스트를 적습니다. 연결된 이슈가 있을 때만 마지막에 `Closes #12` 같은 이슈 번호를 넣고, 번호를 임의로 만들지 마세요.

main에 직접 커밋하지 않고 항상 feature 브랜치와 PR을 사용합니다. 명시적인 요청 없이는 기존 커밋을 amend하거나 history를 rewrite하거나 force push하지 마세요. `reset --hard` 같은 파괴적 명령은 사용자가 직접 실행합니다.

PR에는 변경 목적, 실행법, 실제 검증 결과만 필요한 만큼 적습니다. 인증정보·개인 경로·가상환경·대량 수집 파일은 commit하지 마세요.
