# 정신간호 위기개입·임상의사결정 RAG 튜터

> WHO 가이드라인 기반 학습 보조 챗봇 — 간호대학 학부생을 위한 자기주도적 학습 도구

[![License: CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)](https://streamlit.io/)

---

## 📋 프로젝트 개요

본 시스템은 정신간호학 실습 수강생이 위기 상황에서의 의사소통 및 임상의사결정 
역량을 자기주도적으로 학습할 수 있도록 설계된 **RAG(Retrieval-Augmented 
Generation) 기반 AI 튜터**입니다. 학생이 가상의 정신건강 사례에 대한 자신의 
응답을 입력하면, 시스템이 WHO 국제 표준 가이드라인에 비추어 형성적 피드백을 
제공합니다.

- 🔗 **데모 사이트**: (Streamlit Cloud 배포 후 추가 예정)
- 📺 **시연 영상**: (녹화 후 추가 예정)
- 👤 **개발**: 우소현 (정신간호학 박사)

---

## 🎯 학습 시나리오

```
[가상 환자 상황]
"34세 남성이 응급실에 자해 시도 후 내원했습니다. 면담을 시작하려 합니다."

[학생 응답 입력]
"왜 그런 일을 하셨어요? 가족 생각은 안 하셨어요?"

[AI 통합 피드백]
🟢 의사소통 측면 (WHO PFA Guide 인용)
   ✗ "왜"로 시작하는 질문은 비난으로 해석될 수 있음
   📖 출처: PFA Guide 한국어판, p.XX

🟡 임상 사정 측면 (WHO mhGAP IG 인용)  
   누락된 핵심 사정 항목:
   ✗ 현재 자살 사고 강도
   ✗ 자살 수단 접근성
   📖 출처: mhGAP IG v2.0, SUI module, p.XX

💚 대안 응답 예시:
   "지금 많이 힘드셨을 것 같아요. 안전한지 먼저 확인해도 될까요?"
```

---

## 🧠 교육공학적 설계 근거

### 이론적 기반

본 시스템은 다음 네 가지 교육·간호 이론을 통합 적용합니다.

| 이론 | 적용 방식 |
|------|---------|
| **구성주의 학습이론** (Vygotsky, 1978) | 학습자 능동적 응답 → 피드백 → 재구성. AI 튜터가 ZPD 내 scaffolding 역할 |
| **Peplau의 대인관계이론** (1952) | 정신간호 대인관계 4단계 중 오리엔테이션 단계의 의사소통 역량 학습 |
| **Kolb의 경험학습이론** (1984) | 구체적 경험 → 반성적 관찰 → 추상적 개념화 → 능동적 실험 4단계 UX 구현 |
| **Shute의 형성적 피드백 원칙** (2008) | 구체성·적시성·준거 참조·학습자 통제 |

### 학습목표와 Bloom's Taxonomy 매핑

| 인지 수준 | 학습목표 | 시스템 구현 |
|----------|---------|----------|
| 기억 | 위기개입 원칙·사정 항목을 나열할 수 있다 | 사이드바 용어집 |
| 이해 | 각 원칙의 정의·근거를 설명할 수 있다 | RAG 피드백 내 인용 |
| 적용 | 사례에 적합한 응답을 작성할 수 있다 | 학생 응답 입력 |
| 분석 | 자신의 응답에 누락된 요소를 식별한다 | 자동 분석 결과 |
| 평가 | 자신의 응답을 권고 기준에 따라 평가한다 | 루브릭 기반 점수 |
| 창조 | 더 효과적인 대안 응답을 구성한다 | 재시도 기능 |

### KABONE 학습성과 연계

| KABONE 학습성과 | 기여도 |
|----------------|------|
| 5. 간호상황에서의 비판적 사고 | 응답 자기평가 |
| 9. 효과적 의사소통과 협력관계 | **핵심 학습 영역** |
| 12. 안전하고 질 높은 간호 제공 | 환자안전 관점 피드백 |

자세한 설계 근거는 [`docs/educational_design.md`](docs/educational_design.md) 참조.

---

## 🏗 시스템 아키텍처

```
[학생 브라우저]
    ↓ HTTPS
[Streamlit Cloud]
    ├─ st.session_state (휘발성)
    ├─ st.secrets (API 키, Git 미포함)
    └─ ChromaDB (벡터 검색)
        ├─ WHO PFA Guide (한국어 임베딩)
        └─ WHO mhGAP IG v2.0 (영문 임베딩)
    ↓ API 호출
[Anthropic Claude API]
    └─ 입력 비학습 / 7일 후 자동 삭제
```

### RAG 구조 채택 근거

단순 LLM 사용 대비 RAG 구조는 다음 교육적 요구를 충족합니다.

1. **환각 최소화**: WHO 권위 자료로 LLM 사실 오류 통제
2. **인용 추적 가능성**: 피드백 근거가 명시적으로 학습자에게 제시됨
3. **저작권 안전성**: 사용 자료 출처를 명시적으로 관리

---

## 📚 임베딩 자료 출처

| 자료 | 라이선스 | 언어 |
|------|---------|------|
| WHO Psychological First Aid: Guide for Field Workers (2011) | CC BY-NC-SA 3.0 IGO | 한국어 |
| WHO mhGAP Intervention Guide v2.0 (2016) | CC BY-NC-SA 3.0 IGO | 영문 |

상세 출처는 [`ATTRIBUTION.md`](ATTRIBUTION.md) 참조.

---

## ⚖️ AI 윤리 고려사항

본 시스템은 AI 기본교육과정의 핵심 가치인 **"AI 윤리 + 비판적 사고 + 
근거 기반 의사결정"** 의 정신간호학적 적용 사례로 설계되었습니다.

### 1. 알고리즘 한계 명시
LLM 기반 피드백은 100% 정확하지 않으며, 본 시스템은 학습 보조 도구로서 
교수자·임상지도자와의 토론을 대체할 수 없음을 첫 화면에서 명시합니다.

### 2. 문화적 맥락 고려
서구 중심 LLM의 한계를 보완하기 위해, 한국어 자료를 우선 임베딩하고 
한국 정신보건 체계 맥락을 시스템 프롬프트에 반영합니다.

### 3. 학습자 자율성 보호
AI 피드백 과의존 방지를 위해, 시스템은 정답을 단정하지 않고 
**근거와 함께 대안을 제시**하는 형태로 응답을 구성합니다.

### 4. 데이터 처리 투명성
- Anthropic API 정책에 따라 입력 데이터는 7일 후 자동 삭제
- Anthropic은 입력 데이터를 모델 학습에 사용하지 않음
- 본 앱은 별도의 영구 저장소를 운영하지 않음 (세션 종료 시 휘발)

상세 윤리 검토는 [`docs/ethics_considerations.md`](docs/ethics_considerations.md) 
및 [`docs/license_compliance.md`](docs/license_compliance.md) 참조.

---

## 🚀 실행 방법

### 사전 요구사항
- Python 3.10 이상
- Anthropic API 키 ([Anthropic Console](https://console.anthropic.com)에서 발급)

### 설치 및 실행

```bash
# 1. 저장소 복제
git clone https://github.com/[your-username]/psych-nursing-rag-tutor.git
cd psych-nursing-rag-tutor

# 2. 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 3. 의존성 설치
pip install -r requirements.txt

# 4. WHO 자료 다운로드 (data/source_documents/)
# - PFA 한국어판: https://iris.who.int/bitstream/10665/44615/4/9789241548205_kor.pdf
# - mhGAP IG v2.0: https://www.who.int/publications/i/item/9789241549790

# 5. Streamlit secrets 설정
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# secrets.toml을 열어 ANTHROPIC_API_KEY 입력

# 6. 벡터 DB 구축 (최초 1회)
python -m src.rag_pipeline --build-index

# 7. 앱 실행
streamlit run app.py
```

---

## 📂 디렉토리 구조

```
psych-nursing-rag-tutor/
│
├── README.md                    # 본 문서
├── LICENSE                      # CC BY-NC-SA 4.0
├── ATTRIBUTION.md               # WHO 자료 출처 명시
├── .gitignore                   # 보안 핵심
├── requirements.txt
│
├── .streamlit/
│   └── secrets.toml.example     # API 키 템플릿
│
├── app.py                       # Streamlit 메인
│
├── src/
│   ├── __init__.py
│   ├── rag_pipeline.py          # RAG 검색·생성
│   ├── evaluator.py             # 응답 평가
│   └── consent.py               # 동의 화면
│
├── data/
│   ├── source_documents/        # WHO PDF (다운로드 필요)
│   ├── cases/                   # 가상 사례 카드 (JSON)
│   └── README.md
│
├── chroma_db/                   # 벡터 DB (.gitignore)
│
└── docs/
    ├── educational_design.md    # 교육공학적 설계
    ├── ethics_considerations.md # AI 윤리 검토
    ├── license_compliance.md    # 라이선스 준수 검증
    └── kabone_mapping.md        # KABONE 학습성과 매핑
```

---

## 🔮 향후 확장 계획

- **Phase 1 (현재)**: WHO PFA + mhGAP 통합 RAG 튜터 (파일럿)
- **Phase 2**: 사례 카드 확장 (6개 → 30개), 윤리 딜레마 모듈 추가
- **Phase 3**: WHO LIVE LIFE 자살예방 모듈 통합
- **Phase 4**: 학습자 진행 추적 및 효과 검증 연구 (IRB 신청 후)
- **Phase 5**: 가천대 정신간호학 정규 교과 연계 운영

---

## 📜 라이선스

본 프로젝트는 **CC BY-NC-SA 4.0** 라이선스로 공개됩니다.
WHO 자료의 ShareAlike 조건을 준수합니다.

- 자세한 내용: [`LICENSE`](LICENSE)
- 외부 자료 출처: [`ATTRIBUTION.md`](ATTRIBUTION.md)

---

## ⚠️ 의료 면책 (Medical Disclaimer)

본 시스템은 **간호교육용 학습 보조 도구**이며, 의료적 진단·치료 도구가 아닙니다.
AI 피드백은 오류 가능성이 있으므로 반드시 교수자·임상지도자와의 토론으로 
보완하시기 바랍니다.

**실제 정신건강 위기 상황에서는 다음에 연락하십시오.**
- 정신건강위기상담전화: **1577-0199**
- 자살예방상담전화: **1393**

---

## 🌐 WHO 면책 (WHO Disclaimer)

본 시스템은 WHO와 무관하며, WHO가 본 시스템을 보증·추천하지 않습니다.
WHO 로고는 사용되지 않습니다.

---

## 📮 연락처

본 프로젝트는 **가천대학교 간호대학 임용 지원을 위한 학술 포트폴리오**입니다.

- 개발자: 우소현 (정신간호학 박사)
- 이메일: (지원서 기재 이메일 참조)
