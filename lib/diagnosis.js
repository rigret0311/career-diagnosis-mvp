export const questions = [
  {
    id: "age_group",
    label: "年代を教えてください",
    type: "select",
    options: [
      ["18-24", "18〜24歳"],
      ["25-34", "25〜34歳"],
      ["35-44", "35〜44歳"],
      ["45+", "45歳以上"],
    ],
  },
  {
    id: "current_role",
    label: "現在の職種・担当業務",
    type: "text",
    placeholder: "例：営業事務、接客、Web制作、経理補助",
  },
  {
    id: "work_style",
    label: "心地よく働けるスタイル",
    type: "choice",
    options: [
      ["structured_team", "役割が明確なチームで、安定して進めたい"],
      ["flexible_team", "変化のあるチームで、新しいことに挑戦したい"],
      ["independent_focus", "一人で集中し、専門性を深めたい"],
    ],
  },
  {
    id: "strength",
    label: "周囲から評価されやすい強み",
    type: "choice",
    options: [
      ["support", "段取り・サポート・抜け漏れ防止"],
      ["drive", "行動力・巻き込み・前に進める力"],
      ["analysis", "分析・改善・品質へのこだわり"],
    ],
  },
  {
    id: "motivation",
    label: "今いちばん手に入れたいもの",
    type: "choice",
    options: [
      ["security", "収入や働き方の安定"],
      ["growth", "年収アップやキャリアアップ"],
      ["mastery", "手に職や専門性"],
    ],
  },
  {
    id: "current_concern",
    label: "今いちばん大きい悩み",
    type: "choice",
    options: [
      ["unclear_path", "自分に合う仕事が分からない"],
      ["stuck_growth", "今の仕事の先が見えない"],
      ["lack_skill", "強みになるスキルが足りない気がする"],
    ],
  },
  {
    id: "preferred_environment",
    label: "力を出しやすい職場環境",
    type: "choice",
    options: [
      ["clear_rules", "ルールや評価基準が分かりやすい環境"],
      ["speed_change", "スピード感があり、裁量の大きい環境"],
      ["quiet_depth", "静かに集中でき、技術を磨ける環境"],
    ],
  },
  {
    id: "future_image",
    label: "1年後に近づきたい状態",
    type: "textarea",
    placeholder: "例：在宅でも働ける事務職に移りたい",
  },
  {
    id: "email",
    label: "結果をひもづけるメールアドレス",
    type: "email",
    placeholder: "you@example.com",
  },
];

export const questionSteps = [
  ["age_group", "current_role"],
  ["work_style"],
  ["strength"],
  ["motivation", "current_concern"],
  ["preferred_environment", "future_image"],
  ["email"],
];

const scoreMap = {
  work_style: {
    structured_team: { stable: 3, challenge: 1, specialist: 0 },
    flexible_team: { stable: 0, challenge: 3, specialist: 1 },
    independent_focus: { stable: 1, challenge: 0, specialist: 3 },
  },
  strength: {
    support: { stable: 3, challenge: 0, specialist: 1 },
    drive: { stable: 0, challenge: 3, specialist: 1 },
    analysis: { stable: 1, challenge: 1, specialist: 3 },
  },
  motivation: {
    security: { stable: 3, challenge: 0, specialist: 1 },
    growth: { stable: 0, challenge: 3, specialist: 1 },
    mastery: { stable: 1, challenge: 0, specialist: 3 },
  },
  current_concern: {
    unclear_path: { stable: 2, challenge: 1, specialist: 1 },
    stuck_growth: { stable: 0, challenge: 3, specialist: 1 },
    lack_skill: { stable: 1, challenge: 1, specialist: 3 },
  },
  preferred_environment: {
    clear_rules: { stable: 3, challenge: 0, specialist: 1 },
    speed_change: { stable: 0, challenge: 3, specialist: 1 },
    quiet_depth: { stable: 1, challenge: 0, specialist: 3 },
  },
};

const templates = {
  stable: {
    typeName: "安定再設計タイプ",
    headline: "支える力を、評価される実績へ変える時期です。",
    summary: "安定して成果を出す力があります。一方で、日々の貢献が『できて当たり前』に埋もれると、給与交渉の材料が増えにくい傾向があります。",
    risk: "支える役割だけを続けると、重宝はされても代替可能と見られやすくなります。業務改善や数字で示せる実績をひとつ持つことが分岐点です。",
    leverage: ["調整力を改善実績として言語化する", "Excel・顧客対応・進行管理のどれかを武器にする", "作業者から改善できる人へ見せ方を変える"],
    roles: ["営業事務", "カスタマーサポート", "人事・採用アシスタント", "業務改善サポート"],
    actions: ["職務経歴から改善・調整経験を3件書き出す", "伸ばすスキルをひとつに決める", "改善提案を歓迎する求人を10件比較する"],
  },
  challenge: {
    typeName: "成長加速タイプ",
    headline: "動ける強みを、年収につながる成果へ寄せる時期です。",
    summary: "停滞より前進を選びやすく、行動量や巻き込み力が武器になります。評価指標が曖昧な環境では消耗しやすいため、成果が数字で返る場所選びが重要です。",
    risk: "裁量のない職場に留まると、成果より社内調整に時間を奪われます。忙しいのに市場価値が上がらない状態を避ける必要があります。",
    leverage: ["行動力を数字のある改善経験に変える", "営業・企画・マーケの勝ち筋を絞る", "評価指標が明確な環境を選ぶ"],
    roles: ["法人営業", "キャリアアドバイザー", "マーケティングアシスタント", "プロジェクト進行管理"],
    actions: ["直近の成果を数字つきで3件まとめる", "候補職種を3つ比較して優先順位を決める", "30日以内に応募できる状態をつくる"],
  },
  specialist: {
    typeName: "専門武器化タイプ",
    headline: "学んだことを、見せられる成果物へ変える時期です。",
    summary: "広く浅くより、得意領域を絞って深めるほど評価されやすい傾向があります。分析・制作・設計・改善など、成果物が見える仕事と好相性です。",
    risk: "学習だけで実務に近い成果物が増えないと、知識はあっても採用市場で比較されたときに弱くなります。完成品を外に出すことが分岐点です。",
    leverage: ["専門分野をひとつに絞る", "品質へのこだわりを改善数値で示す", "学習履歴より成果物を優先する"],
    roles: ["Web制作アシスタント", "データ分析アシスタント", "デザインアシスタント", "ITサポート"],
    actions: ["狙う分野をひとつ決める", "30日で完成する成果物を一本つくる", "実務に近い課題や小さな案件へ触れる"],
  },
};

