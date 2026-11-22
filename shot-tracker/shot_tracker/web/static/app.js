"use strict";
// Shot Tracker front end: plain JS, no build step.
// Views: #/ (home: upload + history) and #/s/<id> (one session).

const $app = document.getElementById("app");
let pollTimer = null;

// ---------- helpers ----------------------------------------------------
const h = (tag, attrs = {}, ...kids) => {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) el.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat()) if (kid != null && kid !== false) el.append(kid);
  return el;
};

async function api(path, opts = {}) {
  const res = await fetch(path, opts);
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = (await res.json()).detail || msg; } catch (_) {}
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return res.json();
}

const fmt = (v, d = 1) => (v == null || Number.isNaN(v) ? "–" : Number(v).toFixed(d));
const signed = (v, d = 1) => (v == null ? "–" : (v > 0 ? "+" : "") + Number(v).toFixed(d));
const dateStr = (ts) => new Date(ts * 1000).toLocaleString("zh-TW", { month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit" });
const STATUS = { uploaded: "上傳完成", preparing: "轉檔中", ready: "待標記籃框", queued: "排隊中", analyzing: "分析中", done: "完成", error: "錯誤" };
const MISS = { short: "偏短", long: "偏長", rim_out: "其他" };

function store(key, value) {
  try {
    if (value === undefined) return JSON.parse(localStorage.getItem(key));
    localStorage.setItem(key, JSON.stringify(value));
  } catch (_) { return null; }
}

function stopPolling() { if (pollTimer) clearTimeout(pollTimer); pollTimer = null; }

// ---------- router -----------------------------------------------------
function route() {
  stopPolling();
  const m = location.hash.match(/^#\/s\/([0-9a-f]{12})/);
  if (m) showSession(m[1]); else showHome();
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", route);

// ---------- home -------------------------------------------------------
async function showHome() {
  const fileInput = h("input", { type: "file", accept: "video/*", class: "hidden", onchange: (e) => upload(e.target.files[0]) });
  const progress = h("div", { class: "card hidden" },
    h("p", { class: "step" }, "上傳中…"), h("div", { class: "bar" }, h("i")), h("p", { class: "muted" }, ""));
  const list = h("div", { class: "list" }, h("p", { class: "muted" }, "載入中…"));

  $app.replaceChildren(
    h("h1", {}, "投籃練習分析"),
    h("p", { class: "muted" }, "從側面拍攝投籃影片，上傳後標記籃框，就能看到每一球的弧度、落點和命中率。"),
    h("div", { class: "stack", style: "margin-top:14px" },
      h("button", { class: "btn primary", onclick: () => fileInput.click() }, "＋ 上傳投籃影片"),
    ),
    fileInput, progress,
    h("details", { class: "card" },
      h("summary", {}, h("b", {}, "拍攝小提醒")),
      h("ul", { class: "advice", style: "margin-top:8px" },
        h("li", {}, "手機用腳架固定在投籃方向的正側面"),
        h("li", {}, "出手點和籃框都要在畫面內"),
        h("li", {}, "橫拍、60fps 以上；慢動作影片也可以"),
      )),
    h("h2", {}, "練習紀錄"), list,
  );

  function upload(file) {
    if (!file) return;
    const bar = progress.querySelector("i");
    const note = progress.querySelector(".muted");
    progress.classList.remove("hidden");
    const fd = new FormData();
    fd.append("file", file);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/sessions");
    xhr.upload.onprogress = (e) => {
      if (!e.lengthComputable) return;
      bar.style.width = `${(100 * e.loaded) / e.total}%`;
      note.textContent = `${(e.loaded / 1e6).toFixed(0)} / ${(e.total / 1e6).toFixed(0)} MB`;
    };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) location.hash = `#/s/${JSON.parse(xhr.responseText).id}`;
      else { note.textContent = `上傳失敗：${xhr.responseText}`; }
    };
    xhr.onerror = () => { note.textContent = "上傳失敗：連不到電腦，請確認在同一個 Wi-Fi。"; };
    xhr.send(fd);
  }

  try {
    const sessions = await api("/api/sessions");
    if (!sessions.length) {
      list.replaceChildren(h("div", { class: "card empty muted" }, "還沒有紀錄，先上傳一段影片吧。"));
      return;
    }
    list.replaceChildren(h("div", { class: "card" }, sessions.map((s) => {
      const sm = s.summary;
      const right = s.status === "done" && sm && sm.shots
        ? h("div", { style: "text-align:right" }, h("div", { class: "pct" }, `${fmt(sm.fg_pct, 0)}%`), h("div", { class: "muted" }, `${sm.makes}/${sm.shots}`))
        : h("span", { class: `badge ${s.status}` }, STATUS[s.status] || s.status);
      return h("a", { href: `#/s/${s.id}` },
        h("div", { style: "min-width:0" }, h("div", { class: "name" }, s.name || "未命名"), h("div", { class: "muted" }, dateStr(s.created))),
        right);
    })));
  } catch (e) {
    list.replaceChildren(h("div", { class: "card muted" }, `讀取失敗：${e.message}`));
  }
}

// ---------- session ----------------------------------------------------
async function showSession(id, opts = {}) {
  let s;
  try { s = await api(`/api/sessions/${id}`); }
  catch (e) { $app.replaceChildren(h("div", { class: "card" }, `找不到這筆紀錄：${e.message}`), h("a", { class: "btn", href: "#/" }, "回首頁")); return; }

  const title = h("h1", {}, s.name || "未命名");
  if (["uploaded", "preparing", "queued", "analyzing"].includes(s.status)) {
    $app.replaceChildren(title, waitingCard(s));
    pollTimer = setTimeout(() => showSession(id), 1000);
  } else if (s.status === "ready" || opts.repick) {
    $app.replaceChildren(title, rimPicker(s));
  } else if (s.status === "done") {
    $app.replaceChildren(title, ...(await results(s)));
  } else {
    $app.replaceChildren(title,
      h("div", { class: "card" }, h("p", { class: "miss" }, s.error || "發生錯誤")),
      s.video ? h("button", { class: "btn primary", onclick: () => showSession(id, { repick: true }) }, "重新標記籃框再試一次") : null,
      h("div", { style: "height:10px" }), deleteButton(s));
  }
}

function waitingCard(s) {
  const label = { uploaded: "準備轉檔…", preparing: "影片轉檔中…", queued: "排隊中…" }[s.status]
    || (s.stage === "rendering" ? "產生標註影片中…" : "追蹤籃球中…");
  const pct = Math.round(100 * (s.progress || 0));
  return h("div", { class: "card", style: "text-align:center" },
    h("div", { class: "spinner" }), h("p", { class: "step" }, label),
    s.status === "analyzing" ? h("div", {}, h("div", { class: "bar" }, h("i", { style: `width:${pct}%` })), h("p", { class: "muted" }, `${pct}%`)) : null,
    h("p", { class: "muted" }, "可以先關掉這頁，分析會在電腦上繼續進行。"));
}

// ---------- rim picker ---------------------------------------------------
// 1) tap near the rim  2) in the magnified view tap left edge, then right edge
function rimPicker(s) {
  const { width: W, height: H, duration } = s.video;
  const canvas = h("canvas", { width: W, height: H, "aria-label": "影片畫面，點選籃框位置" });
  const ctx = canvas.getContext("2d");
  const img = new Image();
  const stepEl = h("p", { class: "step" });
  const hint = h("p", { class: "muted" });
  const slider = h("input", { type: "range", min: 0, max: Math.max(0, duration - 0.1).toFixed(2), step: 0.1, value: 0, "aria-label": "選擇畫面時間" });
  const speedSel = h("select", { "aria-label": "影片速度" },
    h("option", { value: "" }, "自動偵測（建議）"),
    h("option", { value: "1" }, "正常速度"),
    h("option", { value: "0.25" }, "慢動作 1/4（120fps 錄製）"),
    h("option", { value: "0.125" }, "慢動作 1/8（240fps 錄製）"));
  const resetBtn = h("button", { class: "btn", onclick: () => setStep(0) }, "重新選");
  const goBtn = h("button", { class: "btn primary", disabled: true, onclick: submit }, "開始分析");
  const last = store("lastRim");
  const lastBtn = last && last.W === W && last.H === H
    ? h("button", { class: "btn", onclick: () => { pts = [[last.rim[0], last.rim[1]], [last.rim[2], last.rim[3]]]; setStep(3); } }, "使用上次的籃框位置")
    : null;

  let step = 0;       // 0 tap near rim, 1 left edge, 2 right edge, 3 confirm
  let zoom = null;    // {x, y, size} crop in video px
  let pts = [];

  function loadFrame() {
    img.onload = draw;
    img.src = `/api/sessions/${s.id}/frame.jpg?t=${slider.value}`;
  }
  slider.addEventListener("change", loadFrame);

  function setStep(n) {
    step = n;
    if (n === 0) { pts = []; zoom = null; }
    stepEl.innerHTML = [
      "步驟 1：點一下<b>籃框</b>的位置",
      "步驟 2：點籃框的<b>左邊緣</b>",
      "步驟 3：點籃框的<b>右邊緣</b>",
      "確認黃線剛好橫跨籃框",
    ][n];
    hint.textContent = n === 0 ? "如果籃框被擋住，可以拖動下方滑桿換一個畫面。"
      : n < 3 ? "已放大畫面，點在籃框鐵圈最外側的位置。" : "黃線的長度會用來換算真實距離，越準確數據越準。";
    goBtn.disabled = n !== 3;
    draw();
  }

  function draw() {
    if (!img.complete || !img.naturalWidth) return;
    if (zoom && step < 3) {
      canvas.width = canvas.height = 600;
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(img, zoom.x, zoom.y, zoom.size, zoom.size, 0, 0, 600, 600);
      const k = 600 / zoom.size;
      ctx.strokeStyle = "rgba(255,255,255,.35)"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(300, 0); ctx.lineTo(300, 600); ctx.moveTo(0, 300); ctx.lineTo(600, 300); ctx.stroke();
      for (const [x, y] of pts) dot((x - zoom.x) * k, (y - zoom.y) * k, 9);
    } else {
      canvas.width = W; canvas.height = H;
      ctx.drawImage(img, 0, 0, W, H);
      if (pts.length === 2) {
        ctx.strokeStyle = "#ffd400"; ctx.lineWidth = Math.max(2, W / 400);
        ctx.beginPath(); ctx.moveTo(...pts[0]); ctx.lineTo(...pts[1]); ctx.stroke();
        pts.forEach(([x, y]) => dot(x, y, Math.max(4, W / 250)));
      }
    }
  }
  function dot(x, y, r) {
    ctx.fillStyle = "#ffd400"; ctx.strokeStyle = "#000"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(x, y, r, 0, 2 * Math.PI); ctx.fill(); ctx.stroke();
  }

  canvas.addEventListener("click", (e) => {
    const r = canvas.getBoundingClientRect();
    const cx = ((e.clientX - r.left) / r.width) * canvas.width;
    const cy = ((e.clientY - r.top) / r.height) * canvas.height;
    if (step === 0) {
      const size = Math.round(Math.max(80, Math.min(W, H) * 0.25));
      zoom = {
        x: Math.round(Math.min(Math.max(0, cx - size / 2), W - size)),
        y: Math.round(Math.min(Math.max(0, cy - size / 2), H - size)),
        size,
      };
      setStep(1);
    } else if (step === 1 || step === 2) {
      pts.push([zoom.x + (cx / 600) * zoom.size, zoom.y + (cy / 600) * zoom.size]);
      setStep(step === 1 ? 2 : 3);
    }
  });

  async function submit() {
    goBtn.disabled = true;
    const rim = [...pts[0], ...pts[1]].map((v) => Math.round(v * 10) / 10);
    store("lastRim", { W, H, rim });
    try {
      await api(`/api/sessions/${s.id}/analyze`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rim, speed: speedSel.value ? Number(speedSel.value) : null }),
      });
      showSession(s.id);
    } catch (e) { hint.textContent = `無法開始分析：${e.message}`; goBtn.disabled = false; }
  }

  setStep(0);
  loadFrame();
  return h("div", {},
    h("div", { class: "card" }, stepEl, h("div", { class: "picker" }, canvas), hint,
      h("label", { class: "muted" }, "畫面時間", slider)),
    h("div", { class: "row" }, resetBtn, goBtn),
    lastBtn ? h("div", { style: "margin-top:10px" }, lastBtn) : null,
    h("details", { class: "card" }, h("summary", {}, "進階：影片速度"),
      h("p", { class: "muted" }, "程式會用重力自動判斷影片是不是慢動作。自動判斷不準時再手動指定。"), speedSel),
    h("p", { class: "muted" }, `影片 ${W}×${H}、${s.video.fps} fps、${fmt(duration, 1)} 秒`),
  );
}

