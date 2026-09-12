# Coffee Price Prediction

학부 때 만든 커피 가격 예측 프로젝트를 다시 정리하고 있습니다. 데이터를 받는 과정부터 예측 결과를 차트로 보여주는 것까지 직접 연결하는 게 목표입니다.

현재는 커피 선물·환율·거시지표·기상·투자자 포지션을 한 스크립트로 수집해 Parquet로 저장합니다. 2016~2025년 데이터 12개 테이블의 수집·저장을 확인했고, 커피 가격은 2,519행입니다. 다음 단계는 CatBoost 기준 모델과 FastAPI·대시보드입니다.

## 실행하기

프로젝트 루트에서 기존 Python 3.14 환경을 사용합니다. FRED 수집에는 `.env`의 `FRED_API_KEY`가 필요합니다.

새로 clone한 환경에서만 `python3.14 -m venv .venv`로 환경을 만든 뒤, 활성화하고 `python -m pip install -r requirements.txt`로 패키지를 설치합니다. 이미 `.venv`가 있으면 그대로 사용합니다.

```sh
source .venv/bin/activate
python data_code/02_backfill_10y.py
```

기본 기간은 **2016-01-01 ~ 2025-12-31**입니다. 짧게 확인하거나 특정 소스만 다시 받을 수도 있습니다.

```sh
python data_code/02_backfill_10y.py --start 2025-01-01 --end 2025-01-31
python data_code/02_backfill_10y.py --sources yahoo fred
```

결과는 `data/processed/2016-01-01_2025-12-31/`에 저장합니다. 다른 기간은 별도 폴더를 사용합니다. 같은 기간을 다시 실행하면 해당 테이블을 갱신하고, 실패한 테이블의 기존 파일은 유지합니다. 실패한 소스 이름은 터미널에 표시하며 하나라도 실패하면 종료 코드 1을 반환합니다.

## 수집하는 데이터

| 데이터 | 출처 | 저장 파일 |
|---|---|---|
| 커피 선물·브라질 환율 일봉 | [yfinance](https://ranaroussi.github.io/yfinance/reference/api/yfinance.Ticker.history.html) | `coffee.parquet`, `brl.parquet` |
| 실효금리·광의 달러지수·WTI 현물 | [FRED](https://fred.stlouisfed.org/docs/api/fred/series_observations.html) | `dff.parquet`, `dtwexbgs.parquet`, `dcoilwtico.parquet` |
| 브라질·콜롬비아 6개 지점의 강수·기온·습도 | [NASA POWER](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) | `weather_<지역>.parquet` |
| 커피 선물 주별 투자자 포지션 | [CFTC](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm) | `cot.parquet` |

날짜를 정렬하고 중복·빈 응답을 확인합니다. FRED의 `.`와 NASA 결측 표시는 NaN으로 바꿉니다. 가격은 임의로 채우지 않고, 각 소스의 원래 주기로 저장합니다. 가격 단위는 cents/lb, 환율은 BRL/USD이며 COT의 날짜는 발표일이 아닌 포지션 기준일입니다. 수집값은 현재 제공되는 과거 자료입니다.

## 코드 위치

- [02_backfill_10y.py](data_code/02_backfill_10y.py): 수집 → 결측 표시 정리 → Parquet 저장.
- [regions.yaml](configs/regions.yaml): 기상 데이터를 요청할 6개 좌표.
- [01_small_batch_probe.ipynb](data_code/01_small_batch_probe.ipynb): 저장된 파일럿 자료의 검증 표와 가격 그래프.
- `data_code/old_code/`, `data/old_data/`, `docs/old_docs/`: 학부 프로젝트 자료.

설계 선택은 [설계 노트](docs/architecture.md), Yahoo 가격 조사는 [트러블슈팅](docs/troubleshooting.md)에 정리했습니다.

## Troubleshooting & 배운 점

Yahoo 커피 데이터에서 Close가 당일 High–Low 범위를 벗어난 행을 발견했습니다. 원응답과 대조해보니 Yahoo 응답에도 같은 값이 있었습니다. 정산 방식이나 계약 연결 차이가 원인일 수 있어, 값을 억지로 고치기보다 Close를 유지하고 첫 모델은 과거 Close에서 만든 피처로 시작하려고 합니다. 로그수익률로 바꿔도 롤오버 영향이 없어지는 것은 아니라는 점도 함께 고려하고 있습니다.

파일럿 원응답은 `data/raw/pilot_probe/`에 소스별로 한 벌만 보관합니다. `.env`와 수집 데이터는 로컬 파일이며, 공개 저장소에서 새로 받으려면 수집 스크립트를 실행합니다.
