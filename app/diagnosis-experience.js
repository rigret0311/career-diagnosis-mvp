"use client";

import { useEffect, useState } from "react";
import {
  answerLabel,
  buildDiagnosisResult,
  questionSteps,
  questions,
  reportText,
  validateStep,
} from "../lib/diagnosis";

const DRAFT_KEY = "career-route-draft-v1";
const HISTORY_KEY = "career-route-history-v1";
const EVENT_KEY = "career-route-events-v1";
const contactEmail = process.env.NEXT_PUBLIC_CONTACT_EMAIL || "";

function track(eventType, details = {}) {
  try {
    const events = JSON.parse(localStorage.getItem(EVENT_KEY) || "[]");
    events.push({ eventType, occurredAt: new Date().toISOString(), ...details });
    localStorage.setItem(EVENT_KEY, JSON.stringify(events.slice(-100)));
  } catch {
    // Tracking must never block diagnosis completion.
  }
}

function QuestionField({ question, value, error, onChange }) {
  const id = `question-${question.id}`;

  if (question.type === "choice") {
    return (
      <fieldset className="field-block">
        <legend>{question.label}</legend>
        <div className="choice-grid">
          {question.options.map(([key, label], index) => (
            <label className={`choice-card ${value === key ? "is-selected" : ""}`} key={key}>
              <input
                type="radio"
                name={question.id}
                value={key}
                checked={value === key}
                onChange={() => onChange(question.id, key)}
              />
              <span className="choice-index">0{index + 1}</span>
              <span>{label}</span>
            </label>
          ))}
        </div>
        {error && <p className="field-error">{error}</p>}
      </fieldset>
    );
  }

  return (
    <div className="field-block">
      <label htmlFor={id}>{question.label}</label>
      {question.type === "select" ? (
        <select id={id} value={value} onChange={(event) => onChange(question.id, event.target.value)}>
          <option value="">選択してください</option>
          {question.options.map(([key, label]) => <option value={key} key={key}>{label}</option>)}
        </select>
      ) : question.type === "textarea" ? (
        <textarea id={id} rows="4" value={value} placeholder={question.placeholder} onChange={(event) => onChange(question.id, event.target.value)} />
      ) : (
        <input id={id} type={question.type} value={value} placeholder={question.placeholder} onChange={(event) => onChange(question.id, event.target.value)} />
      )}
      {question.id === "email" && <p className="field-help">入力内容はこの端末内だけに保存されます。外部へ自動送信されません。</p>}
      {error && <p className="field-error">{error}</p>}
    </div>
  );
}

