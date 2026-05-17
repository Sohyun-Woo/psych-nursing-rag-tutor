"""
평가자 모듈
대화 종료 후 4개 항목 루브릭으로 일괄 평가.

원칙:
- 턴별 피드백 없음 (PROJECT_SUMMARY 확정 사양)
- 루브릭 가중치 합 = 100
- excellent/adequate/needs_improvement 3단계 평가
"""
import json
import re
from typing import Any

import streamlit as st
from anthropic import Anthropic

from src.simulator import get_client


def _build_evaluation_prompt(
    case: dict[str, Any],
    conversation_history: list[dict[str, str]],
    rag_context: str,
) -> str:
    """평가용 프롬프트 구성."""

    # 대화 내용 정리
    conv_text_parts = []
    for i, msg in enumerate(conversation_history):
        speaker = "환자" if msg["role"] == "patient" else "학습자(간호사)"
        conv_text_parts.append(f"[{i+1}] {speaker}: {msg['content']}")
    conv_text = "\n".join(conv_text_parts)

    # 루브릭 항목 정리
    rubric = case["final_rubric"]["criteria"]
    rubric_text_parts = []
    for c in rubric:
        rubric_text_parts.append(
            f"- **{c['name']}** (가중치 {c['weight']}%): {c['description']}\n"
            f"    * excellent: {c['levels']['excellent']}\n"
            f"    * adequate: {c['levels']['adequate']}\n"
            f"    * needs_improvement: {c['levels']['needs_improvement']}"
        )
    rubric_text = "\n".join(rubric_text_parts)

    # Red flags 정리
    red_flags_text = "\n".join(f"- {rf}" for rf in case.get("overall_red_flags", []))
    competencies_text = "\n".join(f"- {c}" for c in case.get("overall_competencies", []))

    return f"""당신은 정신간호학 임상 교육 전문가입니다. 아래 시뮬레이션 대화를 4개 항목 루브릭으로 평가하십시오.

# 사례 정보
- 사례 ID: {case['case_id']}
- 제목: {case['title']}
- 맥락: {case['scenario']['context']}

# 핵심 역량 (학습자가 발휘해야 할 역량)
{competencies_text}

# 적신호 (Red Flags - 학습자가 절대 해서는 안 되는 행동)
{red_flags_text}

# 학습자-환자 대화 내용 (총 {len([m for m in conversation_history if m['role']=='learner'])}턴의 학습자 발화)
{conv_text}

# 평가 루브릭
{rubric_text}

# 근거기반 컨텍스트 (WHO PFA / mhGAP IG)
{rag_context}

# 평가 지침
1. 각 항목의 가중치 만점 기준으로 점수를 부여하시오.
   - excellent → 가중치의 90~100%
   - adequate → 가중치의 60~80%
   - needs_improvement → 가중치의 20~50%
2. Red flags가 명백히 관찰되면 해당 항목 점수를 needs_improvement 수준으로 평가하시오.
3. 학습자의 실제 발화에서 근거를 찾아 피드백을 작성하시오 (추측·일반론 금지).
4. 강점·개선점은 각 2-4개의 구체적 항목으로 작성하시오.

# 출력 형식 (반드시 아래 JSON 형식으로만 응답. 다른 텍스트·코드펜스 금지)
{{
  "criteria_scores": [
    {{
      "name": "<루브릭 항목명>",
      "weight": <가중치 정수>,
      "score": <가중치 만점 기준 정수>,
      "level": "<excellent|adequate|needs_improvement>",
      "feedback": "<학습자 발화 근거 기반 구체적 피드백 2-3문장>"
    }}
  ],
  "total_score": <0~100 정수>,
  "interpretation": "<우수|양호|미흡|재학습 권장 중 하나 + 짧은 한 줄 설명>",
  "strengths": ["<강점 1>", "<강점 2>", ...],
  "improvements": ["<개선점 1>", "<개선점 2>", ...],
  "references": ["<인용 출처 1>", "<인용 출처 2>", ...]
}}
"""


def _extract_json(text: str) -> dict[str, Any] | None:
    """응답에서 JSON 블록을 안전하게 추출."""
    # 코드펜스 제거
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text)
    # JSON 객체 영역 추출 (첫 { ~ 마지막 })
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _validate_evaluation(evaluation: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    """평가 결과 검증·보정."""
    rubric_names = [c["name"] for c in case["final_rubric"]["criteria"]]

    # criteria_scores 누락 보완
    scores = evaluation.get("criteria_scores", [])
    if len(scores) != len(rubric_names):
        # 누락된 항목은 0점으로 처리
        existing_names = {s.get("name") for s in scores}
        for c in case["final_rubric"]["criteria"]:
            if c["name"] not in existing_names:
                scores.append({
                    "name": c["name"],
                    "weight": c["weight"],
                    "score": 0,
                    "level": "needs_improvement",
                    "feedback": "[평가 데이터 누락 - 새 세션에서 재시도를 권장합니다]",
                })
        evaluation["criteria_scores"] = scores

    # total_score 재계산 (불일치 시 합산값으로 보정)
    computed_total = sum(s.get("score", 0) for s in scores)
    evaluation["total_score"] = int(computed_total)

    # interpretation 보정
    total = evaluation["total_score"]
    if total >= 90:
        default_interp = "우수 - 임상 실무 적용 가능 수준"
    elif total >= 70:
        default_interp = "양호 - 일부 영역 보완 필요"
    elif total >= 50:
        default_interp = "미흡 - 핵심 역량 추가 학습 필요"
    else:
        default_interp = "재학습 권장 - 사례 재시도 및 보충 학습 필수"

    if not evaluation.get("interpretation"):
        evaluation["interpretation"] = default_interp

    # 빈 필드 기본값
    evaluation.setdefault("strengths", ["[강점 분석 데이터 없음]"])
    evaluation.setdefault("improvements", ["[개선점 분석 데이터 없음]"])
    evaluation.setdefault("references", case.get("rag_priority_sources", []))

    return evaluation


def evaluate_conversation(
    case: dict[str, Any],
    conversation_history: list[dict[str, str]],
    rag_context: str,
) -> dict[str, Any]:
    """
    대화 종료 후 일괄 평가.

    Args:
        case: 사례 JSON 데이터
        conversation_history: 전체 대화 (내부 형식)
        rag_context: RAG 파이프라인이 검색한 근거기반 컨텍스트

    Returns:
        평가 결과 딕셔너리
    """
    client = get_client()
    prompt = _build_evaluation_prompt(case, conversation_history, rag_context)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = response.content[0].text

        evaluation = _extract_json(raw_text)
        if not evaluation:
            st.error("평가 응답 형식 오류. 다시 시도해주세요.")
            return _build_fallback_evaluation(case, raw_text)

        return _validate_evaluation(evaluation, case)
    except Exception as e:
        st.error(f"평가 중 오류가 발생했습니다: {e}")
        return _build_fallback_evaluation(case, str(e))


def _build_fallback_evaluation(case: dict[str, Any], error_info: str) -> dict[str, Any]:
    """평가 실패 시 폴백 결과."""
    return {
        "criteria_scores": [
            {
                "name": c["name"],
                "weight": c["weight"],
                "score": 0,
                "level": "needs_improvement",
                "feedback": "[평가 시스템 오류로 점수를 산출할 수 없습니다]",
            }
            for c in case["final_rubric"]["criteria"]
        ],
        "total_score": 0,
        "interpretation": "평가 시스템 오류",
        "strengths": ["[평가 실패로 분석 불가]"],
        "improvements": [f"[오류 정보: {error_info[:200]}]"],
        "references": case.get("rag_priority_sources", []),
    }
