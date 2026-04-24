from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"
EVENTS_FILE = DATA_DIR / "events.json"

QUESTIONS = [
    {
        "id": "age_group",
        "label": "1. 年代を選んでください",
        "type": "select",
        "required": True,
        "options": [
            {"value": "18-24", "label": "18〜24歳"},
            {"value": "25-34", "label": "25〜34歳"},
            {"value": "35-44", "label": "35〜44歳"},
            {"value": "45+", "label": "45歳以上"},
        ],
    },
    {
        "id": "current_role",
        "label": "2. 現在の職種・担当業務を教えてください",
        "type": "text",
        "required": True,
        "placeholder": "例: 営業事務、接客、Web制作、経理補助",
    },
    {
        "id": "work_style",
        "label": "3. 働き方の好みに近いものを選んでください",
        "type": "radio",
        "required": True,
        "options": [
            {
                "value": "structured_team",
                "label": "役割が明確なチームで、安定して進めたい",
                "scores": {"stable": 3, "challenge": 1, "specialist": 0},
            },
            {
                "value": "flexible_team",
                "label": "変化のあるチームで、新しいことに挑戦したい",
                "scores": {"stable": 0, "challenge": 3, "specialist": 1},
            },
            {
                "value": "independent_focus",
                "label": "一人で集中し、専門性を深めたい",
                "scores": {"stable": 1, "challenge": 0, "specialist": 3},
            },
        ],
    },
    {
        "id": "strength",
        "label": "4. 自分の強みとして近いものを選んでください",
        "type": "radio",
        "required": True,
        "options": [
            {
                "value": "support",
                "label": "段取り・サポート・抜け漏れ防止",
                "scores": {"stable": 3, "challenge": 0, "specialist": 1},
            },
            {
                "value": "drive",
                "label": "行動力・巻き込み・前に進める力",
                "scores": {"stable": 0, "challenge": 3, "specialist": 1},
            },
            {
                "value": "analysis",
                "label": "分析・改善・品質へのこだわり",
                "scores": {"stable": 1, "challenge": 1, "specialist": 3},
            },
        ],
    },
    {
        "id": "motivation",
        "label": "5. 今いちばん得たいものは何ですか？",
        "type": "radio",
        "required": True,
        "options": [
            {
                "value": "security",
                "label": "収入や働き方の安定",
                "scores": {"stable": 3, "challenge": 0, "specialist": 1},
            },
            {
                "value": "growth",
                "label": "年収アップやキャリアアップ",
                "scores": {"stable": 0, "challenge": 3, "specialist": 1},
            },
            {
                "value": "mastery",
                "label": "手に職や専門性",
                "scores": {"stable": 1, "challenge": 0, "specialist": 3},
            },
        ],
    },
    {
        "id": "current_concern",
        "label": "6. いちばん大きい悩みに近いものを選んでください",
        "type": "radio",
        "required": True,
        "options": [
            {
                "value": "unclear_path",
                "label": "自分に合う仕事が分からない",
                "scores": {"stable": 2, "challenge": 1, "specialist": 1},
            },
            {
                "value": "stuck_growth",
                "label": "今の仕事の先が見えない",
                "scores": {"stable": 0, "challenge": 3, "specialist": 1},
            },
            {
                "value": "lack_skill",
                "label": "強みになるスキルが足りない気がする",
                "scores": {"stable": 1, "challenge": 1, "specialist": 3},
            },
        ],
    },
    {
        "id": "preferred_environment",
        "label": "7. 理想の職場環境に近いものを選んでください",
        "type": "radio",
        "required": True,
        "options": [
            {
                "value": "clear_rules",
                "label": "ルールや評価基準が分かりやすい環境",
                "scores": {"stable": 3, "challenge": 0, "specialist": 1},
            },
            {
                "value": "speed_change",
                "label": "スピード感があり、裁量の大きい環境",
                "scores": {"stable": 0, "challenge": 3, "specialist": 1},
            },
            {
                "value": "quiet_depth",
                "label": "静かに集中でき、技術を磨ける環境",
                "scores": {"stable": 1, "challenge": 0, "specialist": 3},
            },
        ],
    },
    {
        "id": "future_image",
        "label": "8. 1年後に一番近づきたい状態を教えてください",
        "type": "textarea",
        "required": True,
        "placeholder": "例: 在宅でも働ける事務職に移りたい / 手に職をつけて転職したい",
    },
    {
        "id": "email",
        "label": "9. 診断結果の保存先メールアドレスを入力してください",
        "type": "email",
        "required": True,
        "placeholder": "you@example.com",
        "help_text": "診断結果と今後の改善ヒントを自動メールで送ります。",
    },
]