function ResultView({ result, onReset }) {
  const [consultation, setConsultation] = useState({ name: "", email: result.email, message: "" });
  const [notice, setNotice] = useState("");

  const download = (filename, content) => {
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const saveReport = () => {
    download(`career-report-${result.rank}.txt`, reportText(result));
    track("report_download", { leadId: result.id, rank: result.rank });
  };

  const shareReport = async () => {
    const text = `キャリア現在地診断は${result.rank}ランク・${result.typeName}でした。`;
    try {
      if (navigator.share) await navigator.share({ title: "キャリア現在地診断", text, url: window.location.origin });
      else await navigator.clipboard.writeText(`${text} ${window.location.origin}`);
      setNotice(navigator.share ? "共有画面を開きました。" : "共有文をコピーしました。");
      track("result_share", { leadId: result.id, rank: result.rank });
    } catch {
      setNotice("共有をキャンセルしました。");
    }
  };

  const requestConsultation = (event) => {
    event.preventDefault();
    if (!consultation.name.trim() || !consultation.email.trim() || !consultation.message.trim()) {
      setNotice("相談フォームをすべて入力してください。");
      return;
    }
    const body = [
      "無料相談を希望します。",
      "",
      `名前: ${consultation.name}`,
      `返信先: ${consultation.email}`,
      `診断結果: ${result.rank} / ${result.typeName}`,
      `現在の職種: ${result.role}`,
      "",
      "相談したいこと:",
      consultation.message,
    ].join("\n");
    track("consultation_intent", { leadId: result.id, rank: result.rank });
    if (contactEmail) {
      window.location.href = `mailto:${contactEmail}?subject=${encodeURIComponent("キャリア無料相談の希望")}&body=${encodeURIComponent(body)}`;
      setNotice("メールアプリを開きました。内容を確認して送信してください。");
    } else {
      download(`consultation-${result.id.slice(0, 8)}.txt`, body);
      setNotice("相談内容をファイルに保存しました。運営者の連絡先設定後、そのまま送れます。");
    }
  };

  return (
    <section className="result-section" id="result" aria-live="polite">
      <div className="result-lead reveal">
        <div>
          <p className="kicker light">YOUR CAREER SIGNAL</p>
          <p className="result-label">推定市場価値ランク</p>
          <div className="rank-line"><strong>{result.rank}</strong><span>{result.typeName}</span></div>
          <h2>{result.headline}</h2>
          <p>{result.summary}</p>
        </div>
        <div className="score-dial" style={{ "--score": `${result.score * 3.6}deg` }}>
          <div><strong>{result.score}</strong><span>/ 100</span></div>
        </div>
      </div>

      <div className="metric-row reveal delay-1">
        <article><span>想定年収レンジ</span><strong>{result.salaryRange}</strong></article>
        <article><span>行動緊急度</span><strong>{result.urgency}</strong></article>
        <article><span>現在の職種</span><strong>{result.role}</strong></article>
      </div>

      <div className="insight-grid">
        <article className="insight-card risk-card reveal delay-1">
          <p className="card-number">01 / RISK</p>
          <h3>このまま進んだ場合の詰まりどころ</h3>
          <p>{result.risk}</p>
        </article>
        <article className="insight-card reveal delay-2">
          <p className="card-number">02 / LEVERAGE</p>
          <h3>今伸ばすと効く武器</h3>
          <ul>{result.leverage.map((item) => <li key={item}>{item}</li>)}</ul>
        </article>
        <article className="insight-card reveal delay-2">
          <p className="card-number">03 / ROUTES</p>
          <h3>相性を検証したい職種</h3>
          <div className="role-tags">{result.roles.map((item) => <span key={item}>{item}</span>)}</div>
        </article>
      </div>

      <section className="action-plan reveal">
        <div className="section-copy">
          <p className="kicker">30 DAY ROUTE</p>
          <h2>迷う時間を、動く30日に変える。</h2>
          <p>全部を変える必要はありません。順番だけ決めて、小さく証拠をつくります。</p>
        </div>
        <ol>
          {result.actions.map((item, index) => (
            <li key={item}><span>WEEK {index + 1}</span><strong>{item}</strong></li>
          ))}
          <li><span>WEEK 4</span><strong>結果を振り返り、応募・学習・相談の次の一手をひとつ選ぶ</strong></li>
        </ol>
      </section>

      <div className="result-tools reveal">
        <button type="button" className="button secondary" onClick={saveReport}>結果を保存</button>
        <button type="button" className="button secondary" onClick={() => window.print()}>印刷 / PDF</button>
        <button type="button" className="button secondary" onClick={shareReport}>結果を共有</button>
      </div>

      <section className="consultation-panel reveal" id="consultation">
        <div className="consultation-copy">
          <p className="kicker light">NEXT CONVERSATION</p>
          <h2>診断を、あなた専用の転職ルートへ。</h2>
          <p>候補職種の絞り方、職務経歴書で見せる実績、最初の30日を相談用メモにまとめます。</p>
          <ul><li>相談内容の整理</li><li>診断結果を自動で添付</li><li>無理な勧誘を前提にしない</li></ul>
        </div>
        <form onSubmit={requestConsultation}>
          <label>お名前<input value={consultation.name} onChange={(e) => setConsultation({ ...consultation, name: e.target.value })} placeholder="山田 太郎" /></label>
          <label>返信先メール<input type="email" value={consultation.email} onChange={(e) => setConsultation({ ...consultation, email: e.target.value })} /></label>
          <label>相談したいこと<textarea rows="4" value={consultation.message} onChange={(e) => setConsultation({ ...consultation, message: e.target.value })} placeholder="今の職種から年収を上げるルートを知りたい" /></label>
          <button className="button coral" type="submit">{contactEmail ? "メールで無料相談を申し込む" : "相談内容をファイルにまとめる"}</button>
          <p className="microcopy">{contactEmail ? "メールアプリを開きます。送信前に内容を確認できます。" : "公開用の連絡先は未設定です。内容は端末に保存されます。"}</p>
        </form>
      </section>

      {notice && <div className="toast" role="status">{notice}</div>}
      <div className="reset-row"><button type="button" className="text-button" onClick={onReset}>回答を変えて再診断する</button></div>
    </section>
  );
}

export default function DiagnosisExperience() {
  const [answers, setAnswers] = useState({});
  const [step, setStep] = useState(0);
  const [errors, setErrors] = useState({});
  const [result, setResult] = useState(null);
  const [started, setStarted] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    document.documentElement.dataset.appReady = "true";
    try {
      const draft = JSON.parse(localStorage.getItem(DRAFT_KEY) || "{}");
      const savedHistory = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
      setAnswers(draft);
      setHistory(savedHistory);
    } catch {
      localStorage.removeItem(DRAFT_KEY);
    }
  }, []);

  useEffect(() => {
    if (Object.keys(answers).length) localStorage.setItem(DRAFT_KEY, JSON.stringify(answers));
  }, [answers]);

  const updateAnswer = (id, value) => {
    setAnswers((current) => ({ ...current, [id]: value }));
    setErrors((current) => ({ ...current, [id]: undefined }));
  };

  const begin = () => {
    setStarted(true);
    track("diagnosis_start");
    setTimeout(() => document.querySelector("#diagnosis")?.scrollIntoView({ behavior: "smooth" }), 20);
  };

  const next = () => {
    const found = validateStep(answers, step);
    if (Object.keys(found).length) {
      setErrors(found);
      return;
    }
    if (step < questionSteps.length - 1) {
      setStep(step + 1);
      setErrors({});
      document.querySelector("#diagnosis")?.scrollIntoView({ behavior: "smooth" });
      return;
    }
    const completed = buildDiagnosisResult(answers);
    const nextHistory = [completed, ...history.filter((item) => item.id !== completed.id)].slice(0, 5);
    setHistory(nextHistory);
    setResult(completed);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(nextHistory));
    localStorage.removeItem(DRAFT_KEY);
    track("diagnosis_complete", { leadId: completed.id, rank: completed.rank, type: completed.dominantType });
    setTimeout(() => document.querySelector("#result")?.scrollIntoView({ behavior: "smooth" }), 20);
  };

  const reset = () => {
    setAnswers({});
    setStep(0);
    setResult(null);
    setStarted(true);
    localStorage.removeItem(DRAFT_KEY);
    setTimeout(() => document.querySelector("#diagnosis")?.scrollIntoView({ behavior: "smooth" }), 20);
  };

  const stepQuestions = questions.filter((question) => questionSteps[step].includes(question.id));
  const progress = ((step + 1) / questionSteps.length) * 100;

  return (
    <>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="キャリア現在地診断 トップ"><span>CR</span><strong>キャリア現在地診断</strong></a>
        <nav><a href="#method">診断について</a><a href="#faq">よくある質問</a><button onClick={begin}>無料で診断</button></nav>
      </header>

      <main id="top">
        <section className="hero-section">
          <div className="hero-grid">
            <div className="hero-copy reveal">
              <p className="kicker">CAREER ROUTE CHECK / 03 MIN</p>
              <h1>今のままでいいのかを、<em>3分で言葉にする。</em></h1>
              <p className="hero-description">9つの回答から、市場価値の現在地、年収の目安、次に検証すべき職種、30日でやることまで一本のルートにします。</p>
              <div className="hero-actions"><button className="button primary" onClick={begin}>無料で現在地を診断する <span>↗</span></button><p>アカウント登録なし<br />回答はこの端末内に保存</p></div>
            </div>
            <div className="signal-card reveal delay-1" aria-hidden="true">
              <div className="signal-top"><span>CAREER SIGNAL</span><span>PREVIEW</span></div>
              <div className="preview-rank"><small>MARKET RANK</small><strong>B+</strong><span>68 / 100</span></div>
              <div className="signal-chart"><i></i><i></i><i></i><i></i><i></i><i></i></div>
              <div className="signal-footer"><span>想定年収<br /><strong>380〜490万</strong></span><span>次の一手<br /><strong>30日で設計</strong></span></div>
            </div>
          </div>
          <div className="trust-strip reveal delay-2"><span>市場価値ランク</span><span>想定年収レンジ</span><span>適職ルート</span><span>30日アクション</span></div>
        </section>

        <section className="problem-section">
          <p className="vertical-note">THE COST OF STAYING STILL</p>
          <div className="section-copy reveal"><p className="kicker">WHY NOW</p><h2>転職するかより先に、<br />自分の現在地を知る。</h2></div>
          <div className="problem-list">
            <article className="reveal"><span>01</span><h3>頑張りが市場価値に変わっていない</h3><p>忙しさと評価は別物。外でも伝わる実績に翻訳します。</p></article>
            <article className="reveal delay-1"><span>02</span><h3>次の職種を感覚だけで選んでいる</h3><p>強み・環境・動機の組み合わせから候補を絞ります。</p></article>
            <article className="reveal delay-2"><span>03</span><h3>不安はあるのに、最初の一歩が曖昧</h3><p>結果を30日単位の行動に分解し、迷いを減らします。</p></article>
          </div>
        </section>

        <section className={`diagnosis-section ${started ? "is-open" : ""}`} id="diagnosis">
          {!started ? (
            <div className="diagnosis-gate reveal"><p className="kicker light">READY WHEN YOU ARE</p><h2>答えは、9つの質問の先に。</h2><button className="button coral" onClick={begin}>診断をはじめる</button></div>
          ) : !result ? (
            <div className="diagnosis-panel">
              <div className="progress-meta"><span>STEP {String(step + 1).padStart(2, "0")} / {String(questionSteps.length).padStart(2, "0")}</span><span>{Math.round(progress)}%</span></div>
              <div className="progress-track"><i style={{ width: `${progress}%` }} /></div>
              <div className="step-heading"><p className="kicker light">YOUR ANSWER</p><h2>{["まず、今の立ち位置から。", "どんな進め方が合う？", "あなたの武器はどれ？", "何を変えたい？", "力が出る未来を描く。", "結果を保存する準備。 "][step]}</h2></div>
              <div className="step-fields">{stepQuestions.map((question) => <QuestionField key={question.id} question={question} value={answers[question.id] || ""} error={errors[question.id]} onChange={updateAnswer} />)}</div>
              <div className="step-actions">
                {step > 0 && <button className="text-button light" onClick={() => setStep(step - 1)}>← 戻る</button>}
                <button className="button coral" onClick={next}>{step === questionSteps.length - 1 ? "診断結果を見る" : "次の質問へ"} <span>→</span></button>
              </div>
            </div>
          ) : null}
        </section>

        {result && <ResultView result={result} onReset={reset} />}

        <section className="method-section" id="method">
          <div className="section-copy reveal"><p className="kicker">HOW IT WORKS</p><h2>占いではなく、<br />意思決定のたたき台。</h2><p>働き方、強み、動機、悩み、環境の回答を3タイプの傾向に集約し、行動に変換します。</p></div>
          <div className="method-visual reveal delay-1"><div><span>INPUT</span><strong>9 answers</strong></div><b>→</b><div><span>SIGNAL</span><strong>3 patterns</strong></div><b>→</b><div><span>ROUTE</span><strong>30 days</strong></div></div>
          <p className="method-note">年収レンジは回答から算出する簡易推定です。実際の求人、地域、経験年数、雇用条件によって変わります。</p>
        </section>

        {history.length > 0 && (
          <section className="history-section">
            <div><p className="kicker">ON THIS DEVICE</p><h2>最近の診断</h2></div>
            <div className="history-list">{history.slice(0, 3).map((item) => <button key={item.id} onClick={() => { setResult(item); setStarted(true); }}><strong>{item.rank}</strong><span>{item.typeName}<small>{new Date(item.createdAt).toLocaleDateString("ja-JP")}</small></span></button>)}</div>
          </section>
        )}

        <section className="faq-section" id="faq">
          <div className="section-copy"><p className="kicker">FAQ</p><h2>よくある質問</h2></div>
          <div className="faq-list">
            <details><summary>診断結果は正確ですか？</summary><p>回答傾向を整理する簡易診断です。採用可否や年収を保証するものではなく、求人調査や専門家への相談前のたたき台として使ってください。</p></details>
            <details><summary>入力した内容はどこに保存されますか？</summary><p>公開版ではブラウザのローカルストレージにのみ保存します。サーバーへ自動送信しません。ブラウザのデータ削除で消去できます。</p></details>
            <details><summary>転職する気がなくても使えますか？</summary><p>使えます。現在地と伸ばすべき武器を確認するための診断なので、社内異動や学び直しの整理にも利用できます。</p></details>
          </div>
        </section>

        <section className="closing-section"><p className="kicker light">START WHERE YOU ARE</p><h2>未来を決める前に、<br />現在地を測ろう。</h2><button className="button coral" onClick={begin}>3分で無料診断する <span>↗</span></button></section>
      </main>

      <footer><a className="brand footer-brand" href="#top"><span>CR</span><strong>キャリア現在地診断</strong></a><p>© 2026 Career Route Check</p><p>本サービスはキャリア選択の参考情報を提供する簡易診断です。</p></footer>
      {!started && <button className="mobile-cta" onClick={begin}>無料で診断する <span>↗</span></button>}
    </>
  );
}
