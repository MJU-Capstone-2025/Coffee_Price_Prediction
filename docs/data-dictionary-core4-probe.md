# Core-4 Probe 데이터 사전

대상은 `data/raw/probes/20260912T063021795259Z_99d695f0/`의 실제 파일이다. 설계안의 예정 컬럼을 수집 완료로 섞지 않았다. `validation/`의 모든 CSV 컬럼과 `system/validation_summary.csv`를 아래에서 설명한다. CFTC 원본의 추가 191개 컬럼은 별도 전수 부록에 연결한다.

- **원자료**: FRED/NASA JSON, CFTC ZIP·원본 텍스트. 공급자가 자체 계산한 지수·재분석값도 우리 관점에서는 수집 원자료다.
- **라이브러리 반환값**: `library_return/yahoo/`. yfinance를 거친 값이며 HTTP 원문이 아니다. 특히 Volume null→0 변환이 있다.
- **정규화/검증용 데이터**: `validation/`. 승인 구간 필터·날짜/숫자 파싱·명시된 sentinel 결측 변환만 수행했다.
- **파생 피처**: 이번에 생성하지 않았다. 이동평균·수익률·국가 가중평균·순포지션도 없다.
- **시스템 메타데이터/진단 통계**: 요청 설정, 수집시각, 종합표, 기상 비교표. 예측 입력으로 채택한 컬럼이 아니다.

## 공통 시점·가용성 컬럼

| 컬럼 | 타입/단위 | 의미와 현재 값의 해석 |
|---|---|---|
| `observation_date` | 날짜 YYYY-MM-DD | 값이 속한 날짜. Yahoo는 공급자 일봉의 현지 날짜(KC=F America/New_York, BRL=X Europe/London), FRED는 경제 관측일, NASA는 UTC 집계일. 동일한 날짜 문자열이 동일한 이용 가능 시각을 뜻하지 않음 |
| `retrieved_at` | UTC ISO 8601 | 이번 실행에서 응답/반환값을 수집한 시각. 과거 경제활동 시각이나 당시 발표시각이 아님 |
| `published_at` | nullable timestamp | 개별 값의 실제 공개시각을 보존하기 위한 자리. 이번에는 전부 결측으로, 공개되지 않았다는 뜻이 아니라 확보하지 못했다는 뜻 |
| `available_at` | nullable timestamp | 예측 시스템에서 그 값을 이용 가능했다고 판단할 근거 시각. 이번에는 전부 결측. observation_date나 retrieved_at으로 대신 채우지 않음 |
| `availability_basis` | 문자열 | 가용성 판단 근거 상태. FRED/NASA/CFTC는 `unknown`. Yahoo 검증 CSV에는 이 컬럼 자체가 없음 |

CSV에는 엄격한 타입 정보가 들어 있지 않으므로 다시 읽을 때 날짜와 코드를 명시적으로 파싱해야 한다. 특히 CFTC 코드를 숫자로 읽으면 선행 0을 잃는다.

## Yahoo — market_daily

파일: `validation/market_KC_F.csv`(506행), `validation/market_BRL_X.csv`(523행). 한 행은 한 종목의 공급자 일봉이다. 공통 시점 컬럼 4개를 포함해 **각 11개 컬럼**이다.

