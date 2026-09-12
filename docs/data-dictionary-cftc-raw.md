# CFTC 원본 191개 컬럼 전수 사전

대상: Probe의 2023/2024/2025 `disaggregated_futures_only_YYYY_member.txt`. 세 파일의 원본 헤더 191개가 동일함을 대조했다. 원본 컬럼 순서·이중 underscore를 아래에서 그대로 보존한다. 본문 [Core-4 데이터 사전](data-dictionary-core4-probe.md)의 12개 검증 컬럼과는 범위가 다르다.

## 읽는 기준

- **All**은 모든 만기를 포괄한다. options를 포함한다는 뜻이 아니다. 이번 파일의 보고서 종류는 `FutOnly`다.
- **Old/Other**는 CFTC가 적용하는 작황연도별 만기 범위다. old를 전년도 데이터, other를 다른 상품이라고 해석하지 않는다. Coffee C의 범위별 만기 배정은 별도 검증하지 않았다.
- **Long/Short/Spread**는 방향·상쇄 포지션 분류다. Managed Money/Swap/Other Reportables의 Long/Short는 별도 spreading 이외 잔여 포지션이다. Spread를 거래량이나 두 상품 간 스프레드 가격으로 해석하지 않는다.
- **Change_in**은 이전 보고 대비 변화이므로 음수가 정상일 수 있다. 이번 validation에서는 Change 열을 채택하지 않았다.
- **Pct**는 OI 대비 백분율이고 **Traders**는 계약 수가 아닌 거래자 수다. 거래자별 여러 방향·spreading 중복 때문에 방향별 인원 합계가 전체 인원과 다를 수 있다. 원본 `.` 등 억제 표시는 0이 아니다.
- **Conc**는 상위 거래자의 포지션 집중도이며 Gross는 상쇄 전, Net은 거래자별 매수/매도 상쇄 후 기준이다.
- Old/Other의 long/short/spreading 단순 합이 All과 반드시 같지는 않다. 서로 다른 crop-year 사이에서 상쇄되는 포지션의 분류가 달라질 수 있다.
- 아래 타입은 의미상 타입이다. ZIP 원본은 텍스트이며 이번 조사에서는 모든 원본 열을 문자열로 읽었다. 포지션 컬럼 전부의 숫자 품질 검증을 완료했다는 뜻이 아니다.

