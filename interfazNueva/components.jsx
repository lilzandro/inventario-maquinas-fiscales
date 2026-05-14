
// ─────────────────────────────────────────────
//  Shared Components – Sistema de Gestión
// ─────────────────────────────────────────────

// ── Icons (inline SVG helpers) ─────────────────
const Icon = ({ name, size = 18, color = "currentColor" }) => {
  const icons = {
    dashboard: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>,
    inventory: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>,
    fiscal: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>,
    services: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>,
    clients: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
    suppliers: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>,
    reports: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>,
    users: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="8" r="4"/><path d="M6 20v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><circle cx="19" cy="8" r="3"/><path d="M22 20v-1a3 3 0 0 0-3-3"/></svg>,
    search: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
    bell: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>,
    plus: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>,
    edit: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>,
    trash: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>,
    check: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>,
    alert: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><triangle points="10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
    close: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
    chevronRight: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>,
    logout: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>,
    menu: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>,
    eye: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>,
    settings: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>,
    printer: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>,
    filter: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>,
    download: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>,
    arrowUp: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>,
    arrowDown: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>,
    calendar: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>,
    clock: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
    tag: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>,
    box: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>,
  };
  return icons[name] || <svg width={size} height={size} viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="none" stroke={color} strokeWidth="2"/></svg>;
};

// ── Badge ──────────────────────────────────────
const Badge = ({ label, variant = "default" }) => {
  const variants = {
    default:  { bg: "#EFF6FF", color: "#2563EB", border: "#BFDBFE" },
    success:  { bg: "#F0FDF4", color: "#16A34A", border: "#BBF7D0" },
    warning:  { bg: "#FFFBEB", color: "#D97706", border: "#FDE68A" },
    danger:   { bg: "#FEF2F2", color: "#DC2626", border: "#FECACA" },
    neutral:  { bg: "#F8FAFC", color: "#64748B", border: "#E2E8F0" },
    purple:   { bg: "#FAF5FF", color: "#7C3AED", border: "#E9D5FF" },
  };
  const s = variants[variant] || variants.default;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 4,
      padding: "2px 10px", borderRadius: 20,
      fontSize: 11, fontWeight: 600, letterSpacing: "0.02em",
      background: s.bg, color: s.color, border: `1px solid ${s.border}`,
    }}>
      {label}
    </span>
  );
};

