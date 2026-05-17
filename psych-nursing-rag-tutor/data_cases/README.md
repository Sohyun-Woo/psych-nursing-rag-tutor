# 사례 데이터

이 폴더는 합성 사례 JSON 파일을 저장합니다.

## 현재 등록된 사례 (v0.1 파일럿)

| ID | 카테고리 | 맥락 | 상태 |
|---|---|---|---|
| SUI-001 | suicide | 응급실 자살시도 후 내원 | ✅ |
| DEP-001 | depression | 지역사회 정신건강복지센터 우울증 사례관리 | ✅ |
| PSY-001 | psychosis | 입원병동 초발 정신증 | ⏳ 추후 추가 |

## 사례 JSON 스키마 (핵심 필드)

```
{
  "case_id": "SUI-001",
  "category": "suicide" | "depression" | "psychosis",
  "title": "...",
  "synthetic_disclaimer": "...",
  "learning_objectives": [...],
  "scenario": {
    "setting": "...",
    "patient_profile": "...",
    "initial_presentation": "...",
    "context": "..."
  },
  "patient_persona_prompt": "...",   // Claude API system prompt
  "max_turns": 5,
  "overall_competencies": [...],
  "overall_red_flags": [...],
  "rag_keywords": [...],
  "rag_priority_sources": [...],
  "final_rubric": {
    "criteria": [
      {"name": "...", "weight": <int>, "levels": {...}}
    ]
  }
}
```

## 원칙

1. 모든 사례 **100% 합성**, 실제 환자 정보 금지
2. 자살수단의 구체 묘사 금지 (모방 위험)
3. 환자 페르소나는 **한국어 전용**
4. 루브릭 가중치 합은 반드시 **100**