| 컬럼 | 단위/타입 | 설명 |
|---|---|---|
| `observation_date` | 날짜 | 공급자 일봉 날짜. 시장별 timezone은 위 공통 설명 참조 |
| `Open` | 가격/환율 | Yahoo가 open으로 반환한 시가 필드. BRL=X 3행이 Low보다 낮으므로 동일 세션의 첫 체결가라는 해석은 확인 필요 |
| `High` | 가격/환율 | Yahoo가 high로 반환한 일별 고가 필드. Close와 동일한 가격·집계 기준인지 미확인 |
| `Low` | 가격/환율 | Yahoo가 low로 반환한 일별 저가 필드 |
| `Close` | 가격/환율 | Yahoo close 필드. KC=F를 마지막 체결가 또는 ICE 정산가로 확정하지 않음. OHLC 범위 이탈은 별도 보고서 참조 |
| `Adj Close` | 가격/환율 | Yahoo adjusted-close 필드. 일반적으로 split/dividend 조정 개념이지만 두 종목에서는 실제 Close와 모두 같음. 선물 롤 조정 완료값이라는 뜻이 아님 |
| `Volume` | 수량/정수 | yfinance의 거래량 반환값. KC=F 계약 수로 읽되 계약 연결 범위는 미확인. BRL=X는 실효 거래량 지표로 검증되지 않았으며 모두 0. 원응답 null도 yfinance가 0으로 바꾸므로 0=실제 무거래로 단정하지 않음 |
| `symbol` | 문자열 | `KC=F`: Coffee C 연속 조회 심볼, `BRL=X`: USD/BRL. KC=F 자체에는 날짜별 만기 계약 정보가 없음 |
| `retrieved_at` | UTC timestamp | 수집시각 |
| `published_at` | 결측 | 실제 공개시각 미확보 |
| `available_at` | 결측 | 과거 이용 가능 시각 미확보 |

KC=F 가격 원단위는 **US cents/lb**(응답 USX와 ICE 명세 교차 확인), BRL=X는 **1 USD당 BRL**이다. 예를 들어 5.00은 1달러=5헤알을 뜻한다. CSV의 가격을 달러/lb로 바꾸거나 환율 역수를 계산하지 않았다. 단위는 CSV에 별도 컬럼으로 삽입하지 않았으며 메타데이터/종합표에 기록되어 있다.

원본 library CSV에는 `symbol`·시점 메타데이터 대신 timezone이 포함된 `Date` 인덱스와 Open/High/Low/Close/Adj Close/Volume이 있다. `Date`는 CSV로 저장한 인덱스 이름이다. `.pkl`은 같은 library 반환값의 dtype/index 보존 사본이다.

