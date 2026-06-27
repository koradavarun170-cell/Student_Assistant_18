import { useState, useRef, useEffect, useCallback } from "react";

function renderMarkdown(text) {
  if (!text) return "";
  const lines = text.split("\n");
  const out = [];
  let inOl = false, inUl = false;

  const closeList = () => {
    if (inUl) { out.push("</ul>"); inUl = false; }
    if (inOl) { out.push("</ol>"); inOl = false; }
  };

  const inlineFormat = (s) =>
    s
      .replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>")
      .replace(/\*\*(.+?)\*\*/g,     "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g,         "<em>$1</em>")
      .replace(/`(.+?)`/g,           "<code>$1</code>");

  lines.forEach((raw) => {
    const line = raw.trimEnd();

    // Headings
    const h3 = line.match(/^###\s+(.*)/);
    const h2 = line.match(/^##\s+(.*)/);
    const h1 = line.match(/^#\s+(.*)/);
    if (h3) { closeList(); out.push(`<h3>${inlineFormat(h3[1])}</h3>`); return; }
    if (h2) { closeList(); out.push(`<h2>${inlineFormat(h2[1])}</h2>`); return; }
    if (h1) { closeList(); out.push(`<h1>${inlineFormat(h1[1])}</h1>`); return; }

    const ol = line.match(/^\s*\d+[.)]\s+(.*)/);
    if (ol) {
      if (inUl) { out.push("</ul>"); inUl = false; }
      if (!inOl) { out.push('<ol>'); inOl = true; }
      out.push(`<li>${inlineFormat(ol[1])}</li>`);
      return;
    }

    const ul = line.match(/^\s*[\*\-•]\s+(.*)/);
    if (ul) {
      if (inOl) { out.push("</ol>"); inOl = false; }
      if (!inUl) { out.push('<ul>'); inUl = true; }
      out.push(`<li>${inlineFormat(ul[1])}</li>`);
      return;
    }

    if (line.trim() === "") {
      closeList();
      out.push("<br/>");
      return;
    }

    // Normal paragraph line
    closeList();
    out.push(`<p>${inlineFormat(line)}</p>`);
  });

  closeList();
  return out.join("");
}

function MarkdownBubble({ content, style }) {
  return (
    <div
      className="md-bubble"
      style={style}
      dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
    />
  );
}

const API_BASE = "http://13.232.86.221:8000";
// ─── Design tokens ────────────────────────────────────────────────────────────
const C = {
  bg:           "#F8F5F1",
  surface:      "#FFFFFF",
  surfaceAlt:   "#F2EEE9",
  border:       "#E4DDD6",
  borderStrong: "#C8BFB5",
  accent:       "#1A1612",
  accentSoft:   "#1A16120D",
  blue:         "#2563EB",
  blueSoft:     "#2563EB12",
  blueBorder:   "#BFCFEF",
  green:        "#16A34A",
  greenSoft:    "#16A34A12",
  greenBorder:  "#BBDFC8",
  red:          "#DC2626",
  redSoft:      "#DC262612",
  redBorder:    "#F5BFBF",
  amber:        "#B45309",
  amberSoft:    "#B4530912",
  amberBorder:  "#EDD5A3",
  textPrimary:  "#1A1612",
  textSecondary:"#6B5F54",
  textMuted:    "#A8998C",
};

const S = {
  app: {
    display: "flex",
    height: "100vh",
    background: C.bg,
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    color: C.textPrimary,
    overflow: "hidden",
  },
  // ── Sidebar ──
  sidebar: {
    width: "288px",
    minWidth: "288px",
    background: C.surface,
    borderRight: `1px solid ${C.border}`,
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  },
  sidebarTop: {
    padding: "20px 18px 16px",
    borderBottom: `1px solid ${C.border}`,
    flexShrink: 0,
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "18px",
  },
  brandMark: {
    width: "32px",
    height: "32px",
    borderRadius: "8px",
    background: C.accent,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "15px",
    flexShrink: 0,
  },
  brandName: {
    fontSize: "14px",
    fontWeight: "600",
    color: C.textPrimary,
    lineHeight: "1.2",
  },
  brandSub: {
    fontSize: "11px",
    color: C.textMuted,
  },
  fieldLabel: {
    fontSize: "10px",
    fontWeight: "600",
    letterSpacing: "0.8px",
    textTransform: "uppercase",
    color: C.textMuted,
    marginBottom: "6px",
    display: "block",
  },
  textInput: {
    width: "100%",
    height: "34px",
    background: C.surfaceAlt,
    border: `1px solid ${C.border}`,
    borderRadius: "8px",
    padding: "0 10px",
    fontSize: "13px",
    color: C.textPrimary,
    outline: "none",
    fontFamily: "inherit",
    boxSizing: "border-box",
  },
  sidebarBody: {
    flex: 1,
    overflowY: "auto",
    padding: "16px 18px",
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
  // ── Tabs ──
  tabs: {
    display: "flex",
    background: C.surfaceAlt,
    borderRadius: "8px",
    padding: "3px",
    gap: "2px",
  },
  tab: (active) => ({
    flex: 1,
    height: "28px",
    border: "none",
    borderRadius: "6px",
    fontSize: "12px",
    fontWeight: "500",
    cursor: "pointer",
    fontFamily: "inherit",
    transition: "all .15s",
    background: active ? C.surface : "transparent",
    color: active ? C.textPrimary : C.textMuted,
    boxShadow: active ? `0 1px 3px ${C.border}` : "none",
  }),
  // ── Upload tab ──
  dropZone: (over) => ({
    border: `1.5px dashed ${over ? C.blue : C.borderStrong}`,
    borderRadius: "10px",
    padding: "20px 12px",
    textAlign: "center",
    cursor: "pointer",
    background: over ? C.blueSoft : "transparent",
    transition: "all .15s",
  }),
  dzIcon: { fontSize: "22px", marginBottom: "6px" },
  dzText: { fontSize: "12px", color: C.textSecondary, lineHeight: "1.5" },
  dzHint: { fontSize: "10px", color: C.textMuted, marginTop: "3px" },
  fileCard: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "8px 10px",
    background: C.surfaceAlt,
    borderRadius: "8px",
    border: `1px solid ${C.border}`,
  },
  extBadge: (type) => {
    const map = {
      pdf:  { bg: C.redSoft,   color: C.red,   border: C.redBorder },
      docx: { bg: C.blueSoft,  color: C.blue,  border: C.blueBorder },
      doc:  { bg: C.blueSoft,  color: C.blue,  border: C.blueBorder },
      pptx: { bg: C.amberSoft, color: C.amber, border: C.amberBorder },
      ppt:  { bg: C.amberSoft, color: C.amber, border: C.amberBorder },
    };
    const t = map[type] || map.pdf;
    return {
      width: "30px", height: "30px", borderRadius: "6px",
      background: t.bg, border: `1px solid ${t.border}`,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: "9px", fontWeight: "700", color: t.color,
      textTransform: "uppercase", flexShrink: 0,
    };
  },
  fileName: {
    flex: 1, fontSize: "12px", color: C.textSecondary,
    overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
  },
  iconBtn: (danger) => ({
    background: "none", border: "none", cursor: "pointer",
    color: danger ? C.red : C.textMuted,
    padding: "3px", borderRadius: "4px",
    display: "flex", alignItems: "center",
    fontSize: "14px", flexShrink: 0,
    transition: "color .1s",
  }),
  primaryBtn: (disabled) => ({
    width: "100%", height: "34px", borderRadius: "8px",
    border: "none", background: disabled ? C.borderStrong : C.accent,
    color: "#fff", fontSize: "13px", fontWeight: "500",
    cursor: disabled ? "not-allowed" : "pointer",
    fontFamily: "inherit", transition: "opacity .15s",
    display: "flex", alignItems: "center", justifyContent: "center", gap: "6px",
    opacity: disabled ? 0.5 : 1,
  }),
  toast: (type) => ({
    display: "flex", alignItems: "center", gap: "7px",
    padding: "8px 10px", borderRadius: "8px", fontSize: "12px",
    background: type === "ok" ? C.greenSoft : C.redSoft,
    border: `1px solid ${type === "ok" ? C.greenBorder : C.redBorder}`,
    color: type === "ok" ? C.green : C.red,
  }),
  // ── Manage tab ──
  uploadedCard: {
    display: "flex", alignItems: "center", gap: "8px",
    padding: "8px 10px", background: C.surfaceAlt,
    borderRadius: "8px", border: `1px solid ${C.border}`,
    marginBottom: "5px",
  },
  dangerBtn: {
    background: "none", border: `1px solid ${C.redBorder}`,
    borderRadius: "6px", padding: "4px 9px",
    fontSize: "11px", fontWeight: "500", color: C.red,
    cursor: "pointer", fontFamily: "inherit", transition: "all .15s",
    display: "flex", alignItems: "center", gap: "4px", flexShrink: 0,
  },
  emptySmall: {
    textAlign: "center", padding: "20px 10px",
    fontSize: "12px", color: C.textMuted, lineHeight: "1.6",
  },
  sidebarFooter: {
    padding: "12px 18px",
    borderTop: `1px solid ${C.border}`,
    flexShrink: 0,
  },
  clearBtn: {
    width: "100%", height: "30px", background: "none",
    border: `1px solid ${C.border}`, borderRadius: "8px",
    color: C.textSecondary, fontSize: "12px",
    cursor: "pointer", fontFamily: "inherit", transition: "all .15s",
  },
  // ── Main ──
  main: { flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", background: C.bg },
  topbar: {
    padding: "13px 24px", borderBottom: `1px solid ${C.border}`,
    display: "flex", alignItems: "center", justifyContent: "space-between",
    background: C.surface, flexShrink: 0,
  },
  topbarTitle: { fontSize: "13px", fontWeight: "600", color: C.textPrimary },
  topbarSub:   { fontSize: "11px", color: C.textMuted, marginTop: "1px" },
  statusPill: {
    display: "flex", alignItems: "center", gap: "5px",
    padding: "4px 10px", borderRadius: "20px",
    background: C.greenSoft, border: `1px solid ${C.greenBorder}`,
  },
  statusDot: { width: "5px", height: "5px", borderRadius: "50%", background: C.green },
  statusText: { fontSize: "11px", color: C.green, fontWeight: "500" },
  messages: {
    flex: 1, overflowY: "auto", padding: "28px 24px",
    display: "flex", flexDirection: "column", gap: "20px",
  },
  // Empty state
  emptyState: {
    flex: 1, display: "flex", flexDirection: "column",
    alignItems: "center", justifyContent: "center",
    gap: "12px", textAlign: "center", padding: "40px 20px",
  },
  emptyRing: {
    width: "58px", height: "58px", borderRadius: "50%",
    border: `1.5px dashed ${C.borderStrong}`,
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: "24px",
  },
  emptyTitle: { fontSize: "15px", fontWeight: "600", color: C.textSecondary },
  emptyBody:  { fontSize: "13px", color: C.textMuted, lineHeight: "1.6", maxWidth: "280px" },
  chips: { display: "flex", gap: "6px", flexWrap: "wrap", justifyContent: "center", marginTop: "4px" },
  chip: {
    padding: "5px 12px", background: C.surface,
    border: `1px solid ${C.border}`, borderRadius: "20px",
    fontSize: "11px", color: C.textSecondary,
    cursor: "pointer", fontFamily: "inherit", transition: "all .15s",
  },
  // Messages
  msgUserWrap:  { display: "flex", justifyContent: "flex-end" },
  msgUser: {
    maxWidth: "68%", background: C.surface,
    border: `1px solid ${C.border}`, borderRadius: "12px 12px 3px 12px",
    padding: "11px 14px", fontSize: "13px", lineHeight: "1.6", color: C.textPrimary,
  },
  msgAI: { alignSelf: "flex-start", maxWidth: "88%", display: "flex", flexDirection: "column", gap: "10px" },
  msgBubble: {
    background: C.surface, border: `1px solid ${C.border}`,
    borderRadius: "3px 12px 12px 12px", padding: "14px 16px",
    fontSize: "13px", lineHeight: "1.75", color: C.textPrimary,
  },
  sources: { display: "flex", flexWrap: "wrap", gap: "5px" },
  sourceChip: {
    display: "flex", alignItems: "center", gap: "4px",
    padding: "3px 9px", background: C.blueSoft,
    border: `1px solid ${C.blueBorder}`, borderRadius: "20px",
    fontSize: "11px", color: C.blue,
  },
  msgError: {
    display: "flex", alignItems: "center", gap: "8px",
    padding: "10px 14px", background: C.redSoft,
    border: `1px solid ${C.redBorder}`, borderRadius: "8px",
    fontSize: "13px", color: C.red,
  },
  thinkingBubble: {
    alignSelf: "flex-start", display: "flex", alignItems: "center",
    gap: "10px", padding: "12px 16px", background: C.surface,
    border: `1px solid ${C.border}`, borderRadius: "3px 12px 12px 12px",
    fontSize: "13px", color: C.textMuted,
  },
  // Input
  inputArea: {
    padding: "16px 24px", borderTop: `1px solid ${C.border}`,
    background: C.surface, display: "flex", gap: "10px", alignItems: "flex-end",
    flexShrink: 0,
  },
  chatInput: {
    flex: 1, background: C.surfaceAlt, border: `1px solid ${C.border}`,
    borderRadius: "10px", padding: "10px 14px", color: C.textPrimary,
    fontSize: "13px", outline: "none", resize: "none",
    fontFamily: "inherit", lineHeight: "1.5",
    minHeight: "40px", maxHeight: "120px",
  },
  sendBtn: (disabled) => ({
    width: "40px", height: "40px", background: disabled ? C.borderStrong : C.accent,
    border: "none", borderRadius: "10px",
    display: "flex", alignItems: "center", justifyContent: "center",
    cursor: disabled ? "not-allowed" : "pointer", flexShrink: 0,
    fontSize: "16px", color: "#fff", transition: "all .15s",
    opacity: disabled ? 0.4 : 1,
  }),
};

// ─── Helpers ──────────────────────────────────────────────────────────────────
function getExt(name = "") { return name.split(".").pop().toLowerCase(); }

function ExtBadge({ name }) {
  const ext = getExt(name);
  return <div style={S.extBadge(ext)}>{ext}</div>;
}

function Toast({ status }) {
  if (!status) return null;
  return (
    <div style={S.toast(status.type)}>
      <span>{status.type === "ok" ? "✓" : "✕"}</span>
      <span>{status.msg}</span>
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [userId, setUserId]         = useState("");
  const [tab, setTab]               = useState("upload");   // "upload" | "manage"
  const [pendingFiles, setPending]  = useState([]);
  const [uploadedFiles, setUploaded]= useState([]);         // files already on server
  const [isDragging, setDragging]   = useState(false);
  const [uploading, setUploading]   = useState(false);
  const [uploadStatus, setUpStatus] = useState(null);
  const [deleteStatus, setDelStatus]= useState(null);
  const [deletingFile, setDeleting] = useState(null);       // filename being deleted
  const [messages, setMessages]     = useState([]);
  const [question, setQuestion]     = useState("");
  const [thinking, setThinking]     = useState(false);

  const fileInputRef  = useRef(null);
  const messagesEnd   = useRef(null);
  const textareaRef   = useRef(null);

  useEffect(() => { messagesEnd.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, thinking]);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "";
    ta.style.height = Math.min(ta.scrollHeight, 120) + "px";
  }, [question]);

  // ── File staging ──
  const addFiles = (raw) => {
    const valid = Array.from(raw).filter((f) =>
      ["pdf", "doc", "docx", "ppt", "pptx"].includes(getExt(f.name))
    );
    setPending((prev) => [...prev, ...valid]);
  };
  const removeFile = (i) => setPending((prev) => prev.filter((_, j) => j !== i));

  // ── Upload ──
  const handleUpload = async () => {
    if (!userId.trim() || !pendingFiles.length) return;
    setUploading(true);
    setUpStatus(null);
    try {
      const fd = new FormData();
      fd.append("user_id", userId.trim());
      pendingFiles.forEach((f) => fd.append("files", f));
      const res = await fetch(`${API_BASE}/upload`, { method: "POST", body: fd });
      if (!res.ok) throw new Error((await res.json()).detail || "Upload failed");
      const newNames = pendingFiles.map((f) => f.name);
      setUploaded((prev) => {
        const merged = [...prev];
        newNames.forEach((n) => { if (!merged.includes(n)) merged.push(n); });
        return merged;
      });
      setPending([]);
      setUpStatus({ type: "ok", msg: `${newNames.length} file(s) uploaded` });
      setTimeout(() => setUpStatus(null), 4000);
    } catch (err) {
      setUpStatus({ type: "err", msg: err.message });
    } finally {
      setUploading(false);
    }
  };

  // ── Delete ──
  const handleDelete = async (filename) => {
    if (!userId.trim()) return;
    setDeleting(filename);
    setDelStatus(null);
    try {
      const res = await fetch(`${API_BASE}/delete`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId.trim(), filename }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Delete failed");
      setUploaded((prev) => prev.filter((f) => f !== filename));
      setDelStatus({ type: "ok", msg: `"${filename}" deleted` });
      setTimeout(() => setDelStatus(null), 4000);
    } catch (err) {
      setDelStatus({ type: "err", msg: err.message });
    } finally {
      setDeleting(null);
    }
  };

  // ── Query ──
  const handleSend = async () => {
    const q = question.trim();
    if (!q || !userId.trim() || thinking) return;
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setQuestion("");
    setThinking(true);
    try {
      const res = await fetch(`${API_BASE}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId.trim(), question: q }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Query failed");
      const data = await res.json();
      const seen = new Set();
      const sources = (data.sources || []).filter(({ file, page }) => {
        const k = file + "|" + page;
        if (seen.has(k)) return false;
        seen.add(k); return true;
      });
      setMessages((prev) => [...prev, { role: "assistant", content: data.answer, sources }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", content: err.message }]);
    } finally {
      setThinking(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const fillQ = (text) => { if (userId.trim()) setQuestion(text); };

  const userQCount = messages.filter((m) => m.role === "user").length;
  const canUpload  = !!userId.trim() && pendingFiles.length > 0 && !uploading;
  const canSend    = !!question.trim() && !!userId.trim() && !thinking;

  return (
    <>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes spin    { to { transform: rotate(360deg); } }
        .anim  { animation: fadeUp .2s ease; }
        .spin  { animation: spin .7s linear infinite; }
        input:focus, textarea:focus { border-color: #2563EB !important; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #E4DDD6; border-radius: 4px; }
        .chip-btn:hover   { background: #EEF4FF !important; border-color: #BFCFEF !important; color: #2563EB !important; }
        .clear-btn:hover  { background: #FEF2F2 !important; border-color: #F5BFBF !important; color: #DC2626 !important; }
        .danger-btn:hover { background: #FEF2F2 !important; }
        .tab-btn:hover    { color: #1A1612 !important; }
        .md-bubble p      { margin: 0 0 6px; line-height: 1.7; }
        .md-bubble p:last-child { margin-bottom: 0; }
        .md-bubble h1     { font-size: 15px; font-weight: 700; margin: 12px 0 6px; }
        .md-bubble h2     { font-size: 14px; font-weight: 700; margin: 10px 0 5px; }
        .md-bubble h3     { font-size: 13px; font-weight: 600; margin: 8px 0 4px; }
        .md-bubble h1:first-child,.md-bubble h2:first-child,.md-bubble h3:first-child { margin-top: 0; }
        .md-bubble ol     { padding-left: 20px; margin: 4px 0 8px; display: flex; flex-direction: column; gap: 5px; }
        .md-bubble ul     { padding-left: 20px; margin: 4px 0 8px; list-style: disc; display: flex; flex-direction: column; gap: 5px; }
        .md-bubble li     { line-height: 1.65; font-size: 13px; }
        .md-bubble ol li  { list-style: decimal; }
        .md-bubble strong { font-weight: 600; color: #1A1612; }
        .md-bubble em     { font-style: italic; }
        .md-bubble code   { font-family: Menlo, Consolas, monospace; font-size: 12px; background: #F2EEE9; border: 1px solid #E4DDD6; border-radius: 4px; padding: 1px 5px; color: #B45309; }
      `}</style>

      <div style={S.app}>
        {/* ── Sidebar ── */}
        <div style={S.sidebar}>
          <div style={S.sidebarTop}>
            {/* Brand */}
            <div style={S.brand}>
              <div style={S.brandMark}>📚</div>
              <div>
                <div style={S.brandName}>StudyMind</div>
                <div style={S.brandSub}>Document assistant</div>
              </div>
            </div>

            {/* Session ID */}
            <label style={S.fieldLabel}>Session ID</label>
            <input
              style={S.textInput}
              placeholder="Enter your ID…"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
            />
          </div>

          {/* Tabs */}
          <div style={{ padding: "12px 18px 0", flexShrink: 0 }}>
            <div style={S.tabs}>
              {["upload", "manage"].map((t) => (
                <button key={t} className="tab-btn" style={S.tab(tab === t)} onClick={() => setTab(t)}>
                  {t === "upload" ? "⬆ Upload" : "📂 Manage"}
                </button>
              ))}
            </div>
          </div>

          <div style={S.sidebarBody}>
            {/* ── Upload tab ── */}
            {tab === "upload" && (
              <>
                {/* Drop zone */}
                <div
                  style={S.dropZone(isDragging)}
                  onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={(e) => { e.preventDefault(); setDragging(false); addFiles(e.dataTransfer.files); }}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div style={S.dzIcon}>☁️</div>
                  <div style={S.dzText}>Drop files here or click to browse</div>
                  <div style={S.dzHint}>PDF · DOCX · PPTX</div>
                  <input
                    ref={fileInputRef} type="file" multiple
                    accept=".pdf,.doc,.docx,.ppt,.pptx"
                    style={{ display: "none" }}
                    onChange={(e) => { addFiles(e.target.files); e.target.value = ""; }}
                  />
                </div>

                {/* Pending file list */}
                {pendingFiles.length > 0 && (
                  <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
                    {pendingFiles.map((f, i) => (
                      <div key={i} style={S.fileCard} className="anim">
                        <ExtBadge name={f.name} />
                        <span style={S.fileName} title={f.name}>{f.name}</span>
                        <button style={S.iconBtn(true)} onClick={() => removeFile(i)} aria-label={`Remove ${f.name}`}>✕</button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Upload button */}
                <button style={S.primaryBtn(!canUpload)} disabled={!canUpload} onClick={handleUpload}>
                  {uploading ? "Uploading…" : `Upload${pendingFiles.length ? ` (${pendingFiles.length})` : ""}`}
                </button>

                <Toast status={uploadStatus} />
              </>
            )}

            {/* ── Manage tab ── */}
            {tab === "manage" && (
              <>
                {!userId.trim() ? (
                  <div style={S.emptySmall}>Set a session ID first to manage documents.</div>
                ) : uploadedFiles.length === 0 ? (
                  <div style={S.emptySmall}>No documents uploaded yet.<br />Switch to Upload to add files.</div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column" }}>
                    <label style={{ ...S.fieldLabel, marginBottom: "10px" }}>
                      {uploadedFiles.length} file{uploadedFiles.length !== 1 ? "s" : ""} in session
                    </label>
                    {uploadedFiles.map((name) => (
                      <div key={name} style={S.uploadedCard} className="anim">
                        <ExtBadge name={name} />
                        <span style={S.fileName} title={name}>{name}</span>
                        <button
                          className="danger-btn"
                          style={S.dangerBtn}
                          disabled={deletingFile === name}
                          onClick={() => handleDelete(name)}
                          aria-label={`Delete ${name}`}
                        >
                          {deletingFile === name ? "…" : "✕ Delete"}
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                <Toast status={deleteStatus} />
              </>
            )}
          </div>

          {/* Footer: clear chat */}
          {messages.length > 0 && (
            <div style={S.sidebarFooter}>
              <button
                className="clear-btn"
                style={S.clearBtn}
                onClick={() => setMessages([])}
              >
                Clear conversation
              </button>
            </div>
          )}
        </div>

        {/* ── Main ── */}
        <div style={S.main}>
          {/* Topbar */}
          <div style={S.topbar}>
            <div>
              <div style={S.topbarTitle}>
                {userId ? `Session: ${userId}` : "No session active"}
              </div>
              <div style={S.topbarSub}>
                {userQCount} question{userQCount !== 1 ? "s" : ""} asked
              </div>
            </div>
            <div style={S.statusPill}>
              <div style={S.statusDot} />
              <span style={S.statusText}>API connected</span>
            </div>
          </div>

          {/* Messages */}
          <div style={S.messages}>
            {messages.length === 0 && !thinking ? (
              <div style={S.emptyState}>
                <div style={S.emptyRing}>💬</div>
                <div style={S.emptyTitle}>Ask anything about your documents</div>
                <div style={S.emptyBody}>
                  Upload your study materials, then ask questions to get detailed, sourced answers.
                </div>
                <div style={S.chips}>
                  {["Summarize key concepts", "What are the main topics?", "Give me a study plan"].map((s) => (
                    <button key={s} className="chip-btn" style={S.chip} onClick={() => fillQ(s)}>{s}</button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg, i) => (
                  <div key={i} className="anim">
                    {msg.role === "user" && (
                      <div style={S.msgUserWrap}>
                        <div style={S.msgUser}>{msg.content}</div>
                      </div>
                    )}
                    {msg.role === "assistant" && (
                      <div style={S.msgAI}>
                        <MarkdownBubble content={msg.content} style={S.msgBubble} />
                        {msg.sources?.length > 0 && (
                          <div style={S.sources}>
                            {msg.sources.map((s, j) => (
                              <div key={j} style={S.sourceChip}>
                                <span>📄</span>
                                <span>{s.file}</span>
                                {s.page !== "N/A" && (
                                  <span style={{ opacity: 0.7 }}>
                                    · p.{typeof s.page === "number" ? s.page + 1 : s.page}
                                  </span>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                    {msg.role === "error" && (
                      <div style={S.msgError}>⚠ {msg.content}</div>
                    )}
                  </div>
                ))}
                {thinking && (
                  <div style={S.thinkingBubble} className="anim">
                    <div className="spin" style={{
                      width: "14px", height: "14px",
                      border: `1.5px solid ${C.border}`,
                      borderTopColor: C.blue, borderRadius: "50%", flexShrink: 0,
                    }} />
                    <span>Searching your documents…</span>
                  </div>
                )}
              </>
            )}
            <div ref={messagesEnd} />
          </div>

          {/* Input area */}
          <div style={S.inputArea}>
            <textarea
              ref={textareaRef}
              style={S.chatInput}
              placeholder={userId ? "Ask a question about your documents…" : "Set a session ID first…"}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={!userId.trim() || thinking}
              rows={1}
            />
            <button style={S.sendBtn(!canSend)} disabled={!canSend} onClick={handleSend} aria-label="Send">
              ➤
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
