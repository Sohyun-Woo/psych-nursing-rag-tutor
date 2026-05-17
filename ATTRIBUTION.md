# 출처 및 라이선스 명시 (Attribution and License)

본 문서는 본 프로젝트에서 활용한 외부 자료의 출처와 라이선스를 명시하기 위해 
작성되었습니다. Creative Commons BY-NC-SA 3.0 IGO 라이선스의 BY(저작자 표시) 
조건을 준수합니다.

---

## 1. WHO Psychological First Aid: Guide for Field Workers (PFA)

### 원본 정보
- **제목 (English)**: Psychological first aid: Guide for field workers
- **제목 (한국어)**: 심리적 응급처치: 현장실무자들을 위한 가이드
- **발행기관**: World Health Organization, War Trauma Foundation, World Vision International
- **발행연도**: 2011 (영문 원본), 2013 (한국어 번역)
- **한국어 번역**: 한국 월드비전 (World Vision Korea)
- **ISBN**: 9789241548205

### 출처 URL
- **WHO IRIS (영문)**: https://iris.who.int/handle/10665/44615
- **WHO IRIS (한국어판)**: https://iris.who.int/bitstream/10665/44615/4/9789241548205_kor.pdf
- **WHO 공식 페이지**: https://www.who.int/publications/i/item/9789241548205

### 라이선스
**CC BY-NC-SA 3.0 IGO** (Creative Commons Attribution-NonCommercial-ShareAlike 
3.0 Intergovernmental Organization)
- 전문: https://creativecommons.org/licenses/by-nc-sa/3.0/igo/

### 인용 방식 (Suggested Citation)
```
World Health Organization, War Trauma Foundation & World Vision International. 
(2011). 심리적 응급처치: 현장실무자들을 위한 가이드 [Psychological first aid: 
Guide for field workers]. (한국 월드비전 번역). World Health Organization. 
https://iris.who.int/handle/10665/44615
License: CC BY-NC-SA 3.0 IGO
```

### 본 프로젝트에서의 사용 방식
- **목적**: 위기 상황에서의 치료적 의사소통 학습 자료
- **활용 방법**: RAG(Retrieval-Augmented Generation) 시스템의 검색용 임베딩
- **변형 정도**: 원문을 청크 단위로 분할하여 의미 검색에 활용. 
  학생 질문에 대한 응답 시 관련 청크를 검색하여 인용하며, 원문 표현을 
  최대한 보존함

---

## 2. WHO mhGAP Intervention Guide v2.0

### 원본 정보
- **제목**: mhGAP intervention guide for mental, neurological and substance 
  use disorders in non-specialized health settings – version 2.0
- **발행기관**: World Health Organization
- **발행연도**: 2016
- **ISBN**: 978-92-4-154979-0
- **한국어판**: 공식 한국어 번역본 존재하지 않음 (영문 원본 사용)

### 출처 URL
- **WHO 공식 페이지**: https://www.who.int/publications/i/item/9789241549790
- **WHO IRIS PDF**: https://iris.who.int/server/api/core/bitstreams/6ded7ffd-9d69-493a-b48a-0b3e6250c173/content

### 라이선스
**CC BY-NC-SA 3.0 IGO**
- 전문: https://creativecommons.org/licenses/by-nc-sa/3.0/igo/

### 인용 방식 (Suggested Citation)
```
World Health Organization. (2016). mhGAP intervention guide for mental, 
neurological and substance use disorders in non-specialized health settings 
– version 2.0. Geneva: World Health Organization. 
https://www.who.int/publications/i/item/9789241549790
License: CC BY-NC-SA 3.0 IGO
```

### 본 프로젝트에서의 사용 방식
- **목적**: 우선순위 정신건강 질환의 임상 사정 및 관리 권고 학습 자료
- **활용 방법**: RAG 시스템의 검색용 임베딩
- **변형 정도**: 원문 텍스트 권고사항만 청크 분할하여 임베딩. 표·그림은 
  제3자 권리 가능성을 고려하여 임베딩 대상에서 제외함

---

## 3. 라이선스 준수 체크리스트

### BY (Attribution) - 저작자 표시
- [x] LICENSE 파일에 WHO 저작권 명시
- [x] ATTRIBUTION.md에 상세 출처 정보 기록
- [x] README.md에 자료 출처 명시
- [x] RAG 응답 생성 시 모든 인용에 출처 자동 표시
- [x] 원본 PDF에 포함된 WHO 저작권 표시 보존

### NC (NonCommercial) - 비영리
- [x] 광고 게재 없음
- [x] 유료 결제 또는 구독 모델 없음
- [x] 사용자 데이터 상업적 활용 없음
- [x] 본인의 영리 활동(유료 강의·컨설팅 등)에 사용하지 않음
- [x] 학술 포트폴리오 및 교육 연구 목적으로만 사용

### SA (ShareAlike) - 동일조건변경허락
- [x] 본 프로젝트를 CC BY-NC-SA 4.0으로 공개
  (CC가 인정하는 CC BY-NC-SA 3.0 IGO와의 호환 라이선스)

### 추가 조건 - WHO 보증 인상 금지
- [x] WHO 로고 사용하지 않음
- [x] WHO가 본 시스템을 보증·추천하지 않음을 명시
- [x] 본 시스템이 WHO와 무관함을 README와 앱 화면에 명시

### 제3자 자료 처리
- [x] WHO 자료 내 외부 출처 표시가 있는 표·그림은 임베딩 대상에서 제외
- [x] 임베딩 자료는 WHO가 직접 작성한 텍스트 권고사항으로 한정

---

## 4. AI 시스템(Claude API)에서의 데이터 처리

본 시스템은 Anthropic Claude API를 활용하여 응답을 생성합니다. 
Anthropic의 API 데이터 처리 정책:

- 입력 데이터는 모델 학습에 사용되지 않음 (Anthropic Commercial Terms)
- 어뷰즈 모니터링 목적으로 약 7일간 보관 후 자동 삭제
- 사용자 입력에 WHO 자료의 일부 청크가 컨텍스트로 전송되나, 
  이는 Anthropic의 비학습 정책에 따라 처리됨

위 처리는 CC BY-NC-SA의 NonCommercial 조건과 양립 가능한 것으로 판단되며, 
사용자에게 본 데이터 처리 방식이 앱 첫 화면에서 고지됨.

---

## 5. 본 프로젝트가 생성하는 부가 콘텐츠의 라이선스

### 본 프로젝트가 자체 작성한 콘텐츠
- 가상 환자 사례 카드 (data/cases/*.json)
- 평가 루브릭 및 프롬프트 (src/evaluator.py)
- 교육공학적 설계 문서 (docs/educational_design.md)
- 시스템 아키텍처 코드 (app.py, src/*.py)

위 콘텐츠는 WHO 자료의 derivative work로 간주되어, 
ShareAlike 조건에 따라 CC BY-NC-SA 4.0으로 공개됩니다.

---

## 6. 문의 및 면책

본 문서의 라이선스 해석은 일반적 이해에 기반한 것이며, 법적 자문이 아닙니다.
상업적 활용을 고려하시는 경우 별도 법률 자문을 받으시기 바랍니다.

WHO에 대한 별도 사용 허가 문의는 https://www.who.int/copyright 를 참조하시기 
바랍니다.
