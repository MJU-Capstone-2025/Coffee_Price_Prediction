# Core-4 단일 notebook 실제 접근·정합성 검증

- 실행일: 2026-09-12. Git: `develop` / `004ac9760611f658fef140ce617728f3f1e30b49`.
- Notebook: `data_code/01_small_batch_probe.ipynb`, 6개 논리적 섹션·28개 셀. 새 커널에서 코드 셀 22개를 순서대로 실행했고 실행 오류 없이 종료했다.
- Run ID: `20260912T063021795259Z_99d695f0`.
- 승인 구간: **2023-12-31~2025-12-31, 양끝 포함**. 달력상 732일. Yahoo 요청의 exclusive end만 2026-01-01로 설정한 뒤 승인 구간으로 필터링했다.
- 결정문: [ADR-003](../adr/ADR-003-probe-weather-locations.md), **Accepted — Probe 범위 한정**. 기존 Context 및 ADR-001/002는 수정하지 않았다.

## 결론과 상태의 의미

12개 데이터셋 모두 실제 외부 수집과 파싱에 성공했다. 요청 실패·인증 실패·접근 제한은 없었다. FRED/NASA/CFTC의 직접 HTTP 요청 15건은 모두 첫 시도 HTTP 200이었다. Yahoo history 호출 2건은 성공했지만 내부 HTTP 상태를 직접 확보하지 못해 `null`로 기록했다. manifest의 request_count=17은 이 15건과 history 2건의 합이며 Yahoo 내부 HTTP·메타데이터 호출 수를 뜻하지 않는다.

**품질 검증은 Yahoo 2건 failed, 나머지 10건 warning**이다. warning에는 과거 available_at·빈티지 미복원이라는 한계가 포함된다. FRED의 두 시리즈에는 공급자 결측도 있다. 이 상태를 모든 품질 검증 통과 또는 누수 없는 학습 데이터셋 완성으로 표현하지 않는다.

이번 실제 API 실행은 과거 환경 테스트의 fixture 성공과 별개다. 기존 Parquet timestamp fixture 실패는 해결하지 않았고 이전 승인 대기를 유지한다.

## 실행 환경과 의존성

- 실제 커널: `/Users/sj/MyDrive/MyWorkspace/Projects/Coffee_Price_Prediction/.venv/bin/python`.
- CPython **3.14.7**, **macOS 27.0**, **arm64**, 저장소의 기존 `.venv`.
- numpy 2.5.3, pandas 3.0.5, requests 2.34.2, yfinance 1.7.0.
- 최소 설치안을 제시한 뒤 추가: python-dotenv 1.2.3, ipykernel 7.3.0, nbformat 5.11.1, nbclient 0.11.0 및 그 전이 의존성. 총 33개 wheel 설치, 기존 57개 패키지 버전 유지. Python 변경·환경 재생성·기존 패키지 교체 없음.
- 네이티브 의존성은 arm64/universal2 wheel로 설치됐으며 해당 커널의 순차 실행으로 import·실제 사용을 검증했다. 모든 새 wheel 이름·해시는 `core4-probe-environment-2026-09-12.json` 참조.
- 기존 `requirements.txt`는 수정하지 않았다. 이번 기록은 사용한 패키지·설치 wheel의 증거이며 기존 manifest의 모든 패키지를 검증했다는 뜻이 아니다. JupyterLab은 추가 설치하지 않았다.
- `.env`는 notebook 시작 위치(`data_code/`)에서 저장소 루트를 찾아 명시적으로 로드했다. `FRED_API_KEY`의 존재 여부만 출력했고 세 시리즈 인증 성공을 확인했다. NASA_API_KEY는 요청에 사용하지 않았다.

## 소스별 행 수·구간·단위

아래 결측은 **검사 대상 값의 셀 수**다. 날짜 중복은 모든 검증 테이블에서 0건이다. 행 수는 공급자의 거래일·영업일·보고일 기준이며 732개 달력 날짜를 임의로 채우지 않았다.

