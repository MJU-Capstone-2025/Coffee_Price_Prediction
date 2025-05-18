## 모델 개발 상황 정리
예측을 할 때 test 데이터 전체에 대해서 각 시점의 14일 후를 예측하도록 해줌 <br>
### 🟦 고려사항 정리
1. Coffe_Price는 정규화하지 않고 그대로 쓰는게 가격의 변화를 더 민감하게 잡아낼 수 있을 것이다. <br>
- 정규화를 하지 않으면 loss값이 과도하게 커지거나 진동하게 되어 수렴이 늦어지게 된다. 또한 모델이 작은 변화에 민감해지기 더 어렵기 때문에 정규화를 똑같이 진행하였다.
2. 모델 학습 후 학습한 결과와 실제간의 잔차에 대해서 다시 학습하는 모델을 만들어 두 모델 결과를 합친 것을 최종 결과로 사용한다 -> 병렬적으로 수행 <br>

|모델|역할|
|----|----|
|기존 학습 모델| bias를 줄이기 위한 구조 |
|잔차 학습 모델| variance를 줄이기 위한 구조 |

### 🟦 기존 학습 모델
### ⭐ 모델 수정 사항

|hyperparameter|tuning|
|----|----|
|drop out| 0.1 -> 0.3 |
|batch size| 10 -> 64 |
|hidden size| 100 -> 32|
|epoch| 200 -> 80|
|Learning rate|0.001기본으로 설정하며 10 epoch당 개선이 없으면 0.3 씩 줄여줌(스케줄러 사용)|

### ⭐ 결과 비교

|tuning 전|tuning 후|
|----|----|
|![image](https://github.com/user-attachments/assets/0780c2c9-b6c9-4ad4-9266-88fa92b9b2e1)|![image](https://github.com/user-attachments/assets/7d8edcc2-a0b2-461b-b8b2-df772075986e)|

여전히 실제값과의 차이가 있지만 이전에 비해 더 정확하게 추세를 예측한다.

### 🟦 잔차 학습 모델
### ⭐ 목적
기존 모델이 예측하지 못한 비선형/급격한 잔차를 보완하고자 한다
- 기존 모델(LSTM + Attention)은 전반적인 추세와 완만한 패턴을 잡아내지만 global한 유연성이 부족하다.
- 이를 보안하기 위해 기존 모델이 놓친 급변이나 복잡한 시계열 상호작용을 보완하는 것이 필요하다.
- Transformer 모델을 사용하는데 잔차 모델이 전체 예측을 뒤집어씌우는 식으로 작용한다면 잔차모델이 사실상 주 모델이 되는 문제가 발생한다.
- 따라서 기본 모델로 대부분의 구조를 커버하고 잔차 모델은 변화를 감지하는 정도의 역할로 사용하게 한다. -> loss function을 이상치에 덜 민감한 걸로 해줌
### ⭐ Transformer 모델 구조
참고 코드
> [Transformer Encoder Model for Time Series – YongTaeIn](https://github.com/YongTaeIn/Transformer-Encoder-model-for-time-series)
#### 모델 설계 요약도
| 구성요소        | 방식                    | 기능 및 목적                    |
| --------------- | ----------------------- | ----------------------- |
| 시계열 인코더 | Transformer Encoder | 시계열 내 전역 의존성 파악|
| 위치 인코딩 | Positional Encoding | 순차 정보 반영|
| 인코딩 출력 요약| Attention Encoding | 시점별 중요도 반영하여 대표 정보 추출|
| 예측 해드 | 2-layer FC + Dropout | 잔차 예측, 복잡한 비선형 잔차 패턴 학습|
| Loss Function	| Huber Loss | 이상치에 덜 민감한 예측 오류 보정|
|Optimizer|	Adam	| 안정적 학습 |
|Learning Rate 스케줄|	ReduceLROnPlateau|	Validation 성능 정체 시 학습률 자동 감소|

#### 모델 구조 흐름 요약
<img src = "https://github.com/user-attachments/assets/3f461094-d536-4d1f-81da-acbb95e3ee4b" width= 500>

### ⭐ 결과 비교

|기존 모델만 사용|잔차 학습 모델까지 사용|
|----|----|
|![image](https://github.com/user-attachments/assets/7d8edcc2-a0b2-461b-b8b2-df772075986e)|![image](https://github.com/user-attachments/assets/3b40e505-ea1b-4ad3-9dc2-c679c1dac9a7)|

기존에 비해 25일 이후의 추세가 더 보정되었지만 25일 전은 크게 달라진 것이 없으며 여전히 예측값의 차이가 난다.


### ⭐ 전체 모델 구조 요약

<img src = "https://github.com/user-attachments/assets/8282d7f9-5e73-4a08-b7e1-8ab38826efce" width= 400>

### ⭐ 결과
- 약간의 개선 정도만 해냈으며 전반적인 오차는 여전함
