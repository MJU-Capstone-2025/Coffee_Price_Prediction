# Core-4 소량 수집 준비 상태

- 확인일: 2026-09-12. 이번 확인은 로컬 설정 여부·공식 접근 문서 조사이며 live 데이터 수집 성공 기록이 아니다.
- 실행 방식: ADR-002에 따라 새 notebook으로 진행. 원자료 수집과 모델 피처·평가 계약 확정을 구분한다.

## 인증 준비

| 소스 후보 | 필요한 인증 준비 | 현재 상태·한계 |
|---|---|---|
| FRED: DFF, DTWEXBGS, DCOILWTICO | FRED API key | `.env`에 비어 있지 않은 `FRED_API_KEY` 할당 존재. 값·길이·원문을 출력하지 않음. 유효성·실제 인증은 미검증 |
| Yahoo: KC=F, BRL=X via yfinance | 문서의 기본 접근은 사용자가 별도 API key를 제공하지 않음 | 비공식 접근, cookie·세션·차단 가능성 및 단위·연속계약 정의는 실제 응답 조사 필요 |
| NASA POWER Daily | 공식 예제의 공개 HTTP 요청 경로에는 API key가 없음 | 추가 NASA 키를 요구하지 않음. 지정 좌표와 시간 기준이 필요 |
| CFTC Disaggregated Futures Only, 083731 | 공개 연간 다운로드 경로 이용 시 별도 키 준비 없음 | 월별 검사여도 배포 단위는 연간 파일. 실제 파일 다운로드·필터 성공은 미검증 |
| 뉴욕 연준 GSCPI | 공개 데이터 다운로드 경로 이용 시 별도 키 준비 없음 | FRED key로 대체하지 않음. 실제 파일 위치·형식·컬럼 검증 필요 |

