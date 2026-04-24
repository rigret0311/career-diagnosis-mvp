from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from app import create_app
from mailer import DiagnosisMailer
from scripts.send_due_emails import send_due_emails
from storage import read_json_list, write_json_list


class DummyMailer:
    def __init__(self, status: str = "sent") -> None:
        self.status = status
        self.calls: list[dict] = []

    def send_sequence_email(self, recipient_email: str, result: dict, lead_id: str, step: int) -> dict:
        self.calls.append(
            {
                "recipient_email": recipient_email,
                "lead_id": lead_id,
                "step": step,
                "market_value_rank": result["market_value_rank"],
            }
        )
        delivered = self.status == "sent"
        return {
            "status": self.status,
            "delivered": delivered,
            "message": "登録メールアドレスへ詳細結果を自動送信しました。",
            "preview_path": None,
        }


class CareerDiagnosisAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "submissions.json"
        self.events_file = Path(self.temp_dir.name) / "events.json"
        self.mailer = DummyMailer()
        app = create_app(
            {
                "TESTING": True,
                "DATA_FILE": self.data_file,
                "EVENTS_FILE": self.events_file,
                "MAILER": self.mailer,
            }
        )
        self.client = app.test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_home_page_loads(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("あなたの市場価値", response.get_data(as_text=True))

    def test_submission_saves_lead_and_email_sequence(self) -> None:
        response = self.client.post("/diagnose", data=self._sample_payload())
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("推定市場価値", body)
        self.assertTrue(self.data_file.exists())

        saved = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(len(saved), 1)
        self.assertTrue(saved[0]["lead_id"])
        self.assertEqual(saved[0]["answers"]["current_role"], "営業事務")
        self.assertEqual(saved[0]["answers"]["email"], "test@example.com")
        self.assertIn(saved[0]["result"]["type_name"], {"安定再設計タイプ", "成長加速タイプ", "専門武器化タイプ"})
        self.assertIn(saved[0]["result"]["market_value_rank"], {"A", "B+", "B", "C+", "C"})

        sequence = saved[0]["email_sequence"]
        self.assertEqual([item["step"] for item in sequence], [1, 2, 3])
        self.assertEqual(sequence[0]["status"], "sent")
        self.assertEqual(sequence[1]["status"], "pending")
        self.assertEqual(sequence[2]["status"], "pending")
        self.assertEqual(len(self.mailer.calls), 1)
        self.assertEqual(self.mailer.calls[0]["step"], 1)
        self.assertEqual(self.mailer.calls[0]["recipient_email"], "test@example.com")

    def test_missing_value_returns_400(self) -> None:
        invalid_payload = self._sample_payload()
        invalid_payload["future_image"] = ""

        response = self.client.post("/diagnose", data=invalid_payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("入力不足があります", response.get_data(as_text=True))

    def test_invalid_email_returns_400(self) -> None:
        invalid_payload = self._sample_payload()
        invalid_payload["email"] = "invalid-email"

        response = self.client.post("/diagnose", data=invalid_payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("メールアドレスの形式が正しくありません", response.get_data(as_text=True))

    def test_track_click_saves_event_and_redirects_to_consultation(self) -> None:
        lead_id = self._create_submission()

        response = self.client.get(f"/track/{lead_id}/1")

        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/consultation?lead_id={lead_id}&step=1", response.headers["Location"])
        events = read_json_list(self.events_file)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "email_click")
        self.assertEqual(events[0]["lead_id"], lead_id)
        self.assertEqual(events[0]["step"], 1)

    def test_consultation_submit_saves_conversion_event(self) -> None:
        lead_id = self._create_submission()

        response = self.client.post(
            "/consultation",
            data={
                "lead_id": lead_id,
                "step": "2",
                "name": "山田 太郎",
                "email": "test@example.com",
                "contact_method": "email",
                "message": "今の職種から年収を上げる転職ルートを知りたい",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("相談希望を受け付けました", response.get_data(as_text=True))
        events = read_json_list(self.events_file)
        self.assertEqual(events[-1]["event_type"], "consultation_submit")
        self.assertEqual(events[-1]["lead_id"], lead_id)
        self.assertEqual(events[-1]["contact_method"], "email")

    def test_unknown_lead_returns_404(self) -> None:
        response = self.client.get("/track/missing/1")
        self.assertEqual(response.status_code, 404)

    def _create_submission(self) -> str:
        response = self.client.post("/diagnose", data=self._sample_payload())
        self.assertEqual(response.status_code, 200)
        return read_json_list(self.data_file)[0]["lead_id"]

    @staticmethod
    def _sample_payload() -> dict[str, str]:
        return {
            "age_group": "25-34",
            "current_role": "営業事務",
            "work_style": "structured_team",
            "strength": "support",
            "motivation": "security",
            "current_concern": "unclear_path",
            "preferred_environment": "clear_rules",
            "future_image": "安定して長く働けるバックオフィス職に移りたい",
            "email": "test@example.com",
        }


class EmailWorkflowTests(unittest.TestCase):
    def test_mailer_saves_preview_when_smtp_is_unconfigured(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {}, clear=True):
                mailer = DiagnosisMailer(Path(temp_dir))
                delivery = mailer.send_sequence_email(
                    recipient_email="test@example.com",
                    result=self._sample_result("lead-1"),
                    lead_id="lead-1",
                    step=1,
                )

            self.assertEqual(delivery["status"], "preview_saved")
            self.assertFalse(delivery["delivered"])
            self.assertTrue(Path(delivery["preview_path"]).exists())

    def test_send_due_emails_only_sends_due_pending_messages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            submissions_file = Path(temp_dir) / "submissions.json"
            now = datetime(2026, 4, 24, 9, 0, tzinfo=timezone.utc)
            submission = self._sample_submission(now)
            write_json_list(submissions_file, [submission])

            mailer = DummyMailer()
            summary = send_due_emails(submissions_file=submissions_file, mailer=mailer, now=now)

            self.assertEqual(summary["checked"], 1)
            self.assertEqual(summary["sent"], 1)
            self.assertEqual(len(mailer.calls), 1)
            self.assertEqual(mailer.calls[0]["step"], 2)

            updated = read_json_list(submissions_file)[0]["email_sequence"]
            self.assertEqual(updated[1]["status"], "sent")
            self.assertEqual(updated[2]["status"], "pending")

    @staticmethod
    def _sample_result(lead_id: str) -> dict:
        return {
            "lead_id": lead_id,
            "type_key": "stable",
            "type_name": "安定再設計タイプ",
            "market_value_rank": "C+",
            "estimated_salary_range": "330〜420万円",
            "risk_summary": "このままだと市場価値が伸びにくい状態です。",
            "recommended_roles": ["営業事務", "カスタマーサポート"],
            "actions": ["職務経歴を棚卸しする", "Excelを深掘りする", "改善提案歓迎の求人を見る"],
            "disclaimer": "この結果は推定値です。",
        }

    def _sample_submission(self, now: datetime) -> dict:
        lead_id = "lead-due-test"
        return {
            "lead_id": lead_id,
            "submitted_at": now.isoformat(timespec="seconds"),
            "answers": {"email": "test@example.com"},
            "result": self._sample_result(lead_id),
            "email_sequence": [
                {
                    "step": 1,
                    "subject": "sent",
                    "due_at": (now - timedelta(days=1)).isoformat(timespec="seconds"),
                    "status": "sent",
                    "sent_at": (now - timedelta(days=1)).isoformat(timespec="seconds"),
                    "delivery": {"status": "sent"},
                },
                {
                    "step": 2,
                    "subject": "due",
                    "due_at": (now - timedelta(minutes=1)).isoformat(timespec="seconds"),
                    "status": "pending",
                    "sent_at": None,
                    "delivery": None,
                },
                {
                    "step": 3,
                    "subject": "future",
                    "due_at": (now + timedelta(days=1)).isoformat(timespec="seconds"),
                    "status": "pending",
                    "sent_at": None,
                    "delivery": None,
                },
            ],
        }


if __name__ == "__main__":
    unittest.main()
