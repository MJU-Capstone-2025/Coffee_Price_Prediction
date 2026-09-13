# Coffee Price Prediction

학부 때 만든 커피 가격 예측 프로젝트를 다시 정리하고 있습니다. 데이터를 받는 과정부터 예측 결과를 차트로 보여주는 것까지 직접 연결하는 게 목표입니다.

커피 선물·환율·거시지표·기상·투자자 포지션을 한 스크립트로 수집해 Parquet로 저장합니다. 2016~2025년 12개 테이블을 묶어 Naive·Ridge·CatBoost까지 비교했습니다. 다음 단계는 FastAPI와 대시보드입니다.

## 실행하기

Python 3.12를 사용합니다. 가상환경은 Google Drive가 동기화하는 프로젝트 폴더 밖에 둡니다. FRED 수집에는 `.env`의 `FRED_API_KEY`가 필요합니다.

처음 설치할 때만 가상환경을 만듭니다. PyCaret은 실행을 확인한 **4.0.0a8 알파 버전**으로 고정했습니다. 설치 extra는 `timeseries`입니다.

```sh
uv venv --python 3.12 "$HOME/.virtualenvs/coffee-price-prediction"
source "$HOME/.virtualenvs/coffee-price-prediction/bin/activate"
uv pip install -r requirements.txt
python -m ipykernel install --user --name coffee-price-prediction --display-name "Coffee Price Prediction (Python 3.12)"
```

이후에는 활성화 명령만 실행하면 됩니다. Notebook에서는 위 이름의 커널을 선택합니다. Apple Silicon에서 OpenMP 라이브러리가 없다는 오류가 나면 `brew install libomp`로 설치합니다.

```sh
source "$HOME/.virtualenvs/coffee-price-prediction/bin/activate"
python data_code/02_backfill_10y.py
```

기본 기간은 **2016-01-01 ~ 2025-12-31**입니다. 짧게 확인하거나 특정 소스만 다시 받을 수도 있습니다.

```sh
python data_code/02_backfill_10y.py --start 2025-01-01 --end 2025-01-31
python data_code/02_backfill_10y.py --sources yahoo fred
```

결과는 `data/processed/2016-01-01_2025-12-31/`에 저장합니다. 다른 기간은 별도 폴더를 사용합니다. 같은 기간을 다시 실행하면 해당 테이블을 갱신하고, 실패한 테이블의 기존 파일은 유지합니다. 실패한 소스 이름은 터미널에 표시하며 하나라도 실패하면 종료 코드 1을 반환합니다.

기상 파일은 30일 집계에 쓸 버퍼를 앞뒤로 더 받습니다. 기본 기간에서는 `2015-12-02 ~ 2026-01-30`이 저장되며 모델 기간은 2016~2025년 그대로입니다. 기상만 수집하려면 `python data_code/02_backfill_10y.py --sources nasa`를 실행합니다.

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
- [03_eda_and_baseline_models.ipynb](data_code/03_eda_and_baseline_models.ipynb): As-of Join, 분포·계절성·상관관계·회귀 분석, 피처 선택·파생 피처 실험과 PyCaret 단변량 기준 모델 비교. Python 3.12 커널에서 위부터 실행합니다.
- `data_code/old_code/`, `data/old_data/`, `docs/old_docs/`: 학부 프로젝트 자료.

설계 선택은 [설계 노트](docs/architecture.md), Yahoo 가격 조사는 [트러블슈팅](docs/troubleshooting.md)에 정리했습니다.

## 첫 모델 비교

5거래일 뒤 로그수익률을 예측했습니다. 2016~2021년 학습, 2022~2023년 검증으로 설정을 고른 뒤 2016~2023년으로 다시 학습했습니다. 아래는 2024~2025년 테스트 498건의 결과입니다.

| 모델 | MAE | RMSE | 방향성 정확도 |
|---|---:|---:|---:|
| Naive (수익률 0) | 0.042810 | 0.054442 | 0.40% |
| Ridge | 0.044329 | 0.057099 | 46.79% |
| CatBoost | 0.043006 | 0.054674 | 47.19% |

0은 보합으로 셉니다. Naive의 방향성 정확도는 실제 수익률이 0인 비율이며, 오차 비교를 위한 기준 모델입니다. CatBoost는 아직 Naive를 넘지 못했습니다. 중요도는 Huila의 30일 평균 기온, 20거래일 수익률, BRL 환율 순이었습니다.

PyCaret 4에서는 외생변수 없이 다섯 단변량 모델을 비교했습니다. 2022~2023년 순차 검증에서는 가격 유지가 가장 낮은 RMSE를 보였고, 기존 테스트에서도 같은 Naive 기준으로 남았습니다. 피처 선택과 파생 피처 추가도 검증 오차를 줄이지 못해 전체 피처 구성을 유지했습니다. 실험 과정과 비교표는 `03` notebook 하단에 있습니다.

개발 구간의 종가와 WTI·COT 순매수 비율 사이에는 상관이 있었지만, 5거래일 뒤 수익률과의 상관은 약했습니다. 21개 단일 피처 회귀의 검증 R²는 모두 음수였습니다. 기상 버퍼로 초반 결측은 해결했지만, 예측력이 좋아진 것은 아니었습니다.

관측일에 바로 붙이지 않고 공개 지연을 가정해 병합했습니다. 과거 발표시각·수정 전 값은 파일에 없으며, 지연 가정과 COT 발표 예외는 notebook에 적었습니다. 가격 그래프도 매일 계산한 5거래일 앞 예측을 해당 날짜에 맞춰 그렸습니다.

## Troubleshooting & 배운 점

Yahoo 커피 데이터에서 Close가 당일 High–Low 범위를 벗어난 행을 발견했습니다. 원응답과 대조해보니 Yahoo 응답에도 같은 값이 있었습니다. 정산 방식이나 계약 연결 차이가 원인일 수 있어, 값을 억지로 고치기보다 가격 피처를 과거 Close로 만들었습니다. 로그수익률로 바꿔도 롤오버 영향이 없어지는 것은 아니라는 점도 함께 고려하고 있습니다.

기상 피처의 초반 NaN은 원자료 누락이 아니라 30일 집계에 필요한 과거 관측값 부족이었습니다. 중앙값 대치를 없애고 기상 수집에 버퍼를 뒀습니다. [버퍼 전후 Jupyter 출력과 해결 과정](docs/troubleshooting.md#30일-기상-집계에서-생긴-초반-nan)을 함께 남겼습니다.

파일럿 원응답은 `data/raw/pilot_probe/`에 소스별로 한 벌만 보관합니다. `.env`와 수집 데이터는 로컬 파일이며, 공개 저장소에서 새로 받으려면 수집 스크립트를 실행합니다.