// ---------- results ----------------------------------------------------
async function results(s) {
  const base = `/api/sessions/${s.id}/files`;
  const report = await api(`${base}/report.json`);
  const sm = report.summary;
  const shots = report.shots;
  const fps = s.video.fps || 30;

  if (!sm.shots) {
    return [
      h("div", { class: "card" }, h("p", { class: "step" }, "沒有偵測到投籃"),
        h("p", { class: "muted" }, "可能原因：籃框標記錯誤、球太小或顏色和背景太接近、出手點不在畫面內。")),
      h("img", { class: "result-img", src: `${base}/overlay.png`, alt: "軌跡疊圖" }),
      h("div", { style: "height:10px" }),
      h("button", { class: "btn", onclick: () => showSession(s.id, { repick: true }) }, "重新標記籃框"),
      h("div", { style: "height:10px" }), deleteButton(s),
    ];
  }

  const video = h("video", { src: `${base}/annotated.mp4`, poster: `${base}/overlay.png`, controls: true, playsinline: true, preload: "metadata" });
  const warnings = [];
  if (sm.video_speed && sm.video_speed !== 1) warnings.push(`偵測到影片播放速度是真實時間的 ×${fmt(sm.video_speed, 2)}，數據已自動校正。`);
  const g = sm.gravity_ratio_median;
  if (g && (g < 0.8 || g > 1.25)) warnings.push("拍攝角度可能不是正側面（或籃框標記不準），角度和深度的數字僅供參考；進球判定不受影響。");

  const tile = (label, value, unit, ideal) => h("div", { class: "tile" },
    h("div", { class: "label" }, label), h("div", { class: "value" }, value, h("small", {}, unit)),
    ideal ? h("div", { class: "ideal" }, ideal) : null);
  const mt = sm.miss_types || {};

  return [
    h("div", { class: "card hero" },
      h("div", { class: "big" }, `${fmt(sm.fg_pct, 0)}%`),
      h("div", { class: "sub" }, `${sm.makes} / ${sm.shots} 進球`),
      h("p", { class: "legend" }, `失手：偏短 ${mt.short || 0}・偏長 ${mt.long || 0}・其他 ${mt.rim_out || 0}`)),
    ...warnings.map((w) => h("div", { class: "warn" }, w)),
    h("div", { class: "tiles" },
      tile("入框角度", fmt(sm.entry_angle_deg.mean), `° ±${fmt(sm.entry_angle_deg.std)}`, "理想 43–47°"),
      tile("落點深度", signed(sm.depth_cm.mean), ` cm ±${fmt(sm.depth_cm.std)}`, "理想 +5～+8 cm"),
      tile("出手角度", fmt(sm.release_angle_deg.mean), `° ±${fmt(sm.release_angle_deg.std)}`),
      tile("最高點", fmt(sm.apex_height_cm.mean, 0), " cm", "離地高度")),
    h("h2", {}, "建議"),
    h("div", { class: "card" }, h("ul", { class: "advice" }, (sm.advice || []).map((t) => h("li", {}, t)))),
    h("h2", {}, "標註影片"), video,
    h("p", { class: "muted" }, "點下方表格的任一球，影片會跳到那一球。"),
    h("h2", {}, "每一球"),
    h("div", { class: "table-wrap" }, h("table", {},
      h("thead", {}, h("tr", {}, ["#", "結果", "入框°", "深度", "出手°", "最高"].map((t) => h("th", {}, t)))),
      h("tbody", {}, shots.map((sh) => h("tr", {
        onclick: () => { video.currentTime = Math.max(0, sh.release_frame / fps - 0.5); video.play(); video.scrollIntoView({ behavior: "smooth", block: "center" }); },
      },
        h("td", {}, sh.id),
        h("td", { class: sh.result === "make" ? "make" : sh.result === "miss" ? "miss" : "" },
          sh.result === "make" ? "進" : sh.result === "miss" ? `不進${sh.miss_type ? "・" + MISS[sh.miss_type] : ""}` : "?"),
        h("td", {}, fmt(sh.entry_angle_deg)), h("td", {}, signed(sh.depth_cm)),
        h("td", {}, fmt(sh.release_angle_deg)), h("td", {}, fmt(sh.apex_height_cm, 0))))))),
    h("h2", {}, "軌跡疊圖"),
    h("img", { class: "result-img", src: `${base}/overlay.png`, alt: "所有投籃軌跡，綠色是進球，紅色是不進" }),
    h("p", { class: "legend" }, h("span", { class: "make" }, "綠色＝進"), "　", h("span", { class: "miss" }, "紅色＝不進")),
    h("div", { class: "stack", style: "margin-top:20px" },
      h("a", { class: "btn", href: `${base}/shots.csv`, download: `${s.name || "shots"}.csv` }, "下載數據（CSV）"),
      h("button", { class: "btn", onclick: () => showSession(s.id, { repick: true }) }, "重新標記籃框"),
      deleteButton(s)),
  ];
}

function deleteButton(s) {
  return h("button", {
    class: "btn danger",
    onclick: async () => {
      if (!confirm("確定要刪除這筆紀錄和影片嗎？")) return;
      try { await api(`/api/sessions/${s.id}`, { method: "DELETE" }); location.hash = "#/"; }
      catch (e) { alert(e.message); }
    },
  }, "刪除這筆紀錄");
}

route();