근거: [Yahoo Adjusted Close](https://in.help.yahoo.com/kb/finance/adjusted-close-sln28256.html), [ICE Coffee C](https://www.ice.com/products/15/Coffee-C-Futures), 설치된 yfinance `parse_quotes` 및 Volume 처리 코드, [실제 원응답 대조 보고서](reports/yahoo-ohlc-investigation-2026-09-12.md).

## FRED — macro_observations

파일: `macro_DFF.csv`, `macro_DTWEXBGS.csv`, `macro_DCOILWTICO.csv`. 한 행은 한 시리즈·한 경제 관측일이며 **각 14개 컬럼**이다.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `realtime_start` | 날짜 | FRED가 반환한 real-time 조회/유효 구간의 시작 경계. 개별 값의 최초 발표일로 단정할 수 없음 |
| `realtime_end` | 날짜 | 위 real-time 구간의 종료 경계. observation_date 구간과 별개 |
| `observation_date` | 날짜 | 경제값이 설명하는 관측일. raw JSON의 `date`를 이름 변경 |
| `value` | 숫자/결측 | 관측값. raw의 문자열 `.`만 validation에서 결측으로 변환. 의미/단위는 아래 시리즈 표 참조 |
| `units` | 문자열 | 시리즈 메타데이터의 단위 원문 |
| `frequency` | 문자열 | 관측 주기 원문. DFF `Daily, 7-Day`, 다른 둘 `Daily`. 발표 주기를 뜻하지 않음 |
| `frequency_short` | 문자열 | 관측 주기 코드. 이번 모두 `D` |
| `seasonal_adjustment` | 문자열 | 계절조정 상태. 이번 모두 `Not Seasonally Adjusted` |
| `seasonal_adjustment_short` | 문자열 | 계절조정 코드. 이번 모두 `NSA` |
| `series_id` | 문자열 | DFF / DTWEXBGS / DCOILWTICO |
| `retrieved_at` | UTC timestamp | observations 응답 수집시각 |
| `published_at` | 결측 | 개별 관측치 공개시각 미확보 |
| `available_at` | 결측 | 과거 이용 가능 시각 미확보 |
| `availability_basis` | 문자열 | `unknown` |

| series_id | value의 경제적 의미 | 단위 | 주의 |
|---|---|---|---|
| `DFF` | Federal Funds Effective Rate: 금융기관의 익일물 연방기금 거래에서 형성된 실효금리 | Percent | FOMC의 정책 목표 범위 자체가 아님. 5.33이면 5.33% |
| `DTWEXBGS` | Nominal Broad U.S. Dollar Index: 광의 명목 달러지수 | Index Jan 2006=100 | 특정 환율 한 쌍이나 ICE DXY가 아님. 120은 기준월 대비 지수 수준 |
| `DCOILWTICO` | WTI, Cushing Oklahoma 현물 유가 시리즈 | Dollars per Barrel | 원유 선물 가격으로 해석하지 않음 |

메타데이터는 관측 행과 별도의 시리즈 설명이다. 같은 `realtime_start/end`라는 키도 시리즈 응답과 observations 응답에서 각각 확인해야 한다. `last_updated`는 시리즈 갱신시각이고 개별 관측치의 최초 공개시각이 아니다. [FRED real-time 문서](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html)는 관측값 수정과 시점 조회를 구분한다. 이번은 당시 빈티지 복원 조회가 아니다.

시리즈 근거: [DFF](https://fred.stlouisfed.org/series/DFF), [DTWEXBGS](https://fred.stlouisfed.org/series/DTWEXBGS), [DCOILWTICO](https://fred.stlouisfed.org/series/DCOILWTICO), 보존된 각 series metadata.

## NASA POWER — weather_daily

파일: `weather_<region_id>.csv` 6개, 각 732행·**14개 컬럼**. 한 행은 한 승인 요청 지점의 한 UTC 일자다. 국가 평균이나 연구소 장비의 직접 관측값이 아니다.

| 컬럼 | 단위/타입 | 설명 |
|---|---|---|
| `observation_date` | 날짜 | UTC 일별 집계일 |
| `PRECTOTCORR` | mm/day | 공급자가 보정해 제공한 강수량(Precipitation Corrected). 우리 코드에서 추가 보정한 값이 아님 |
| `T2M` | °C | 지표 위 2m 기온의 일별 평균값 |
| `T2M_MIN` | °C | 지표 위 2m 기온의 일별 최솟값 |
| `T2M_MAX` | °C | 지표 위 2m 기온의 일별 최댓값 |
| `RH2M` | % | 지표 위 2m 상대습도의 일별 값. Daily 집계 자료이며 순간 관측값이 아님 |
| `region_id` | 문자열 | br_sul_minas / br_cerrado / br_alta_mogiana / co_huila / co_caldas / co_antioquia |
| `requested_latitude` | 십진도 | 사용자가 승인한 요청 위도. 남위 음수, 북위 양수 |
| `requested_longitude` | 십진도 | 승인한 요청 경도. 이번 모두 서경으로 음수 |
| `aggregation_time_standard` | 문자열 | 응답 헤더의 집계 기준, 모두 `UTC` |
| `retrieved_at` | UTC timestamp | 응답 수집시각 |
| `published_at` | 결측 | 해당 자료 버전의 공개시각 미확보 |
| `available_at` | 결측 | 당시 이용 가능 시각 미확보 |
| `availability_basis` | 문자열 | `unknown` |

응답의 `parameters.<변수>.units/longname`으로 단위·변수명을 확인했다. raw fill_value -999.0은 결측 표시다(이번에는 실제 출현 0). 요청 좌표는 원천 격자 중심이나 생산량 중심점이 아니다. 별도 저장한 geometry 위경도는 요청 좌표의 소수 3자리 반올림과 일치하지만 실제 native grid_id는 미확인이다. [NASA Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)와 [ADR-003](adr/ADR-003-probe-weather-locations.md) 참조.

## CFTC — cot_weekly

파일: `cot_083731.csv`, 105행·**12개 컬럼**. 한 행은 Coffee C 시장의 한 report_date이며, **Disaggregated Futures Only** 보고서의 여러 만기 계약을 포괄한다. Yahoo KC=F의 특정 한 계약에 대한 포지션 테이블이 아니다.

| 검증 컬럼 | 원본 컬럼/출처 | 설명 |
|---|---|---|
| `market_code` | `CFTC_Contract_Market_Code` | 시장·상품 식별 문자열 `083731`. 선행 0 보존 필수 |
| `market_name` | `Market_and_Exchange_Names` | `COFFEE C - ICE FUTURES U.S.` |
| `report_date` | `Report_Date_as_YYYY-MM-DD` | 보고 포지션의 기준일. 발표일 아님 |
| `open_interest` | `Open_Interest_All` | 아직 청산·해소되지 않은 미결제약정의 계약 수. 거래량과 다르며 매수·매도 양쪽을 더해 두 배로 세지 않음 |
| `managed_money_long` | `M_Money_Positions_Long_All` | Managed Money 범주의 long으로 보고된 포지션 계약 수. 별도 spreading을 뺀 잔여 long 분류 |
| `managed_money_short` | `M_Money_Positions_Short_All` | 같은 범주의 short으로 보고된 포지션 계약 수. 별도 spreading을 뺀 잔여 short 분류 |
| `report_type` | 요청 설정 | `Disaggregated Futures Only`. options combined가 아님 |
| `archive_year` | 다운로드 파일 연도 | 2023/2024/2025 중 출처 파일. 필터 후 실제 행에는 2024·2025만 있음 |
| `retrieved_at` | 요청 메타데이터 | 해당 연간 아카이브 수집시각 |
| `published_at` | 미확보 | 개별 보고서 실제 공개시각, 이번 결측 |
| `available_at` | 미확보 | 과거 이용 가능 시각, 이번 결측 |
| `availability_basis` | 시스템 | `unknown` |

Managed Money는 고객 자금을 운용하는 CTA/CPO 및 CFTC가 식별한 펀드 등의 분류이며 그 포지션 전체를 단순히 투기 의도나 방향 예측의 정답으로 보지 않는다. `long-short` 순포지션은 이번 CSV에 없다. 필요하더라도 이후 별도 파생 피처로 만들어야 한다.

근거: [Disaggregated 설명](https://www.cftc.gov/idc/groups/public/@commitmentsoftraders/documents/file/disaggregatedcotexplanatorynot.pdf), [CFTC Explanatory Notes](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm). 원본 191개 컬럼 각각의 설명은 [CFTC 전수 부록](data-dictionary-cftc-raw.md) 참조. 모든 원본 컬럼을 검증용 테이블에 채택한 것은 아니다.

## 기상 지점 비교표 — weather_pairwise.csv

75행·9개 컬럼. **기상 관측값이 아니라 진단 결과**다.

| 컬럼 | 설명 |
|---|---|
| `left_region` | 비교할 첫 지점 region_id |
| `right_region` | 비교할 두 번째 지점 region_id |
| `variable` | 비교 변수 이름(PRECTOTCORR 등) |
| `comparison_status` | 비교 수행 상태. 이번 모두 `compared` |
| `common_valid_count` | 두 지점에서 모두 결측이 아니고 유한한 값이 있는 동일 날짜 수. 이번 모두 732 |
| `exact_on_common_valid` | 공통 유효 날짜 값이 모두 정확히 같은지. 공통 유효값이 없으면 참으로 판정하지 않음. 이번 모두 False |
| `missing_pattern_equal` | 날짜별 결측 위치가 같은지. 이번은 둘 다 결측이 없어 모두 True지만 값 일치라는 뜻은 아님 |
| `complete_nonmissing_match` | 승인된 모든 날짜에 양쪽 유효값이 있고 값까지 완전히 같은지. 이번 모두 False |
| `correlation` | 공통 유효값의 Pearson 상관계수. 높은 상관만으로 동일 격자라고 판정하지 않음 |

## 종합 검증표 — system/validation_summary.csv

12행·17개 컬럼. 한 행은 하나의 요청 데이터셋 결과다.

| 컬럼 | 설명 |
|---|---|
| `source` | Yahoo / FRED / NASA / CFTC |
| `dataset_id` | 종목 코드·FRED 시리즈·NASA region_id·CFTC 시장 코드 |
| `request_status` | 요청 성공 여부. 품질 검사 성공과 별개 |
| `http_status` | 직접 확보한 HTTP 상태. Yahoo는 null, CFTC는 연도별 상태 배열. CSV에서는 JSON 형태 문자열 |
| `parse_status` | 응답을 표 구조로 해석한 결과 |
| `raw_row_count` | 변환 전 반환 행 수. Yahoo는 library 행 수, CFTC는 전체 시장 연간 파일 합계로 범위가 다름 |
| `filtered_row_count` | 승인 구간·대상으로 필터한 검증 행 수 |
| `observed_start` | 실제 반환 관측일/보고일의 최솟값. 요청 시작일과 다를 수 있음 |
| `observed_end` | 실제 반환 관측일/보고일의 최댓값 |
| `missing_count` | 검사 대상 값의 결측 **셀 수**, 행 수가 아님. Yahoo OHLC+Volume, FRED value, NASA 5변수, CFTC 3포지션 컬럼 기준. 공통 published_at/available_at 결측은 이 집계에 넣지 않음 |
| `duplicate_count` | 관측일/보고일 기준 중복 건수. 이번 모두 0 |
| `unit` | 확인된 단위. NASA는 변수별 단위를 JSON 문자열로 표시 |
| `unit_verification_status` | 단위 확인 근거/미확인 상태 |
| `validation_status` | passed / warning / failed / not_run. 과거 available_at 미확보도 warning 이유이므로 수치 오류 여부는 상세 결과의 violations와 함께 읽음 |
| `warnings` | 해석상 주의·제한 목록. CSV에서는 JSON 형태 문자열 |
| `retrieved_at` | 수집시각. CFTC 합산 행은 아카이브 수집시각 중 가장 늦은 시각 |
| `artifact_path` | 해당 검증 테이블 경로. raw 원문 경로는 상세 JSON/manifest에서 별도 확인 |

## 원본 JSON·메타데이터 읽는 법

### FRED

- observations 응답의 `observations[]` 각 항목은 `realtime_start`, `realtime_end`, `date`, `value` 4필드이며 위 검증 컬럼에 대응한다. raw `value`는 문자열이고 `.`는 결측 표시다.
- 최상위 `observation_start/end`는 응답의 조회 범위, `units`는 요청 변환 코드(이번 `lin`: 변환 없음), `output_type`은 API 출력 방식, `file_type`은 형식이다. 최상위 `units=lin`을 금리/유가의 경제 단위로 읽지 않는다.
- `count`, `offset`, `limit`, `order_by`, `sort_order`는 결과 개수·페이지·정렬 메타데이터다. 존재하는 키만 해석한다.
- `seriess[]` 또는 별도 series metadata의 `id/title`은 식별자/이름, `observation_start/end`는 시리즈 전체 제공 범위로 이번 Probe 범위와 다르다.
- `units/units_short`, `frequency/frequency_short`, `seasonal_adjustment/seasonal_adjustment_short`는 단위·주기·계절조정 설명이다. `last_updated`는 시리즈 갱신시각, `popularity`는 FRED 인기도 메타데이터로 경제 관측값이 아니며 산식은 이번에 확인하지 않았다. `notes`는 출처와 정의 설명이다.

### NASA

- `properties.parameter.<변수>.<YYYYMMDD>`가 원래 관측값이다. JSON에는 같은 이름의 날짜별 열 대신 날짜를 key로 한 객체가 있다.
- `parameters.<변수>.units/longname`은 단위/변수 설명이다.
- `header.fill_value`는 결측 sentinel, `header.time_standard`는 집계 시간 기준, `header.start/end`는 응답 범위, `header.sources`는 원천 제품, `header.api`는 서비스 이름/버전, `header.title`은 응답 제목이다.
- `geometry.type`은 Point이며 `geometry.coordinates` 순서는 경도·위도·세 번째 위치 값이다. 세 번째 값을 현장 실측 고도로 확정하지 않았고 격자 ID도 아니다. `messages`는 응답 경고/오류 메시지 목록이다.
- `times`가 있으면 API 처리 관련 메타데이터다. 기상 관측시각·당시 발표시각으로 사용하지 않는다.

### Yahoo

- 원래 Probe의 `history_metadata`는 Mapping 객체가 문자열로 직렬화되어 **JSON 객체가 아니다**. `quote_metadata`는 객체다. 상세 한계는 조사 보고서 참조. 문자열을 `eval`로 실행해서 복구하면 안 된다.
- 이번 진단에서 보존한 chart 응답은 `chart.result[].timestamp`와 `indicators.quote[]`의 open/high/low/close/volume, `indicators.adjclose[]`의 adjclose로 구성된다. timestamp는 Unix seconds이며 exchangeTimezoneName을 사용해 공급자 날짜로 읽었다. `chart.error`는 요청 오류 정보다.
- `meta` 및 quote metadata의 `symbol/shortName/longName`, `currency`, `exchange/fullExchangeName`, `exchangeTimezoneName`은 종목·단위·시장·시간대 설명이다. 조회 당시 이름을 과거 날짜별 계약명으로 적용하지 않는다.
- `regularMarket*`, `previousClose/open/dayLow/dayHigh/volume`, `bid/ask`, `regularMarketTime`, `marketState`는 **조회 시점의 quote 스냅샷**이다. 2024~2025의 매일 값이 아니다. bid/ask는 호가이며 특정 과거 OHLC의 집계 방식을 증명하지 않는다.
- `underlyingSymbol/headSymbolAsString/expireDate/expireIsoDate`, `contractSymbol`은 현재 심볼·만기 관련 메타데이터다. 실제 반환 타입을 유지하며 `contractSymbol=False`를 유효한 날짜별 계약 코드로 해석하지 않는다.
- `averageVolume*`, `fiftyDayAverage*`, `twoHundredDayAverage*`, `fiftyTwoWeek*`, `allTime*`는 공급자 스냅샷의 기간 요약/변동 정보다. 이 값을 과거 학습 행에 복사하면 시점 문제가 생긴다. 구체적 계산 범위는 검증하지 않았다.
- `priceHint`, `maxAge`, `sourceInterval`, `exchangeDataDelayedBy`, 각종 UI/거래 가능 flag 및 기타 보조 키는 표시·서비스 메타데이터다. 특히 sourceInterval을 초·분으로 임의 확정하거나 maxAge를 과거 available_at 지연으로 쓰지 않는다. 이 보조 필드들은 이번 예측 데이터 컬럼으로 채택하지 않았다.

### 실행 manifest와 상세 검증 JSON

`run_id`, `environment`, `period`, `request_count`, `dataset_count`는 실행 식별/설정이다. `artifacts[].path/kind/bytes/sha256`은 저장 파일 종류·크기·무결성 확인값이다. `secret_redaction_applied`는 저장 과정의 비밀값 치환 여부다. `violations`와 `sentinel_counts`, `volume_zero_count` 등의 수치는 진단 집계이며 실제 측정 피처가 아니다. `grid_id=null`은 확인 실패/미확인이지 특정 격자 번호가 0이라는 뜻이 아니다.

## 이번 Yahoo 조사에서 추가된 진단 컬럼

별도 run `20260912T084033463809Z_yahoo_diagnostic_b09941/`의 `*_ohlc_violations.csv`는 원래 OHLC/Volume/Adj Close와 observation_date에 아래 4개 진단 컬럼을 더했다. 가격 데이터나 예측 피처를 보정한 것이 아니다.

| 컬럼 | 설명 |
|---|---|
| `above_high_by` | max(Close − High, 0). Close가 High를 초과한 크기, 원래 가격/환율 단위 |
| `below_low_by` | max(Low − Close, 0). Close가 Low보다 낮은 크기, 원래 단위 |
| `open_outside_range` | Open이 Low보다 낮거나 High보다 높으면 True |
| `close_outside_range` | Close가 Low보다 낮거나 High보다 높으면 True |

## 현재 해석의 한계

원본 0과 결측, 발표일과 수집시각, 가격과 정산가, 일 거래량과 미결제약정, 관측값과 API 메타데이터를 구분한다. 이번 컬럼 설명은 가격 정의·평가 정책 변경이나 해당 컬럼의 모델 채택 승인이 아니다. 기존 값·스키마·notebook은 수정하지 않았다.