// ── Stat Card ──────────────────────────────────
const StatCard = ({ icon, iconBg, iconColor, label, value, delta, deltaUp }) => (
  <div style={{
    background: "#fff", borderRadius: 12, padding: "20px 22px",
    border: "1px solid #E8EDF2", display: "flex", flexDirection: "column", gap: 10,
    boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
  }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
      <div style={{
        width: 40, height: 40, borderRadius: 10,
        background: iconBg, display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        <Icon name={icon} size={18} color={iconColor} />
      </div>
      {delta && (
        <span style={{
          display: "flex", alignItems: "center", gap: 3,
          fontSize: 11, fontWeight: 600,
          color: deltaUp ? "#16A34A" : "#DC2626",
        }}>
          <Icon name={deltaUp ? "arrowUp" : "arrowDown"} size={12} color={deltaUp ? "#16A34A" : "#DC2626"} />
          {delta}
        </span>
      )}
    </div>
    <div>
      <div style={{ fontSize: 26, fontWeight: 700, color: "#0F172A", lineHeight: 1.1 }}>{value}</div>
      <div style={{ fontSize: 12, color: "#94A3B8", marginTop: 3 }}>{label}</div>
    </div>
  </div>
);

// ── Button ─────────────────────────────────────
const Button = ({ children, variant = "primary", size = "md", icon, onClick, style: extraStyle }) => {
  const [hovered, setHovered] = React.useState(false);
  const base = {
    display: "inline-flex", alignItems: "center", gap: 6,
    border: "none", cursor: "pointer", fontWeight: 600,
    borderRadius: 8, transition: "all 0.15s", outline: "none",
    fontFamily: "inherit",
  };
  const sizes = { sm: { padding: "5px 12px", fontSize: 12 }, md: { padding: "8px 16px", fontSize: 13 }, lg: { padding: "10px 20px", fontSize: 14 } };
  const variants = {
    primary: { background: hovered ? "#4A8BC5" : "#5B9BD5", color: "#fff", boxShadow: "0 1px 3px rgba(91,155,213,0.3)" },
    secondary: { background: hovered ? "#EFF6FF" : "#F8FAFC", color: "#334155", border: "1px solid #E2E8F0" },
    danger: { background: hovered ? "#C01E1E" : "#DC2626", color: "#fff" },
    ghost: { background: hovered ? "#F1F5F9" : "transparent", color: "#64748B" },
    success: { background: hovered ? "#15803D" : "#16A34A", color: "#fff" },
  };
  return (
    <button
      style={{ ...base, ...sizes[size], ...variants[variant], ...extraStyle }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={onClick}
    >
      {icon && <Icon name={icon} size={size === "sm" ? 13 : 15} color={variants[variant].color} />}
      {children}
    </button>
  );
};

// ── Table ──────────────────────────────────────
const Table = ({ columns, rows, onEdit, onDelete, onView }) => (
  <div style={{ overflowX: "auto" }}>
    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
      <thead>
        <tr style={{ borderBottom: "2px solid #E8EDF2" }}>
          {columns.map((col, i) => (
            <th key={i} style={{ padding: "10px 14px", textAlign: "left", color: "#64748B", fontWeight: 600, fontSize: 11, letterSpacing: "0.05em", textTransform: "uppercase", whiteSpace: "nowrap" }}>
              {col}
            </th>
          ))}
          {(onEdit || onDelete || onView) && <th style={{ padding: "10px 14px", width: 100 }}></th>}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, ri) => (
          <tr key={ri} style={{ borderBottom: "1px solid #F1F5F9", background: ri % 2 === 0 ? "#fff" : "#FAFBFC" }}>
            {row.map((cell, ci) => (
              <td key={ci} style={{ padding: "10px 14px", color: "#1E293B", verticalAlign: "middle" }}>
                {cell}
              </td>
            ))}
            {(onEdit || onDelete || onView) && (
              <td style={{ padding: "10px 14px" }}>
                <div style={{ display: "flex", gap: 4 }}>
                  {onView && <button onClick={() => onView(ri)} style={{ background: "none", border: "none", cursor: "pointer", color: "#64748B", padding: 4, borderRadius: 6, display:"flex" }} title="Ver"><Icon name="eye" size={15} /></button>}
                  {onEdit && <button onClick={() => onEdit(ri)} style={{ background: "none", border: "none", cursor: "pointer", color: "#5B9BD5", padding: 4, borderRadius: 6, display:"flex" }} title="Editar"><Icon name="edit" size={15} /></button>}
                  {onDelete && <button onClick={() => onDelete(ri)} style={{ background: "none", border: "none", cursor: "pointer", color: "#EF4444", padding: 4, borderRadius: 6, display:"flex" }} title="Eliminar"><Icon name="trash" size={15} /></button>}
                </div>
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// ── Modal ──────────────────────────────────────
const Modal = ({ open, onClose, title, children, width = 520 }) => {
  if (!open) return null;
  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(15,23,42,0.45)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}
      onClick={onClose}>
      <div style={{ background: "#fff", borderRadius: 14, width, maxWidth: "95vw", maxHeight: "90vh", overflowY: "auto", boxShadow: "0 20px 60px rgba(0,0,0,0.2)" }}
        onClick={e => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "18px 22px", borderBottom: "1px solid #F1F5F9" }}>
          <span style={{ fontWeight: 700, fontSize: 16, color: "#0F172A" }}>{title}</span>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: "#94A3B8", display:"flex" }}><Icon name="close" size={18} /></button>
        </div>
        <div style={{ padding: "22px" }}>{children}</div>
      </div>
    </div>
  );
};

// ── Form Field ─────────────────────────────────
const Field = ({ label, children, required }) => (
  <div style={{ marginBottom: 16 }}>
    <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 5 }}>
      {label}{required && <span style={{ color: "#EF4444" }}> *</span>}
    </label>
    {children}
  </div>
);

const Input = ({ placeholder, value, onChange, type = "text" }) => (
  <input type={type} placeholder={placeholder} value={value} onChange={onChange}
    style={{ width: "100%", padding: "8px 12px", border: "1.5px solid #E2E8F0", borderRadius: 8, fontSize: 13, color: "#0F172A", outline: "none", background: "#F8FAFC", boxSizing: "border-box", fontFamily: "inherit" }} />
);

