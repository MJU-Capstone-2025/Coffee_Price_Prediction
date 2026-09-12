# 로컬 환경 검증 — 2026-09-12

## 범위와 실제 환경

Core-4 후보 구현의 의존성 호환성을 검증했다. 수집기, 데이터 소스 채택, 운영 스키마·가용성 정책, 모델·전처리 변경은 범위 밖이다. 기존 `.venv`를 사용했으며 재생성·Python 하향·패키지 대체·기존 패키지 제거는 하지 않았다.

- CPython 3.14.7, native arm64, macOS 27.0 (26A428).
- `sysconfig.get_platform()`: `macosx-26.0-arm64`; system-site-packages 비활성화.
- pip 26.2.1. 기존 `.venv`의 numpy 2.5.3, pandas 3.0.5를 보존하며 추가 27개 wheel 설치.
- 실제 설치 파일명·SHA-256 및 import/wheel 태그: [local-environment-packages.json](local-environment-packages.json). 파일에는 API 키·개인 Drive 경로·인증 URL을 기록하지 않는다.

## 설치 명령과 결과

```sh
.venv/bin/python -m pip --isolated --disable-pip-version-check --no-cache-dir install --index-url https://pypi.org/simple --only-binary=:all: --report /tmp/coffee-core4-install.json numpy==2.5.3 pandas==3.0.5 requests duckdb pyarrow PyYAML openpyxl yfinance pytest
.venv/bin/python -m pip --isolated --disable-pip-version-check check
```

첫 설치는 샌드박스의 `pypi.org` DNS 해석 실패로 exit 1. `No matching distribution found for requests`도 함께 출력됐지만 네트워크 오류였으므로 패키지 비호환으로 분류하지 않았다. 권한 확대한 동일 명령 재시도는 exit 0, 27개 추가 설치 성공. `pip check`는 **No broken requirements found.**

`--only-binary=:all:`은 소스 배포본 빌드를 허용하지 않는다. 아키텍처 독립 패키지의 `py3-none-any` 및 arm64를 포함하는 `universal2`도 현재 환경의 유효 wheel이다. [pip 공식 설치 옵션](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-only-binary)

| 직접 의존성 | 실측 버전 | 용도 | wheel |
|---|---|---|---|
| numpy | 2.5.3 | 표 연산 기반, 기존 설치 유지 | cp314 / macosx_14_0_arm64 |
| pandas | 3.0.5 | CSV·표·시각 및 파일 인터페이스, 기존 설치 유지 | cp314 / macosx_11_0_arm64 |
| requests | 2.34.2 | FRED·NASA·CFTC·GSCPI 후보 HTTP 접근 | py3-none-any |
| duckdb | 1.5.5 | 로컬 Parquet SQL 조회 | cp314 / macosx_11_0_arm64 |
| pyarrow | 25.0.1 | Parquet 저장·읽기 | cp314 / macosx_12_0_arm64 |
| PyYAML | 6.0.3 | 후보 YAML 설정 파싱 | cp314 / macosx_11_0_arm64 |
| openpyxl | 3.1.5 | Excel 제공 자료 후보 파서; 실제 소스 workbook 형식은 미검증 | py2/py3-none-any |
| yfinance | 1.7.0 | Context에 있는 Yahoo 접근 후보 검증 | py3-none-any |
| pytest | 9.1.1 | 로컬 테스트 실행 | py3-none-any |

native 의존성 `curl_cffi 0.16.3`, `cffi 2.1.1`, `lxml 6.1.3`, `protobuf 7.36.1`도 현재 interpreter와 wheel 태그 교집합 및 import 확인에 성공했다. yfinance 설치·fixture 성공은 Yahoo 소스 채택이나 재배포 가능성·실제 접근 성공을 의미하지 않는다. 프로젝트는 Yahoo의 공식 도구가 아님을 명시한다. [yfinance 프로젝트 설명](https://pypi.org/project/yfinance/)

## 기능 테스트와 실제 실패

```sh
.venv/bin/python -m pytest -q tests/test_core4_environment.py
.venv/bin/python -m pytest -q tests/test_core4_environment.py -k http_transport_loopback_only
```

첫 전체 실행: **16 passed, 1 failed, 2 errors (3.97s)**.

- 13개 패키지 import/wheel, 승인된 runtime, YAML/ZIP/CSV/Excel fixture, yfinance quote parser fixture는 성공했다.
- HTTP 2개는 샌드박스의 `127.0.0.1` bind `PermissionError: [Errno 1] Operation not permitted`였다. 권한 확대한 HTTP 전용 재실행: **2 passed, 17 deselected (1.23s)**. requests와 curl_cffi의 loopback HTTP 왕복이며 외부 API·TLS 검증은 아니다.
- Parquet 왕복은 모두 null인 `published_at`의 `timestamp[s, tz=UTC]`가 저장 후 `timestamp[ms, tz=UTC]`로 바뀌어 `Table.equals`에서 실패했다. 진단 재현에서 값 리스트와 null 개수(2)는 동일했다. 뒤에 있는 pandas 및 DuckDB 왕복 assertion은 첫 실패 때문에 아직 실행되지 않았다.
- PyArrow 문서는 Parquet에 초 해상도가 없어 기본적으로 밀리초로 변환한다고 명시한다. 따라서 이 증거는 Python 3.14/arm64 비호환이나 데이터 손실을 입증하지 않는다. [PyArrow write_table의 coerce_timestamps](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html)

사용자의 패키지 테스트 실패 승인 절차에 따라 처리안을 요청했다. A: fixture 시각을 UTC microseconds로 명시하고 초→밀리초는 별도 테스트(추천). B: dtype 대신 값·timezone·null만 비교. C: 검증 보류. 실제 데이터 시간 정책이나 Python·패키지는 어느 안에서도 자동 변경하지 않는다. 승인 응답 전에는 실패 assertion을 우회하거나 성공으로 기록하지 않는다.

## 미검증 경계

- Core-4 live API 수집: **미실행**. 인증키·실제 응답·소스 단위·공개일·빈티지·coverage는 검증하지 않았다.
- 새 checkout에서 `.venv` 재생성과 전체 transitive dependency의 완전 고정 재설치는 미실행.
- 모델용 torch, LightGBM, entmax, scikit-learn 및 Jupyter 실행·MPS 학습은 이번 Core-4 호환성 범위 밖이다. 기존 설치 목록을 그대로 requirements에 넣지 않는다.
- raw·정규화·파생 피처·예측 이력 변경 없음. 테스트의 합성 관측은 메모리 및 임시 디렉터리에서만 사용한다.
