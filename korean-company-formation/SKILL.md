---
name: korean-company-formation
description: Research South Korean legal requirements and collect laws, administrative rules, and official forms, including company formation and HR topics, using the National Law Information Center Open API.
---

# 대한민국 법령 조사 및 자료 수집

사용자의 분야, 적용 대상, 기준일과 원하는 산출물을 파악한다. 법령, 시행령·시행규칙, 행정규칙과 별표·서식을 구분하고 분야를 좁혀 검색한다. 검색 결과에서 적합한 자료를 선별해 원문과 제공되는 서식을 다운로드하고 요청한 폴더에 출처, 조회일과 함께 정리한다. 제목 검색만으로 포괄적 검색이 되지는 않으므로 적절한 유의어와 본문 검색을 병행하고 누락 가능성을 밝힌다. 인사제도와 같은 광범위한 주제는 업종, 근로자 규모, 관심 주제 등에 맞춰 범위를 정한다.

국가법령정보센터 Open API 사용법은 [references/api.md](references/api.md)를 읽는다. `LAW_API_OC` 환경변수에 신청한 인증값이 있을 때 [scripts/law_api.py](scripts/law_api.py)를 사용한다. 인증값을 요구하는 출력이나 저장물에 노출하지 않는다. 인증이 없거나 API 사용이 거절되면 이 사실을 밝히고, 공식 웹 자료 등 이용 가능한 출처로 조사하되 API 연동에 성공했다고 주장하지 않는다. 누락되거나 실패한 첨부 파일을 알린다.

시행일과 부칙, 예외, 기한의 기산점 및 사실관계를 확인하고, 법령의 문언과 해석을 구분한다. 주장별 법령명·조항과 직접 확인한 공식 출처를 연결한다. 행정규칙과 법령의 위계를 구분하며, 법적 요건에 해당하지 않는 일반 실무 양식은 별도로 표시한다. 확인되지 않은 내용은 확정적으로 말하지 않는다. 개별 사건의 전문적인 검토가 필요하면 적절한 전문가의 확인을 권한다.

기존 [주식회사 설립 조사](references/original-report.md)와 [검증 기록](references/verification/verification-report.md)은 2026-10-31 기준 참고 사례이며, 조문 존재와 제목 확인이 각 주장의 정확성이나 현재 효력을 보증하지 않는다.
