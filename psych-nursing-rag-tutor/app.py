"""
정신간호 위기개입·임상의사결정 RAG 튜터
Main entry point for Streamlit application

구조: 사례 선택 → 5턴 대화 시뮬레이션 → 종료 후 일괄 평가
License: CC BY-NC-SA 4.0
"""
import json
from pathlib import Path

import streamlit as st

from src.consent import require_consent
from src.simulator import generate_patient_response, load_case
from src.evaluator import evaluate_conversation
from src.rag_pipeline import retrieve_context

# ============================================
# 페이지 설정 (반드시 최상단)
# ============================================
st.set_page_config(
    page_title="정신간호 RAG 튜터",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================
# 사례 메타데이터 (사이드바 표시용)
# ============================================
CASE_REGISTRY = {
    "SUI-001": {
        "label": "🔴 응급실 자살시도 후 내원",
        "file": "data/cases/SUI-001.json",
    },
    "DEP-001": {
        "label": "🟡 지역사회 정신건강복지센터 우울증 사례관리",
        "file": "data/cases/DEP-001.json",
    },
    # "PSY-001": 추후 추가 예정
}


# ============================================
# 세션 상태 초기화
# ============================================
def initialize_session():
    """세션 상태 변수 초기화."""
    defaults = {
        "selected_case_id": "SUI-001",
        "case_data": None,
        "messages": [],          # [{"role": "patient"|"learner", "content": str}]
        "turn_count": 0,         # 학습자가 발화한 턴 수
        "session_locked": False, # 평가 완료 후 잠금
        "evaluation_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session(keep_consent: bool = True):
    """세션 초기화 (동의 상태는 유지)."""
    keys_to_keep = {"consented"} if keep_consent else set()
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]


def load_selected_case():
    """선택된 사례 JSON 로드 (캐싱)."""
    case_id = st.session_state.selected_case_id
    if st.session_state.case_data is None or st.session_state.case_data.get("case_id") != case_id:
        case_path = Path(CASE_REGISTRY[case_id]["file"])
        st.session_state.case_data = load_case(case_path)


# ============================================
# 메인 앱
# ============================================
def main():
    # 1단계: 동의 확인
    require_consent()

    # 2단계: 세션 초기화
    initialize_session()
    load_selected_case()

    case = st.session_state.case_data
    MAX_TURNS = case.get("max_turns", 5)

    # ============================================
    # 사이드바
    # ============================================
    with st.sidebar:
        st.title("🧠 정신간호 RAG 튜터")
        st.caption("v0.1 파일럿 · WHO PFA + mhGAP 기반")

        st.divider()

        # 사례 선택 (세션 잠금 중에는 비활성화)
        st.subheader("📋 학습 사례")
        if st.session_state.session_locked or len(st.session_state.messages) > 0:
            st.info("진행 중인 세션이 있어 사례 변경이 잠겨 있습니다.\n새 세션을 시작하려면 아래 '🔄 새 세션 시작'을 누르세요.")
            st.markdown(f"**현재 사례**: {CASE_REGISTRY[st.session_state.selected_case_id]['label']}")
        else:
            selected = st.radio(
                "사례 선택",
                options=list(CASE_REGISTRY.keys()),
                format_func=lambda x: CASE_REGISTRY[x]["label"],
                key="case_radio",
            )
            if selected != st.session_state.selected_case_id:
                st.session_state.selected_case_id = selected
                st.session_state.case_data = None
                st.rerun()

        st.divider()

        # 학습 가이드
        st.subheader("📖 학습 가이드")
        with st.expander("WHO PFA 3원칙"):
            st.markdown(
                "- **Look (살펴보기)**: 안전·욕구·심각한 고통 사정\n"
                "- **Listen (들어주기)**: 다가가기·경청·지원\n"
                "- **Link (연계하기)**: 정보·서비스·사회적 지지 연계"
            )
        with st.expander("자살위험 4대 사정"):
            st.markdown(
                "1. 자살 **사고**의 강도와 빈도\n"
                "2. 자살 **계획**의 구체성\n"
                "3. 자살 **수단** 접근성\n"
                "4. 이전 자해·자살 **시도력**"
            )

        st.divider()

        # 세션 상태
        st.caption(f"🔢 진행: {st.session_state.turn_count}/{MAX_TURNS} 턴")
        if st.session_state.session_locked:
            st.caption("🔒 평가 완료 (세션 잠금)")
        st.caption("⏱ 세션 종료 시 자동 휘발")

        if st.button("🔄 새 세션 시작", use_container_width=True):
            reset_session()
            st.rerun()

    # ============================================
    # 메인 영역
    # ============================================
    st.title("치료적 의사소통·임상의사결정 학습")
    st.caption("⚠️ 합성된 가상 사례만 사용. 학습 보조 목적이며 의료 진단 도구가 아닙니다.")

    # ----- 사례 카드 -----
    with st.container(border=True):
        st.subheader(f"📝 {case['title']}")
        st.caption(case["synthetic_disclaimer"])

        scenario = case["scenario"]
        st.markdown(f"**📍 상황**: {scenario['setting']}")
        st.markdown(f"**👤 대상자**: {scenario['patient_profile']}")
        st.markdown(f"**🔍 첫 인상**: {scenario['initial_presentation']}")
        st.markdown(f"**ℹ️ 맥락**: {scenario['context']}")

        with st.expander("🎯 학습 목표"):
            for obj in case["learning_objectives"]:
                st.markdown(f"- {obj}")

    st.divider()

    # ----- 대화 영역 -----
    st.subheader("💬 대화 시뮬레이션")

    # 첫 진입 시 환자 첫 발화 자동 생성
    if len(st.session_state.messages) == 0 and not st.session_state.session_locked:
        with st.spinner("환자가 첫 발화를 시작합니다..."):
            first_utterance = generate_patient_response(
                case=case,
                conversation_history=[],
                is_first_turn=True,
            )
            st.session_state.messages.append({"role": "patient", "content": first_utterance})

    # 대화 히스토리 표시
    for msg in st.session_state.messages:
        if msg["role"] == "patient":
            with st.chat_message("user", avatar="🧑‍⚕️"):
                st.markdown(f"**환자**: {msg['content']}")
        else:
            with st.chat_message("assistant", avatar="👩‍⚕️"):
                st.markdown(f"**학습자(나)**: {msg['content']}")

    # ----- 학습자 입력 또는 평가 결과 -----
    turns_remaining = MAX_TURNS - st.session_state.turn_count

    if st.session_state.session_locked:
        # 평가 결과 표시
        render_evaluation(st.session_state.evaluation_result)
    elif turns_remaining > 0:
        # 학습자 입력
        st.markdown(f"**남은 턴**: {turns_remaining}회")
        with st.form(key="learner_input_form", clear_on_submit=True):
            learner_response = st.text_area(
                "환자에게 어떻게 응답하시겠습니까?",
                height=120,
                max_chars=500,
                placeholder="환자에게 할 말을 직접 적어보세요...",
            )
            submitted = st.form_submit_button("📤 응답 전송", type="primary", use_container_width=True)

            if submitted:
                if not learner_response.strip():
                    st.warning("⚠️ 응답을 입력해주세요.")
                else:
                    # 학습자 응답 저장
                    st.session_state.messages.append({"role": "learner", "content": learner_response.strip()})
                    st.session_state.turn_count += 1

                    # 마지막 턴이 아니면 환자 다음 발화 생성
                    if st.session_state.turn_count < MAX_TURNS:
                        with st.spinner("환자가 응답을 생각하고 있습니다..."):
                            patient_reply = generate_patient_response(
                                case=case,
                                conversation_history=st.session_state.messages,
                                is_first_turn=False,
                            )
                            st.session_state.messages.append({"role": "patient", "content": patient_reply})
                    st.rerun()
    else:
        # 5턴 도달 → 평가 트리거
        st.info(f"🎓 {MAX_TURNS}턴 대화가 완료되었습니다. 종합 평가를 진행합니다.")
        if st.button("📊 평가 받기", type="primary", use_container_width=True):
            with st.spinner("대화 내용을 분석하고 평가 중입니다... (WHO PFA + mhGAP 기준)"):
                # RAG 컨텍스트 검색
                rag_context = retrieve_context(
                    case=case,
                    conversation_history=st.session_state.messages,
                )
                # 일괄 평가
                evaluation = evaluate_conversation(
                    case=case,
                    conversation_history=st.session_state.messages,
                    rag_context=rag_context,
                )
                st.session_state.evaluation_result = evaluation
                st.session_state.session_locked = True
                st.rerun()

    # ============================================
    # 푸터 (위기 상황 안내 상시 표시)
    # ============================================
    st.divider()
    st.caption(
        "⚠️ 본 시스템은 학습 보조 도구이며 의료 진단·치료 도구가 아닙니다. | "
        "실제 위기 상황: 정신건강위기상담 **1577-0199** | 자살예방상담 **1393**"
    )
    st.caption(
        "📜 CC BY-NC-SA 4.0 | "
        "🌐 본 시스템은 WHO와 무관하며 WHO 보증을 받지 않습니다 | "
        "👤 개발: 우소현 (정신간호학 박사)"
    )


# ============================================
# 평가 결과 렌더링
# ============================================
def render_evaluation(evaluation: dict):
    """평가 결과를 화면에 렌더링."""
    st.subheader("📊 종합 평가 결과")

    if not evaluation:
        st.error("평가 결과를 불러올 수 없습니다.")
        return

    # 총점 표시
    total_score = evaluation.get("total_score", 0)
    interpretation = evaluation.get("interpretation", "")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("총점", f"{total_score}/100")
    with col2:
        if total_score >= 90:
            st.success(f"🌟 **{interpretation}**")
        elif total_score >= 70:
            st.info(f"👍 **{interpretation}**")
        elif total_score >= 50:
            st.warning(f"⚠️ **{interpretation}**")
        else:
            st.error(f"📚 **{interpretation}**")

    st.divider()

    # 항목별 평가
    st.markdown("### 📋 항목별 평가")
    for item in evaluation.get("criteria_scores", []):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{item['name']}** (가중치 {item['weight']}%)")
            with col2:
                st.markdown(f"**{item['score']}/{item['weight']}점**")
            st.markdown(f"**평가 수준**: `{item['level']}`")
            st.markdown(f"**피드백**: {item['feedback']}")

    # 강점과 개선점
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ✅ 강점")
        for s in evaluation.get("strengths", []):
            st.markdown(f"- {s}")
    with col2:
        st.markdown("### 🔧 개선 영역")
        for i in evaluation.get("improvements", []):
            st.markdown(f"- {i}")

    # 근거 출처
    st.divider()
    st.markdown("### 📖 근거 출처")
    for src in evaluation.get("references", []):
        st.markdown(f"- {src}")

    # 새 세션 안내
    st.divider()
    st.info("🔄 재시도하려면 사이드바의 **'새 세션 시작'** 버튼을 눌러주세요. (대화 중간 되돌리기는 지원되지 않습니다)")


if __name__ == "__main__":
    main()
