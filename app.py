from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from flask import Flask, abort, redirect, render_template, request, url_for

from config import BASE_DIR, EVENTS_FILE, QUESTIONS, SUBMISSIONS_FILE
from diagnosis import build_diagnosis_result, get_answer_labels, validate_answers
from mailer import EMAIL_SEQUENCE_DEFINITIONS, build_mailer
from storage import append_event, append_submission, find_submission_by_lead_id


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="career-mvp-local",
        DATA_FILE=SUBMISSIONS_FILE,
        EVENTS_FILE=EVENTS_FILE,
        MAILER=None,
    )

    if test_config:
        app.config.update(test_config)

    if app.config["MAILER"] is None:
        app.config["MAILER"] = build_mailer(BASE_DIR)

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            questions=QUESTIONS,
            errors=[],
            values={},
        )

    @app.post("/diagnose")
    def diagnose():
        answers = {question["id"]: request.form.get(question["id"], "").strip() for question in QUESTIONS}
        errors = validate_answers(answers)

        if errors:
            return (
                render_template(
                    "index.html",
                    questions=QUESTIONS,
                    errors=errors,
                    values=answers,
                ),
                400,
            )

        answer_labels = get_answer_labels(answers)
        result = build_diagnosis_result(answers, answer_labels)
        lead_id = uuid4().hex
        result["lead_id"] = lead_id

        submitted_at = _parse_datetime(result["submitted_at"])
        email_sequence = _build_email_sequence(submitted_at)
        first_email = email_sequence[0]
        mail_delivery = app.config["MAILER"].send_sequence_email(
            recipient_email=answers["email"],
            result=result,
            lead_id=lead_id,
            step=1,
        )
        first_email["status"] = mail_delivery["status"]
        first_email["delivery"] = mail_delivery
        if mail_delivery.get("delivered"):
            first_email["sent_at"] = _now_iso()

        result["mail_delivery"] = mail_delivery

        submission = {
            "lead_id": lead_id,
            "submitted_at": result["submitted_at"],
            "answers": answers,
            "answer_labels": answer_labels,
            "result": {
                "lead_id": lead_id,
                "type_key": result["type_key"],
                "type_name": result["type_name"],
                "headline": result["headline"],
                "summary": result["summary"],
                "market_value_rank": result["market_value_rank"],
                "market_value_score": result["market_value_score"],
                "estimated_salary_range": result["estimated_salary_range"],
                "urgency_label": result["urgency_label"],
                "risk_summary": result["risk_summary"],
                "leverage_points": result["leverage_points"],
                "recommended_roles": result["recommended_roles"],
                "actions": result["actions"],
                "score_breakdown": result["score_breakdown"],
                "registered_email": result["registered_email"],
                "disclaimer": result["disclaimer"],
            },
            "mail_delivery": mail_delivery,
            "email_sequence": email_sequence,
        }
        append_submission(Path(app.config["DATA_FILE"]), submission)

        return render_template("result.html", result=result, answers=answer_labels)

    @app.get("/track/<lead_id>/<int:step>")
    def track_email_click(lead_id: str, step: int):
        submission = find_submission_by_lead_id(Path(app.config["DATA_FILE"]), lead_id)
        if not submission or not _sequence_has_step(submission, step):
            abort(404)

        append_event(
            Path(app.config["EVENTS_FILE"]),
            {
                "event_id": uuid4().hex,
                "event_type": "email_click",
                "occurred_at": _now_iso(),
                "lead_id": lead_id,
                "step": step,
                "email": submission.get("answers", {}).get("email", ""),
                "type_key": submission.get("result", {}).get("type_key", ""),
                "user_agent": request.headers.get("User-Agent", ""),
                "referrer": request.headers.get("Referer", ""),
                "target": "consultation",
            },
        )
        return redirect(url_for("consultation", lead_id=lead_id, step=step))

    @app.get("/consultation")
    def consultation():
        lead_id = request.args.get("lead_id", "").strip()
        step = request.args.get("step", "").strip()
        submission = find_submission_by_lead_id(Path(app.config["DATA_FILE"]), lead_id)
        if not submission:
            abort(404)

        return render_template(
            "consultation.html",
            submission=submission,
            step=step,
            errors=[],
            values={
                "lead_id": lead_id,
                "step": step,
                "name": "",
                "email": submission.get("answers", {}).get("email", ""),
                "contact_method": "email",
                "message": "",
            },
        )

    @app.post("/consultation")
    def submit_consultation():
        values = {
            "lead_id": request.form.get("lead_id", "").strip(),
            "step": request.form.get("step", "").strip(),
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "contact_method": request.form.get("contact_method", "").strip(),
            "message": request.form.get("message", "").strip(),
        }
        submission = find_submission_by_lead_id(Path(app.config["DATA_FILE"]), values["lead_id"])
        if not submission:
            abort(404)

        errors = _validate_consultation(values)
        if errors:
            return (
                render_template(
                    "consultation.html",
                    submission=submission,
                    step=values["step"],
                    errors=errors,
                    values=values,
                ),
                400,
            )

        event = {
            "event_id": uuid4().hex,
            "event_type": "consultation_submit",
            "occurred_at": _now_iso(),
            "lead_id": values["lead_id"],
            "step": values["step"],
            "name": values["name"],
            "email": values["email"],
            "contact_method": values["contact_method"],
            "message": values["message"],
            "type_key": submission.get("result", {}).get("type_key", ""),
            "market_value_rank": submission.get("result", {}).get("market_value_rank", ""),
        }
        append_event(Path(app.config["EVENTS_FILE"]), event)

        return render_template("consultation_complete.html", submission=submission, event=event)

    return app


app = create_app()


def _build_email_sequence(submitted_at: datetime) -> list[dict]:
    due_offsets = {
        1: timedelta(seconds=0),
        2: timedelta(days=1),
        3: timedelta(days=3),
    }
    sequence = []
    for step, offset in due_offsets.items():
        sequence.append(
            {
                "step": step,
                "subject": EMAIL_SEQUENCE_DEFINITIONS[step]["subject"],
                "due_at": (submitted_at + offset).isoformat(timespec="seconds"),
                "status": "pending",
                "sent_at": None,
                "delivery": None,
            }
        )
    return sequence


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc).astimezone()
    return parsed


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _sequence_has_step(submission: dict, step: int) -> bool:
    return any(item.get("step") == step for item in submission.get("email_sequence", []))


def _validate_consultation(values: dict[str, str]) -> list[str]:
    errors = []
    if not values["name"]:
        errors.append("お名前を入力してください。")
    if not values["email"]:
        errors.append("メールアドレスを入力してください。")
    elif "@" not in values["email"] or "." not in values["email"].split("@")[-1]:
        errors.append("メールアドレスの形式が正しくありません。")
    if values["contact_method"] not in {"email", "phone", "other"}:
        errors.append("希望連絡方法を選択してください。")
    if not values["message"]:
        errors.append("相談したい内容を入力してください。")
    return errors


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