RESULT_TEMPLATES = {
    "stable": {
        "type_name": "安定再設計タイプ",
        "headline": "今は市場価値を守れていても、武器が見えないままだと収入が伸びにくい状態です。",
        "summary_template": "現状の悩みが「{current_concern}」で、働き方も安定志向寄りです。サポート力は高い一方で、実績が『見えるスキル』として伝わらないと市場価値が停滞しやすい傾向があります。",
        "risk_template": "このまま『支える役割』のまま働き続けると、5年後も重宝はされても給与交渉の材料が増えにくい状態になりやすいです。特に{current_concern}のままだと、代替可能な人材と見られるリスクがあります。",
        "leverage_points": [
            "事務処理だけでなく、業務改善まで担える形に実績を変える",
            "Excel、顧客対応、進行管理のどれか1つを強みとして固定する",
            "『支える人』から『数字や効率を改善できる人』に見せ方を変える",
        ],
        "recommended_roles": ["営業事務", "カスタマーサポート", "総務・人事補助", "経理補助"],
        "actions": [
            "まずは職務経歴を棚卸しし、調整力・改善経験を3件書き出す",
            "今後30日でExcel、顧客対応、運用改善のうち1つを深掘りする",
            "応募先は『定型業務のみ』より『改善提案歓迎』の求人を優先する",
        ],
    },
    "challenge": {
        "type_name": "成長加速タイプ",
        "headline": "伸びる余地は大きい一方で、今の職場に留まると成長機会を取りこぼしやすい状態です。",
        "summary_template": "「{current_concern}」を打破したい意欲が強く、停滞よりも前進を選びやすい傾向があります。行動量や巻き込み力は市場で武器になりやすい反面、環境選びを間違えると消耗しやすいタイプです。",
        "risk_template": "5年後に詰まりやすい理由は、動けるのに裁量のない職場へ居続けることです。特に{current_concern}が続くと、成果より社内調整に時間を奪われて年収が頭打ちになりやすいです。",
        "leverage_points": [
            "行動力を『成果のある改善経験』として言語化する",
            "営業、企画、マーケのどこで勝つかを早めに絞る",
            "裁量と評価指標が見える環境へ移ると収入が伸びやすい",
        ],
        "recommended_roles": ["法人営業", "キャリアアドバイザー", "マーケティング補助", "プロジェクト進行管理"],
        "actions": [
            "直近の成果を数字ベースで3つまとめ、履歴書に反映する",
            "転職サイトで営業、企画、マーケ系を横断比較し、仮説を立てる",
            "成長余地のある企業だけに絞って、30日以内に応募導線を作る",
        ],
    },
    "specialist": {
        "type_name": "専門武器化タイプ",
        "headline": "市場価値を上げやすい素地はありますが、専門性を見える実績に変えないと評価されにくい状態です。",
        "summary_template": "今の役割が「{current_role}」であることも踏まえると、広く浅くより、得意領域を絞って伸ばす方が収入に結びつきやすいです。分析、制作、設計、改善のように成果物が見える仕事と相性があります。",
        "risk_template": "5年後に詰まりやすい理由は、学習だけで実務実績が増えないことです。特に{current_concern}の状態が続くと、知識はあるのに採用市場で比較されたときに弱くなりやすいです。",
        "leverage_points": [
            "専門分野を1つに絞り、ポートフォリオや成果物を作る",
            "品質へのこだわりを『改善した数値』に変換して見せる",
            "学習履歴より実務に近いアウトプットを優先する",
        ],
        "recommended_roles": ["Web制作補助", "データ入力・分析補助", "デザイナー補助", "エンジニア学習職"],
        "actions": [
            "狙う分野を1つ決めて、30日で出せる成果物を1本作る",
            "応募前にポートフォリオや改善事例メモを最低3件用意する",
            "学習だけで終わらず、実務に近い課題や副業案件に触れる",
        ],
    },
}