정의 근거: [CFTC Disaggregated 설명](https://www.cftc.gov/idc/groups/public/@commitmentsoftraders/documents/file/disaggregatedcotexplanatorynot.pdf), [CFTC Explanatory Notes](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm). 이름과 실제 값은 이미 보존된 사용자 Probe 원본에서 직접 확인했다. 지역/하위그룹 코드의 이름 대응 등 확인하지 않은 내용은 미검증으로 표기했다.

| # | 실제 원본 컬럼 | 의미 | 단위/타입 |
|---:|---|---|---|
| 1 | `Market_and_Exchange_Names` | 시장·거래소 명칭. Coffee C는 COFFEE C - ICE FUTURES U.S. | 문자열 |
| 2 | `As_of_Date_In_Form_YYMMDD` | 보고 기준일 YYMMDD 표기. 발표일이 아님 | 날짜 코드 문자열 |
| 3 | `Report_Date_as_YYYY-MM-DD` | 보고 기준일 YYYY-MM-DD. validation report_date의 출처 | 날짜 문자열 |
| 4 | `CFTC_Contract_Market_Code` | 계약 시장 코드. 083731, 선행 0 보존 | 코드 문자열 |
| 5 | `CFTC_Market_Code` | 거래소/시장 코드. Coffee C에서 ICUS 확인 | 코드 문자열 |
| 6 | `CFTC_Region_Code` | CFTC 지역 코드. Coffee C에서 01; 코드의 지역명 대응은 미검증 | 코드 문자열 |
| 7 | `CFTC_Commodity_Code` | 상품 코드. Coffee C에서 083 및 원본 공백 존재 | 코드 문자열 |
| 8 | `Open_Interest_All` | 미결제약정 계약 수; 모든 만기 | contracts |
| 9 | `Prod_Merc_Positions_Long_All` | 생산·상업·가공·사용자 매수 포지션; 모든 만기 | contracts |
| 10 | `Prod_Merc_Positions_Short_All` | 생산·상업·가공·사용자 매도 포지션; 모든 만기 | contracts |
| 11 | `Swap_Positions_Long_All` | 스왑 딜러 매수 포지션; 모든 만기 | contracts |
| 12 | `Swap__Positions_Short_All` | 스왑 딜러 매도 포지션; 모든 만기 | contracts |
| 13 | `Swap__Positions_Spread_All` | 스왑 딜러 상쇄되는 spreading 포지션; 모든 만기 | contracts |
| 14 | `M_Money_Positions_Long_All` | Managed Money 매수 포지션; 모든 만기 | contracts |
| 15 | `M_Money_Positions_Short_All` | Managed Money 매도 포지션; 모든 만기 | contracts |
| 16 | `M_Money_Positions_Spread_All` | Managed Money 상쇄되는 spreading 포지션; 모든 만기 | contracts |
| 17 | `Other_Rept_Positions_Long_All` | 기타 보고대상 매수 포지션; 모든 만기 | contracts |
| 18 | `Other_Rept_Positions_Short_All` | 기타 보고대상 매도 포지션; 모든 만기 | contracts |
| 19 | `Other_Rept_Positions_Spread_All` | 기타 보고대상 상쇄되는 spreading 포지션; 모든 만기 | contracts |
| 20 | `Tot_Rept_Positions_Long_All` | 전체 보고대상 매수 포지션; 모든 만기 | contracts |
| 21 | `Tot_Rept_Positions_Short_All` | 전체 보고대상 매도 포지션; 모든 만기 | contracts |
| 22 | `NonRept_Positions_Long_All` | 비보고대상 매수 포지션; 모든 만기 | contracts |
| 23 | `NonRept_Positions_Short_All` | 비보고대상 매도 포지션; 모든 만기 | contracts |
| 24 | `Open_Interest_Old` | 미결제약정 계약 수; old crop-year 범위 | contracts |
| 25 | `Prod_Merc_Positions_Long_Old` | 생산·상업·가공·사용자 매수 포지션; old crop-year 범위 | contracts |
| 26 | `Prod_Merc_Positions_Short_Old` | 생산·상업·가공·사용자 매도 포지션; old crop-year 범위 | contracts |
| 27 | `Swap_Positions_Long_Old` | 스왑 딜러 매수 포지션; old crop-year 범위 | contracts |
| 28 | `Swap__Positions_Short_Old` | 스왑 딜러 매도 포지션; old crop-year 범위 | contracts |
| 29 | `Swap__Positions_Spread_Old` | 스왑 딜러 상쇄되는 spreading 포지션; old crop-year 범위 | contracts |
| 30 | `M_Money_Positions_Long_Old` | Managed Money 매수 포지션; old crop-year 범위 | contracts |
| 31 | `M_Money_Positions_Short_Old` | Managed Money 매도 포지션; old crop-year 범위 | contracts |
| 32 | `M_Money_Positions_Spread_Old` | Managed Money 상쇄되는 spreading 포지션; old crop-year 범위 | contracts |
| 33 | `Other_Rept_Positions_Long_Old` | 기타 보고대상 매수 포지션; old crop-year 범위 | contracts |
| 34 | `Other_Rept_Positions_Short_Old` | 기타 보고대상 매도 포지션; old crop-year 범위 | contracts |
| 35 | `Other_Rept_Positions_Spread_Old` | 기타 보고대상 상쇄되는 spreading 포지션; old crop-year 범위 | contracts |
| 36 | `Tot_Rept_Positions_Long_Old` | 전체 보고대상 매수 포지션; old crop-year 범위 | contracts |
| 37 | `Tot_Rept_Positions_Short_Old` | 전체 보고대상 매도 포지션; old crop-year 범위 | contracts |
| 38 | `NonRept_Positions_Long_Old` | 비보고대상 매수 포지션; old crop-year 범위 | contracts |
| 39 | `NonRept_Positions_Short_Old` | 비보고대상 매도 포지션; old crop-year 범위 | contracts |
| 40 | `Open_Interest_Other` | 미결제약정 계약 수; other crop-year 범위 | contracts |
| 41 | `Prod_Merc_Positions_Long_Other` | 생산·상업·가공·사용자 매수 포지션; other crop-year 범위 | contracts |
| 42 | `Prod_Merc_Positions_Short_Other` | 생산·상업·가공·사용자 매도 포지션; other crop-year 범위 | contracts |
| 43 | `Swap_Positions_Long_Other` | 스왑 딜러 매수 포지션; other crop-year 범위 | contracts |
| 44 | `Swap__Positions_Short_Other` | 스왑 딜러 매도 포지션; other crop-year 범위 | contracts |
| 45 | `Swap__Positions_Spread_Other` | 스왑 딜러 상쇄되는 spreading 포지션; other crop-year 범위 | contracts |
| 46 | `M_Money_Positions_Long_Other` | Managed Money 매수 포지션; other crop-year 범위 | contracts |
| 47 | `M_Money_Positions_Short_Other` | Managed Money 매도 포지션; other crop-year 범위 | contracts |
| 48 | `M_Money_Positions_Spread_Other` | Managed Money 상쇄되는 spreading 포지션; other crop-year 범위 | contracts |
| 49 | `Other_Rept_Positions_Long_Other` | 기타 보고대상 매수 포지션; other crop-year 범위 | contracts |
| 50 | `Other_Rept_Positions_Short_Other` | 기타 보고대상 매도 포지션; other crop-year 범위 | contracts |
| 51 | `Other_Rept_Positions_Spread_Other` | 기타 보고대상 상쇄되는 spreading 포지션; other crop-year 범위 | contracts |
| 52 | `Tot_Rept_Positions_Long_Other` | 전체 보고대상 매수 포지션; other crop-year 범위 | contracts |
| 53 | `Tot_Rept_Positions_Short_Other` | 전체 보고대상 매도 포지션; other crop-year 범위 | contracts |
| 54 | `NonRept_Positions_Long_Other` | 비보고대상 매수 포지션; other crop-year 범위 | contracts |
| 55 | `NonRept_Positions_Short_Other` | 비보고대상 매도 포지션; other crop-year 범위 | contracts |
| 56 | `Change_in_Open_Interest_All` | 이전 보고 대비 미결제약정 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 57 | `Change_in_Prod_Merc_Long_All` | 생산·상업·가공·사용자 매수 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 58 | `Change_in_Prod_Merc_Short_All` | 생산·상업·가공·사용자 매도 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 59 | `Change_in_Swap_Long_All` | 스왑 딜러 매수 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 60 | `Change_in_Swap_Short_All` | 스왑 딜러 매도 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 61 | `Change_in_Swap_Spread_All` | 스왑 딜러 상쇄되는 spreading 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 62 | `Change_in_M_Money_Long_All` | Managed Money 매수 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 63 | `Change_in_M_Money_Short_All` | Managed Money 매도 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 64 | `Change_in_M_Money_Spread_All` | Managed Money 상쇄되는 spreading 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 65 | `Change_in_Other_Rept_Long_All` | 기타 보고대상 매수 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 66 | `Change_in_Other_Rept_Short_All` | 기타 보고대상 매도 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 67 | `Change_in_Other_Rept_Spread_All` | 기타 보고대상 상쇄되는 spreading 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 68 | `Change_in_Tot_Rept_Long_All` | 전체 보고대상 매수 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 69 | `Change_in_Tot_Rept_Short_All` | 전체 보고대상 매도 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 70 | `Change_in_NonRept_Long_All` | 비보고대상 매수 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 71 | `Change_in_NonRept_Short_All` | 비보고대상 매도 포지션의 이전 보고 대비 변화. 음수 가능; 모든 만기 | contracts 변화량 |
| 72 | `Pct_of_Open_Interest_All` | 해당 범위 OI를 분모로 한 OI 기준 비율. 이번 Coffee 표에서 100.0; 다른 crop-year에 대한 비중으로 읽지 않음; 모든 만기 | % |
| 73 | `Pct_of_OI_Prod_Merc_Long_All` | 생산·상업·가공·사용자 매수 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 74 | `Pct_of_OI_Prod_Merc_Short_All` | 생산·상업·가공·사용자 매도 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 75 | `Pct_of_OI_Swap_Long_All` | 스왑 딜러 매수 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 76 | `Pct_of_OI_Swap_Short_All` | 스왑 딜러 매도 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 77 | `Pct_of_OI_Swap_Spread_All` | 스왑 딜러 상쇄되는 spreading 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 78 | `Pct_of_OI_M_Money_Long_All` | Managed Money 매수 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 79 | `Pct_of_OI_M_Money_Short_All` | Managed Money 매도 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 80 | `Pct_of_OI_M_Money_Spread_All` | Managed Money 상쇄되는 spreading 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 81 | `Pct_of_OI_Other_Rept_Long_All` | 기타 보고대상 매수 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 82 | `Pct_of_OI_Other_Rept_Short_All` | 기타 보고대상 매도 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 83 | `Pct_of_OI_Other_Rept_Spread_All` | 기타 보고대상 상쇄되는 spreading 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 84 | `Pct_of_OI_Tot_Rept_Long_All` | 전체 보고대상 매수 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 85 | `Pct_of_OI_Tot_Rept_Short_All` | 전체 보고대상 매도 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 86 | `Pct_of_OI_NonRept_Long_All` | 비보고대상 매수 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 87 | `Pct_of_OI_NonRept_Short_All` | 비보고대상 매도 포지션의 해당 범위 OI 대비 비율; 모든 만기 | % |
| 88 | `Pct_of_Open_Interest_Old` | 해당 범위 OI를 분모로 한 OI 기준 비율. 이번 Coffee 표에서 100.0; 다른 crop-year에 대한 비중으로 읽지 않음; old crop-year 범위 | % |
| 89 | `Pct_of_OI_Prod_Merc_Long_Old` | 생산·상업·가공·사용자 매수 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 90 | `Pct_of_OI_Prod_Merc_Short_Old` | 생산·상업·가공·사용자 매도 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 91 | `Pct_of_OI_Swap_Long_Old` | 스왑 딜러 매수 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 92 | `Pct_of_OI_Swap_Short_Old` | 스왑 딜러 매도 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 93 | `Pct_of_OI_Swap_Spread_Old` | 스왑 딜러 상쇄되는 spreading 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 94 | `Pct_of_OI_M_Money_Long_Old` | Managed Money 매수 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 95 | `Pct_of_OI_M_Money_Short_Old` | Managed Money 매도 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 96 | `Pct_of_OI_M_Money_Spread_Old` | Managed Money 상쇄되는 spreading 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 97 | `Pct_of_OI_Other_Rept_Long_Old` | 기타 보고대상 매수 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 98 | `Pct_of_OI_Other_Rept_Short_Old` | 기타 보고대상 매도 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 99 | `Pct_of_OI_Other_Rept_Spread_Old` | 기타 보고대상 상쇄되는 spreading 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 100 | `Pct_of_OI_Tot_Rept_Long_Old` | 전체 보고대상 매수 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 101 | `Pct_of_OI_Tot_Rept_Short_Old` | 전체 보고대상 매도 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 102 | `Pct_of_OI_NonRept_Long_Old` | 비보고대상 매수 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 103 | `Pct_of_OI_NonRept_Short_Old` | 비보고대상 매도 포지션의 해당 범위 OI 대비 비율; old crop-year 범위 | % |
| 104 | `Pct_of_Open_Interest_Other` | 해당 범위 OI를 분모로 한 OI 기준 비율. 이번 Coffee 표에서 100.0; 다른 crop-year에 대한 비중으로 읽지 않음; other crop-year 범위 | % |
| 105 | `Pct_of_OI_Prod_Merc_Long_Other` | 생산·상업·가공·사용자 매수 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 106 | `Pct_of_OI_Prod_Merc_Short_Other` | 생산·상업·가공·사용자 매도 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 107 | `Pct_of_OI_Swap_Long_Other` | 스왑 딜러 매수 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 108 | `Pct_of_OI_Swap_Short_Other` | 스왑 딜러 매도 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 109 | `Pct_of_OI_Swap_Spread_Other` | 스왑 딜러 상쇄되는 spreading 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 110 | `Pct_of_OI_M_Money_Long_Other` | Managed Money 매수 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 111 | `Pct_of_OI_M_Money_Short_Other` | Managed Money 매도 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 112 | `Pct_of_OI_M_Money_Spread_Other` | Managed Money 상쇄되는 spreading 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 113 | `Pct_of_OI_Other_Rept_Long_Other` | 기타 보고대상 매수 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 114 | `Pct_of_OI_Other_Rept_Short_Other` | 기타 보고대상 매도 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 115 | `Pct_of_OI_Other_Rept_Spread_Other` | 기타 보고대상 상쇄되는 spreading 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 116 | `Pct_of_OI_Tot_Rept_Long_Other` | 전체 보고대상 매수 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 117 | `Pct_of_OI_Tot_Rept_Short_Other` | 전체 보고대상 매도 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 118 | `Pct_of_OI_NonRept_Long_Other` | 비보고대상 매수 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 119 | `Pct_of_OI_NonRept_Short_Other` | 비보고대상 매도 포지션의 해당 범위 OI 대비 비율; other crop-year 범위 | % |
| 120 | `Traders_Tot_All` | 중복 제거한 전체 보고대상 거래자 수; 모든 만기 | 거래자 수 |
| 121 | `Traders_Prod_Merc_Long_All` | 생산·상업·가공·사용자 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 122 | `Traders_Prod_Merc_Short_All` | 생산·상업·가공·사용자 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 123 | `Traders_Swap_Long_All` | 스왑 딜러 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 124 | `Traders_Swap_Short_All` | 스왑 딜러 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 125 | `Traders_Swap_Spread_All` | 스왑 딜러 상쇄되는 spreading 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 126 | `Traders_M_Money_Long_All` | Managed Money 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 127 | `Traders_M_Money_Short_All` | Managed Money 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 128 | `Traders_M_Money_Spread_All` | Managed Money 상쇄되는 spreading 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 129 | `Traders_Other_Rept_Long_All` | 기타 보고대상 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 130 | `Traders_Other_Rept_Short_All` | 기타 보고대상 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 131 | `Traders_Other_Rept_Spread_All` | 기타 보고대상 상쇄되는 spreading 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 132 | `Traders_Tot_Rept_Long_All` | 전체 보고대상 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 133 | `Traders_Tot_Rept_Short_All` | 전체 보고대상 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; 모든 만기 | 거래자 수 |
| 134 | `Traders_Tot_Old` | 중복 제거한 전체 보고대상 거래자 수; old crop-year 범위 | 거래자 수 |
| 135 | `Traders_Prod_Merc_Long_Old` | 생산·상업·가공·사용자 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 136 | `Traders_Prod_Merc_Short_Old` | 생산·상업·가공·사용자 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 137 | `Traders_Swap_Long_Old` | 스왑 딜러 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 138 | `Traders_Swap_Short_Old` | 스왑 딜러 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 139 | `Traders_Swap_Spread_Old` | 스왑 딜러 상쇄되는 spreading 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 140 | `Traders_M_Money_Long_Old` | Managed Money 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 141 | `Traders_M_Money_Short_Old` | Managed Money 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 142 | `Traders_M_Money_Spread_Old` | Managed Money 상쇄되는 spreading 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 143 | `Traders_Other_Rept_Long_Old` | 기타 보고대상 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 144 | `Traders_Other_Rept_Short_Old` | 기타 보고대상 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 145 | `Traders_Other_Rept_Spread_Old` | 기타 보고대상 상쇄되는 spreading 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 146 | `Traders_Tot_Rept_Long_Old` | 전체 보고대상 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 147 | `Traders_Tot_Rept_Short_Old` | 전체 보고대상 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; old crop-year 범위 | 거래자 수 |
| 148 | `Traders_Tot_Other` | 중복 제거한 전체 보고대상 거래자 수; other crop-year 범위 | 거래자 수 |
| 149 | `Traders_Prod_Merc_Long_Other` | 생산·상업·가공·사용자 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 150 | `Traders_Prod_Merc_Short_Other` | 생산·상업·가공·사용자 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 151 | `Traders_Swap_Long_Other` | 스왑 딜러 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 152 | `Traders_Swap_Short_Other` | 스왑 딜러 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 153 | `Traders_Swap_Spread_Other` | 스왑 딜러 상쇄되는 spreading 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 154 | `Traders_M_Money_Long_Other` | Managed Money 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 155 | `Traders_M_Money_Short_Other` | Managed Money 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 156 | `Traders_M_Money_Spread_Other` | Managed Money 상쇄되는 spreading 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 157 | `Traders_Other_Rept_Long_Other` | 기타 보고대상 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 158 | `Traders_Other_Rept_Short_Other` | 기타 보고대상 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 159 | `Traders_Other_Rept_Spread_Other` | 기타 보고대상 상쇄되는 spreading 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 160 | `Traders_Tot_Rept_Long_Other` | 전체 보고대상 매수 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 161 | `Traders_Tot_Rept_Short_Other` | 전체 보고대상 매도 포지션을 가진 보고대상 거래자 수; 전체 거래자 수와 단순 합산 불가, 소수 인원은 원본 점 표시 가능; other crop-year 범위 | 거래자 수 |
| 162 | `Conc_Gross_LE_4_TDR_Long_All` | 상위 최대 4개 보고대상 거래자의 매수 집중도; 상쇄 전 gross 기준; 모든 만기 | % of OI |
| 163 | `Conc_Gross_LE_4_TDR_Short_All` | 상위 최대 4개 보고대상 거래자의 매도 집중도; 상쇄 전 gross 기준; 모든 만기 | % of OI |
| 164 | `Conc_Gross_LE_8_TDR_Long_All` | 상위 최대 8개 보고대상 거래자의 매수 집중도; 상쇄 전 gross 기준; 모든 만기 | % of OI |
| 165 | `Conc_Gross_LE_8_TDR_Short_All` | 상위 최대 8개 보고대상 거래자의 매도 집중도; 상쇄 전 gross 기준; 모든 만기 | % of OI |
| 166 | `Conc_Net_LE_4_TDR_Long_All` | 상위 최대 4개 보고대상 거래자의 매수 집중도; 거래자별 long/short 상쇄 후 net 기준; 모든 만기 | % of OI |
| 167 | `Conc_Net_LE_4_TDR_Short_All` | 상위 최대 4개 보고대상 거래자의 매도 집중도; 거래자별 long/short 상쇄 후 net 기준; 모든 만기 | % of OI |
| 168 | `Conc_Net_LE_8_TDR_Long_All` | 상위 최대 8개 보고대상 거래자의 매수 집중도; 거래자별 long/short 상쇄 후 net 기준; 모든 만기 | % of OI |
| 169 | `Conc_Net_LE_8_TDR_Short_All` | 상위 최대 8개 보고대상 거래자의 매도 집중도; 거래자별 long/short 상쇄 후 net 기준; 모든 만기 | % of OI |
| 170 | `Conc_Gross_LE_4_TDR_Long_Old` | 상위 최대 4개 보고대상 거래자의 매수 집중도; 상쇄 전 gross 기준; old crop-year 범위 | % of OI |
| 171 | `Conc_Gross_LE_4_TDR_Short_Old` | 상위 최대 4개 보고대상 거래자의 매도 집중도; 상쇄 전 gross 기준; old crop-year 범위 | % of OI |
| 172 | `Conc_Gross_LE_8_TDR_Long_Old` | 상위 최대 8개 보고대상 거래자의 매수 집중도; 상쇄 전 gross 기준; old crop-year 범위 | % of OI |
| 173 | `Conc_Gross_LE_8_TDR_Short_Old` | 상위 최대 8개 보고대상 거래자의 매도 집중도; 상쇄 전 gross 기준; old crop-year 범위 | % of OI |
| 174 | `Conc_Net_LE_4_TDR_Long_Old` | 상위 최대 4개 보고대상 거래자의 매수 집중도; 거래자별 long/short 상쇄 후 net 기준; old crop-year 범위 | % of OI |
| 175 | `Conc_Net_LE_4_TDR_Short_Old` | 상위 최대 4개 보고대상 거래자의 매도 집중도; 거래자별 long/short 상쇄 후 net 기준; old crop-year 범위 | % of OI |
| 176 | `Conc_Net_LE_8_TDR_Long_Old` | 상위 최대 8개 보고대상 거래자의 매수 집중도; 거래자별 long/short 상쇄 후 net 기준; old crop-year 범위 | % of OI |
| 177 | `Conc_Net_LE_8_TDR_Short_Old` | 상위 최대 8개 보고대상 거래자의 매도 집중도; 거래자별 long/short 상쇄 후 net 기준; old crop-year 범위 | % of OI |
| 178 | `Conc_Gross_LE_4_TDR_Long_Other` | 상위 최대 4개 보고대상 거래자의 매수 집중도; 상쇄 전 gross 기준; other crop-year 범위 | % of OI |
| 179 | `Conc_Gross_LE_4_TDR_Short_Other` | 상위 최대 4개 보고대상 거래자의 매도 집중도; 상쇄 전 gross 기준; other crop-year 범위 | % of OI |
| 180 | `Conc_Gross_LE_8_TDR_Long_Other` | 상위 최대 8개 보고대상 거래자의 매수 집중도; 상쇄 전 gross 기준; other crop-year 범위 | % of OI |
| 181 | `Conc_Gross_LE_8_TDR_Short_Other` | 상위 최대 8개 보고대상 거래자의 매도 집중도; 상쇄 전 gross 기준; other crop-year 범위 | % of OI |
| 182 | `Conc_Net_LE_4_TDR_Long_Other` | 상위 최대 4개 보고대상 거래자의 매수 집중도; 거래자별 long/short 상쇄 후 net 기준; other crop-year 범위 | % of OI |
| 183 | `Conc_Net_LE_4_TDR_Short_Other` | 상위 최대 4개 보고대상 거래자의 매도 집중도; 거래자별 long/short 상쇄 후 net 기준; other crop-year 범위 | % of OI |
| 184 | `Conc_Net_LE_8_TDR_Long_Other` | 상위 최대 8개 보고대상 거래자의 매수 집중도; 거래자별 long/short 상쇄 후 net 기준; other crop-year 범위 | % of OI |
| 185 | `Conc_Net_LE_8_TDR_Short_Other` | 상위 최대 8개 보고대상 거래자의 매도 집중도; 거래자별 long/short 상쇄 후 net 기준; other crop-year 범위 | % of OI |
| 186 | `Contract_Units` | 계약 규격 텍스트. Coffee C는 CONTRACTS OF 37,500 POUNDS. 포지션 숫자는 pounds가 아니라 계약 수 | 문자열 |
| 187 | `CFTC_Contract_Market_Code_Quotes` | 동명 계약 시장 코드의 추가 export 필드. 083731; 가격 quote가 아님 | 코드 문자열 |
| 188 | `CFTC_Market_Code_Quotes` | 시장 코드의 추가 export 필드. ICUS; 호가가 아님 | 코드 문자열 |
| 189 | `CFTC_Commodity_Code_Quotes` | 상품 코드의 추가 export 필드. 083 및 원본 공백 보존 | 코드 문자열 |
| 190 | `CFTC_SubGroup_Code` | 상품 하위그룹 분류 코드. Coffee C에서 A50; 분류 명칭 대응은 미검증 | 코드 문자열 |
| 191 | `FutOnly_or_Combined` | 보고서 구분. 이번 FutOnly. Combined 보고서를 뜻하지 않음 | 문자열 |