| source / dataset | 원본 행 → 검증 행 | 실제 관측/보고 구간 | 단위 확인 | 결측 셀 | 품질 결과 |
|---|---:|---|---|---:|---|
| Yahoo KC=F | 506 → 506 | 2024-01-02~2025-12-31 | US cents/lb | 8 | failed: Close 범위 이탈 73행 |
| Yahoo BRL=X | 523 → 523 | 2024-01-01~2025-12-31 | BRL per USD | 16 | failed: OHLC 범위 이탈 고유 4행 |
| FRED DFF | 732 → 732 | 2023-12-31~2025-12-31 | Percent | 0 | warning: 빈티지/공개시각 미복원 |
| FRED DTWEXBGS | 523 → 523 | 2024-01-01~2025-12-31 | Index Jan 2006=100 | 22 | warning: 원본 `.` 22개 및 빈티지 한계 |
| FRED DCOILWTICO | 523 → 523 | 2024-01-01~2025-12-31 | Dollars per Barrel | 25 | warning: 원본 `.` 25개 및 빈티지 한계 |
| NASA 6지점 합계 | 4,392 → 4,392 | 모두 2023-12-31~2025-12-31 | mm/day, °C, %; UTC | 0 | 기초 수치 검사 위반 0; available_at warning |
| CFTC 083731 | 전체 시장 39,765 → Coffee C 105 | 2024-01-02~2025-12-30 | contracts | 0 | 기초 수치 검사 위반 0; 공개시각 warning |

### Yahoo: 발견된 이상을 그대로 보존

`auto_adjust=False`, `back_adjust=False`, `repair=False`, `actions=False`, `keepna=True`, `rounding=False`. 가격 변환·롤오버 보정·삭제·보간은 하지 않았다. `library_return/yahoo/`의 CSV와 pickle은 **공급자에서 받은 가공 전 라이브러리 반환값**이며 HTTP 원문이 아니다. pickle은 실행 결과의 dtype/index 보존용이고 검토에는 CSV를 사용할 수 있다.

