# Yahoo OHLC 불일치 원인 조사

- 사용자 요청: Yahoo 불일치 원인 확인 및 수집 컬럼 설명.
- Git: `develop` / `004ac9760611f658fef140ce617728f3f1e30b49` 유지.
- 원래 Probe: `20260912T063021795259Z_99d695f0`.
- 진단 실행: `20260912T084033463809Z_yahoo_diagnostic_b09941`.
- macOS 기존 `.venv`, yfinance 1.7.0. 추가 패키지·수집 코드 변경·기존 데이터 수정 없음.

## 확인한 결론

**불일치는 우리 notebook의 가격 변환·CSV 저장에서 만들어진 것이 아니다. Yahoo chart HTTP 응답의 같은 날짜 OHLC에 이미 존재한다.** 다만 공급자의 OHLC가 서로 다른 가격 의미·집계 기준을 사용하는지, 실제 공급자 데이터 오류인지는 별개의 문제다. 후자의 근본 원인은 아래와 같이 일부만 좁혔으며 확정하지 않았다.

| 검사 | KC=F | BRL=X |
|---|---:|---:|
| 새 chart HTTP 상태 | 200 | 200 |
| 원응답/새 library/기존 Probe 공통 행 | 506 | 523 |
| 새 원응답 가격과 새 library 가격 일치 | 전 행 일치 | 전 행 일치 |
| 새 원응답 가격과 기존 Probe 가격 일치 | 전 행 일치 | 전 행 일치 |
| 원응답 OHLC 범위 위반 | 73행 | 4행 |
| 기존 Probe 위반과 재현 여부 | 동일 | 동일 |
| Close와 Adj Close | 전 행 동일(공동 결측 포함) | 전 행 동일(공동 결측 포함) |
| 원응답 timestamp의 현지 날짜와 library 날짜 | 전 행 동일 | 전 행 동일 |

가격 5개 열(Open/High/Low/Close/Adj Close)을 절대 오차 1e-12, 상대 오차 0, 공동 결측 동등으로 대조했다. 날짜 집합·순서도 동일하다. 부동소수점의 아주 작은 표시 차이를 넘어선 범위 이탈이며, 한 bar의 날짜 전체를 이동하는 것만으로 같은 bar 안의 OHLC 관계가 달라지지도 않는다.

## KC=F: 유력한 설명과 미확인 부분

- 유효 OHLC 504행 중 Close만 범위를 벗어난 73행이다. Open 범위 이탈과 High < Low는 0이다.
- 위반 행 거래량 중앙값은 **18계약**, 나머지 유효 행은 **13,070계약**이다. 위반 73행 중 **67행이 100계약 이하**, 69행이 1,000계약 이하다.
- 예: 2025-03-06 Open/High 413.450012, Low 409.500000, Close 393.000000, Volume 4. Close가 Low보다 **16.5 cents/lb** 낮다. 미세 반올림으로 설명되지 않는다.
- 범위 이탈이 저거래량 구간에 집중되는 패턴은 **거래가격 범위와 별도로 결정되는 정산가격을 Close로 제공했을 가능성**과 부합한다. 이는 현재 가장 유력한 조사 가설이며 Yahoo 필드 의미의 확정이 아니다.