const Select = ({ value, onChange, options }) => (
  <select value={value} onChange={onChange}
    style={{ width: "100%", padding: "8px 12px", border: "1.5px solid #E2E8F0", borderRadius: 8, fontSize: 13, color: "#0F172A", outline: "none", background: "#F8FAFC", fontFamily: "inherit" }}>
    {options.map((o, i) => <option key={i} value={o.value || o}>{o.label || o}</option>)}
  </select>
);

// ── Page Header ────────────────────────────────
const PageHeader = ({ title, subtitle, actions }) => (
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
    <div>
      <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: "#0F172A" }}>{title}</h1>
      {subtitle && <p style={{ margin: "4px 0 0", fontSize: 13, color: "#64748B" }}>{subtitle}</p>}
    </div>
    {actions && <div style={{ display: "flex", gap: 8 }}>{actions}</div>}
  </div>
);

// ── Search Bar ─────────────────────────────────
const SearchBar = ({ placeholder, value, onChange }) => (
  <div style={{ position: "relative", flex: 1, maxWidth: 320 }}>
    <span style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "#94A3B8", display: "flex" }}>
      <Icon name="search" size={15} />
    </span>
    <input placeholder={placeholder} value={value} onChange={onChange}
      style={{ width: "100%", padding: "7px 12px 7px 34px", border: "1.5px solid #E2E8F0", borderRadius: 8, fontSize: 13, color: "#0F172A", outline: "none", background: "#fff", boxSizing: "border-box", fontFamily: "inherit" }} />
  </div>
);

// ── Status Steps ───────────────────────────────
const StatusSteps = ({ steps, current }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 0 }}>
    {steps.map((step, i) => (
      <React.Fragment key={i}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
          <div style={{
            width: 28, height: 28, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
            background: i < current ? "#16A34A" : i === current ? "#5B9BD5" : "#E2E8F0",
            color: i <= current ? "#fff" : "#94A3B8", fontSize: 12, fontWeight: 700,
          }}>
            {i < current ? <Icon name="check" size={14} color="#fff" /> : i + 1}
          </div>
          <span style={{ fontSize: 10, color: i === current ? "#5B9BD5" : i < current ? "#16A34A" : "#94A3B8", fontWeight: i === current ? 700 : 500, whiteSpace: "nowrap" }}>{step}</span>
        </div>
        {i < steps.length - 1 && (
          <div style={{ flex: 1, height: 2, background: i < current ? "#16A34A" : "#E2E8F0", margin: "0 4px", marginBottom: 20 }} />
        )}
      </React.Fragment>
    ))}
  </div>
);

// ── Mini Chart (SVG bar chart) ─────────────────
const MiniBarChart = ({ data, color = "#5B9BD5", height = 60 }) => {
  const max = Math.max(...data);
  return (
    <svg width="100%" height={height} viewBox={`0 0 ${data.length * 22} ${height}`} preserveAspectRatio="none">
      {data.map((v, i) => {
        const barH = (v / max) * (height - 8);
        return (
          <g key={i}>
            <rect x={i * 22 + 2} y={height - barH - 4} width={18} height={barH} rx={4}
              fill={i === data.length - 1 ? color : color + "60"} />
          </g>
        );
      })}
    </svg>
  );
};

// ── Line Chart ─────────────────────────────────
const MiniLineChart = ({ data, color = "#5B9BD5", height = 60 }) => {
  const max = Math.max(...data), min = Math.min(...data);
  const w = 220, h = height;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / (max - min + 1)) * (h - 8) - 4}`).join(" ");
  return (
    <svg width="100%" height={height} viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
      <polyline points={pts} fill="none" stroke={color} strokeWidth="2.5" strokeLinejoin="round" />
      <polyline points={`0,${h} ${pts} ${w},${h}`} fill={color + "20"} stroke="none" />
    </svg>
  );
};

// Export all to window
Object.assign(window, {
  Icon, Badge, StatCard, Button, Table, Modal, Field, Input, Select,
  PageHeader, SearchBar, StatusSteps, MiniBarChart, MiniLineChart
});
