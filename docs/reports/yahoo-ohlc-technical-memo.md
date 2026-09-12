# Yahoo KC=F / BRL=X OHLC 추가 원인 검증 기술 메모

## 1. 문제 정의

**확인됨:** 승인 구간에서 KC=F 73행·BRL=X 4행의 범위 이탈이 보존된 Yahoo HTTP 응답부터 존재한다. 로컬 가격 조정·CSV 저장이 만든 현상이라는 설명은 반증됐다. **미확인:** 이 값이 공급자 오류인지, OHLC 필드의 가격 정의·집계·계약 연결 차이인지 확정할 증거는 아직 부족하다.

이 메모는 [기존 조사](yahoo-ohlc-investigation-2026-09-12.md)의 후속 기록이다. 기존 보고서는 수정하지 않았다. 새로 확인한 종료 경계 행, 일봉 timestamp 정규화, 고정 사례의 방향·크기·거래량 반례와 공식 자료의 확인 한계를 보완한다. 수집·계산 성공은 가격 정확성 또는 학습용 데이터셋 완성을 뜻하지 않는다.

판정은 **확인됨 / 가설을 지지함 / 반증됨 / 미확인**으로 구분한다. `반증됨`은 표에 명시한 구체적인 설명에만 적용하며 다른 상위 원인까지 부정하지 않는다. 기존 OHLC 검증 정책·단위·가격은 유지했다.

## 2. 데이터·환경

- 작업일: 2026-09-12. 시작 Git: `develop`, `42e26bf3573cf56d3606708a7208b3edd3e4507b`, 작업 트리 clean. 기존 STATUS의 다른 commit은 이전 작업 당시 기록이다.
- 실제 환경: macOS 27.0, native arm64, CPython 3.14.7. 실행 경로: `/Users/sj/MyDrive/MyWorkspace/Projects/Coffee_Price_Prediction/.venv/bin/python`.
- pandas 3.0.5, NumPy 2.5.3, yfinance 1.7.0, requests 2.34.2, curl_cffi 0.16.3. 설치·업그레이드·환경 재생성 없음. Notebook은 실행·수정하지 않았으며 동일 `.venv`의 별도 진단 스크립트로 계산했다.
- 승인 구간: `2023-12-31`–`2025-12-31`, 양 끝 포함. 기존 Yahoo 요청의 exclusive end는 `2026-01-01`이다. 전체 일봉 구간의 외부 재수집은 **0회**다.
- 기존 Probe: `20260912T063021795259Z_99d695f0`. chart HTTP 응답을 보존한 기존 조사: `20260912T084033463809Z_yahoo_diagnostic_b09941`.
- 이번 결과: [`data/raw/probes/20260912T091208763138Z_yahoo_ohlc_memo_b242f9/`](../../data/raw/probes/20260912T091208763138Z_yahoo_ohlc_memo_b242f9/). 이하 `RUN`으로 표기한다.

### 입력의 보존·대응

기존 두 manifest의 **65 + 8 = 73개 artifact SHA-256**을 모두 대조했다. chart → 기존 진단 library CSV → 원래 Probe의 library CSV·pickle·검증 CSV를 비교했다. PKL은 기존 manifest로 무결성을 확인한 로컬 파일만 읽었다. 해시는 현재 내용이 기록된 내용과 같은지를 검증하며, 공급자 값의 사실성을 인증하지는 않는다.

| 입력 chart | SHA-256 | 원문 UTC 수집시각 |
|---|---|---|
| KC=F `chart_response_1.json` | `45f0f61e8b7312ae20ec37d31b777ce97e96f86981a4ef37cc77f34f300fd0c8` | 2026-09-12T08:40:34.929675+00:00 |
| BRL=X `chart_response_2.json` | `fbd2fab9e0f1a08b85ff2ce4bccaa6770838f114e3dcae6a8ae5cb92f10ef604` | 2026-09-12T08:40:35.253422+00:00 |

