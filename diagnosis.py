from __future__ import annotations

import re
from datetime import datetime, timezone

from config import QUESTIONS, RESULT_TEMPLATES

TYPE_PRIORITY = ["stable", "challenge", "specialist"]
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_answers(answers: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for question in QUESTIONS:
        value = answers.get(question["id"], "")
        if question.get("required") and not value:
            errors.append(f"「{question['label']}」は入力必須です。")
        elif question["type"] == "email" and value and not EMAIL_PATTERN.match(value):
            errors.append("メールアドレスの形式が正しくありません。")
    return errors


def get_answer_labels(answers: dict[str, str]) -> dict[str, str]:
    answer_labels: dict[str, str] = {}
    for question in QUESTIONS:
        question_id = question["id"]
        raw_value = answers.get(question_id, "")

        if question["type"] in {"radio", "select"}:
            matched_option = next(
                (option for option in question.get("options", []) if option["value"] == raw_value),
                None,
            )
            answer_labels[question_id] = matched_option["label"] if matched_option else raw_value
        else:
            answer_labels[question_id] = raw_value

    return answer_labels


def build_diagnosis_result(answers: dict[str, str], answer_labels: dict[str, str]) -> dict:
    scores = calculate_scores(answers)
    dominant_type = pick_dominant_type(scores, answers)
    template = RESULT_TEMPLATES[dominant_type]
    market_value_score = calculate_market_value_score(answers, scores, dominant_type)
    market_value_rank = build_market_value_rank(market_value_score)
    estimated_salary_range = build_salary_range(market_value_score, dominant_type)
    urgency_label = build_urgency_label(answers, market_value_score)

    summary = template["summary_template"].format(
        current_concern=answer_labels.get("current_concern", "将来への不安"),
        current_role=answer_labels.get("current_role", "現在の仕事"),
    )
    risk_summary = template["risk_template"].format(
        current_concern=answer_labels.get("current_concern", "強みが曖昧なこと"),
    )

    next_step = (
        f"1年後の理想として「{answer_labels.get('future_image', '')}」を挙げているため、"
        "今すぐ必要なのは『狙う職種を絞ること』と『30日以内に見せられる実績を1つ作ること』です。"
    )

    return {
        "submitted_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "type_key": dominant_type,
        "type_name": template["type_name"],
        "headline": template["headline"],
        "summary": summary,
        "market_value_rank": market_value_rank,
        "market_value_score": market_value_score,
        "estimated_salary_range": estimated_salary_range,
        "urgency_label": urgency_label,
        "risk_summary": risk_summary,
        "leverage_points": template["leverage_points"],
        "recommended_roles": template["recommended_roles"],
        "actions": template["actions"],
        "score_breakdown": scores,
        "next_step": next_step,
        "registered_email": answers.get("email", ""),
        "disclaimer": "この市場価値ランクと年収レンジは、診断内の回答に基づく推定値です。実際の採用条件や年収を保証するものではありません。",
    }


def calculate_scores(answers: dict[str, str]) -> dict[str, int]:
    scores = {type_key: 0 for type_key in TYPE_PRIORITY}

    for question in QUESTIONS:
        if question["type"] not in {"radio", "select"}:
            continue

        selected_value = answers.get(question["id"], "")
        option = next(
            (candidate for candidate in question.get("options", []) if candidate["value"] == selected_value),
            None,
        )
        if not option:
            continue

        for type_key, amount in option.get("scores", {}).items():
            scores[type_key] += amount

    return scores


def pick_dominant_type(scores: dict[str, int], answers: dict[str, str]) -> str:
    ordered = sorted(scores.items(), key=lambda item: (-item[1], TYPE_PRIORITY.index(item[0])))
    top_score = ordered[0][1]
    tied_types = [type_key for type_key, score in ordered if score == top_score]

    if len(tied_types) == 1:
        return tied_types[0]

    motivation = answers.get("motivation", "")
    concern = answers.get("current_concern", "")

    if motivation == "growth" or concern == "stuck_growth":
        if "challenge" in tied_types:
            return "challenge"
    if motivation == "mastery" or concern == "lack_skill":
        if "specialist" in tied_types:
            return "specialist"
    if "stable" in tied_types:
        return "stable"

    return tied_types[0]


def calculate_market_value_score(
    answers: dict[str, str],
    scores: dict[str, int],
    dominant_type: str,
) -> int:
    score = {
        "stable": 52,
        "challenge": 60,
        "specialist": 57,
    }[dominant_type]

    score += {
        "security": 0,
        "growth": 5,
        "mastery": 4,
    }.get(answers.get("motivation", ""), 0)
    score += {
        "support": 0,
        "drive": 4,
        "analysis": 3,
    }.get(answers.get("strength", ""), 0)
    score += {
        "structured_team": 0,
        "flexible_team": 3,
        "independent_focus": 2,
    }.get(answers.get("work_style", ""), 0)
    score += {
        "clear_rules": 0,
        "speed_change": 3,
        "quiet_depth": 2,
    }.get(answers.get("preferred_environment", ""), 0)
    score += {
        "unclear_path": -2,
        "stuck_growth": -1,
        "lack_skill": -3,
    }.get(answers.get("current_concern", ""), 0)

    score += max(0, min(6, scores.get(dominant_type, 0) - 8))
    return max(42, min(78, score))


def build_market_value_rank(score: int) -> str:
    if score >= 74:
        return "A"
    if score >= 67:
        return "B+"
    if score >= 60:
        return "B"
    if score >= 54:
        return "C+"
    return "C"


def build_salary_range(score: int, dominant_type: str) -> str:
    type_offset = {
        "stable": 0,
        "challenge": 40,
        "specialist": 25,
    }[dominant_type]
    base_low = 290 + type_offset + max(score - 45, 0) * 4
    span = {
        "stable": 90,
        "challenge": 110,
        "specialist": 100,
    }[dominant_type]

    low = round(base_low / 10) * 10
    high = round((base_low + span) / 10) * 10
    return f"{low}〜{high}万円"


def build_urgency_label(answers: dict[str, str], score: int) -> str:
    concern = answers.get("current_concern", "")
    if concern in {"stuck_growth", "lack_skill"} or score <= 55:
        return "高"
    return "中"
