# ADR 003: Core-4 Probe용 브라질·콜롬비아 기상 요청 지점 선정

## 상태 (Status)

수락됨

결정일: 2026-09-12. 적용 범위: 초기 Core-4 Probe.

## 배경 (Context)

아라비카 가격 예측에 기상 자료를 활용하기 전에 실제 접근 가능성, 응답 품질, 지점 간 중복 가능성을 확인해야 한다. 모든 생산국·재배지를 처음부터 다루기보다 제한된 지점으로 자료의 특성과 공간적 한계를 검토할 필요가 있다.

브라질·콜롬비아를 우선 탐색하는 근거로 ICO의 2022/23 생산 통계를 사용했다. 세계 아라비카 94.0백만 포대 중 브라질 41.8, 콜롬비아 10.7백만 포대의 합계 비중은 약 55.9%다. 이는 당시 60kg 포대 기준의 계산값이며 최신 비중이나 국가별 3지점 배분의 근거가 아니다.

## 결정 (Decision)

브라질과 콜롬비아의 서로 다른 재배권역을 제한적으로 탐색하기 위해 아래 6개 요청 지점을 사용한다. 좌표는 Probe에 승인된 값이며 본수집의 최종 표본으로 확정하지 않는다.

| region_id | 국가 | 권역 | 요청 지점 | latitude | longitude |
|---|---|---|---|---:|---:|
| br_sul_minas | Brazil | Sul de Minas | Três Pontas | -21.3700 | -45.5100 |
| br_cerrado | Brazil | Cerrado Mineiro | Patrocínio | -18.9439 | -46.9925 |
| br_alta_mogiana | Brazil | Alta Mogiana | Franca | -20.5389 | -47.4008 |
| co_huila | Colombia | Huila | Gigante / Jorge Villamil | 2.3333 | -75.5167 |
| co_caldas | Colombia | Caldas | Chinchiná / Naranjal | 4.9667 | -75.6500 |
| co_antioquia | Colombia | Antioquia | Venecia / El Rosario | 5.9667 | -75.7000 |

NASA POWER Daily Point API의 `community=AG`, UTC 일별 자료를 사용한다. 변수는 PRECTOTCORR, T2M, T2M_MIN, T2M_MAX, RH2M이다. 요청 좌표와 실제 응답의 위치·제품 정보를 구분해 보존한다.

국가 평균·가중평균·예측 피처는 이 결정에 포함하지 않는다. 6개 지점은 같은 날짜의 공간별 자료이며 가격 표본을 6개로 늘리는 근거로 사용하지 않는다.

## 결과 (Consequences)

### 긍정적

#### 제한된 요청 범위에서 두 국가의 재배권역을 비교할 수 있다

한 국가에만 집중하지 않고 여러 권역의 자료 접근성과 지점 간 중복 가능성을 살펴볼 수 있다.

#### 본수집 전 공간적 한계를 검토할 수 있다

지점별 응답과 비교 결과를 바탕으로 좌표·격자 선택을 다시 검토할 근거를 확보할 수 있다.

### 부정적

#### 국가·권역 전체의 대표성을 보장하지 않는다

국가별 3지점은 생산량 비례 배분이 아니며 생산량 가중 중심점이나 최적 관측점도 아니다. 격자 자료가 산악 미기후·고도 효과를 충분히 표현하는지는 별도로 검토해야 한다.

#### 일부 좌표의 출처 확인이 충분하지 않다

결정 당시 Franca 좌표는 문헌과 부합했지만, 나머지 지점은 원문 접근 제한 또는 정확한 좌표 근거 부족으로 독립 확인이 충분하지 않았다. 승인된 요청점이라는 범위를 넘어 검증된 관측장비 위치로 해석하지 않는다.

### 중립적

#### 격자 자료와 직접 관측·과거 빈티지를 구분한다

POWER 값은 연구소 관측장비의 직접 관측값이 아니다. 요청 좌표·API geometry·원천 격자를 동일시하지 않으며 높은 상관만으로 같은 격자라고 판단하지 않는다. 현재 조회한 자료를 과거 공개 시점의 빈티지 재현으로 표현하지 않는다.

#### 본수집 전에 지점 구성을 재검토할 수 있다

동일 시계열, 좌표 근거 오류, 격자·제품 정의 변화 또는 지역 생산·면적 통계가 확인되면 재검토한다. 지점 추가·교체·삭제나 가중치 도입은 후속 결정으로 다룬다.

## 검토한 대안 (Options)

### 대안 1: 단일 국가만 탐색

요청량은 줄지만 두 국가의 서로 다른 재배 환경을 함께 확인할 수 없다. 초기 공간 비교 범위를 확보하기 위해 채택하지 않았다.

### 대안 2: 다른 생산국 추가

공간 범위는 넓어지지만 요청·좌표 근거 조사·검증 범위가 커진다. 초기 Probe의 제한된 탐색 범위를 유지하기 위해 채택하지 않았다.

### 대안 3: 생산량·재배면적 기반 격자 선정

재배 분포에 근거한 표본 설계가 가능하지만 시점별 생산·면적·위치 자료와 가중치 설계가 필요하다. 초기 접근·품질 확인보다 준비 범위가 커서 본수집 전 재검토 대상으로 남겼다.

## 참조

- [ADR 001: Apple Silicon 로컬 개발 환경](ADR-001-local-development-environment.md)
- [ADR 002: 초기 소규모 수집·검증은 notebook으로 실행](ADR-002-notebook-first-small-batch.md)
- [ICO Coffee Report and Outlook, December 2023](https://icocoffee.org/documents/cy2023-24/Coffee_Report_and_Outlook_December_2023_ICO.pdf): 국가 생산 통계.
- [Coffea arabica L: History, phenology and climatic aptitude](https://www.scielo.br/j/aib/a/VhJ6bxGkf8Jfj5mdVyr3YxS/?lang=en): Franca/Alta Mogiana 위치 근거.
- [NASA POWER Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/), [기상 자료 방법론](https://power.larc.nasa.gov/docs/methodology/meteorology/): 시간 기준과 자료 특성.
- [좌표 출처별 확인 기록](../STATUS.md#adr-003에서-이관한-조사실행-기록): 미확인 자료를 포함한 결정 당시의 조사 기록.
