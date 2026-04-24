from __future__ import annotations

import json
from pathlib import Path


def read_json_list(file_path: Path) -> list[dict]:
    if not file_path.exists():
        return []

    try:
        existing_data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if not isinstance(existing_data, list):
        return []

    return existing_data


def write_json_list(file_path: Path, data: list[dict]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_submission(file_path: Path, submission: dict) -> None:
    existing_data = read_json_list(file_path)
    existing_data.append(submission)
    write_json_list(file_path, existing_data)


def append_event(file_path: Path, event: dict) -> None:
    existing_data = read_json_list(file_path)
    existing_data.append(event)
    write_json_list(file_path, existing_data)


def find_submission_by_lead_id(file_path: Path, lead_id: str) -> dict | None:
    for submission in read_json_list(file_path):
        if submission.get("lead_id") == lead_id:
            return submission
    return None