**확인됨 — 기존 집계 표현 보완:** BRL 원문은 **524행**이다. 마지막 `2026-01-01T00:00:00Z` 행의 OHLC·Adj Close·Volume은 모두 null이며 승인 구간 밖이다. 기간 내 523행과 library 523행이 대응한다. 기존 보고서의 “raw 523행·Volume null 4개”는 **기간 필터 후 기준**이다. 원문 전체 Volume null은 5개다. 이 차이는 이상 4행의 발생 원인이 아니다.

## 3. 검증 방법

### 재현 계산

1. chart의 `timestamp`와 `indicators.quote[0]` 배열을 같은 위치로 묶고 `exchangeTimezoneName`으로 현지 날짜를 구한다. 승인 구간 밖 행은 진단용 별도 CSV로 기록한다.
2. 비교 시 날짜 집합·순서·행 수를 검증하고 Open/High/Low/Close/Adj Close를 `rtol=0, atol=1e-12, equal_nan=True`로 대조한다. CSV는 `float_precision="round_trip"`으로 읽는다.
3. OHLC가 모두 유효한 행에서 기존의 엄격한 범위 검사를 적용한다. 가격을 반올림·보간·보정하지 않는다. 아래 `signed_gap`은 새로운 **진단 컬럼**이며 가격 원본이 아니다.

```python
valid = df[["Open", "High", "Low", "Close"]].notna().all(axis=1)
# X = Open 또는 Close. 유효 행에 대해서만 계산한다.
signed_gap = X - Low if X < Low else X - High if X > High else 0
# 음수: 하방 이탈, 양수: 상방 이탈, 0: 범위 안
gap_pct = 100 * signed_gap / (Low if signed_gap < 0 else High)
```

4. 원문 Volume null/0과 library null/0을 분리한다. 이전에 저장한 이상 행 CSV와 날짜·가격도 다시 대조한다.
5. 요청한 KC 6일·BRL 4일을 고정하여 상세 표를 생성한다. 앞뒤 **반환 행** 1개씩만 기존 응답에서 읽어 맥락을 확인한다. 달력상 전일/다음 날이라고 가정하지 않는다.

### yfinance의 서로 다른 처리

**확인됨:** 설치된 소스의 발췌·파일 해시는 [`implementation_evidence.json`](../../data/raw/probes/20260912T091208763138Z_yahoo_ohlc_memo_b242f9/implementation_evidence.json)에 보존했다.

| 처리 | 실제 코드·관찰 | OHLC 이상과의 관계 |
|---|---|---|
| 가격 배열 매핑 | `utils.py:548`의 `parse_quotes`가 같은 timestamp에 quote 배열을 매핑 | 기간 내 1,029행 × 가격 5열 × 비교 표현 4종 전부 일치 |
| 조정·repair | 기존 옵션 `auto_adjust=False`, `back_adjust=False`, `repair=False`, `rounding=False`; Close=Adj Close 전 행 동일 | 로컬 조정 또는 Adj Close 혼용 설명은 반증됨 |
| 종료 경계 제거 | `scrapers/history.py:395`에서 end 이상 마지막 행 제거 | BRL 524→523과 부합; 기간 내 가격 변경 없음 |
| 일봉 날짜 정규화 | `history.py:497`에서 현지 날짜를 자정 인덱스로 만듦 | KC 원문 500행은 현지 00:00, 6행은 09:30. library는 모두 자정이며 **날짜는 전부 일치**. timestamp 시각까지 전부 동일하다는 뜻은 아님 |
| Volume 변환 | `history.py:611`의 `fillna(0).astype(np.int64)` | 원문 결측이 library 0에 합쳐짐. 가격 범위 이탈 원인은 아님 |
| metadata 직렬화 | `HistoryMetadata`는 Mapping, Notebook `safe_object`는 dict만 재귀 처리 | 기존 `history_metadata`는 문자열, `quote_metadata`는 객체. 별도 구현 한계이며 가격 원인이 아님 |

