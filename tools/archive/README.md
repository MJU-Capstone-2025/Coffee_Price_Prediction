# 지난 일회성 진단 도구

`yahoo_ohlc/`는 2026-09-12 Yahoo 추가 조사에 사용한 Python 3개의 당시 버전입니다. 원래 `data/raw/probes/`에 있던 파일을 내용 변경 없이 이곳으로 옮겼습니다.

현재 수집·검증의 실행 진입점은 [단일 Notebook](../../data_code/01_small_batch_probe.ipynb)입니다. 보관 스크립트를 Notebook의 필수 단계로 호출하지 않습니다. 스크립트 안의 RUN 경로와 과거 스냅샷 검사는 당시 디렉터리를 전제로 하므로 현재 위치에서 바로 실행하는 도구로 안내하지 않습니다.

이전 실행 명령·성공/실패 결과는 역사적 기록으로 보존합니다. 파일의 현재 위치와 해시는 [이동 매핑](../../docs/reports/directory-reorganization-2026-09-12.json), 조사 결론은 [기술 메모](../../docs/reports/yahoo-ohlc-technical-memo.md)를 참조합니다. 수집 원응답과 진단 데이터는 `data/`에 남아 있습니다.