KC=F 응답의 currency는 **USX**였고 [ICE Coffee C 상품 명세](https://www.ice.com/products/15/Coffee-C-Futures)의 cents/lb와 교차 확인했다. USD만으로 추정하지 않았다. 메타데이터 이름은 조회 당시 `Coffee Dec 26`이며 2024~2025 전체 기록의 개별 계약·연결·롤 구성은 이 이름만으로 확인되지 않는다. BRL=X는 공급자 이름 `USD/BRL`과 currency `BRL`을 함께 확인했다.

- KC=F: 유효 OHLC 행에서 High < Low 0, Open 범위 이탈 0, **Close 범위 이탈 73행**. OHLC 전체 결측 2행=8셀. Volume 0은 33행, Volume 결측 0.
- BRL=X: High < Low 0, Open 범위 이탈 3행, Close 범위 이탈 4행; **두 조건의 합집합은 4행**. OHLC 전체 결측 4행=16셀. Volume은 523행 모두 0이며 환율에서 이를 선물 거래량 오류로 판정하지 않았다.
- KC=F 예: 2024-02-27 Low 188.550003, High 192.550003, Close 194.050003. BRL=X 예: 2024-01-01 Low 4.851800, Open/Close 4.850500. 보고서 숫자만 소수 6자리로 표시했고 저장값은 변환하지 않았다.
- 범위 이탈의 원인(정산·필드 의미·공급자 문제 등)은 아직 확인하지 않았다. 이를 단순 오타나 롤오버 문제로 단정하지 않는다.

### FRED: 원본과 결측 변환 구분

시리즈별 observations와 series metadata 각각 HTTP 200. raw JSON의 `.`는 유지하고 validation CSV에서만 결측으로 변환했다. metadata의 units/frequency/seasonal_adjustment와 응답의 realtime_start/end를 보존했다. DFF는 Daily, 7-Day이고 732일 모두 존재한다. 다른 두 시리즈의 결측일 원인을 이번 검증에서 전부 판정하지 않았다.

일괄 음수 오류 규칙을 적용하지 않았다. 조회 시점의 현재 스냅샷이며 당시 공개본 재현이 아니다. metadata의 last_updated나 realtime 필드를 개별 관측치의 발표일로 사용하지 않았다. GSCPI는 요청하지 않았다.

### CFTC: 원본 다운로드 범위와 승인 구간 분리

[CFTC 공식 연간 아카이브](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm)의 **Disaggregated Futures Only** `fut_disagg_txt_YYYY.zip` 3개와 압축 해제한 원본 텍스트를 별도로 보존했다. Combined/Legacy로 대체하지 않았다.

| 아카이브 연도 | 전체 시장 원본 행 | Coffee C 원본 행 | 승인 구간 Coffee C 행 |
|---|---:|---:|---:|
| 2023 | 12,534 | 52 | 0 |
| 2024 | 13,601 | 53 | 53 |
| 2025 | 13,630 | 52 | 52 |

2023 Coffee C 마지막 report_date는 2023-12-26이므로 2023-12-31 시작 필터에서는 0행이다. 이 연도를 별도 Coffee 수집 성공으로 세지 않았다. 전체 검증 결과는 105행으로 0건 성공 처리가 아니다.

확인한 실제 원본 컬럼: `CFTC_Contract_Market_Code`, `Market_and_Exchange_Names`, `Report_Date_as_YYYY-MM-DD`, `Open_Interest_All`, `M_Money_Positions_Long_All`, `M_Money_Positions_Short_All`. 모든 코드가 문자열 `083731`, 시장명은 `COFFEE C - ICE FUTURES U.S.`다. 숫자 파싱 실패·결측·음수·날짜 중복은 0건이다. 원본 연간 파일의 행 순서를 유지한 검증 CSV는 날짜 오름차순이 아니며 `dates_sorted=false`로 기록했다. 학습용 정렬·주간 병합은 하지 않았다.

[CFTC 설명](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm)에 따라 단위는 계약 수다. report_date는 보고 기준일이며 실제 개별 발표시각은 확보하지 않아 published_at/available_at은 비워 두었다.

## 기상 6지점 품질과 중복

모두 HTTP 200, payload messages 빈 배열, 5개 변수 존재, UTC 명시를 확인했다. 응답 API 버전은 v2.9.7이고 sources는 MERRA2/POWER다. 응답 fill_value는 **-999.0**이며 실제 등장 횟수는 각 지점·변수 모두 0이다.

| region_id | 행 수 | 날짜 누락 / 중복 | 값 결측 / sentinel | 강수·습도·기온 관계 위반 |
|---|---:|---|---|---:|
| br_sul_minas | 732 | 0 / 0 | 0 / 0 | 0 |
| br_cerrado | 732 | 0 / 0 | 0 / 0 | 0 |
| br_alta_mogiana | 732 | 0 / 0 | 0 / 0 | 0 |
| co_huila | 732 | 0 / 0 | 0 / 0 | 0 |
| co_caldas | 732 | 0 / 0 | 0 / 0 | 0 |
| co_antioquia | 732 | 0 / 0 | 0 / 0 | 0 |

15개 지점 쌍 × 5변수=**75개 비교**에서 공통 유효 날짜는 각각 732일이고, 변수별 완전 일치 및 5변수 전체 동일 지점 쌍은 **0건**이다. all-missing을 정상 동일 시계열로 간주한 비교도 없다.

| 변수 | 15개 지점 쌍 Pearson 상관 최솟값~최댓값 |
|---|---|
| PRECTOTCORR | -0.058878~0.703793 |
| T2M | 0.003794~0.915104 |
| T2M_MIN | -0.101555~0.919361 |
| T2M_MAX | 0.008881~0.878177 |
| RH2M | -0.087193~0.943101 |

일부 상관은 높지만 동일 격자라는 판정 근거로 쓰지 않는다. 응답 geometry의 위경도 6쌍은 요청 좌표를 소수 3자리로 반올림한 값과 일치했다. 이는 요청점 재표시와 부합한다는 **사후 비교 결과**이며 원천 격자 중심의 증명이 아니다. notebook의 기본 비교는 정확도 허용 범위에 따라 일부를 unknown으로 기록했고 원본 geometry를 모두 보존했다. grid_id·격자 중심좌표는 생성하지 않았다. 별도 관측장비 값, 공간 대표성, 서리 라벨 또는 생산량 영향은 확인하지 않았다.

좌표 근거의 확인 수준은 [STATUS의 ADR-003 조사 기록](../STATUS.md#adr-003에서-이관한-조사실행-기록)을 따른다. ICO 수치·Franca 본문은 확인했지만 Três Pontas·콜롬비아 원문 일부에 접근하지 못했고 Patrocínio의 정확한 좌표도 독립 확인하지 못했다. 사용자 승인 좌표를 변경하지 않았다.

## 저장 위치와 데이터 계층

실행 루트: `data/raw/probes/20260912T063021795259Z_99d695f0/`.

- `raw/fred/`, `raw/nasa/`: requests 응답 JSON 바이트. `raw/cftc/`: 공식 ZIP 및 압축 해제 원본 텍스트. 정상 응답 원문에 비밀정보 치환은 발생하지 않았다.
- `library_return/yahoo/`: 변환 전 yfinance CSV/pickle 및 반환 메타데이터.
- `validation/`: 소스별 정규화·승인 구간 필터 CSV 12개 및 weather_pairwise.csv. 원본 응답과 다르며 파생 예측 피처는 없다.
- `system/`: 안전한 요청 로그, 시리즈/변수 메타데이터, 개별 검증 결과, 종합표 CSV/JSON, manifest, 실행된 notebook 사본. `retrieved_at`은 UTC이며 발표일·관측일과 구분했다.
- manifest의 65개 참조 산출물 SHA-256을 대조했고 불일치 0건. manifest 자신의 해시는 자기 참조를 피하기 위해 목록에서 제외했다.

## 실행한 검증과 재실행

| 명령 또는 검사 | 결과 |
|---|---|
| `.venv/bin/python -m pip ... install --dry-run --only-binary=:all: ...` | sandbox DNS 실패 후 권한 확대 요청으로 계획 검증 성공 |
| `.venv/bin/python -m pip --isolated --disable-pip-version-check --no-cache-dir install --only-binary=:all: --index-url https://pypi.org/simple --constraint /tmp/coffee-probe-existing-constraints.txt --report /tmp/coffee-probe-install.json python-dotenv==1.2.3 ipykernel==7.3.0 nbformat==5.11.1 nbclient==0.11.0` | exit 0, 33 wheel 설치, 기존 57개 버전 불변 |
| `.venv/bin/python -m pip --isolated --disable-pip-version-check check` | No broken requirements found |
| `.venv/bin/python -m ipykernel install --prefix .venv --name coffee-probe --display-name 'Coffee Probe (.venv Python 3.14)'` | 저장소 `.venv` 내부 kernel 등록 성공 |
| `nbformat.validate` + 코드 셀 `ast.parse` | 통과 |
| `.venv/bin/python /tmp/execute_coffee_probe.py` | 권한 승인 후 실제 외부 요청, 새 커널에서 22개 코드 셀 순차 실행, exit 0. 임시 실행 보조 파일은 저장소 구현에 추가하지 않음 |
| `.venv/bin/python -m nbclient --help` | `__main__` 미제공 확인. 재실행은 아래 Python API 사용; 패키지 교체 없음 |
| `.venv/bin/python /tmp/verify_coffee_probe.py` | manifest 65개 SHA-256 일치, raw→validation 값 대조 통과, 22개 셀 실행 확인, 71개 산출물/문서에서 비밀값 검출 0, `git diff --check` 통과 |
| 기존 파일·원본 notebook 보존 검사 | STATUS 갱신 전 기존 30개 파일 모두 동일. 갱신 후에는 STATUS만 변경, 나머지 29개 불변. 레거시 notebook 4개는 현재 HEAD 원문과도 byte 일치 |

기존 notebook 편집기에서 `Coffee Probe (.venv Python 3.14)` 커널을 선택하고 **Restart Kernel → Run All → Save**로 재실행할 수 있다. `.env`를 준비하되 키를 셀에 쓰지 않는다. 매 실행 새 run_id가 생기며 기존 raw는 덮어쓰지 않는다. 또는 저장소 루트에서 다음 Python API를 사용한다. 이 명령은 실제 외부 요청을 다시 수행한다.

```sh
.venv/bin/python - <<'PY'
from pathlib import Path
import hashlib, json, re
import nbformat
from nbclient import NotebookClient

root = Path.cwd()
path = root / "data_code/01_small_batch_probe.ipynb"
nb = nbformat.read(path, as_version=4)
nb = NotebookClient(nb, timeout=420, kernel_name="coffee-probe",
    resources={"metadata": {"path": str(root / "data_code")}}).execute()
nbformat.write(nb, path)
text = "".join(o.get("text", "") for c in nb.cells for o in c.get("outputs", []))
run_id = re.search(r"Run ID: (\S+)", text).group(1)
run = root / "data/raw/probes" / run_id
copy = run / "system/executed_notebook.ipynb"
with copy.open("x") as stream:
    nbformat.write(nb, stream)
manifest_path = run / "system/manifest.json"
manifest = json.loads(manifest_path.read_text())
payload = copy.read_bytes()
manifest["artifacts"].append(dict(path=str(copy.relative_to(root)),
    kind="executed_notebook", bytes=len(payload),
    sha256=hashlib.sha256(payload).hexdigest(), secret_redaction_applied=False))
manifest["notebook_execution"] = {"status": "completed", "error_type": None}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print(run)
PY
```

## 미확인 사항과 후속 결정

현재 Probe의 승인 범위는 완료했다. 아래 대안은 **후속 작업 후보**이며 구현·데이터 변경을 하지 않았다.

- 결정할 문제: Yahoo OHLC 범위 불일치와 결측을 이후 데이터 계약에서 어떻게 취급할 것인가.
- **A. 원본 유지·공식 필드 의미와 발생 원인 조사 — 추천.** 현 단계의 잘못된 보정 가능성을 줄이며 기존 데이터 변경과 되돌리기 비용이 없다. 조사 후 처리 정책을 다시 승인받는다.
- **B. 이상 행 표시·제외 정책 승인 후 별도 테이블 생성.** 표본과 평가 조건이 바뀔 수 있고 삭제만으로 원인이 해결되지는 않는다. 원본을 보존하면 되돌릴 수 있지만 데이터셋 재생성·비교 비용이 생긴다.
- **C. 공급자 교체 또는 별도 계약 데이터 비교 승인.** 단위·권한·연결 규칙·비용 및 재수집 검증 범위가 커진다. Core-4 소스 변경 ADR이 필요하며 되돌리기 비용이 가장 크다.
- 승인 후 변경 범위: A는 조사 문서 및 필요 시 동일 소스의 제한된 진단 notebook; B/C는 먼저 accepted ADR·데이터 계약을 작성한 뒤 별도 새 검증 테이블/후속 notebook을 변경한다. 원본 가격을 덮어쓰지 않는다.
- 본수집 전 별도 확인: 미열람 좌표 근거, 공간 대표성·원천 격자, 실제 공개시각/가용성/빈티지 정책, 모델 타깃·cutoff·holdout 계약. 국가별 가중치·지점 교체는 추가 승인 사항이다.
- 기존 Parquet timestamp fixture 승인 대기는 별개로 남아 있다. 모델·학습·대량 수집·API/UI·scheduler·자동 commit/push는 수행하지 않았다.