KC의 09:30 timestamp 6행 중 이상은 3행이고, 고정 KC 사례 6일은 모두 원문 현지 자정이다. bar 전체의 날짜 라벨 변경은 같은 bar 내부 부등식을 바꾸지 않는다. 반면 **공급자 내부에서 OHLC를 서로 다른 시간 창으로 만들었는지**는 이 대조로 배제하지 못한다. metadata 문자열은 eval하거나 다시 저장하지 않았다.

### 공식 자료와 소량 요청

공식 출처·확인 방식·지지 범위는 [`source_evidence.json`](../../data/raw/probes/20260912T091208763138Z_yahoo_ohlc_memo_b242f9/source_evidence.json)에 기록했다. ICE·yfinance 공식 문서 7개는 실제 HTTP 200 원문을 저장했다. Yahoo 도움말·BRL history 설명은 검색 도구가 반환한 **공식 페이지 본문**을 확인했으며, 이를 직접 받은 HTTP 원문이라고 부르지 않는다. Yahoo 직접 페이지 열기의 실패·429와 검색 본문 확인을 구분한다.

[`PriceHistory`](https://ranaroussi.github.io/yfinance/reference/yfinance.price_history.html)는 intraday를 일반적으로 60일로 설명하지만, [`Price Repair`](https://ranaroussi.github.io/yfinance/advanced/price_repair.html)는 1h의 2년 한계를 별도로 설명한다. 설치된 소스도 1h/60m에 730일을 사용한다. 이는 조회 가능성의 근거이며 성공 보장은 아니다. repair는 실행하지 않았다.

| BRL 날짜 | 시간봉 추가 접근 | 결과 |
|---|---|---|
| 2024-01-01 | 요청하지 않음 | 조사일 기준 730일보다 오래됨 |
| 2024-07-29 | 요청하지 않음 | 조사일 기준 730일보다 오래됨 |
| 2024-11-06 | `60m`, UTC 00:00부터 다음 날 00:00 미포함, 1일만 요청 | **HTTP 429**, 23-byte 실패 body 보존, 가격 확보 0행 |
| 2024-12-27 | 위와 같은 1일 조회 예정이었으나 중단 | 같은 endpoint의 접근 제한을 존중하여 요청하지 않음 |

11월·12월 해당 날짜의 London 현지 자정은 UTC 자정과 같다. 이 요청 창을 공급자의 공식 일봉 집계 경계로 확정한 것은 아니다. 429 후 재시도·인증 변경·다른 endpoint·공급자·우회 경로를 사용하지 않았다. 이 결과로 2024-11-06의 시간봉 자체가 존재하지 않는다고 결론 내릴 수는 없다. 최초 sandbox 네트워크 실패는 별도 요청 기록으로 남겼으며 실제 HTTP 429와 구분한다.

## 4. 종목별 결과

### 공통 집계 — 확인됨

| 지표 | KC=F | BRL=X |
|---|---:|---:|
| HTTP 원문 전체 행 | 506 | 524 |
| 승인 구간 내 행 | 506 | 523 |
| 실제 기간 시작 | 2024-01-02 | 2024-01-01 |
| 실제 기간 끝 | 2025-12-31 | 2025-12-31 |
| 유효 OHLC 행 | 504 | 519 |
| OHLC 결측 행 | 2 | 4 |
| 날짜 중복 | 0 | 0 |
| High < Low | 0 | 0 |
| Open 하방 / 상방 이탈 | 0 / 0 | 3 / 0 |
| Close 하방 / 상방 이탈 | 37 / 36 | 3 / 1 |
| 이상 행 합집합 | 73 | 4 |
| 원문 Volume null: 전체 / 구간 내 | 2 / 2 | 5 / 4 |
| 구간 내 원문 Volume 0 | 31 | 519 |
| library Volume null / 0 | 0 / 33 | 0 / 523 |
| 이상 행 Volume null / 0 | 0 / 0 | 0 / 4 |

단위는 기존 확인과 동일하게 **KC: US cents/lb, BRL: BRL per USD**다. KC 메타데이터 `USX`와 [ICE Coffee C 상품 명세](https://www.ice.com/products/15/Coffee-C-Futures)의 가격·tick 정의를 함께 사용한다. USD라는 통화 코드만으로 단위를 추정하지 않았다. 원본 가격 변환은 없다.

### KC=F 고정 사례 — 확인됨

가격·이탈은 cents/lb, 표만 소수 6자리 표시한다. Volume은 Yahoo 반환값이며 날짜별 만기 계약과 Volume 집계 단위의 연결은 독립 확인되지 않았다.

| 날짜 | Open | High | Low | Close | Volume | Close signed gap |
|---|---:|---:|---:|---:|---:|---:|
| 2025-03-06 | 413.450012 | 413.450012 | 409.500000 | 393.000000 | 4 | -16.500000 |
| 2024-05-02 | 218.000000 | 218.000000 | 218.000000 | 208.649994 | 9 | -9.350006 |
| 2024-09-18 | 265.700012 | 265.700012 | 265.700012 | 263.149994 | 15678 | -2.550018 |
| 2025-03-19 | 394.149994 | 394.149994 | 394.100006 | 394.600006 | 12747 | 0.450012 |
| 2025-05-19 | 377.850006 | 378.549988 | 377.850006 | 376.149994 | 10983 | -1.700012 |
| 2025-09-15 | 422.899994 | 425.149994 | 422.899994 | 432.350006 | 24 | 7.200012 |

최대 이탈 16.5는 ICE 최소 변동폭 0.05 기준 **330 ticks**다. 전체 이상 중 최소 이탈도 0.100006이다. 2025-03-06의 경계 대비 이탈은 `100 × (393−409.5)/409.5 = −4.029304%`다. 미세 부동소수점 오차만으로 설명하는 가설은 반증된다.

**가설을 지지함 — 희박한 체결 범위와 다른 가격 산정 기준:** 이상 73행 중 Volume ≤100은 67행, ≤1,000은 69행이다. 이상 행 중앙값 18, 나머지 유효 행 중앙값 13,070이다. 이상 중 High=Low도 28행이다. 다만 Volume ≤100인 유효 행 178개 중 **111개는 범위 검사를 통과**한다. 저거래량은 충분조건이 아니고 고거래량 이상도 있으므로 필요조건도 아니다. 이 기준은 진단용 분류이며 모델 피처·삭제 기준으로 채택하지 않았다.

**가설을 지지함 — 계약 전환 또는 필드별 집계 차이도 추가 조사 후보:** 고거래량 반례의 앞/당일/뒤 반환 행 Volume은 다음과 같다.

| 사례 | 앞 행 날짜·Volume | 당일 Volume | 뒤 행 날짜·Volume | 당일 High−Low |
|---|---|---:|---|---:|
| 2024-09-18 | 09-17: 3 | 15678 | 09-19: 14167 | 0.000000 |
| 2025-03-19 | 03-18: 22 | 12747 | 03-20: 14036 | 0.049988 |
| 2025-05-19 | 05-16: 112 | 10983 | 05-20: 9934 | 0.699982 |

좁은 당일 범위와 거래량 급변의 동시 관찰은 “모든 필드가 같은 계약·같은 표본에서 왔는지”를 확인할 이유다. 이것만으로 roll 날짜나 OHLC/Volume의 서로 다른 계약 사용을 입증하지 못한다. 고거래량도 정산가 가설 전체를 반증하는 것은 아니며, **저거래량만으로 모든 사례를 설명하는 주장**을 반증한다.

### KC 공식 정의·계약 대조의 경계

**확인됨:** [ICE Rule 4.34(b), p.4-31](https://www.ice.com/publicdocs/rulebooks/futures_us/4_Trading.pdf)은 lead contract의 정산 구간 체결가 가중 평균뿐 아니라 다른 계약의 가격차·호가, 거래소 판단에 따른 산정도 허용한다. 따라서 정산가격을 마지막 체결가와 동일시할 수 없다. 다만 정산가가 **동일 계약·동일 전체 거래 집합 안의 체결가만으로 만든 가중 평균**이라면 그 집합의 최저/최고 사이에 있어야 한다. 범위 이탈을 정산으로 설명하려면 거래 집합·계약·호가 등의 차이까지 확인해야 한다.

[2018-12-07 ICE 공지](https://www.ice.com/publicdocs/futures_us/exchange_notices/ICE_Futures_US_KC_ArbBlocks20181207.pdf)는 2019-01-07부터 정산 창을 New York 12:23–12:25로 정하고, 만기 계약 최종 거래일 거래 종료도 12:25로 정했다. 일반 거래 종료와 별개라는 근거다. 모든 2024~2025일에 예외·개정 없이 같은 시간이 적용됐다는 검증은 하지 않았다.

상품 명세는 3·5·7·9·12월 계약, 최종 통지일(인도월 마지막 영업일의 7영업일 전), 그 전 영업일의 최종 거래일을 설명한다. **미확인:** 조회 당시 `Coffee Dec 26` / `KCZ26.NYB`는 과거 행의 계약을 식별하지 않는다. [공식 만기 달력](https://www.ice.com/expiry-calendar)의 입력 화면은 확인했으나 해당 과거 만기 결과를 확보하지 못했다. 거래일 달력과 실제 Yahoo 계약 매핑 없이 만기까지 남은 영업일을 계산하지 않았다. 월·일이 만기 시기에 가깝다는 인상은 확정 증거로 쓰지 않는다.

[Yahoo 공급자 설명](https://help.yahoo.com/kb/SLN2310.html)은 현재 ICE Futures US와 Currency Rates에 ICE Data Services를 열거한다. 이 표는 KC=F의 과거 연결 규칙이나 daily Close=Settlement 계약을 명시하지 않으며 오류의 책임 주체를 특정하지도 않는다. [Yahoo Adjusted Close 설명](https://help.yahoo.com/kb/SLN28256.html)은 split/dividend 조정의 일반 설명이다. 선물 계약 연결·정산가 사용 근거로 확장하지 않았다.

**미확인 — 계약별 공식 가격 대조 0건:** 날짜별 실제 계약 식별이라는 선행 조건을 충족하지 못했다. 계약 코드를 추정하여 ICE 정산가를 조회·대입하지 않았다. [ICE Report Center](https://www.ice.com/report-center)에서 일말 보고서와 유료 CSV 구독 안내를 확인했지만 구독·구매는 하지 않았다. 모든 과거 자료가 유료이거나 무료 자료가 전혀 없다고 단정하지 않는다. 개별 가격 일치 사례도 확보하지 못했으므로 전체 Close 정의를 확정할 수 없다.

### BRL=X 고정 사례 — 확인됨

단위 BRL per USD. 네 행 모두 원문 Volume=0이며, 환율 전체 유효 행 519개의 Volume도 모두 0이다. 이를 거래 부재·유동성 저하의 증거로 사용하지 않는다.

| 날짜 | Open | High | Low | Close | Open signed gap | Close signed gap |
|---|---:|---:|---:|---:|---:|---:|
| 2024-01-01 | 4.850500 | 4.852500 | 4.851800 | 4.850500 | -0.001300 | -0.001300 |
| 2024-07-29 | 5.622841 | 5.666600 | 5.629232 | 5.622841 | -0.006391 | -0.006391 |
| 2024-11-06 | 5.700000 | 5.708000 | 5.690000 | 5.739800 | 0.000000 | 0.031800 |
| 2024-12-27 | 6.148500 | 6.209500 | 6.166166 | 6.148500 | -0.017666 | -0.017666 |

2024-01-01·07-29·12-27은 Open=Close가 Low보다 낮고, 11-06은 Close만 High보다 높다. Open=Close는 이상 행만의 특징이 아니다. 전체 유효 519행 중 **473행**, 이상 4행 중 3행에서 성립한다. 같은 값의 반복만으로 stale quote 또는 오류를 판정할 수 없다.

**확인됨 — 날짜 라벨:** 모든 구간 내 timestamp는 Europe/London 현지 자정이다. 2024-07-29 bar는 UTC `2024-07-28 23:00:00+00:00`에 대응한다. UTC 날짜만 잘라 쓰면 라벨이 달라지지만 기존 library·검증 CSV는 현지 날짜와 일치한다. 나머지 세 사례는 UTC와 현지 자정이 같다. 이것은 **일봉의 표시 기준**이며, 실제 quote 집계 시작/끝·종가 이용 가능 시각의 증명이 아니다.

**미확인 — 호가·집계 정의:** [Yahoo BRL history](https://finance.yahoo.com/quote/BRL%3DX/history/)의 Close 각주는 일반적인 split 조정 문구이며 bid/ask/mid, OHLC별 표본·cutoff를 밝히지 않는다. 실시간 시세 지연 표도 과거 일봉 생성 규칙을 설명하지 않는다. 공개 문서와 현재 보존한 원응답에서 네 날짜의 quote-level bid/ask·집계 규칙을 확보하지 못했고, 추가 시간봉 요청도 429로 실패했다. 선물 정산가격 설명을 환율에 적용하지 않는다.

## 5. 가설별 증거·반례

| 구체적 설명 | 판정 | 증거 | 반례·남은 확인 |
|---|---|---|---|
| 로컬 가격 조정·저장 과정이 77행 이탈을 만들었다 | **반증됨** | 동일 날짜의 원문→반환→검증 가격 5열 일치 | Yahoo 상류 내부 변환은 미확인 |
| 로컬 날짜 라벨 이동 또는 Volume null→0이 OHLC 이탈 원인이다 | **반증됨** | 날짜 일치, 같은 bar 부등식 보존, Volume은 별도 열 | 상류의 필드별 집계 창 차이는 별개 |
| 미세 반올림만으로 이탈이 발생했다 | **반증됨** | 최소 이탈 KC 0.100006, BRL 0.001300; 허용 비교 오차보다 훨씬 큼 | 가격 보정은 수행하지 않음 |
| KC 희박한 체결 범위와 별도 정산가격의 차이다 | **가설을 지지함** | 저거래량 집중, 28개 단일가 범위, ICE의 별도 정산 규칙 | Yahoo Close 정의·동일 계약 공식 정산가 불명; 고거래량 반례 |
| KC 저거래량만으로 모든 이상을 설명한다 | **반증됨** | Volume 15,678·12,747·10,983인 이상 사례 | 저거래량 정상 111행도 존재 |
| KC 계약 전환·필드 집계 차이가 일부 이상에 관여한다 | **가설을 지지함** | 고거래량 세 사례의 좁은 범위와 전후 거래량 전환 | 날짜별 실제 계약·roll 규칙 미확인, 확정 인과관계 아님 |
| KC Yahoo Close는 모든 날짜의 공식 ICE Settlement다 | **미확인** | 거래소 정산 메커니즘은 확인 | Yahoo 명세·날짜별 계약·정산가 대조 없음 |
| BRL OHLC의 bid/ask/mid가 서로 다르다 | **미확인** | Open/Close가 함께 범위를 벗어나는 패턴과 양립 | 호가 표본·spread가 없어 지지 증거와 단순 양립을 구분해야 함 |
| BRL OHLC의 일봉 집계 경계가 서로 다르다 | **미확인** | London 날짜 라벨 확인 | 라벨이 집계 창을 증명하지 않음; 시간봉 확보 실패 |
| Yahoo 또는 상위 공급자의 자료 오류다 | **미확인** | 응답에 수학적 범위 불일치는 확실히 존재 | 모든 필드가 같은 정의라는 명세가 없어 오류와 정의 차이를 구별하지 못함 |

## 6. 미확인 사항·저장·검증 기록

- KC: 6개 고정 사례의 실제 만기 계약, daily Close/High/Low/Volume의 공급자 정의, 과거 roll 규칙, 공식 계약별 가격 대조, 해당일 실제 만기 인접성은 미확인이다.
- BRL: quote side·집계 시간 창·발표/수정 시각은 미확인이다. HTTP 429는 접근 실패이고 데이터 부재 또는 원인 가설의 반증이 아니다.
- `retrieved_at`은 응답 수집시각이다. 원래 관측일·bar timestamp·정산/공개 시각·available_at과 같게 취급하지 않는다. 당시 빈티지나 누수 없는 학습 입력을 복원하지 않았다.
- 자동 수집·모델·환경 테스트는 재실행하지 않았다. 아래 검증은 실제 보존 응답의 분석·문서 검증이며 fixture 통과로 API 성공을 주장하지 않는다.
- **보존 검사의 외부 변경:** 작업 중 별도로 발생한 Git diff에 기존 CSV 8개 경로 삭제, Notebook 2개 수정, requirements의 entmax 추가가 나타났다. CSV 8개는 `data/old_data/`에서 시작 스냅샷과 동일한 해시로 확인했다. 이번 작업이 수행한 변경이 아니며 복원·덮어쓰기하지 않았다. 분석 입력 manifest 73개는 다시 검증해 모두 일치했다. 전체 작업 트리가 그대로라는 주장 대신 이 변경을 `concurrent_changes.json`에 구분한다.

| RUN 내부 | 성격 |
|---|---|
| `reproduce.py` | 기존 응답만 읽는 재현 계산. 외부 요청 0, 기존 출력 디렉터리 사용 거부 |
| `verify_artifacts.py` | 메모 표·링크·입력/산출물 해시·비밀값 미포함과 별도 변경 구분 검사 |
| `analysis_final/summary.json`, `input_integrity.json`, `environment.json` | 최종 집계·기존 artifact 해시·실제 실행 환경 |
| `analysis_final/selected_cases.csv`, `all_violations.csv`, `neighbor_context.csv` | 10개 고정 사례·전체 77개 이상·전후 맥락 **파생 진단표** |
| `analysis_final/*_diagnostic_rows.csv` | 승인 구간 진단 행. 원응답 HTTP JSON과 구분 |
| `analysis_final/*_outside_approved_period.csv` | 구간 밖 행: KC 0행, BRL all-null 1행 |
| `analysis_final/metadata_review.json` | 원래 chart meta와 직렬화 형태 확인 |
| `collect_public_evidence.py`, `public_responses/requests.json` | 제한된 요청 설정·UTC 수집시각·상태·해시; 인증 정보 없음 |
| `public_responses/*.html`, `*.pdf` | requests로 받은 공식 문서 원문 7개 |
| `public_responses/BRL_X_60m_2024-11-06.txt` | **HTTP 429 텍스트 body**. 성공한 시세 JSON이 아님. Content-Type은 requests.json 참조 |
| `source_evidence.json`, `implementation_evidence.json`, `execution_log.json` | 공식 출처·설치 소스·실제 성공/실패 기록 |
| `analysis/`, `analysis_verified/`, `public_attempt/` | 첫 assertion 실패의 부분 산출물·중간 성공 계산·sandbox 네트워크 실패 기록. 최종 결과는 analysis_final |
| `manifest.json`, `verification.json`, `preservation_before.json` | 새 artifact 해시, 문서/수치/비밀정보/기존 파일 보존 검증 |
| `concurrent_changes.json` | 작업 중 감지한 별도 변경과 이동된 과거 CSV 내용 보존 확인 |

`source_evidence.json`의 웹 검색 확인 메모는 HTTP 원문이 아니다. 기존 raw·library·validation 파일은 각자의 경로에서 그대로 보존했다. 이번 공식 자료 확인은 검증 목적이며 모델 입력 소스 채택을 의미하지 않는다.

### 재실행 명령

저장소 루트에서 다음 명령으로 네트워크 없이 재현한다. `mktemp`가 생성하는 고유 디렉터리 아래의 새 하위 경로를 사용해 이전 실행 결과를 덮어쓰지 않는다.

```sh
RUN=data/raw/probes/20260912T091208763138Z_yahoo_ohlc_memo_b242f9
CHECK_DIR=$(mktemp -d /tmp/coffee-yahoo-ohlc.XXXXXX)
.venv/bin/python "$RUN/reproduce.py" --output "$CHECK_DIR/result"
.venv/bin/python "$RUN/verify_artifacts.py"
git diff --check
```

실제 최종 실행은 `--output "$RUN/analysis_final"`로 **exit 0**, 기존 해시 73개·기간 내 1,029행·가격/날짜 대응·이상 행 재현을 통과했다. 첫 시도는 BRL 종료 경계 행을 드러낸 assertion 실패였으며 성공으로 기록하지 않았다. 재현 결과의 수집/실행시각은 과거 timestamp와 분리된다.

산출물 검사도 **exit 0**이다. 사례표 수치 60칸·공통 집계 30칸·맥락 수치 12칸, 로컬 링크 5개, 입력/산출물 해시, 비밀값·인증 query URL 미포함과 `git diff --check`를 확인했다. 보존 스냅샷 180개 중 170개 동일, 별도 이동 CSV 8개 동일 내용, 이번 STATUS 수정 1개, 별도 requirements 수정 1개로 구분한다. 추후 사용자가 문서·환경·기존 데이터를 바꾸면 보존 검사가 실패할 수 있으므로 현재 실행 시점의 확인 결과로 해석한다.

`collect_public_evidence.py`는 외부 요청을 발생시킨다. 이번에는 7개 공식 문서 성공·시간봉 1건 429·1건 미요청으로 끝났으며 일반적인 재현에는 실행할 필요가 없다. 요청 스크립트 exit 0은 소스별 성공을 보장하지 않으므로 반드시 `requests.json`을 확인한다.

## 7. 권고사항·다음 결정

**추천: 조사 결과를 유지하고 가격 의미와 품질 정책은 미확정으로 남긴다.** 이번 조사 범위는 완료했지만 가격 데이터의 품질 문제는 해결되지 않았다. 추가 정보 없이 같은 전체 구간을 반복 수집하거나 값을 자동 수정할 근거는 없다.

다음의 실제 정책 변경은 별도 사용자 승인 사항이다. 현재 승인된 추가 조사는 실행했으며 아래 어느 정책도 새로 채택하지 않았다.

| 결정 대안 | 영향·한계·되돌리기 비용 | 승인 후 변경 범위 |
|---|---|---|
| A. 원본·현 검증 유지, 문제와 미확정 정의를 데이터 계약 초안에 기록 **(추천)** | 해석 가능한 증거가 생길 때 재검토. 값/표본 변화 없음, 되돌리기 비용 낮음. 학습 준비 완료로 볼 수 없음 | 문서 초안·검증 근거 링크. 수집 코드·가격 데이터 변경 없음 |
| B. Close의 의미가 확인된 후 상품별 검증 정책 분리 또는 Settlement 별도 필드 설계 | 정확한 명세와 계약별 대조가 선행되어야 함. 타깃·스키마·검사 결과에 영향, 재검증 비용 중간 | 승인 ADR, 데이터 계약·Notebook/검증 로직, 새 버전 산출물. 기존 raw 보존 |
| C. 이상 행 처리 또는 공급자 교체를 별도 비교 실험으로 검토 | 표본·가격 정의·가용성·비용이 변할 수 있음. 잘못된 보정 위험, 되돌리기/비교 비용 가장 큼 | 먼저 비교 범위·소스·가격 정의 승인 및 ADR. 그 후 별도 코드·데이터 버전 |

유료 자료 구매나 외부 문의가 필요해지면 비용·권한·전송 내용을 먼저 제시한다. 이번에 새 ADR을 쓰지 않은 이유는 이미 승인된 조사만 수행했고 새 가격·소스·검증 정책 결정을 채택하지 않았기 때문이다. Close→Settlement 변경, 이상 행 보정·제외, 공급자 변경, 학습, commit/push는 수행하지 않았다.
