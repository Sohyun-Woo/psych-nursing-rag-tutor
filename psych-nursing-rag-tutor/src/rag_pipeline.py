"""
RAG 파이프라인
WHO PFA Guide + mhGAP IG에서 사례별 근거기반 컨텍스트를 검색.

[MVP 단계]
ChromaDB 인덱싱 대신 사례별 사전 정제된 컨텍스트를 반환.
WHO 자료(PFA/mhGAP)의 핵심 원칙을 발췌·요약한 텍스트로,
CC BY-NC-SA 3.0 IGO 라이선스 하에 인용 가능한 범위만 포함.

[v0.2 이후 계획]
- WHO PFA Guide 2011 한국어판 PDF → chunking → embedding (BAAI/bge-m3)
- WHO mhGAP IG v2.0 2016 영문판 PDF → chunking → embedding
- ChromaDB 영속 인덱스 (data/chroma/)
- 사례 키워드 기반 top-k retrieval
"""
from pathlib import Path
from typing import Any

# ============================================
# 사례별 RAG 컨텍스트 (MVP 하드코딩)
# ============================================
# 출처: WHO PFA Guide 2011 한국어판 / WHO mhGAP IG v2.0 2016
# 라이선스: CC BY-NC-SA 3.0 IGO
# WHO 보증 없음 - 본 시스템은 WHO와 무관

CONTEXT_PFA_LOOK_LISTEN_LINK = """
[출처: WHO Psychological First Aid Guide for Field Workers 2011 한국어판]

PFA 3원칙 - Look, Listen, Link:

**Look (살펴보기)**
- 안전 확인: 즉각적 위험 요소가 있는지 환경을 살핀다.
- 명백히 시급한 기본 욕구: 신체적 부상, 갈증, 추위 등.
- 심각한 고통 반응: 극도의 위축, 해리, 통제 불능의 정서적 반응.

**Listen (들어주기)**
- 다가가기: 자신을 소개하고 도움을 제공해도 되는지 묻는다.
- 도움이 필요한 사람에게 주의를 기울이고 경청한다.
- 침묵을 허용하고, 강요하지 않는다. 사람들이 자기 속도로 말하도록 한다.
- 정서적 반응을 받아들이되 판단하지 않는다.

**Link (연계하기)**
- 기본 욕구 충족 정보 제공.
- 가족·사회적 지지 체계와 연결.
- 필요한 서비스(의료, 정신건강, 사회복지)로 의뢰.
- 안전한 후속 계획에 대해 함께 논의한다.
"""

CONTEXT_MHGAP_SUI = """
[출처: WHO mhGAP Intervention Guide v2.0 2016 - SUI module]

자해·자살(Self-harm/Suicide) 사정과 관리 핵심 권고:

**SUI 2.1 현재 자해·자살에 대한 사정**
- 직접적·구체적 질문이 필수: "지금도 죽고 싶은 마음이 있으십니까?"
- 자살사고 빈도·강도·지속성 확인.
- 자살계획의 구체성: 방법, 시기, 장소 설정 여부.
- 자살수단 접근 가능성 평가.
- 이전 자해·자살 시도력 확인.
- 자살 화제에 대해 직접적으로 질문하는 것이 자살 위험을 증가시키지 않는다는 점은 다수 연구로 확인됨.

**SUI 2.2 자해·자살 관리**
- 즉각적 위험이 있으면 보호자 동반 하 응급 의뢰 또는 입원 고려.
- 위험요소 제거: 환경 내 자살수단 접근 차단.
- 지속적 관찰 및 follow-up 계획 수립.
- 환자의 사회적 지지체계 활용 (가족 동의·동반).
- 정신건강의학과 협진 의뢰가 표준 권고.

**의사소통 원칙 (적신호 회피)**
- "그런 말 하지 마세요", "왜 그랬어요?" 등 설득·훈계·책임 추궁 금지.
- 종교적·도덕적 가치 강요 금지.
- 자살 화제 우회·회피 금지.
- 감정 부정("그래도 살아야죠") 금지.
"""

CONTEXT_MHGAP_DEP = """
[출처: WHO mhGAP Intervention Guide v2.0 2016 - DEP module]

우울증(Depression) 사정과 관리 핵심 권고:

**DEP 2.1 우울증 사정**
- 핵심 증상 평가 (최소 2주 이상 지속):
  * 우울한 기분 또는 흥미·즐거움 상실
  * 활력 저하, 쉽게 피곤함
  * 수면 장애 (불면 또는 과다수면)
  * 식욕·체중 변화
  * 집중력 저하
  * 무가치감·죄책감
  * 일상 기능 손상
- **우울증 환자에서 자살사고 동반 평가는 필수** (SUI 모듈 통합).
- 약물 순응도, 외래 치료 연계성 확인.

**DEP 2.2 우울증 관리**
- 심리사회적 개입 우선: 문제해결 상담, 행동 활성화.
- 약물치료 (필요 시): 항우울제 처방 의사와 협의.
- 지지체계 활용: 가족·사회적 자원 연계 (대상자 동의 하).
- 정기 추적 관찰: 사례관리 일정 협의.
- 위기 상황 대응 계획: 핫라인 안내, 위기 시 절차 사전 공유.

**의사소통 원칙 (적신호 회피)**
- "기운 내세요", "긍정적으로 생각하세요" 등 정서 부정·설득 금지.
- 성급한 해결책·조언("운동하세요", "취미 가지세요") 지양.
- 약물 비순응을 일방적 훈계로 다루지 않음 - 이유 탐색이 우선.
"""

# 사례 카테고리 → 컨텍스트 매핑
CATEGORY_CONTEXT_MAP = {
    "suicide": [CONTEXT_PFA_LOOK_LISTEN_LINK, CONTEXT_MHGAP_SUI],
    "depression": [CONTEXT_PFA_LOOK_LISTEN_LINK, CONTEXT_MHGAP_DEP, CONTEXT_MHGAP_SUI],
    "psychosis": [CONTEXT_PFA_LOOK_LISTEN_LINK],  # PSY 모듈 컨텍스트 추후 추가
}


def retrieve_context(
    case: dict[str, Any],
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    """
    사례에 맞는 RAG 컨텍스트 반환.

    Args:
        case: 사례 JSON 데이터
        conversation_history: 대화 히스토리 (현재 미사용, v0.2에서 키워드 추출에 사용 예정)

    Returns:
        근거기반 컨텍스트 문자열 (평가자에게 전달)
    """
    category = case.get("category", "")
    contexts = CATEGORY_CONTEXT_MAP.get(category, [CONTEXT_PFA_LOOK_LISTEN_LINK])

    # 사례의 priority sources 정보 부가
    priority_sources = case.get("rag_priority_sources", [])
    priority_text = "\n".join(f"- {s}" for s in priority_sources)

    combined = "\n\n---\n\n".join(contexts)
    if priority_text:
        combined += f"\n\n---\n\n[본 사례 우선 참조 출처]\n{priority_text}"

    return combined
