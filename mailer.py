from __future__ import annotations

import os
import re
import smtplib
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

EMAIL_SEQUENCE_DEFINITIONS = {
    1: {
        "subject": "【重要】あなたの市場価値診断の詳細結果",
        "cta": "無料で次の動き方を相談する",
    },
    2: {
        "subject": "【放置注意】市場価値が伸びない人の共通点",
        "cta": "自分の場合の優先順位を相談する",
    },
    3: {
        "subject": "【最後の確認】3ヶ月後に差が出る人の動き方",
        "cta": "無料相談を希望する",
    },
}


def build_mailer(base_dir: Path) -> "DiagnosisMailer":
    return DiagnosisMailer(base_dir=base_dir)


class DiagnosisMailer:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.preview_dir = base_dir / "data" / "email_previews"
        self.smtp_host = os.getenv("SMTP_HOST", "").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", "587").strip() or "587")
        self.smtp_username = os.getenv("SMTP_USERNAME", "").strip()
        self.smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
        self.smtp_use_tls = _read_bool_env("SMTP_USE_TLS", default=True)
        self.smtp_use_ssl = _read_bool_env("SMTP_USE_SSL", default=False)
        self.smtp_timeout = int(os.getenv("SMTP_TIMEOUT", "15").strip() or "15")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "").strip()
        self.from_name = os.getenv("SMTP_FROM_NAME", "キャリア市場価値診断").strip()
        self.reply_to_email = os.getenv("REPLY_TO_EMAIL", "").strip()
        self.app_base_url = (
            os.getenv("APP_BASE_URL", "").strip()
            or os.getenv("GUIDE_LINK", "").strip()
            or "http://127.0.0.1:5000"
        ).rstrip("/")

    def send_diagnosis_email(self, recipient_email: str, result: dict) -> dict:
        return self.send_sequence_email(
            recipient_email=recipient_email,
            result=result,
            lead_id=result.get("lead_id", ""),
            step=1,
        )

    def send_sequence_email(self, recipient_email: str, result: dict, lead_id: str, step: int) -> dict:
        definition = EMAIL_SEQUENCE_DEFINITIONS[step]
        subject = definition["subject"]
        body = self._build_email_body(result=result, lead_id=lead_id, step=step)

        if not self._is_configured():
            preview_path = self._save_preview(recipient_email, subject, body)
            return {
                "status": "preview_saved",
                "delivered": False,
                "message": "SMTP未設定のため、メール本文をローカルのプレビューファイルに保存しました。",
                "preview_path": str(preview_path),
            }

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = formataddr((self.from_name, self.from_email))
        message["To"] = recipient_email
        if self.reply_to_email:
            message["Reply-To"] = self.reply_to_email
        message.set_content(body)

        try:
            if self.smtp_use_ssl:
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=self.smtp_timeout) as smtp:
                    self._login_if_needed(smtp)
                    smtp.send_message(message)
            else:
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=self.smtp_timeout) as smtp:
                    smtp.ehlo()
                    if self.smtp_use_tls:
                        smtp.starttls()
                        smtp.ehlo()
                    self._login_if_needed(smtp)
                    smtp.send_message(message)
        except Exception as exc:
            preview_path = self._save_preview(recipient_email, subject, body)
            return {
                "status": "failed",
                "delivered": False,
                "message": "メール送信に失敗したため、本文をローカルのプレビューファイルに保存しました。",
                "preview_path": str(preview_path),
                "error": str(exc),
            }

        return {
            "status": "sent",
            "delivered": True,
            "message": "登録メールアドレスへ詳細結果を自動送信しました。",
            "preview_path": None,
        }

    def _is_configured(self) -> bool:
        return bool(self.smtp_host and self.from_email)

    def _login_if_needed(self, smtp: smtplib.SMTP) -> None:
        if self.smtp_username and self.smtp_password:
            smtp.login(self.smtp_username, self.smtp_password)

    def _build_email_body(self, result: dict, lead_id: str, step: int) -> str:
        if step == 1:
            return self._build_step_one_body(result, lead_id, step)
        if step == 2:
            return self._build_step_two_body(result, lead_id, step)
        if step == 3:
            return self._build_step_three_body(result, lead_id, step)
        raise ValueError(f"Unsupported email step: {step}")

    def _build_step_one_body(self, result: dict, lead_id: str, step: int) -> str:
        risk_summary = _compact(result.get("risk_summary", "今のままだと改善しにくい状態です。"))
        action_lines = "\n".join(
            f"{index}. {action}" for index, action in enumerate(result.get("actions", []), start=1)
        )
        role_lines = "\n".join(f"- {role}" for role in result.get("recommended_roles", []))
        consultation_link = self._tracking_url(lead_id, step)

        return (
            "診断お疲れ様です。\n"
            "あなたの結果を簡単にまとめると、\n"
            f"・市場価値：{result.get('market_value_rank', '')}ランク（{result.get('type_name', '')}）\n"
            f"・想定年収：{result.get('estimated_salary_range', '')}\n"
            f"・リスク：{risk_summary}\n"
            "でした。\n\n"
            "ここで重要なのは、\n"
            "「今のままだと改善しない」という点です。\n"
            "実際、このタイプの人は\n"
            "3〜6ヶ月以内に行動しないとほぼ固定化します。\n\n"
            "▼次にやるべき3ステップ\n"
            f"{action_lines}\n\n"
            "▼狙い目の職種\n"
            f"{role_lines}\n\n"
            f"▼{EMAIL_SEQUENCE_DEFINITIONS[step]['cta']}\n"
            f"{consultation_link}\n\n"
            "※希望者には個別でアドバイスも可能です\n\n"
            f"{result.get('disclaimer', '')}\n"
        )

    def _build_step_two_body(self, result: dict, lead_id: str, step: int) -> str:
        actions = result.get("actions", [])
        first_action = actions[0] if actions else "まずは職務経歴と応募先を見直す"
        consultation_link = self._tracking_url(lead_id, step)

        return (
            "昨日の市場価値診断の続きです。\n\n"
            "市場価値が伸びない人の共通点は、結果を見て終わることです。\n"
            f"あなたの場合、まず見るべきポイントは「{first_action}」です。\n\n"
            "ここを放置すると、今の悩みがそのまま固定化しやすくなります。\n"
            "逆に、最初の1つを決めて動ける人は3ヶ月後に選択肢が変わります。\n\n"
            f"▼{EMAIL_SEQUENCE_DEFINITIONS[step]['cta']}\n"
            f"{consultation_link}\n\n"
            "迷う場合は、自分だけで判断せずに優先順位を確認してください。\n"
        )

    def _build_step_three_body(self, result: dict, lead_id: str, step: int) -> str:
        risk_summary = _compact(result.get("risk_summary", "行動が遅れるほど選択肢が狭くなります。"))
        consultation_link = self._tracking_url(lead_id, step)

        return (
            "市場価値診断から3日目です。\n\n"
            "ここで決めるべきことはシンプルです。\n"
            "自力で動くか、相談して最短ルートを決めるかです。\n\n"
            f"あなたの診断で出ていたリスクは、{risk_summary}\n\n"
            "3ヶ月後に差が出る人は、完璧な準備より先に方向性を決めています。\n"
            "まずは今の状態で何から着手すべきかを確認してください。\n\n"
            f"▼{EMAIL_SEQUENCE_DEFINITIONS[step]['cta']}\n"
            f"{consultation_link}\n\n"
            "このメールは診断後の初回フォローです。不要な場合は返信で止められます。\n"
        )

    def _save_preview(self, recipient_email: str, subject: str, body: str) -> Path:
        self.preview_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_recipient = re.sub(r"[^A-Za-z0-9_.-]", "_", recipient_email or "unknown")
        preview_path = self.preview_dir / f"{timestamp}-{safe_recipient}.txt"
        preview_path.write_text(
            f"To: {recipient_email}\nSubject: {subject}\n\n{body}",
            encoding="utf-8",
        )
        return preview_path

    def _tracking_url(self, lead_id: str, step: int) -> str:
        return f"{self.app_base_url}/track/{lead_id}/{step}"


def _read_bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()
