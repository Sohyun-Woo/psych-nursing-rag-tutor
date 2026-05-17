"""
환자 페르소나 시뮬레이터 (OpenAI GPT 버전)
사례 JSON의 patient_persona_prompt를 system prompt로 사용하여
GPT API가 환자 역할을 수행하게 한다.

원칙:
- 환자 페르소나는 무조건 한국어 응답
- 자살수단 등 모방 위험 정보 묘사 금지 (페르소나 프롬프트에 명시)
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
from pathlib import Path
from typing import Any

import streamlit as st
from openai import OpenAI


def load_case(case_path: Path) -> dict[str, Any]:
    """사례 JSON 파일 로드."""
    with open(case_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_client() -> OpenAI:
    """OpenAI 클라이언트 생성 (Streamlit secrets에서 API 키 로드)."""
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error(
            "⚠️ OPENAI_API_KEY가 설정되지 않았습니다. "
            "`.streamlit/secrets.toml` 또는 Streamlit Cloud의 Secrets 설정을 확인하세요."
        )
        st.stop()
    return OpenAI(api_key=api_key)


def _format_history_for_api(
    conversation_history: list[dict[str, str]],
    system_prompt: str,
) -> list[dict[str, str]]:
    """
    내부 형식 [{"role":"patient"|"learner","content":...}] 을
    OpenAI Chat Completions 형식으로 변환.

    매핑:
    - learner 발화  → user (학습자가 환자에게 말함)
    - patient 발화  → assistant (GPT가 환자 역할로 응답함)
    - system_prompt → 맨 앞 system 메시지
    """
    api_messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history:
        if msg["role"] == "learner":
            api_messages.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "patient":
            api_messages.append({"role": "assistant", "content": msg["content"]})
    return api_messages


def generate_patient_response(
    case: dict[str, Any],
    conversation_history: list[dict[str, str]],
    is_first_turn: bool = False,
) -> str:
    """
    환자 페르소나로 응답 생성.

    Args:
        case: 사례 JSON 데이터
        conversation_history: 누적 대화 (내부 형식)
        is_first_turn: 첫 발화 여부 (True면 학습자 입력 없이 환자가 먼저 발화)

    Returns:
        환자 발화 문자열 (한국어)
    """
    client = get_client()
    system_prompt = case["patient_persona_prompt"]

    if is_first_turn:
        # 첫 발화: 학습자 입력 없이 환자가 먼저 말함
        api_messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "[시스템 안내: 학습자(간호사)가 방금 접근했습니다. 첫 발화를 시작하십시오. 페르소나 프롬프트의 [정서 상태] 항목에 명시된 첫 발화 지침을 따르십시오.]",
            }
        ]
    else:
        api_messages = _format_history_for_api(conversation_history, system_prompt)
        # API messages는 마지막이 user(=learner)여야 함
        if len(api_messages) < 2 or api_messages[-1]["role"] != "user":
            raise ValueError("환자 응답 생성 시점에 마지막 메시지가 학습자 발화여야 합니다.")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=400,
            messages=api_messages,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"환자 응답 생성 중 오류가 발생했습니다: {e}")
        return "[응답을 생성할 수 없습니다. 사이드바에서 새 세션을 시작해주세요.]"