export function answerLabel(questionId, value) {
  const question = questions.find((item) => item.id === questionId);
  return question?.options?.find(([key]) => key === value)?.[1] ?? value;
}

export function validateStep(answers, stepIndex) {
  const errors = {};
  for (const id of questionSteps[stepIndex]) {
    const value = String(answers[id] ?? "").trim();
    if (!value) errors[id] = "この項目を入力してください";
    if (id === "email" && value && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value)) {
      errors[id] = "メールアドレスの形式を確認してください";
    }
  }
  return errors;
}

export function buildDiagnosisResult(answers, now = new Date()) {
  const scores = { stable: 0, challenge: 0, specialist: 0 };
  for (const [questionId, options] of Object.entries(scoreMap)) {
    const points = options[answers[questionId]] ?? {};
    for (const key of Object.keys(scores)) scores[key] += points[key] ?? 0;
  }

  const typeOrder = ["stable", "challenge", "specialist"];
  let dominantType = typeOrder.slice().sort((a, b) => scores[b] - scores[a])[0];
  const top = Math.max(...Object.values(scores));
  const tied = typeOrder.filter((key) => scores[key] === top);
  if (tied.length > 1) {
    if ((answers.motivation === "growth" || answers.current_concern === "stuck_growth") && tied.includes("challenge")) dominantType = "challenge";
    else if ((answers.motivation === "mastery" || answers.current_concern === "lack_skill") && tied.includes("specialist")) dominantType = "specialist";
    else if (tied.includes("stable")) dominantType = "stable";
  }

  let score = { stable: 52, challenge: 60, specialist: 57 }[dominantType];
  score += { security: 0, growth: 5, mastery: 4 }[answers.motivation] ?? 0;
  score += { support: 0, drive: 4, analysis: 3 }[answers.strength] ?? 0;
  score += { structured_team: 0, flexible_team: 3, independent_focus: 2 }[answers.work_style] ?? 0;
  score += { clear_rules: 0, speed_change: 3, quiet_depth: 2 }[answers.preferred_environment] ?? 0;
  score += { unclear_path: -2, stuck_growth: -1, lack_skill: -3 }[answers.current_concern] ?? 0;
  score += Math.max(0, Math.min(6, scores[dominantType] - 8));
  score = Math.max(42, Math.min(78, score));

  const rank = score >= 74 ? "A" : score >= 67 ? "B+" : score >= 60 ? "B" : score >= 54 ? "C+" : "C";
  const offset = { stable: 0, challenge: 40, specialist: 25 }[dominantType];
  const low = Math.round((290 + offset + Math.max(score - 45, 0) * 4) / 10) * 10;
  const high = Math.round((low + { stable: 90, challenge: 110, specialist: 100 }[dominantType]) / 10) * 10;
  const urgency = ["stuck_growth", "lack_skill"].includes(answers.current_concern) || score <= 55 ? "高" : "中";
  const template = templates[dominantType];

  return {
    id: globalThis.crypto?.randomUUID?.() ?? `${now.getTime()}-${Math.random().toString(16).slice(2)}`,
    createdAt: now.toISOString(),
    dominantType,
    score,
    scores,
    rank,
    salaryRange: `${low}〜${high}万円`,
    urgency,
    ...template,
    role: answers.current_role,
    concern: answerLabel("current_concern", answers.current_concern),
    future: answers.future_image,
    email: answers.email,
  };
}

export function reportText(result) {
  return [
    "キャリア現在地診断レポート",
    `診断日: ${new Date(result.createdAt).toLocaleDateString("ja-JP")}`,
    "",
    `市場価値ランク: ${result.rank}`,
    `市場価値スコア: ${result.score}/100`,
    `想定年収レンジ: ${result.salaryRange}`,
    `診断タイプ: ${result.typeName}`,
    `行動緊急度: ${result.urgency}`,
    "",
    result.headline,
    result.summary,
    "",
    "注意したいリスク",
    result.risk,
    "",
    "今伸ばす武器",
    ...result.leverage.map((item, index) => `${index + 1}. ${item}`),
    "",
    "狙い目の職種",
    ...result.roles.map((item) => `- ${item}`),
    "",
    "30日でやること",
    ...result.actions.map((item, index) => `${index + 1}. ${item}`),
    "",
    "※本診断は回答傾向に基づく簡易推定で、採用条件や年収を保証するものではありません。",
  ].join("\n");
}
