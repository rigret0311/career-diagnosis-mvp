from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import BASE_DIR, SUBMISSIONS_FILE  # noqa: E402
from mailer import build_mailer  # noqa: E402
from storage import read_json_list, write_json_list  # noqa: E402


def send_due_emails(
    submissions_file: Path = SUBMISSIONS_FILE,
    mailer=None,
    now: datetime | None = None,
) -> dict:
    current_time = now or datetime.now(timezone.utc).astimezone()
    submissions = read_json_list(submissions_file)
    mailer = mailer or build_mailer(BASE_DIR)
    summary = {
        "checked": 0,
        "updated": 0,
        "sent": 0,
        "preview_saved": 0,
        "failed": 0,
    }

    for submission in submissions:
        recipient_email = submission.get("answers", {}).get("email", "")
        lead_id = submission.get("lead_id", "")
        result = dict(submission.get("result", {}))
        result["lead_id"] = lead_id

        for email_item in submission.get("email_sequence", []):
            if email_item.get("status") != "pending":
                continue
            if _parse_datetime(email_item.get("due_at", "")) > current_time:
                continue

            summary["checked"] += 1
            step = int(email_item["step"])
            delivery = mailer.send_sequence_email(
                recipient_email=recipient_email,
                result=result,
                lead_id=lead_id,
                step=step,
            )

            email_item["status"] = delivery["status"]
            email_item["delivery"] = delivery
            email_item["sent_at"] = _now_iso() if delivery.get("delivered") else None

            summary["updated"] += 1
            if delivery["status"] in summary:
                summary[delivery["status"]] += 1

    if summary["updated"]:
        write_json_list(submissions_file, submissions)

    return summary


def main() -> int:
    _load_env_file(BASE_DIR / ".env")
    summary = send_due_emails()
    print(
        "追客メール確認: "
        f"対象 {summary['checked']}件 / "
        f"送信 {summary['sent']}件 / "
        f"プレビュー保存 {summary['preview_saved']}件 / "
        f"失敗 {summary['failed']}件"
    )
    return 0


def _load_env_file(file_path: Path) -> None:
    if not file_path.exists():
        return

    for line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc).astimezone()
    return parsed


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


if __name__ == "__main__":
    raise SystemExit(main())
