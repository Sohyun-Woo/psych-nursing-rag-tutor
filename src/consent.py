"""
사용 동의 화면 모듈
첫 진입 시 데이터 처리·면책 사항 동의를 받고, 동의 전에는 메인 앱 차단.
"""
import streamlit as st

CONSENT_TEXT = """
### 📋 사용 전 안내사항

본 시스템은 **정신간호학 교육을 위한 데모용 프로토타입**입니다.

#### 1. 합성 사례 안내
모든 환자 사례는 교육 목적으로 합성된 **가상 사례**이며, 실재 환자와 무관합니다.

#### 2. 데이터 처리
- 입력하신 응답은 Anthropic Claude API를 경유하여 처리됩니다.
- Anthropic은 API 입력 데이터를 **모델 학습에 사용하지 않습니다**.
- 약 30일간 보관 후 자동 삭제됩니다 (Anthropic 정책 기준).
- 본 앱은 별도의 영구 저장소를 운영하지 않으며 **세션 종료 시 휘발**됩니다.

#### 3. 입력 금지 사항
- 본인 또는 타인의 실제 의료정보
- 주민등록번호, 학번, 환자 식별정보
- 본인의 정신건강 관련 자기 노출

#### 4. 시스템의 한계
본 시스템은 **의료적 진단·치료 도구가 아닙니다**. AI 피드백은 학습 보조
목적이며, 오류 가능성이 있으므로 반드시 교수자와의 토론으로 보완하십시오.

#### 5. 위기 상황 안내
실제 정신건강 위기 상황에서는 다음에 연락하십시오.
- 정신건강위기상담전화: **1577-0199**
- 자살예방상담전화: **1393**

#### 6. WHO 면책
본 시스템은 WHO와 무관하며, WHO가 본 시스템을 보증·추천하지 않습니다.
WHO PFA Guide 및 mhGAP IG는 CC BY-NC-SA 3.0 IGO 라이선스 하에 인용되었습니다.
"""


def require_consent() -> bool:
    """첫 진입 시 동의 화면을 표시. 동의 전에는 메인 앱 차단."""
    if "consented" not in st.session_state:
        st.session_state.consented = False

    if st.session_state.consented:
        return True

    st.title("🧠 정신간호 위기개입·임상의사결정 RAG 튜터")
    st.caption("WHO PFA + mhGAP 기반 학습 보조 챗봇 | v0.1 파일럿")
    st.markdown(CONSENT_TEXT)

    agree = st.checkbox("위 내용을 모두 이해하였으며 동의합니다.")
    col1, _ = st.columns([1, 4])
    with col1:
        if st.button("시작하기", disabled=not agree, type="primary"):
            st.session_state.consented = True
            st.rerun()

    st.stop()
    return False