근거: [FRED key 요구](https://fred.stlouisfed.org/docs/api/api_key.html), [yfinance 기본 사용](https://ranaroussi.github.io/yfinance/), [NASA Daily 요청과 시간 기준](https://power.larc.nasa.gov/docs/services/api/temporal/daily/), [CFTC 연간 자료](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm), [뉴욕 연준 GSCPI](https://www.newyorkfed.org/research/policy/gscpi).

이는 현재 공개 접근 경로 기준의 준비 목록이며 모든 API 경로·재배포 권한·장기 접근 보장을 뜻하지 않는다. FRED 이외 추가 비밀키를 사용자에게 요구할 근거는 현재 확인되지 않았다. `.env`의 존재만으로 Jupyter kernel의 `os.environ`에 값이 들어가지는 않으므로 로드 및 존재 확인 셀을 준비해야 한다. 비밀값·키가 들어간 요청 URL·예외 문자열을 저장 출력으로 남기지 않는다.

## 수집 전에 필요한 결정

### 1. 후보 소스의 small-batch 사용 승인

- 문제: Context의 식별자를 후보에서 시험 수집에 사용할 소스로 확정해야 한다. 모델 입력 채택이나 최종 가격 정의 확정과는 별개다.
- 대안 A: 기존 Core-4 후보로 소량 응답 검증을 진행하되 좌표 미확정인 NASA 요청만 승인 후 실행. **추천**: 후보를 바꾸지 않고 응답·단위·공개 시점을 확인하며 비기상 소스부터 독립적으로 검증할 수 있다.
- 대안 B: FRED만 먼저 시험하고 나머지는 별도 승인 후 확장. 초기 범위·요청 수는 더 작지만 소스 간 데이터 구조 확인이 늦어진다.
- 영향·되돌리기 비용: 어느 안도 원본 보존을 전제로 하므로 구현 변경 비용은 작다. 수집된 raw snapshot은 임의 삭제하지 않고 유지한다. A의 비용은 소스별 응답 처리와 CFTC 연간 파일 저장량, B의 한계는 Core-4 전체 검증 지연이다.
- 승인 후 범위: 수집 notebook, 승인된 소스 설정·ADR, 별도 raw snapshot/시스템 메타데이터, fixture 및 live 검증 보고서. 기존 CSV·모델·예측 결과는 변경하지 않는다.

### 2. NASA 좌표·일별 시간 기준

브라질 Varginha·Carmo de Minas·Patrocínio 후보와 콜롬비아 중부 2개+Huila 1개의 **정확한 좌표와 커피 생산지 대표성**은 미확정이다. 사용자가 좌표를 직접 제공할 필요는 없다. 공식 생산지 근거·실제 격자 정보를 조사해 후보를 제시한 뒤 승인받는다. 도시 중심점이나 기존 9지역 좌표를 자동 채택하지 않는다.

- 시간 기준 대안 A: UTC 일별 집계. **초기 비교용 추천 후보**로, 여러 소스의 시간 메타데이터를 일관되게 해석하기 쉽다. 다만 현지의 낮/밤·날짜 경계와 다르다.
- 시간 기준 대안 B: POWER Local Solar Time(LST) 일별 집계. 현지 태양일 해석에 맞지만 civil timezone과 같지 않고 시장 cutoff와의 대응이 복잡하다.
- POWER Daily 기본값은 LST이므로 요청에서 반드시 명시한다. UTC는 아직 채택하지 않았다. UTC/LST 선택은 환경 smoke test의 timestamp dtype 승인과 별개의 실제 데이터 정책이다.
- 바꾸면 같은 날짜라도 관측 집계 값이 달라질 수 있으므로 재수집·파생 피처 재생성이 필요할 수 있다. 승인 후 `regions`/소스 설정, NASA 요청 notebook, 데이터 계약과 ADR을 변경한다.

## 이미 범위가 제안된 내용과 나중에 확정할 내용

- small-batch 구간은 Context의 **2016-01, 2023-12**를 이어 사용한다. 사용자에게 같은 기간을 다시 요청하지 않는다. 날짜 포함 경계와 공급원 end 파라미터 차이는 notebook에서 명시한다. CFTC는 해당 연간 파일에서 검사 구간을 추출한다.
- 타깃 Close/Settlement, 예측 horizon, prediction cutoff, 개발/holdout은 피처 생성·관계 EDA·모델 평가 전에 확정해야 한다. 원응답만 보존하는 비기상 소스 접근 시험 전체의 선행 조건으로 삼지는 않는다.
- 공개·이용 가능 시점을 모르면 unknown/null과 근거를 기록한다. 원래 날짜와 수집 시각을 별도로 남기고 과거 빈티지를 복원한 것으로 주장하지 않는다.
- GSCPI는 기존 Context대로 10년 기본 모델 입력과 사후 EDA/공개 이후 검증을 구분한다. 이번 준비 확인으로 평가 정책을 변경하지 않는다.

## 환경 쪽 남은 일

- `ipykernel`, `jupyterlab`, `nbformat`, `nbclient`, `python-dotenv`는 현재 `.venv`에 설치되어 있지 않다. 필요한 notebook 실행·검증 의존성을 선택해 Python 3.14 wheel 설치와 실제 kernel 실행을 확인해야 한다. 사용자에게 새 계정·클라우드 비용을 요구하는 항목은 아니다.
- [STATUS](STATUS.md)에 기록한 timestamp fixture 처리(A/B/C) 승인은 이 수집 준비 검토 당시 대기 중이었다. notebook 방식 변경을 그 승인으로 해석하지 않았으며, 당시 전체 Parquet/DuckDB 왕복 및 requirements 확정도 미완료였다. 후속 처리 상태는 STATUS에서 확인한다.
- 이번에는 새 수집 notebook이나 live API 호출을 실행하지 않았다. 환경 패키지 목록·인증 설정 존재·공식 문서 조회를 수집 구현 완료로 표시하지 않는다.