[ICE Trading Rules 4.34(b)(i)–(iv), p.31](https://www.ice.com/publicdocs/rulebooks/futures_us/4_Trading.pdf)을 확인했다. 거래가 활발한 계약의 정산가격은 정산 구간 체결가의 거래량 가중 평균을 기본으로 하지만, 다른 계약이나 해당 구간 체결이 없는 계약에는 호가·계약 간 가격차 등의 기준이 사용될 수 있다. 따라서 **정산가격과 마지막 체결가는 같은 개념이 아니다**. 이 규칙만으로 Yahoo의 73개 Close가 실제 ICE 정산가라고 입증되는 것은 아니다.

반례/한계도 있다. 위반 행에는 거래량 15,678·12,747·10,983계약인 날도 있어 저거래량만으로 전부 설명할 수 없다. KC=F에는 날짜별 실제 만기 계약 코드가 없고 조회 당시 메타데이터의 `underlyingSymbol=KCZ26.NYB`를 2024~2025의 계약에 소급할 수 없다. Yahoo의 개별 날짜 계약 연결 규칙, 거래 범위와 정산가의 정확한 공급자 정의 및 해당 날짜·만기의 공식 정산자료 대조가 남았다. 롤오버가 직접 원인이라고 단정하지 않는다.

## BRL=X: Yahoo 응답의 집계 불일치까지 확인

| 날짜 | Open | High | Low | Close | 범위 위반 |
|---|---:|---:|---:|---:|---|
| 2024-01-01 | 4.850500 | 4.852500 | 4.851800 | 4.850500 | Open/Close < Low |
| 2024-07-29 | 5.622841 | 5.666600 | 5.629232 | 5.622841 | Open/Close < Low |
| 2024-11-06 | 5.700000 | 5.708000 | 5.690000 | 5.739800 | Close > High |
| 2024-12-27 | 6.148500 | 6.209500 | 6.166166 | 6.148500 | Open/Close < Low |

단위는 BRL per USD. 표만 소수 6자리 표시, 저장값은 보정하지 않았다. Open과 Close가 함께 Low보다 낮은 행이 3개이고, Close가 High보다 높은 행이 1개다. 선물 정산가 가설을 환율에 그대로 적용할 근거는 없다. 호가의 bid/ask/mid 차이, 일자 집계 경계 차이 또는 공급자 자료 문제가 후보지만 이를 구별할 quote-level 자료·공급자 명세를 확보하지 못했다. **정확한 상위 공급자 원인은 미확인**으로 남긴다.

## 수집 구현에서 배제한 원인

1. `auto_adjust=False`, `back_adjust=False`, `repair=False`, `rounding=False`를 원래 Probe와 동일하게 유지했다. 보정·repair 실행을 통한 값 변경은 하지 않았다.
2. 설치된 yfinance `utils.py`의 `parse_quotes`는 chart의 `open/high/low/close` 배열을 같은 timestamp 인덱스로 매핑한다. `scrapers/history.py`의 보정 분기는 해당 옵션이 활성화됐을 때만 실행된다. 이번 전 행 가격 대조도 통과했다.
3. [yfinance PriceHistory 문서](https://ranaroussi.github.io/yfinance/reference/yfinance.price_history.html)에서 옵션과 exclusive end를 확인했다. [Price Repair 문서](https://ranaroussi.github.io/yfinance/advanced/price_repair.html)는 repair가 가격 재구성을 시도한다고 설명하지만, 이 결과를 정답으로 삼거나 자동 사용하지 않았다.
4. [Yahoo Adjusted Close 설명](https://in.help.yahoo.com/kb/finance/adjusted-close-sln28256.html)은 주식 split/dividend 조정의 일반 정의다. 이번 두 종목은 실제 반환 Close와 Adj Close가 같아 조정종가 혼용 증거가 없다. 이 설명을 선물 롤 조정의 증거로 사용하지 않았다.

## 추가로 발견한 두 가지 구현상의 한계

### Volume: library의 0은 원응답 0과 다를 수 있음

설치된 `scrapers/history.py:611`는 `repair=False`여도 `Volume.fillna(0)` 후 정수화한다. 이번 실제 재조회에서 확인했다.

| 원응답 → library | KC=F | BRL=X |
|---|---:|---:|
| 원응답 Volume null | 2 | 4 |
| 원응답 Volume 0 | 31 | 519 |
| library Volume null | 0 | 0 |
| library Volume 0 | 33 | 523 |

이전 보고서의 Volume 0/결측 건수는 **library 반환값 기준으로 맞지만 공급자 HTTP 원문 기준과는 다르다**. 원래 artifact가 library return이라고 구분한 이유이며, 이번 새 HTTP 응답을 별도로 보존했다. 이를 선물·환율에서 실제 무거래라고 일괄 해석하면 안 된다. 기존 CSV 값이나 검증 정책은 수정하지 않았다.

### history_metadata가 JSON 객체 대신 문자열로 저장됨

기존 `*_metadata.json`의 `quote_metadata`는 JSON 객체지만 `history_metadata`는 문자열이다. 설치된 yfinance `HistoryMetadata`는 `Mapping` 구현이고, notebook의 `safe_object`는 `dict`만 재귀 처리하여 `json.dumps(default=str)` 경로로 저장됐다. 내용이 텍스트로 남았지만 구조화된 JSON 보존은 아니다. 단위 판정에 사용한 quote_metadata(currency/pair)는 구조화되어 있고 이번 chart 원문에도 meta가 있다.

이는 OHLC 불일치를 일으킨 원인은 아니다. 현재는 조사·설명만 수행했으며 기존 notebook과 이전 응답 파일을 재작성하지 않았다. 후속 구현에서 Mapping의 안전한 직렬화 및 원응답 Volume 보존을 보완할 수 있다.

## 실행·저장·검증

- 명령: `.venv/bin/python /tmp/diagnose_yahoo.py`. 허용된 로컬 네트워크 권한으로 실행, exit 0. 기존 승인 구간의 두 Yahoo 종목만 다시 요청했다. timezone은 기존 Probe에서 확인한 America/New_York 및 Europe/London을 사용하여 현재 날짜용 별도 timezone 조회를 피했다.
- yfinance의 실제 `YfData.get` 반환 응답을 통과시키면서 성공한 chart body만 기록했다. 응답 URL/쿠키/인증 헤더/crumb는 기록하지 않았다. mock 또는 공급자 대체가 아니다.
- `data/raw/probes/20260912T084033463809Z_yahoo_diagnostic_b09941/`: `chart_response_1.json`, `chart_response_2.json`, 각 종목 library CSV·이상 행 CSV, `requests.json`, `diagnostic_summary.json`, `manifest.json`.
- 기존 run의 원본·검증 테이블·Notebook·Context·accepted ADR은 보존했다. 모든 과거 스냅샷과 새 artifact 해시·비밀정보 검사 결과는 `yahoo-investigation-preservation-2026-09-12.json`에 기록한다.
- 전체 컬럼 설명: [Core-4 데이터 사전](../data-dictionary-core4-probe.md).

## 다음 작업과 승인 경계

조사로 문제 발생 위치는 Yahoo 응답 상류로 좁혔지만, 값의 정확성과 Close의 계약을 확정하지는 못했다. 현재 품질 검사 실패 기록은 그대로 유지한다.

| 대안 | 영향·한계·되돌리기 비용 |
|---|---|
| A. 원본 보존 + 개별 계약·공식 정산/공급자 정의 추가 확인(추천) | 성급한 수정 방지. 원자료 변경 없음, 되돌리기 비용 낮음. 공개 자료만으로 해소되지 않을 수 있음 |
| B. Close 의미를 확인한 후 소스별 OHLC 검사 정책 분리 | 선물 정산가를 마지막 체결가로 오해하지 않게 할 수 있음. 가격 정의·품질 정책 변경 승인 필요. 이후 검증 재생성 비용 |
| C. 이상 행 제외·보정 또는 공급자 교체 | 표본/타깃이 달라질 수 있고 원인 해결을 보장하지 않음. 승인·별도 ADR·재검증 필요, 비용 가장 큼 |

B/C는 승인 전 실행하지 않는다. 비용·권한이 필요한 자료 접근이나 외부 문의 전송도 하지 않았다.
