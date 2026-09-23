// UI: เลือกข้อ/ขั้น, ช่องเติมคำ, editor, ส่งโค้ดไปตรวจ, แสดงผล
(() => {
  const Q = window.QUESTIONS;
  const LV = window.LEVEL_INFO;
  const $ = (id) => document.getElementById(id);
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // ─────────────── storage (ถ้าเบราว์เซอร์ไม่ให้ใช้ ก็ทำงานต่อได้แค่ไม่จำ)
  const KEY = "async-pretest-gym-v1";
  let store = { progress: {}, drafts: {}, pos: null, briefClosed: false };
  try { Object.assign(store, JSON.parse(localStorage.getItem(KEY)) || {}); } catch (e) {}
  let saveTimer = null;
  const save = () => {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} }, 250);
  };
  const isDone = (qi, li) => !!(store.progress[Q[qi].id] || [])[li];
  const setDone = (qi, li) => {
    const arr = store.progress[Q[qi].id] || [false, false, false, false];
    arr[li] = true;
    store.progress[Q[qi].id] = arr;
    save();
  };
  const draftKey = () => `${Q[cur.q].id}-${cur.l}`;

  // ─────────────── syntax highlight
  const KW = new Set("False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield".split(" "));
  const BI = new Set("print len range sorted list dict set tuple str int float bool sum min max enumerate zip isinstance type super repr abs any all map filter open".split(" "));
  const TOK = /(#[^\n]*)|((?:[rRbBfFuU]{1,2})?(?:"""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|"(?:[^"\\\n]|\\.)*"?|'(?:[^'\\\n]|\\.)*'?))|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z0-9_]*)/g;

  function highlight(src) {
    let out = "", last = 0, prev = "";
    src.replace(TOK, (m, com, str, num, id, off) => {
      out += esc(src.slice(last, off));
      last = off + m.length;
      let cls = "";
      if (com) cls = "com";
      else if (str) cls = "str";
      else if (num) cls = "num";
      else if (KW.has(id)) cls = "kw";
      else if (prev === "def" || prev === "class") cls = "def";
      else if (BI.has(id)) cls = "bi";
      out += cls ? `<span class="tok-${cls}">${esc(m)}</span>` : esc(m);
      prev = id || "";
      return m;
    });
    return out + esc(src.slice(last));
  }

  // ─────────────── state
  let cur = { q: 0, l: 0 };
  let mode = null;          // "cloze" | "editor"
  let blanks = [];          // cloze: [{answers, input}]
  let template = "";
  let textarea = null, pre = null;
  let hintShown = 0;
  let runLines = [];
  let lastErrLine = null;

  const runner = new PyRunner({
    onStatus(s, msg) {
      const el = $("py-status");
      el.dataset.s = s;
      el.textContent = s === "ready" ? "Python พร้อม" : s === "fatal" ? "โหลด Python ไม่สำเร็จ" : "กำลังโหลด Python…";
      $("btn-run").disabled = s !== "ready";
      if (s === "ready") $("run-msg").textContent = "พร้อมตรวจ";
      if (s === "fatal") $("run-msg").textContent = "โหลด Pyodide ไม่ได้ (" + msg + ") — ครั้งแรกต้องต่ออินเทอร์เน็ต ลองรีเฟรชหน้า";
    },
    onEmit(ev) {
      if (ev.event === "run-start") { runLines = []; $("console").innerHTML = ""; }
      else if (ev.event === "line") { runLines.push(ev); appendLine(ev); }
      else if (ev.event === "run-end") { $("run-time").textContent = `รวม ${ev.t.toFixed(2)} วิ`; }
    },
  });

  // ─────────────── rail + tabs + brief
  function renderRail() {
    const rail = $("rail");
    rail.innerHTML = `<div class="label">โจทย์</div>` + Q.map((q, i) => {
      const done = [0, 1, 2, 3].map((l) => isDone(i, l));
      return `<button class="q-link${done.every(Boolean) ? " all-done" : ""}" data-q="${i}" aria-current="${i === cur.q}" type="button">
        <span class="n">${q.num}</span><span class="t">${esc(q.title)}</span>
        <span class="pips">${done.map((d) => `<i class="${d ? "done" : ""}"></i>`).join("")}</span>
      </button>`;
    }).join("") + `<div class="foot">แต่ละข้อมี 4 ขั้น ยากขึ้นเรื่อย ๆ จนถึงขั้น “เหมือนสอบ” ที่ต้องเขียนเองทั้งไฟล์</div>`;
    const total = Q.length * 4;
    const passed = Q.reduce((s, _, i) => s + [0, 1, 2, 3].filter((l) => isDone(i, l)).length, 0);
    $("meter-text").textContent = `${passed}/${total}`;
    $("meter-fill").style.width = (passed / total * 100) + "%";
  }

  function renderTabs() {
    $("levels").innerHTML = LV.map((lv, i) => `
      <button class="lvl${isDone(cur.q, i) ? " done" : ""}" role="tab" aria-selected="${i === cur.l}" data-l="${i}" type="button">
        <span class="k">ขั้น ${i + 1}</span><span class="nm">${lv.name}</span>
        <span class="steps">${[0, 1, 2, 3].map((k) => `<i class="${k <= i ? "on" : ""}"></i>`).join("")}</span>
      </button>`).join("");
    $("level-desc").textContent = LV[cur.l].desc;
  }

  function renderBrief() {
    const q = Q[cur.q];
    $("q-kicker").textContent = `ข้อ ${q.num} · ${q.topic}`;
    $("q-title").textContent = q.title;
    $("q-points").textContent = `${q.points} คะแนน`;
    $("q-brief").innerHTML = q.brief;
    $("q-output").textContent = q.output;
    $("q-rubric").innerHTML = q.rubric.map(([p, t]) => `<li><b>${p}</b><span>${esc(t)}</span></li>`).join("");
    $("brief").classList.toggle("collapsed", !!store.briefClosed);
    $("brief-head").setAttribute("aria-expanded", String(!store.briefClosed));
  }

  // ─────────────── code area
  const BLANK = /⟦([^⟧]*)⟧/g;
  const norm = (s) => s.replace(/\s+/g, "").replace(/'/g, '"');

  function setGutter(n) {
    $("gutter").innerHTML = Array.from({ length: n }, (_, i) =>
      i + 1 === lastErrLine ? `<span class="err">${i + 1}</span>` : String(i + 1)).join("\n");
  }

  function renderCode() {
    const q = Q[cur.q];
    const src = q.levels[cur.l];
    const body = $("code-body");
    mode = cur.l < 2 ? "cloze" : "editor";
    lastErrLine = null;
    body.innerHTML = "";
    blanks = [];
    textarea = pre = null;

    if (mode === "cloze") {
      template = src;
      const saved = (store.drafts[draftKey()] || {}).values || [];
      let i = 0;
      const withMarks = src.replace(BLANK, (_, a) => {
        blanks.push({ answers: a.split("‖") });
        return "" + String.fromCharCode(0xE100 + i++) + "";
      });
      const el = document.createElement("pre");
      el.className = "cloze";
      el.innerHTML = highlight(withMarks).replace(/(.)/g, (_, c) => {
        const k = c.charCodeAt(0) - 0xE100;
        return `<input id="blank-${k}" data-i="${k}" type="text" spellcheck="false" autocomplete="off" autocapitalize="off" aria-label="ช่องที่ ${k + 1}">`;
      });
      body.appendChild(el);
      blanks.forEach((b, k) => {
        b.input = el.querySelector(`[data-i="${k}"]`);
        b.input.value = saved[k] || "";
        sizeBlank(b);
      });
      el.addEventListener("input", (e) => {
        const b = blanks[+e.target.dataset.i];
        if (!b) return;
        sizeBlank(b);
        b.input.classList.remove("good", "diff", "hinted");
        saveCloze();
        updateFill();
      });
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !(e.ctrlKey || e.metaKey)) {
          e.preventDefault();
          const k = +e.target.dataset.i;
          (blanks[k + 1] || blanks[0]).input.focus();
        }
      });
      setGutter(src.replace(/\n$/, "").split("\n").length);
      $("fill-count").hidden = false;
      updateFill();
    } else {
      const saved = store.drafts[draftKey()];
      const code = typeof saved === "string" ? saved : src;
      const wrap = document.createElement("div");
      wrap.className = "editor";
      pre = document.createElement("pre");
      textarea = document.createElement("textarea");
      textarea.id = "code-editor";
      textarea.spellcheck = false;
      textarea.setAttribute("autocomplete", "off");
      textarea.setAttribute("autocapitalize", "off");
      textarea.setAttribute("wrap", "off");
      textarea.setAttribute("aria-label", "เขียนโค้ด Python");
      textarea.value = code;
      wrap.append(pre, textarea);
      body.appendChild(wrap);
      syncEditor();
      textarea.addEventListener("input", () => {
        lastErrLine = null;
        syncEditor();
        store.drafts[draftKey()] = textarea.value;
        save();
      });
      textarea.addEventListener("keydown", editorKeys);
      $("fill-count").hidden = true;
    }
    hintShown = 0;
    $("hint-panel").hidden = true;
    $("solution-panel").hidden = true;
    $("btn-hint").textContent = "ใบ้";
    resetResults();
  }

  function sizeBlank(b) {
    const len = Math.max(b.answers[0].length, b.input.value.length, 2);
    b.input.style.width = len + "ch";
  }

  function saveCloze() {
    store.drafts[draftKey()] = { values: blanks.map((b) => b.input.value) };
    save();
  }

  function updateFill() {
    const filled = blanks.filter((b) => b.input.value.trim()).length;
    $("fill-count").textContent = `เติมแล้ว ${filled}/${blanks.length} ช่อง`;
  }

  function syncEditor() {
    pre.innerHTML = highlight(textarea.value) + "\n ";
    setGutter(textarea.value.split("\n").length);
    markErrLine();
  }

  function markErrLine() {
    const body = $("code-body");
    body.querySelectorAll(".line-err").forEach((n) => n.remove());
    if (!lastErrLine) return;
    const lh = parseFloat(getComputedStyle(body).lineHeight);
    const d = document.createElement("div");
    d.className = "line-err";
    d.style.cssText = `position:absolute;left:4px;right:4px;top:${14 + (lastErrLine - 1) * lh}px;height:${lh}px;z-index:0;pointer-events:none`;
    body.prepend(d);
    body.querySelectorAll("pre").forEach((p) => { p.style.position = "relative"; p.style.zIndex = 1; });
  }

  // editor: Tab ย่อหน้า, Enter คงย่อหน้า (+4 หลัง :), Backspace ลบทีละ 4 ช่อง
  function insertText(text) {
    textarea.focus();
    if (!document.execCommand || !document.execCommand("insertText", false, text)) {
      textarea.setRangeText(text, textarea.selectionStart, textarea.selectionEnd, "end");
      textarea.dispatchEvent(new Event("input"));
    }
  }

  function editorKeys(e) {
    const ta = textarea;
    const v = ta.value, s = ta.selectionStart, en = ta.selectionEnd;
    const lineStart = v.lastIndexOf("\n", s - 1) + 1;
    if (e.key === "Tab") {
      e.preventDefault();
      const multi = v.slice(s, en).includes("\n");
      if (!multi && !e.shiftKey) return insertText("    ");
      const blockEnd = v.indexOf("\n", en - (en > s && v[en - 1] === "\n" ? 1 : 0));
      const endIdx = blockEnd === -1 ? v.length : blockEnd;
      const block = v.slice(lineStart, endIdx);
      const lines = block.split("\n").map((ln) => e.shiftKey ? ln.replace(/^ {1,4}/, "") : "    " + ln);
      ta.setSelectionRange(lineStart, endIdx);
      insertText(lines.join("\n"));
      ta.setSelectionRange(lineStart, lineStart + lines.join("\n").length);
    } else if (e.key === "Enter" && !(e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      const line = v.slice(lineStart, s);
      let indent = line.match(/^ */)[0];
      if (/:\s*(#.*)?$/.test(line)) indent += "    ";
      insertText("\n" + indent);
    } else if (e.key === "Backspace" && s === en && s > lineStart) {
      const before = v.slice(lineStart, s);
      if (/^ +$/.test(before) && before.length % 4 === 0) {
        e.preventDefault();
        ta.setSelectionRange(s - 4, s);
        insertText("");
      }
    }
  }

  function currentCode() {
    if (mode === "editor") return textarea.value;
    let i = 0;
    return template.replace(BLANK, () => blanks[i++].input.value);
  }

  // ─────────────── hints / solution / reset
  $("btn-hint").addEventListener("click", () => {
    const q = Q[cur.q];
    if (mode === "cloze") {
      const b = blanks.find((b) => !b.answers.some((a) => norm(a) === norm(b.input.value)));
      if (!b) { $("run-msg").textContent = "ทุกช่องตรงกับเฉลยแล้ว ลองกดรันได้เลย"; return; }
      b.input.value = b.answers[0];
      sizeBlank(b);
      b.input.classList.remove("good", "diff");
      b.input.classList.add("hinted");
      b.input.focus();
      saveCloze();
      updateFill();
      return;
    }
    hintShown = Math.min(hintShown + 1, q.hints.length);
    $("hint-list").innerHTML = q.hints.slice(0, hintShown).map((h) => `<li>${esc(h)}</li>`).join("");
    $("hint-panel").hidden = false;
    $("btn-hint").textContent = hintShown < q.hints.length ? `ใบ้เพิ่ม (${hintShown}/${q.hints.length})` : `ใบ้ครบแล้ว`;
  });

  $("btn-solution").addEventListener("click", () => {
    const p = $("solution-panel");
    p.hidden = !p.hidden;
    $("solution-code").innerHTML = highlight(Q[cur.q].solution);
    $("btn-use").textContent = mode === "cloze" ? "เติมเฉลยทุกช่อง" : "ใส่ลงในช่องเขียนโค้ด";
  });

  $("btn-copy").addEventListener("click", () => {
    const text = Q[cur.q].solution;
    const btn = $("btn-copy");
    navigator.clipboard.writeText(text).then(() => { btn.textContent = "คัดลอกแล้ว"; },
      () => { const r = document.createRange(); r.selectNodeContents($("solution-code")); getSelection().removeAllRanges(); getSelection().addRange(r); btn.textContent = "เลือกข้อความไว้แล้ว กด Ctrl+C"; });
    setTimeout(() => { btn.textContent = "คัดลอก"; }, 2000);
  });

  $("btn-use").addEventListener("click", () => {
    if (mode === "cloze") {
      blanks.forEach((b) => { b.input.value = b.answers[0]; sizeBlank(b); b.input.classList.add("hinted"); });
      saveCloze();
      updateFill();
    } else {
      textarea.select();
      insertText(Q[cur.q].solution);
    }
  });

  let resetArmed = null;
  $("btn-reset").addEventListener("click", () => {
    const btn = $("btn-reset");
    if (!resetArmed) {
      btn.textContent = "กดอีกครั้งเพื่อล้าง";
      btn.classList.add("confirm");
      resetArmed = setTimeout(() => { btn.textContent = "เริ่มขั้นนี้ใหม่"; btn.classList.remove("confirm"); resetArmed = null; }, 3000);
      return;
    }
    clearTimeout(resetArmed);
    resetArmed = null;
    btn.textContent = "เริ่มขั้นนี้ใหม่";
    btn.classList.remove("confirm");
    delete store.drafts[draftKey()];
    save();
    renderCode();
  });

  // ─────────────── run + results
  function resetResults() {
    $("console").innerHTML = `<div class="empty">กด “รันและตรวจ” แล้วผลจาก print() จะขึ้นที่นี่ พร้อมเวลาที่แต่ละบรรทัดออกมา</div>`;
    $("timeline").hidden = true;
    $("run-time").textContent = "";
    $("checks").innerHTML = `<div class="placeholder">ยังไม่ได้ตรวจ</div>`;
    $("score").textContent = "";
    $("pass-banner").hidden = true;
  }

  function appendLine(ev) {
    const c = $("console");
    const d = document.createElement("div");
    d.className = "ln" + (ev.stream === "err" ? " err" : "");
    d.innerHTML = `<span class="ts">+${ev.t.toFixed(2)}s</span><span></span>`;
    d.lastChild.textContent = ev.text;
    c.appendChild(d);
    c.scrollTop = c.scrollHeight;
  }

  function renderTimeline(total) {
    const out = runLines.filter((l) => l.stream === "out").slice(0, 8);
    const tl = $("timeline");
    if (!out.length && total < 0.05) { tl.hidden = true; return; }
    const end = Math.max(total, ...out.map((l) => l.t));
    const max = Math.max(1, Math.ceil((end + 0.15) / 0.5) * 0.5);
    const step = max <= 4 ? 0.5 : 1;
    const pct = (t) => (t / max * 100).toFixed(2) + "%";
    let html = `<div class="track"><div class="axis"></div>`;
    for (let t = 0; t <= max + 1e-9; t += step) html += `<span class="tick" style="left:${pct(t)}">${t.toFixed(1)}s</span>`;
    html += `<span class="end" style="left:${pct(total)}" title="จบที่ ${total.toFixed(2)} วิ"></span>`;
    out.forEach((l) => {
      const label = l.text.length > 14 ? l.text.slice(0, 13) + "…" : l.text;
      html += `<span class="mark" style="left:${pct(l.t)}"><span>${esc(label)}</span></span>`;
    });
    tl.innerHTML = html + `</div>`;
    tl.hidden = false;
  }

  async function run() {
    if (!runner.ready || $("btn-run").disabled) return;
    if (mode === "cloze") {
      const empty = blanks.filter((b) => !b.input.value.trim());
      if (empty.length) {
        $("run-msg").textContent = `ยังว่างอยู่ ${empty.length} ช่อง`;
        empty[0].input.focus();
        return;
      }
    }
    const qi = cur.q, li = cur.l;
    const code = currentCode();
    $("btn-run").disabled = true;
    $("run-msg").textContent = "กำลังรันไฟล์และตรวจ… (โจทย์มีการรอเวลาจริง ใช้ไม่กี่วินาที)";
    $("pass-banner").hidden = true;
    $("console").innerHTML = "";
    $("checks").innerHTML = `<div class="placeholder">กำลังตรวจ…</div>`;
    $("score").textContent = "";
    runLines = [];
    const res = await runner.run(code, Q[qi].id);
    $("btn-run").disabled = !runner.ready;
    if (qi !== cur.q || li !== cur.l) return;   // เปลี่ยนข้อระหว่างรัน
    showResult(res, qi, li);
  }

  function showResult(res, qi, li) {
    const q = Q[qi];
    const tests = res.tests || [];
    const got = tests.filter((t) => t.ok).reduce((s, t) => s + t.pts, 0);
    const total = q.points;
    const allOk = tests.length > 0 && tests.every((t) => t.ok) && !res.error;

    if (!$("console").children.length) {
      $("console").innerHTML = `<div class="empty">${res.error && res.error.kind === "syntax" ? "ไฟล์ยังรันไม่ได้เพราะไวยากรณ์ผิด" : "ไฟล์นี้ไม่ได้ print อะไรออกมา"}</div>`;
    }
    renderTimeline(res.runTime || 0);

    let html = "";
    if (res.error) {
      const e = res.error;
      html += `<div class="error-box"><div><code>${esc(e.message)}</code>${e.line ? ` <span>(บรรทัด ${e.line})</span>` : ""}</div>${e.hint ? `<div class="h">→ ${esc(e.hint)}</div>` : ""}</div>`;
      lastErrLine = e.line || null;
    } else {
      lastErrLine = null;
    }
    if (res.lint && res.lint.length) html += `<div class="lint">${res.lint.map((n) => `<div>⚠ ${esc(n.text)}</div>`).join("")}</div>`;
    if (tests.length) {
      html += `<ul class="checks">` + tests.map((t) => `
        <li class="${t.ok ? "ok" : "no"}">
          <span class="ic">${t.ok ? "✓" : "✕"}</span>
          <div><div class="lbl">${esc(t.label)}</div>${t.detail ? `<div class="det">${esc(t.detail)}</div>` : ""}</div>
          <span class="p">${t.pts ? (t.ok ? `+${t.pts}` : `0/${t.pts}`) : "ต้องผ่าน"}</span>
        </li>`).join("") + `</ul>`;
      $("score").textContent = `${got}/${total}`;
    }
    $("checks").innerHTML = html || `<div class="placeholder">ไม่มีผลตรวจ</div>`;

    if (mode === "editor") syncEditor();
    else {
      setGutter(template.replace(/\n$/, "").split("\n").length);
      markErrLine();
      blanks.forEach((b) => {
        const match = b.answers.some((a) => norm(a) === norm(b.input.value));
        b.input.classList.remove("good", "diff");
        if (allOk || match) b.input.classList.add("good");
        else b.input.classList.add("diff");
      });
    }

    if (allOk) {
      setDone(qi, li);
      renderRail();
      renderTabs();
      const next = nextStep(qi, li);
      $("pass-title").textContent = `ผ่าน ขั้น ${li + 1} แล้ว!`;
      $("pass-text").textContent = next
        ? `ได้ ${got}/${total} คะแนน · ต่อไป: ข้อ ${Q[next.q].num} ขั้น ${next.l + 1} ${LV[next.l].name}`
        : `ได้ ${got}/${total} คะแนน · ผ่านครบทุกขั้นทุกข้อแล้ว`;
      $("btn-next").hidden = !next;
      $("pass-banner").hidden = false;
      $("run-msg").textContent = "ผ่านทุกข้อตรวจ";
    } else {
      const fails = tests.filter((t) => !t.ok).length;
      $("run-msg").textContent = res.error ? "มี error — ดูกล่องสีแดงในผลการตรวจ" : `ยังไม่ผ่าน ${fails} ข้อตรวจ`;
    }
  }

  function nextStep(qi, li) {
    if (li < 3) return { q: qi, l: li + 1 };
    if (qi < Q.length - 1) return { q: qi + 1, l: 0 };
    return null;
  }

  // ─────────────── navigation
  function go(qi, li) {
    cur = { q: qi, l: li };
    store.pos = cur;
    save();
    renderRail();
    renderTabs();
    renderBrief();
    renderCode();
  }

  const firstOpen = (qi) => { const l = [0, 1, 2, 3].find((l) => !isDone(qi, l)); return l === undefined ? 3 : l; };

  $("rail").addEventListener("click", (e) => {
    const b = e.target.closest("[data-q]");
    if (b) go(+b.dataset.q, firstOpen(+b.dataset.q));
  });
  $("levels").addEventListener("click", (e) => {
    const b = e.target.closest("[data-l]");
    if (b) go(cur.q, +b.dataset.l);
  });
  const toggleBrief = () => {
    store.briefClosed = !store.briefClosed;
    save();
    renderBrief();
  };
  $("brief-head").addEventListener("click", toggleBrief);
  $("brief-head").addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggleBrief(); } });
  $("btn-run").addEventListener("click", run);
  $("btn-next").addEventListener("click", () => { const n = nextStep(cur.q, cur.l); if (n) go(n.q, n.l); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); run(); }
  });

  // ─────────────── start
  const p = store.pos;
  if (p && Q[p.q] && p.l >= 0 && p.l < 4) go(p.q, p.l);
  else go(0, 0);
  runner.start();
})();
