import assert from "node:assert/strict";
import test from "node:test";

import { buildDiagnosisResult, reportText, validateStep } from "../lib/diagnosis.js";

const answers = {
  age_group: "25-34",
  current_role: "営業事務",
  work_style: "structured_team",
  strength: "support",
  motivation: "security",
  current_concern: "unclear_path",
  preferred_environment: "clear_rules",
  future_image: "在宅でも働けるバックオフィス職に移りたい",
  email: "test@example.com",
};

test("診断結果にランク・年収・行動が含まれる", () => {
  const result = buildDiagnosisResult(answers, new Date("2026-07-14T00:00:00Z"));
  assert.equal(result.dominantType, "stable");
  assert.match(result.rank, /^(A|B\+|B|C\+|C)$/);
  assert.match(result.salaryRange, /^\d+〜\d+万円$/);
  assert.equal(result.actions.length, 3);
  assert.match(reportText(result), /30日でやること/);
});

test("必須項目とメール形式を検証する", () => {
  assert.deepEqual(validateStep({}, 0), {
    age_group: "この項目を入力してください",
    current_role: "この項目を入力してください",
  });
  assert.deepEqual(validateStep({ email: "invalid" }, 5), {
    email: "メールアドレスの形式を確認してください",
  });
});
