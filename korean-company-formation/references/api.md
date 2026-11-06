# 국가법령정보센터 API 사용

공동활용 신청과 OC 발급: https://open.law.go.kr/LSO/usrJoin.do . 서비스·자료 유형 및 서버 IP/도메인 등록이 필요할 수 있다. OC를 사용자에게 채팅으로 보내달라고 하지 말고 사용자가 실행 환경의 `LAW_API_OC`에 직접 설정하도록 안내한다. 예: PowerShell에서 `$env:LAW_API_OC = '발급받은_인증값'` (현재 세션). 영구 설정 또는 비밀 저장은 사용자 환경의 적절한 방법을 따른다. 발급 여부, 허용 데이터와 연결은 실제 호출로 확인한다. 공식 `test` 값은 사용자 인증 오류가 날 수 있다.

Python 표준 라이브러리만 필요하다. `python`은 사용 가능한 Python 3 실행 경로로 바꾼다. 스크립트는 스킬의 `scripts/law_api.py`를 뜻한다.

```powershell
python scripts/law_api.py search --target eflaw --query 근로기준법 --limit 20
python scripts/law_api.py search --target admrul --query 근로감독 --limit 20
python scripts/law_api.py search --target licbyl --query 근로계약 --limit 20
python scripts/law_api.py search --target admbyl --query 근로 --limit 20
```

검색범위 `--search 1`은 제목, `2`는 법령·행정규칙의 본문 또는 별표서식의 관련 법령명, `3`은 별표 본문 검색이다. API별 지원 범위는 공식 가이드에서 확인한다. 결과가 많으면 `--page`를 바꿔 확인한다. 법령 검색은 `nw=3` 현행 필터를 사용한다.

선별한 법령은 결과의 `법령일련번호`, `시행일자`를 사용한다. 행정규칙은 `행정규칙일련번호`를 사용한다. 본문 XML과 응답에서 찾은 첨부 파일을 저장한다.

```powershell
python scripts/law_api.py collect --target eflaw --id 일련번호 --effective 시행일8자리 --name 근로기준법 --output 자료폴더
python scripts/law_api.py collect --target admrul --id 일련번호 --name 규칙명 --output 자료폴더
```

별표서식은 같은 검색어, 검색범위, 페이지와 결과의 `별표일련번호`를 사용한다. 제공된 원본 또는 PDF 링크를 다운로드한다.

```powershell
python scripts/law_api.py form --target licbyl --query 근로계약 --id 일련번호 --name 서식명 --output 자료폴더
```

결과의 `출처.json`은 출처, 조회일, 다운로드 성공·실패를 기록한다. 기존 동일 폴더는 덮어쓰지 않는다. 국가법령정보센터에서 제공하지 않는 실무 서식이나 다른 기관의 지침은 해당 기관의 공식 출처에서 별도 확인한다. 법령 API의 현행 필터가 과거 특정일 분석을 대신하지 않는다. 파일의 실질 내용, 유효성, 연관성과 효력은 사람이 읽고 확인해야 한다. 자료를 정리할 때 주제별 요약과 목록을 별도로 작성하되 원문과 요약을 구분한다.

공식 가이드: https://open.law.go.kr/LSO/openApi/guideList.do ; 시행일 법령 https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=lsEfYdListGuide ; 별표서식 https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=lsBylListGuide .
