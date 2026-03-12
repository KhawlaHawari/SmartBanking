import { useState, useEffect, useRef } from "react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, LineChart, Line, CartesianGrid } from "recharts";

// ── DESIGN TOKENS ─────────────────────────────────────────
const C = {
  bg:      "#03070f",
  surface: "#080f1e",
  card:    "#0c1525",
  border:  "#112240",
  accent:  "#00d4ff",
  gold:    "#f0a500",
  green:   "#00e5a0",
  red:     "#ff4757",
  amber:   "#ffb347",
  muted:   "#4a6080",
  text:    "#c8d8f0",
  dim:     "#6b8aad",
};

// ── MOCK DATA ─────────────────────────────────────────────
const SEGMENTS = [
  { name: "At-Risk Middle",      value: 969,  pct: 48.5, color: "#f0a500" },
  { name: "Standard",            value: 512,  pct: 25.6, color: "#00d4ff" },
  { name: "High Value High Risk",value: 253,  pct: 12.7, color: "#ff4757" },
  { name: "Growth Potential",    value: 182,  pct: 9.1,  color: "#00e5a0" },
  { name: "Strategic Premium",   value: 52,   pct: 2.6,  color: "#a78bfa" },
  { name: "High Risk Low Value", value: 32,   pct: 1.6,  color: "#ff6b9d" },
];

const RISK = [
  { name: "Very Low", value: 133, color: "#00d4ff" },
  { name: "Low",      value: 466, color: "#00e5a0" },
  { name: "Medium",   value:1289, color: "#f0a500" },
  { name: "High",     value: 110, color: "#ff4757" },
  { name: "Very High",value:   2, color: "#7f0000" },
];

const METRICS = [
  { label: "Segmentation", metric: "F1-Macro", value: 0.56,  color: "#00d4ff", icon: "◈" },
  { label: "Risk Detection", metric: "AUC-ROC",  value: 0.997, color: "#ff4757", icon: "⬡" },
  { label: "Churn Predict",  metric: "AUC-ROC",  value: 0.961, color: "#f0a500", icon: "◎" },
  { label: "Rec. Actions",   metric: "Top-3 Acc",value: 0.987, color: "#00e5a0", icon: "⬟" },
];

const CHURN_BY_SEG = [
  { seg: "High Risk Low Value", val: 0.312, color: "#ff4757" },
  { seg: "At-Risk Middle",      val: 0.289, color: "#f0a500" },
  { seg: "High Value High Risk",val: 0.241, color: "#ff6b9d" },
  { seg: "Growth Potential",    val: 0.198, color: "#00d4ff" },
  { seg: "Standard",            val: 0.156, color: "#6b8aad" },
  { seg: "Strategic Premium",   val: 0.089, color: "#00e5a0" },
];

const ACTIONS = [
  { name: "Financial Advisory",   count: 969, short: "Fin. Advisory" },
  { name: "Digital Engagement",   count: 512, short: "Digital Eng." },
  { name: "Credit Review",        count: 253, short: "Credit Rev." },
  { name: "Cross-Sell",           count: 182, short: "Cross-Sell" },
  { name: "VIP Loyalty",          count:  52, short: "VIP Loyalty" },
  { name: "Credit Freeze",        count:  32, short: "Credit Freeze" },
];

const CORRELATIONS = [
  { f: "num_defaults",       risk: 0.88, val: -0.72 },
  { f: "credit_util",        risk: 0.76, val: -0.61 },
  { f: "num_late_payments",  risk: 0.71, val: -0.55 },
  { f: "overdraft_count",    risk: 0.65, val: -0.48 },
  { f: "credit_score",       risk: -0.82, val: 0.79 },
  { f: "monthly_income",     risk: -0.58, val: 0.84 },
  { f: "tenure_months",      risk: -0.44, val: 0.66 },
  { f: "num_products",       risk: -0.31, val: 0.72 },
];

// ── STYLES ────────────────────────────────────────────────
const injectStyles = () => `
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=DM+Serif+Display&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: ${C.bg};
    color: ${C.text};
    font-family: 'Outfit', sans-serif;
    min-height: 100vh;
  }

  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: ${C.bg}; }
  ::-webkit-scrollbar-thumb { background: ${C.border}; border-radius: 2px; }

  .app-shell {
    display: flex;
    min-height: 100vh;
  }

  /* SIDEBAR */
  .sidebar {
    width: 220px;
    background: ${C.surface};
    border-right: 1px solid ${C.border};
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0; left: 0; bottom: 0;
    z-index: 100;
  }

  .sidebar-logo {
    padding: 28px 24px 20px;
    border-bottom: 1px solid ${C.border};
  }

  .logo-mark {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: #fff;
    letter-spacing: -0.5px;
    line-height: 1;
  }

  .logo-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: ${C.accent};
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 4px;
  }

  .sidebar-nav {
    padding: 20px 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13.5px;
    font-weight: 500;
    color: ${C.muted};
    border: 1px solid transparent;
    transition: all 0.15s;
    letter-spacing: 0.2px;
  }

  .nav-item:hover {
    background: rgba(0,212,255,0.05);
    color: ${C.text};
    border-color: ${C.border};
  }

  .nav-item.active {
    background: rgba(0,212,255,0.08);
    color: ${C.accent};
    border-color: rgba(0,212,255,0.2);
  }

  .nav-icon {
    font-size: 15px;
    width: 18px;
    text-align: center;
  }

  .sidebar-footer {
    padding: 16px;
    border-top: 1px solid ${C.border};
  }

  .status-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: ${C.green};
    letter-spacing: 1px;
  }

  .status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: ${C.green};
    box-shadow: 0 0 8px ${C.green};
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  /* MAIN */
  .main {
    margin-left: 220px;
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .topbar {
    background: ${C.surface};
    border-bottom: 1px solid ${C.border};
    padding: 0 32px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 50;
  }

  .page-title {
    font-family: 'DM Serif Display', serif;
    font-size: 20px;
    color: #fff;
    letter-spacing: -0.3px;
  }

  .topbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .data-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: ${C.accent};
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.2);
    padding: 4px 10px;
    border-radius: 4px;
    letter-spacing: 1.5px;
  }

  .content {
    padding: 28px 32px;
    flex: 1;
  }

  /* CARDS */
  .card {
    background: ${C.card};
    border: 1px solid ${C.border};
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
  }

  .card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.3), transparent);
  }

  .card-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: ${C.muted};
    margin-bottom: 16px;
  }

  /* METRIC CARDS */
  .metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
  }

  .metric-card {
    background: ${C.card};
    border: 1px solid ${C.border};
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    cursor: default;
    transition: transform 0.2s, border-color 0.2s;
  }

  .metric-card:hover {
    transform: translateY(-2px);
  }

  .metric-icon {
    font-size: 22px;
    margin-bottom: 12px;
    display: block;
  }

  .metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: ${C.muted};
    margin-bottom: 6px;
  }

  .metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -1px;
    line-height: 1;
  }

  .metric-sub {
    font-size: 11px;
    color: ${C.dim};
    margin-top: 4px;
  }

  .metric-bar {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
  }

  /* GRID LAYOUTS */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 24px; }
  .grid-5-7 { display: grid; grid-template-columns: 5fr 7fr; gap: 16px; margin-bottom: 24px; }

  /* SEGMENT LIST */
  .seg-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(17,34,64,0.6);
  }

  .seg-dot {
    width: 8px; height: 8px;
    border-radius: 2px;
    flex-shrink: 0;
  }

  .seg-name {
    font-size: 12.5px;
    color: ${C.text};
    flex: 1;
  }

  .seg-count {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: ${C.dim};
  }

  .seg-pct {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: ${C.muted};
    width: 42px;
    text-align: right;
  }

  .seg-bar-wrap {
    width: 60px;
    height: 3px;
    background: ${C.border};
    border-radius: 2px;
  }

  .seg-bar-fill {
    height: 100%;
    border-radius: 2px;
  }

  /* TOOLTIP */
  .custom-tooltip {
    background: #0d1b2e;
    border: 1px solid ${C.border};
    border-radius: 8px;
    padding: 10px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: ${C.text};
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  }

  /* TABS */
  .tabs {
    display: flex;
    gap: 2px;
    background: ${C.surface};
    border: 1px solid ${C.border};
    border-radius: 8px;
    padding: 3px;
    margin-bottom: 24px;
    width: fit-content;
  }

  .tab {
    padding: 7px 18px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12.5px;
    font-weight: 500;
    color: ${C.muted};
    transition: all 0.15s;
    letter-spacing: 0.3px;
  }

  .tab.active {
    background: ${C.card};
    color: ${C.accent};
    border: 1px solid rgba(0,212,255,0.2);
  }

  /* PREDICT PAGE */
  .predict-layout {
    display: grid;
    grid-template-columns: 420px 1fr;
    gap: 20px;
    align-items: start;
  }

  .form-section {
    border: 1px solid ${C.border};
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 10px;
  }

  .form-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: rgba(17,34,64,0.5);
    cursor: pointer;
    font-size: 12.5px;
    font-weight: 600;
    color: ${C.text};
    border-bottom: 1px solid transparent;
    transition: all 0.15s;
  }

  .form-section-header.open {
    border-bottom-color: ${C.border};
    color: ${C.accent};
  }

  .form-section-body {
    padding: 14px 16px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }

  .field-group { display: flex; flex-direction: column; gap: 4px; }
  .field-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: ${C.muted};
  }

  .field-input {
    background: ${C.bg};
    border: 1px solid ${C.border};
    border-radius: 6px;
    padding: 7px 10px;
    color: ${C.text};
    font-size: 12.5px;
    font-family: 'JetBrains Mono', monospace;
    outline: none;
    transition: border-color 0.15s;
    width: 100%;
  }

  .field-input:focus { border-color: ${C.accent}; }

  .submit-btn {
    width: 100%;
    padding: 13px;
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(0,212,255,0.05));
    border: 1px solid rgba(0,212,255,0.4);
    border-radius: 8px;
    color: ${C.accent};
    font-size: 13px;
    font-weight: 600;
    font-family: 'Outfit', sans-serif;
    cursor: pointer;
    letter-spacing: 1px;
    transition: all 0.2s;
    margin-top: 14px;
  }

  .submit-btn:hover {
    background: rgba(0,212,255,0.2);
    box-shadow: 0 0 20px rgba(0,212,255,0.15);
  }

  /* RESULT CARDS */
  .result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

  .result-card {
    background: ${C.card};
    border: 1px solid ${C.border};
    border-radius: 12px;
    padding: 18px;
    position: relative;
    overflow: hidden;
  }

  .result-card.full { grid-column: 1 / -1; }

  .result-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: ${C.muted};
    margin-bottom: 12px;
  }

  .result-segment {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    line-height: 1.2;
    margin-bottom: 12px;
  }

  .confidence-bar {
    height: 3px;
    background: ${C.border};
    border-radius: 2px;
    overflow: hidden;
  }

  .confidence-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.6s ease;
  }

  .risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
    margin-bottom: 8px;
  }

  .prob-text {
    font-size: 28px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    letter-spacing: -1px;
  }

  /* GAUGE */
  .gauge-wrap { display: flex; justify-content: center; margin-bottom: 8px; }

  /* SHAP */
  .shap-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
  }

  .shap-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: ${C.dim};
    width: 120px;
    flex-shrink: 0;
  }

  .shap-bar-wrap { flex: 1; height: 6px; background: ${C.border}; border-radius: 3px; overflow: hidden; }
  .shap-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }
  .shap-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    width: 44px;
    text-align: right;
  }

  /* ACTIONS PAGE */
  .action-card {
    background: ${C.card};
    border: 1px solid ${C.border};
    border-radius: 12px;
    padding: 16px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 10px;
    transition: border-color 0.15s, transform 0.15s;
    cursor: default;
  }

  .action-card:hover {
    border-color: rgba(0,212,255,0.25);
    transform: translateX(3px);
  }

  .action-icon-wrap {
    width: 40px; height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
  }

  .action-name { font-size: 13.5px; font-weight: 600; color: ${C.text}; margin-bottom: 3px; }
  .action-desc { font-size: 11.5px; color: ${C.dim}; line-height: 1.4; }

  .action-count {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 700;
    color: ${C.text};
    text-align: right;
  }

  .action-count-sub { font-size: 9px; color: ${C.muted}; letter-spacing: 1px; text-transform: uppercase; }

  /* SECTION LABEL */
  .section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: ${C.muted};
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: ${C.border};
  }


  /* ── LOGIN PAGE ─────────────────────────────────── */
  .login-shell {
    min-height: 100vh;
    background: #03070f;
    display: grid;
    grid-template-columns: 1fr 1fr;
  }

  .login-left {
    position: relative;
    background: linear-gradient(145deg, #050d1c 0%, #091428 50%, #0a1f3a 100%);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 48px;
    overflow: hidden;
  }

  .login-left-grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,212,255,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,212,255,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
  }

  .login-left-glow {
    position: absolute;
    width: 600px; height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,212,255,0.08) 0%, transparent 70%);
    top: -100px; left: -100px;
    pointer-events: none;
  }

  .login-brand {
    position: relative; z-index: 1;
  }

  .login-brand-name {
    font-family: 'DM Serif Display', serif;
    font-size: 36px;
    color: #fff;
    letter-spacing: -1px;
    line-height: 1;
    margin-bottom: 6px;
  }

  .login-brand-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    color: #00d4ff;
    text-transform: uppercase;
  }

  .login-feature-list {
    position: relative; z-index: 1;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .login-feature-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
  }

  .login-feature-icon {
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.15);
  }

  .login-feature-title {
    font-size: 13.5px;
    font-weight: 600;
    color: #fff;
    margin-bottom: 2px;
  }

  .login-feature-desc {
    font-size: 11.5px;
    color: #6b8aad;
    line-height: 1.4;
  }

  .login-copy {
    position: relative; z-index: 1;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #4a6080;
    letter-spacing: 1px;
  }

  .login-right {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 48px;
    background: #080f1e;
  }

  .login-form-wrap {
    width: 100%;
    max-width: 400px;
  }

  .login-title {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    color: #fff;
    margin-bottom: 6px;
  }

  .login-subtitle {
    font-size: 13px;
    color: #6b8aad;
    margin-bottom: 36px;
  }

  .login-field {
    margin-bottom: 18px;
  }

  .login-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a6080;
    margin-bottom: 6px;
    display: block;
  }

  .login-input {
    width: 100%;
    background: #0c1525;
    border: 1px solid #112240;
    border-radius: 8px;
    padding: 12px 14px;
    color: #c8d8f0;
    font-size: 13.5px;
    font-family: 'Outfit', sans-serif;
    outline: none;
    transition: border-color 0.15s, box-shadow 0.15s;
  }

  .login-input:focus {
    border-color: #00d4ff;
    box-shadow: 0 0 0 3px rgba(0,212,255,0.08);
  }

  .login-input::placeholder { color: #4a6080; }

  .login-btn {
    width: 100%;
    padding: 14px;
    background: linear-gradient(135deg, rgba(0,212,255,0.18), rgba(0,212,255,0.06));
    border: 1px solid rgba(0,212,255,0.4);
    border-radius: 10px;
    color: #00d4ff;
    font-size: 13.5px;
    font-weight: 600;
    font-family: 'Outfit', sans-serif;
    cursor: pointer;
    letter-spacing: 1.5px;
    transition: all 0.2s;
    margin-top: 8px;
    position: relative;
    overflow: hidden;
  }

  .login-btn:hover {
    background: rgba(0,212,255,0.22);
    box-shadow: 0 0 24px rgba(0,212,255,0.15);
  }

  .login-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .login-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 24px 0;
    color: #4a6080;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 1px;
  }

  .login-divider::before, .login-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #112240;
  }

  .login-info-strip {
    background: rgba(0,212,255,0.04);
    border: 1px solid rgba(0,212,255,0.12);
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 24px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .login-info-text {
    font-size: 11.5px;
    color: #6b8aad;
    line-height: 1.4;
  }

  .login-error {
    background: rgba(255,71,87,0.08);
    border: 1px solid rgba(255,71,87,0.3);
    border-radius: 8px;
    padding: 11px 14px;
    color: #ff4757;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 18px;
  }

  /* ── CHAT ASSISTANT ─────────────────────────────── */
  .chat-btn {
    position: fixed;
    bottom: 28px;
    right: 28px;
    width: 52px; height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,212,255,0.08));
    border: 1px solid rgba(0,212,255,0.4);
    color: #00d4ff;
    font-size: 22px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4), 0 0 20px rgba(0,212,255,0.1);
    transition: all 0.2s;
  }

  .chat-btn:hover {
    transform: scale(1.08);
    box-shadow: 0 4px 28px rgba(0,0,0,0.5), 0 0 30px rgba(0,212,255,0.2);
  }

  .chat-panel {
    position: fixed;
    bottom: 92px;
    right: 28px;
    width: 360px;
    height: 520px;
    background: #080f1e;
    border: 1px solid #112240;
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    z-index: 998;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6);
    overflow: hidden;
    animation: chatSlideIn 0.25s cubic-bezier(.16,1,.3,1);
  }

  @keyframes chatSlideIn {
    from { opacity: 0; transform: translateY(20px) scale(0.95); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }

  .chat-header {
    padding: 16px 18px;
    background: #0c1525;
    border-bottom: 1px solid #112240;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .chat-avatar {
    width: 34px; height: 34px;
    border-radius: 10px;
    background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,212,255,0.05));
    border: 1px solid rgba(0,212,255,0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
  }

  .chat-header-name {
    font-size: 13.5px;
    font-weight: 600;
    color: #fff;
  }

  .chat-header-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: #00e5a0;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .chat-msg {
    display: flex;
    gap: 8px;
    align-items: flex-end;
  }

  .chat-msg.user { flex-direction: row-reverse; }

  .chat-bubble {
    max-width: 78%;
    padding: 10px 13px;
    border-radius: 14px;
    font-size: 12.5px;
    line-height: 1.5;
    color: #c8d8f0;
  }

  .chat-bubble.bot {
    background: #0c1525;
    border: 1px solid #112240;
    border-bottom-left-radius: 4px;
  }

  .chat-bubble.user {
    background: linear-gradient(135deg, rgba(0,212,255,0.18), rgba(0,212,255,0.08));
    border: 1px solid rgba(0,212,255,0.25);
    color: #e0f4ff;
    border-bottom-right-radius: 4px;
  }

  .chat-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 8.5px;
    color: #4a6080;
    padding: 0 4px;
    margin-bottom: 2px;
  }

  .chat-suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 0 16px 8px;
  }

  .chat-chip {
    padding: 5px 11px;
    border-radius: 20px;
    border: 1px solid #112240;
    background: #0c1525;
    color: #6b8aad;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
  }

  .chat-chip:hover {
    border-color: rgba(0,212,255,0.3);
    color: #00d4ff;
    background: rgba(0,212,255,0.05);
  }

  .chat-input-row {
    padding: 12px 14px;
    border-top: 1px solid #112240;
    display: flex;
    gap: 8px;
    background: #0c1525;
  }

  .chat-input {
    flex: 1;
    background: #03070f;
    border: 1px solid #112240;
    border-radius: 8px;
    padding: 9px 12px;
    color: #c8d8f0;
    font-size: 12.5px;
    font-family: 'Outfit', sans-serif;
    outline: none;
    resize: none;
    transition: border-color 0.15s;
    line-height: 1.4;
  }

  .chat-input:focus { border-color: rgba(0,212,255,0.4); }

  .chat-send {
    width: 36px; height: 36px;
    border-radius: 8px;
    background: rgba(0,212,255,0.12);
    border: 1px solid rgba(0,212,255,0.3);
    color: #00d4ff;
    font-size: 14px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.15s;
    flex-shrink: 0;
    align-self: flex-end;
  }

  .chat-send:hover {
    background: rgba(0,212,255,0.22);
    transform: scale(1.05);
  }

  .chat-typing {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 10px 13px;
    background: #0c1525;
    border: 1px solid #112240;
    border-radius: 14px;
    border-bottom-left-radius: 4px;
    width: fit-content;
  }

  .typing-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #4a6080;
    animation: typingBounce 1.2s infinite;
  }

  .typing-dot:nth-child(2) { animation-delay: 0.2s; }
  .typing-dot:nth-child(3) { animation-delay: 0.4s; }

  @keyframes typingBounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-5px); opacity: 1; }
  }


  /* SCANLINE EFFECT */
  .scanlines {
    position: fixed;
    inset: 0;
    pointer-events: none;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.03) 2px,
      rgba(0,0,0,0.03) 4px
    );
    z-index: 1000;
  }

  /* ANIMATED COUNTER */
  @keyframes countUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .animate-in { animation: countUp 0.4s ease forwards; }
`;

// ── COMPONENTS ────────────────────────────────────────────

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="custom-tooltip">
      <div style={{ color: C.accent, marginBottom: 4, fontSize: 10, letterSpacing: 1 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color || C.text }}>
          {p.name}: <span style={{ fontWeight: 700 }}>{typeof p.value === 'number' ? p.value.toFixed(3) : p.value}</span>
        </div>
      ))}
    </div>
  );
};

function GaugeChart({ value, color }) {
  const r = 52, cx = 70, cy = 70;
  const circumference = Math.PI * r;
  const filled = circumference * (1 - value);
  return (
    <svg width="140" height="80" viewBox="0 0 140 80">
      <defs>
        <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={color} stopOpacity="0.3"/>
          <stop offset="100%" stopColor={color}/>
        </linearGradient>
      </defs>
      <path d={`M ${cx-r} ${cy} A ${r} ${r} 0 0 1 ${cx+r} ${cy}`}
        fill="none" stroke={C.border} strokeWidth="8" strokeLinecap="round"/>
      <path d={`M ${cx-r} ${cy} A ${r} ${r} 0 0 1 ${cx+r} ${cy}`}
        fill="none" stroke="url(#gaugeGrad)" strokeWidth="8" strokeLinecap="round"
        strokeDasharray={`${circumference}`}
        strokeDashoffset={filled}
        style={{ transition: 'stroke-dashoffset 0.8s ease' }}/>
      <text x={cx} y={cy-8} textAnchor="middle" fill={color}
        style={{ fontFamily: 'JetBrains Mono', fontSize: 20, fontWeight: 700 }}>
        {(value * 100).toFixed(0)}%
      </text>
      <text x={cx} y={cy+6} textAnchor="middle" fill={C.muted}
        style={{ fontFamily: 'JetBrains Mono', fontSize: 8, letterSpacing: 1 }}>CHURN RISK</text>
    </svg>
  );
}

function CorrelationChart() {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={CORRELATIONS} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false}/>
        <XAxis dataKey="f" tick={{ fill: C.muted, fontSize: 9, fontFamily: 'JetBrains Mono' }} tickLine={false}/>
        <YAxis tick={{ fill: C.muted, fontSize: 9, fontFamily: 'JetBrains Mono' }} tickLine={false} axisLine={false} domain={[-1, 1]}/>
        <Tooltip content={<CustomTooltip />}/>
        <Bar dataKey="risk" name="Risk Corr" fill={C.red} radius={[3,3,0,0]}/>
        <Bar dataKey="val"  name="Value Corr" fill={C.green} radius={[3,3,0,0]}/>
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── PAGES ─────────────────────────────────────────────────

function DashboardPage() {
  return (
    <div className="content">
      <div className="section-label">PERFORMANCE OVERVIEW</div>
      <div className="metric-grid">
        {METRICS.map((m, i) => (
          <div key={i} className="metric-card animate-in" style={{ animationDelay: `${i*0.08}s` }}>
            <span className="metric-icon" style={{ color: m.color }}>{m.icon}</span>
            <div className="metric-label">{m.label}</div>
            <div className="metric-value" style={{ color: m.color }}>
              {m.value.toFixed(m.value < 1 ? 3 : 0)}
            </div>
            <div className="metric-sub">{m.metric}</div>
            <div className="metric-bar" style={{ background: `linear-gradient(90deg, ${m.color}33, ${m.color})` }}/>
          </div>
        ))}
      </div>

      <div className="grid-5-7">
        <div className="card">
          <div className="card-title">SEGMENT DISTRIBUTION</div>
          {SEGMENTS.map((s, i) => (
            <div key={i} className="seg-item">
              <div className="seg-dot" style={{ background: s.color }}/>
              <div className="seg-name" style={{ fontSize: 11.5 }}>{s.name}</div>
              <div className="seg-bar-wrap">
                <div className="seg-bar-fill" style={{ width: `${s.pct * 2}%`, background: s.color }}/>
              </div>
              <div className="seg-count">{s.value}</div>
              <div className="seg-pct">{s.pct}%</div>
            </div>
          ))}
        </div>

        <div className="card">
          <div className="card-title">CHURN PROBABILITY BY SEGMENT</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={CHURN_BY_SEG} layout="vertical" margin={{ left: 10, right: 30, top: 0, bottom: 0 }}>
              <XAxis type="number" domain={[0, 0.4]} tick={{ fill: C.muted, fontSize: 9, fontFamily: 'JetBrains Mono' }} tickLine={false} axisLine={{ stroke: C.border }}/>
              <YAxis type="category" dataKey="seg" tick={{ fill: C.dim, fontSize: 9.5, fontFamily: 'Outfit' }} tickLine={false} axisLine={false} width={120}/>
              <Tooltip content={<CustomTooltip />}/>
              <Bar dataKey="val" name="Avg Churn Prob" radius={[0,4,4,0]}>
                {CHURN_BY_SEG.map((s, i) => <Cell key={i} fill={s.color}/>)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">RISK CLASS DISTRIBUTION</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <ResponsiveContainer width={160} height={160}>
              <PieChart>
                <Pie data={RISK} dataKey="value" innerRadius={45} outerRadius={75} paddingAngle={2}>
                  {RISK.map((r, i) => <Cell key={i} fill={r.color}/>)}
                </Pie>
                <Tooltip content={<CustomTooltip />}/>
              </PieChart>
            </ResponsiveContainer>
            <div style={{ flex: 1 }}>
              {RISK.map((r, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <div style={{ width: 8, height: 8, borderRadius: 2, background: r.color, flexShrink: 0 }}/>
                  <span style={{ fontSize: 11.5, color: C.text, flex: 1 }}>{r.name}</span>
                  <span style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: C.dim }}>{r.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-title">RECOMMENDED ACTIONS</div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={ACTIONS} margin={{ left: -20, right: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={C.border} horizontal={true} vertical={false}/>
              <XAxis dataKey="short" tick={{ fill: C.muted, fontSize: 9.5, fontFamily: 'Outfit' }} tickLine={false} axisLine={{ stroke: C.border }}/>
              <YAxis tick={{ fill: C.muted, fontSize: 9, fontFamily: 'JetBrains Mono' }} tickLine={false} axisLine={false}/>
              <Tooltip content={<CustomTooltip />}/>
              <Bar dataKey="count" name="Customers" radius={[4,4,0,0]}>
                {ACTIONS.map((_, i) => <Cell key={i} fill={SEGMENTS[i].color}/>)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="card-title">FEATURE CORRELATIONS</div>
        <CorrelationChart />
        <div style={{ display: 'flex', gap: 20, marginTop: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 12, height: 6, background: C.red, borderRadius: 2 }}/>
            <span style={{ fontFamily: 'JetBrains Mono', fontSize: 9, color: C.dim, letterSpacing: 1 }}>RISK CORR</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 12, height: 6, background: C.green, borderRadius: 2 }}/>
            <span style={{ fontFamily: 'JetBrains Mono', fontSize: 9, color: C.dim, letterSpacing: 1 }}>VALUE CORR</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function PredictPage() {
  const [open, setOpen] = useState([true, false, false, false]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    age: 45, gender: "M", marital_status: "Single",
    education_level: "Bachelor", region: "North", employment_status: "Employee",
    monthly_income: 5000, account_balance: 12000, savings_balance: 3000,
    num_products: 2, tenure_months: 36,
    credit_score: 680, credit_utilization: 0.35, num_defaults: 0,
    num_late_payments: 1, total_debt: 8000,
    days_since_last_activity: 15, complaint_count: 0,
    overdraft_count: 0, online_banking_usage: "Often"
  });

  const toggle = i => setOpen(o => o.map((v, j) => j === i ? !v : v));

  const mockPredict = () => {
    setLoading(true);
    setTimeout(() => {
      setResult({
        segment: "At-Risk Middle",
        segment_confidence: 0.72,
        risk_label: "Low Risk",
        risk_probability: 0.18,
        churn_probability: 0.31,
        churn_label: "Medium Churn Risk",
        recommended_action: "Financial Advisory + Debt Restructuring",
        action_confidence: 0.68,
        shap_features: [
          { feature: "credit_score", value: 680, impact: 0.42 },
          { feature: "num_defaults", value: 0, impact: -0.31 },
          { feature: "credit_utilization", value: 0.35, impact: 0.28 },
          { feature: "days_since_last_activity", value: 15, impact: -0.19 },
          { feature: "monthly_income", value: 5000, impact: -0.14 },
        ]
      });
      setLoading(false);
    }, 1200);
  };

  const segColor = SEGMENTS.find(s => s.name === result?.segment)?.color || C.accent;
  const churnColor = result ? (result.churn_probability > 0.5 ? C.red : result.churn_probability > 0.25 ? C.amber : C.green) : C.green;
  const maxImpact = result ? Math.max(...result.shap_features.map(f => Math.abs(f.impact))) : 1;

  const sections = [
    { label: "👤 Demographics", fields: [
      { key:"age",label:"Age",type:"number" }, { key:"gender",label:"Gender",type:"select",opts:["M","F"] },
      { key:"marital_status",label:"Marital",type:"select",opts:["Single","Married","Divorced"] },
      { key:"education_level",label:"Education",type:"select",opts:["High School","Bachelor","Master","PhD"] },
      { key:"region",label:"Region",type:"select",opts:["North","South","Center","East","West"] },
      { key:"employment_status",label:"Employment",type:"select",opts:["Employee","Self-Employed","Retired","Unemployed"] },
    ]},
    { label: "💰 Financial", fields: [
      { key:"monthly_income",label:"Monthly Income",type:"number" }, { key:"account_balance",label:"Account Balance",type:"number" },
      { key:"savings_balance",label:"Savings",type:"number" }, { key:"num_products",label:"Products",type:"number" },
      { key:"tenure_months",label:"Tenure (months)",type:"number" },
    ]},
    { label: "📊 Credit Profile", fields: [
      { key:"credit_score",label:"Credit Score",type:"number" }, { key:"credit_utilization",label:"Utilization",type:"number" },
      { key:"num_defaults",label:"Defaults",type:"number" }, { key:"num_late_payments",label:"Late Payments",type:"number" },
      { key:"total_debt",label:"Total Debt",type:"number" },
    ]},
    { label: "📱 Behavior", fields: [
      { key:"days_since_last_activity",label:"Days Inactive",type:"number" }, { key:"complaint_count",label:"Complaints",type:"number" },
      { key:"overdraft_count",label:"Overdrafts",type:"number" },
      { key:"online_banking_usage",label:"Online Banking",type:"select",opts:["Never","Sometimes","Often","Always"] },
    ]},
  ];

  return (
    <div className="content">
      <div className="predict-layout">
        {/* FORM */}
        <div>
          {sections.map((sec, i) => (
            <div key={i} className="form-section">
              <div className={`form-section-header ${open[i] ? 'open' : ''}`} onClick={() => toggle(i)}>
                <span>{sec.label}</span>
                <span style={{ fontFamily: 'JetBrains Mono', fontSize: 12, color: C.muted, transform: open[i] ? 'rotate(180deg)' : 'none', display: 'inline-block', transition: '0.2s' }}>▾</span>
              </div>
              {open[i] && (
                <div className="form-section-body">
                  {sec.fields.map(f => (
                    <div key={f.key} className="field-group">
                      <label className="field-label">{f.label}</label>
                      {f.type === 'select' ? (
                        <select className="field-input" value={form[f.key]} onChange={e => setForm({...form,[f.key]:e.target.value})}>
                          {f.opts.map(o => <option key={o} value={o}>{o}</option>)}
                        </select>
                      ) : (
                        <input className="field-input" type="number" value={form[f.key]} onChange={e => setForm({...form,[f.key]:parseFloat(e.target.value)||0})}/>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          <button className="submit-btn" onClick={mockPredict} disabled={loading}>
            {loading ? "⟳ ANALYZING..." : "ANALYZE CUSTOMER →"}
          </button>
        </div>

        {/* RESULTS */}
        {result ? (
          <div className="result-grid animate-in">
            {/* Segment */}
            <div className="result-card" style={{ borderLeftColor: segColor, borderLeftWidth: 3 }}>
              <div className="result-tag">PREDICTED SEGMENT</div>
              <div className="result-segment" style={{ color: segColor }}>{result.segment}</div>
              <div style={{ display:'flex', justifyContent:'space-between', marginBottom: 6 }}>
                <span style={{ fontFamily:'JetBrains Mono', fontSize:10, color:C.muted }}>CONFIDENCE</span>
                <span style={{ fontFamily:'JetBrains Mono', fontSize:10, color:segColor }}>{(result.segment_confidence*100).toFixed(0)}%</span>
              </div>
              <div className="confidence-bar">
                <div className="confidence-fill" style={{ width:`${result.segment_confidence*100}%`, background: segColor }}/>
              </div>
            </div>

            {/* Risk */}
            <div className="result-card">
              <div className="result-tag">RISK ASSESSMENT</div>
              <div className="risk-badge" style={{
                background: result.risk_label==="High Risk" ? `${C.red}15` : `${C.green}15`,
                border: `1px solid ${result.risk_label==="High Risk" ? C.red : C.green}40`,
                color: result.risk_label==="High Risk" ? C.red : C.green
              }}>
                <span>{result.risk_label==="High Risk" ? "⬡" : "◎"}</span>
                {result.risk_label}
              </div>
              <div className="prob-text" style={{ color: result.risk_label==="High Risk" ? C.red : C.green }}>
                {(result.risk_probability*100).toFixed(1)}%
              </div>
              <div style={{ fontSize: 11, color: C.dim, marginTop: 4 }}>probability of being high-risk</div>
            </div>

            {/* Churn */}
            <div className="result-card">
              <div className="result-tag">CHURN PREDICTION</div>
              <div className="gauge-wrap">
                <GaugeChart value={result.churn_probability} color={churnColor}/>
              </div>
              <div style={{ textAlign:'center', fontFamily:'JetBrains Mono', fontSize:11, color: churnColor, letterSpacing:1 }}>
                {result.churn_label.toUpperCase()}
              </div>
            </div>

            {/* Action */}
            <div className="result-card">
              <div className="result-tag">RECOMMENDED ACTION</div>
              <div style={{ fontSize:18, marginBottom:10 }}>💼</div>
              <div style={{ fontSize:13.5, fontWeight:600, color:C.text, lineHeight:1.4, marginBottom:8 }}>
                {result.recommended_action}
              </div>
              <div style={{ display:'flex', justifyContent:'space-between' }}>
                <span style={{ fontFamily:'JetBrains Mono', fontSize:10, color:C.muted }}>CONFIDENCE</span>
                <span style={{ fontFamily:'JetBrains Mono', fontSize:10, color:C.accent }}>{(result.action_confidence*100).toFixed(0)}%</span>
              </div>
              <div className="confidence-bar" style={{ marginTop:6 }}>
                <div className="confidence-fill" style={{ width:`${result.action_confidence*100}%`, background:C.accent }}/>
              </div>
            </div>

            {/* SHAP */}
            <div className="result-card full">
              <div className="result-tag">SHAP FEATURE IMPACT — RISK MODEL</div>
              {result.shap_features.map((f, i) => (
                <div key={i} className="shap-row">
                  <div className="shap-name">{f.feature}</div>
                  <div style={{ fontFamily:'JetBrains Mono', fontSize:10, color:C.dim, width:50 }}>{f.value}</div>
                  <div className="shap-bar-wrap">
                    <div className="shap-bar-fill" style={{
                      width: `${(Math.abs(f.impact)/maxImpact)*100}%`,
                      background: f.impact > 0 ? C.red : C.green
                    }}/>
                  </div>
                  <div className="shap-val" style={{ color: f.impact > 0 ? C.red : C.green }}>
                    {f.impact > 0 ? '+' : ''}{f.impact.toFixed(3)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:400 }}>
            <div style={{ textAlign:'center' }}>
              <div style={{ fontSize:48, marginBottom:16, opacity:0.2 }}>◈</div>
              <div style={{ fontFamily:'JetBrains Mono', fontSize:11, color:C.muted, letterSpacing:2 }}>AWAITING INPUT</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ActionsPage() {
  const actions = [
    { icon:"💼", name:"Financial Advisory + Debt Restructuring", desc:"Full financial review and personalised debt management plan", count:969, color:"#f59e0b", bg:"rgba(240,165,0,0.1)" },
    { icon:"📱", name:"Standard Digital Engagement", desc:"Push digital channels and online product onboarding campaigns", count:512, color:"#00d4ff", bg:"rgba(0,212,255,0.1)" },
    { icon:"🔍", name:"Credit Review + Risk Mitigation Plan", desc:"Thorough credit audit with tailored risk reduction roadmap", count:253, color:"#ff4757", bg:"rgba(255,71,87,0.1)" },
    { icon:"📈", name:"Cross-Sell Investment & Insurance", desc:"Upsell investment accounts and bundled insurance products", count:182, color:"#00e5a0", bg:"rgba(0,229,160,0.1)" },
    { icon:"👑", name:"VIP Loyalty Program + Premium Offers", desc:"Exclusive premium tier with dedicated relationship manager", count:52, color:"#a78bfa", bg:"rgba(167,139,250,0.1)" },
    { icon:"🚫", name:"Credit Freeze + Early Warning Monitoring", desc:"Immediate credit suspension with continuous risk monitoring", count:32, color:"#ff6b9d", bg:"rgba(255,107,157,0.1)" },
  ];

  return (
    <div className="content">
      <div className="section-label">ACTION DISTRIBUTION</div>
      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="card">
          <div className="card-title">CUSTOMERS PER ACTION</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={ACTIONS} margin={{ left:-20, right:10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={C.border} horizontal vertical={false}/>
              <XAxis dataKey="short" tick={{ fill:C.muted, fontSize:9, fontFamily:'Outfit' }} tickLine={false} axisLine={{ stroke:C.border }}/>
              <YAxis tick={{ fill:C.muted, fontSize:9, fontFamily:'JetBrains Mono' }} tickLine={false} axisLine={false}/>
              <Tooltip content={<CustomTooltip />}/>
              <Bar dataKey="count" name="Customers" radius={[4,4,0,0]}>
                {actions.map((a, i) => <Cell key={i} fill={a.color}/>)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <div className="card-title">DISTRIBUTION</div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={actions} dataKey="count" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2}>
                {actions.map((a, i) => <Cell key={i} fill={a.color}/>)}
              </Pie>
              <Tooltip content={<CustomTooltip />}/>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="section-label">ACTION REGISTRY</div>
      {actions.map((a, i) => (
        <div key={i} className="action-card">
          <div className="action-icon-wrap" style={{ background:a.bg }}>
            <span>{a.icon}</span>
          </div>
          <div style={{ flex: 1 }}>
            <div className="action-name">{a.name}</div>
            <div className="action-desc">{a.desc}</div>
          </div>
          <div className="action-count">
            {a.count}
            <div className="action-count-sub">clients</div>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── LOGIN PAGE ───────────────────────────────────────────
function LoginPage({ onLogin }) {
  const [step, setStep] = useState("login"); // login | otp
  const [form, setForm] = useState({ enterprise:"", username:"", password:"", otp:"" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [otpDigits, setOtpDigits] = useState(["","","","",""]);
  const otpRefs = [useRef(),useRef(),useRef(),useRef(),useRef()];

  // Demo credentials
  const DEMO = { enterprise:"AlphaBank", username:"khawla.hawari", password:"demo1234" };

  const handleLogin = () => {
    setError("");
    if (!form.enterprise.trim()) { setError("Enterprise name is required."); return; }
    if (!form.username.trim())   { setError("Username is required."); return; }
    if (!form.password.trim())   { setError("Password is required."); return; }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setStep("otp");
    }, 1200);
  };

  const handleOtp = () => {
    const code = otpDigits.join("");
    if (code.length < 5) { setError("Enter the full 5-digit code."); return; }
    setLoading(true);
    setError("");
    setTimeout(() => {
      setLoading(false);
      onLogin({ enterprise: form.enterprise, username: form.username });
    }, 900);
  };

  const handleOtpKey = (i, e) => {
    const val = e.target.value.replace(/\D/g,"").slice(-1);
    const next = [...otpDigits]; next[i] = val; setOtpDigits(next);
    if (val && i < 4) otpRefs[i+1].current.focus();
    if (!val && e.nativeEvent.inputType === "deleteContentBackward" && i > 0) otpRefs[i-1].current.focus();
  };

  const fillDemo = () => setForm({ ...form, enterprise:DEMO.enterprise, username:DEMO.username, password:DEMO.password });

  const features = [
    { icon:"◈", title:"4-Model ML Pipeline", desc:"Segmentation, Risk Detection, Churn Prediction & Action Recommendations" },
    { icon:"⬡", title:"Real-Time Predictions", desc:"Single customer or batch Excel upload with instant results" },
    { icon:"⬟", title:"SHAP Explainability",  desc:"Transparent AI decisions with feature impact explanations" },
    { icon:"▦", title:"Analytics Dashboard",  desc:"Live KPIs, segment distributions and risk correlations" },
  ];

  return (
    <div className="login-shell">
      {/* LEFT PANEL */}
      <div className="login-left">
        <div className="login-left-grid"/>
        <div className="login-left-glow"/>

        <div className="login-brand">
          <div className="login-brand-name">SmartBank</div>
          <div className="login-brand-tag">ML ANALYTICS PLATFORM</div>
        </div>

        <div style={{ position:"relative", zIndex:1 }}>
          <div style={{ fontFamily:"DM Serif Display,serif", fontSize:32, color:"#fff", lineHeight:1.2, marginBottom:16 }}>
            Customer Intelligence<br/>
            <span style={{ color:"#00d4ff" }}>at Enterprise Scale</span>
          </div>
          <div style={{ fontSize:13.5, color:"#6b8aad", lineHeight:1.6, marginBottom:36, maxWidth:380 }}>
            Predict segment, risk, churn and recommended actions for every customer — powered by 4 calibrated ML models.
          </div>
          <div className="login-feature-list">
            {features.map((f,i) => (
              <div key={i} className="login-feature-item">
                <div className="login-feature-icon" style={{ color:"#00d4ff" }}>{f.icon}</div>
                <div>
                  <div className="login-feature-title">{f.title}</div>
                  <div className="login-feature-desc">{f.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="login-copy">
          © 2025 SmartBank Analytics · Khawla Hawari · v1.0.0
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="login-right">
        <div className="login-form-wrap">

          {/* Logo mark */}
          <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:32 }}>
            <div style={{ width:38, height:38, borderRadius:10, background:"rgba(0,212,255,0.1)", border:"1px solid rgba(0,212,255,0.25)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:18, color:"#00d4ff" }}>◈</div>
            <div>
              <div style={{ fontFamily:"DM Serif Display,serif", fontSize:16, color:"#fff" }}>SmartBank</div>
              <div style={{ fontFamily:"JetBrains Mono", fontSize:8, color:"#4a6080", letterSpacing:2 }}>ANALYTICS</div>
            </div>
          </div>

          {step === "login" ? (
            <>
              <div className="login-title">Welcome back</div>
              <div className="login-subtitle">Sign in to your analytics workspace</div>

              {error && <div className="login-error">⚠ {error}</div>}

              <div className="login-field">
                <label className="login-label">Enterprise Name</label>
                <input className="login-input" placeholder="e.g. AlphaBank" value={form.enterprise}
                  onChange={e=>setForm({...form,enterprise:e.target.value})}
                  onKeyDown={e=>e.key==="Enter"&&handleLogin()}/>
              </div>

              <div className="login-field">
                <label className="login-label">Username / Email</label>
                <input className="login-input" placeholder="you@enterprise.com" value={form.username}
                  onChange={e=>setForm({...form,username:e.target.value})}
                  onKeyDown={e=>e.key==="Enter"&&handleLogin()}/>
              </div>

              <div className="login-field">
                <label className="login-label">Password</label>
                <input className="login-input" type="password" placeholder="••••••••" value={form.password}
                  onChange={e=>setForm({...form,password:e.target.value})}
                  onKeyDown={e=>e.key==="Enter"&&handleLogin()}/>
              </div>

              <div style={{ display:"flex", justifyContent:"flex-end", marginBottom:20 }}>
                <span style={{ fontSize:12, color:"#00d4ff", cursor:"pointer", fontFamily:"Outfit" }}>Forgot password?</span>
              </div>

              <button className="login-btn" onClick={handleLogin} disabled={loading}>
                {loading ? "AUTHENTICATING..." : "SIGN IN →"}
              </button>

              <div className="login-divider">DEMO ACCESS</div>

              <button onClick={fillDemo} style={{ width:"100%", padding:"11px", borderRadius:10, border:"1px solid #112240", background:"transparent", color:"#6b8aad", fontSize:12.5, cursor:"pointer", fontFamily:"Outfit", transition:"all 0.15s" }}
                onMouseEnter={e=>e.target.style.borderColor="#00d4ff55"}
                onMouseLeave={e=>e.target.style.borderColor="#112240"}>
                Fill demo credentials
              </button>

              <div className="login-info-strip">
                <span style={{ fontSize:16 }}>🔒</span>
                <div className="login-info-text">
                  Protected by enterprise SSO. All sessions are encrypted and audited.
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="login-title">Verify your identity</div>
              <div className="login-subtitle" style={{ marginBottom:28 }}>
                Enter the 5-digit code sent to your registered device for <span style={{ color:"#fff" }}>{form.username}</span>
              </div>

              {error && <div className="login-error">⚠ {error}</div>}

              <div style={{ display:"flex", gap:10, justifyContent:"center", marginBottom:28 }}>
                {otpDigits.map((d,i) => (
                  <input key={i} ref={otpRefs[i]} value={d} onChange={e=>handleOtpKey(i,e)}
                    maxLength={1} inputMode="numeric"
                    style={{ width:54, height:62, textAlign:"center", fontFamily:"JetBrains Mono", fontSize:24, fontWeight:700,
                      background:"#0c1525", border:`1px solid ${d?"#00d4ff":"#112240"}`,
                      borderRadius:10, color:"#fff", outline:"none", transition:"border-color 0.15s",
                      boxShadow: d?"0 0 0 3px rgba(0,212,255,0.08)":"none" }}/>
                ))}
              </div>

              <button className="login-btn" onClick={handleOtp} disabled={loading}>
                {loading ? "VERIFYING..." : "CONFIRM →"}
              </button>

              <div style={{ textAlign:"center", marginTop:16 }}>
                <span style={{ fontSize:12, color:"#4a6080", fontFamily:"Outfit" }}>Didn't receive a code? </span>
                <span style={{ fontSize:12, color:"#00d4ff", cursor:"pointer", fontFamily:"Outfit" }}>Resend</span>
              </div>

              <button onClick={()=>{setStep("login");setError("");setOtpDigits(["","","","",""]);}} style={{ width:"100%", marginTop:12, padding:"10px", background:"transparent", border:"none", color:"#4a6080", fontSize:12.5, cursor:"pointer", fontFamily:"Outfit" }}>
                ← Back to sign in
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}


// ── CHAT ASSISTANT ────────────────────────────────────────
const CHAT_KNOWLEDGE = {
  "high risk": "Currently **{highRisk} customers** are flagged as High Risk. They have elevated default counts, credit utilization and late payments. Recommended action: Credit Review or Credit Freeze.",
  "churn": "Average churn probability across all segments is **28.9%**. High Risk Low Value segment has the highest churn at 31.2%. Consider proactive outreach.",
  "segment": "The dataset has 6 segments. **At-Risk Middle** is the largest at 48.5% (969 customers). **Strategic Premium** is the smallest at 2.6% (52 customers).",
  "model": "4 ML models are deployed: Segmentation (F1=0.56), Risk Detection (AUC=0.997), Churn Prediction (AUC=0.961) and Action Recommendation (Top-3=0.987).",
  "action": "The most recommended action is **Financial Advisory + Debt Restructuring** (969 customers), followed by **Digital Engagement** (512) and **Credit Review** (253).",
  "accuracy": "Risk Detection achieves AUC-ROC of 0.997 with 100% recall — zero high-risk customers are missed. Churn AUC is 0.961.",
  "predict": "Go to the **Predict** page to analyze a single customer, or use **Batch Upload** to score an entire Excel file at once.",
  "batch": "The Batch Upload page accepts .xlsx, .xls or .csv files up to 500 rows. After upload you get a preview, run predictions, then filter and export the results.",
  "shap": "SHAP (SHapley Additive exPlanations) shows which features pushed the risk score up or down for each customer. See it on the Predict page after analysis.",
  "default": "I can answer questions about customer segments, risk scores, churn probability, model performance, and how to use the platform. What would you like to know?",
};

const BOT_SUGGESTIONS = [
  "How many high risk customers?",
  "What is the churn rate?",
  "Explain model accuracy",
  "How to batch predict?",
  "What is SHAP?",
];

function ChatAssistant({ user }) {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState([
    { role:"bot", text:`Hello **${user?.username || "Analyst"}** 👋 I'm your Smart Banking AI assistant. Ask me anything about your customers, models, or how to use the platform.`, time: new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) }
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const bottomRef = useRef();

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior:"smooth" });
  }, [msgs, open, typing]);

  const getResponse = (q) => {
    const lq = q.toLowerCase();
    for (const [key, val] of Object.entries(CHAT_KNOWLEDGE)) {
      if (lq.includes(key)) return val.replace("{highRisk}", "112");
    }
    if (lq.includes("hello") || lq.includes("hi")) return "Hello! How can I help you with Smart Banking analytics today?";
    if (lq.includes("help")) return "I can help with: customer segments, risk detection, churn analysis, model metrics, batch predictions, and platform navigation.";
    if (lq.includes("dashboard")) return "The Dashboard shows 4 model KPIs, segment distribution, churn by segment, risk distribution and feature correlations.";
    return CHAT_KNOWLEDGE["default"];
  };

  const formatMsg = (text) => {
    return text.replace(/\*\*(.*?)\*\*/g, (_, m) =>
      `<strong style="color:#e2e8f0">${m}</strong>`
    );
  };

  const sessionId = useRef("session-" + Math.random().toString(36).slice(2));

  const send = async (text) => {
    const q = (text || input).trim();
    if (!q) return;
    const time = new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
    setMsgs(m => [...m, { role:"user", text:q, time }]);
    setInput(""); setTyping(true);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: q, session_id: sessionId.current }),
      });
      const data = await res.json();
      setTyping(false);
      setMsgs(m => [...m, { role:"bot", text: data.reply || getResponse(q), time: new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}) }]);
    } catch {
      setTyping(false);
      setMsgs(m => [...m, { role:"bot", text: getResponse(q), time: new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}) }]);
    }
  };
  return (
    <>
      {/* FAB */}
      <button className="chat-btn" onClick={() => setOpen(o => !o)} title="AI Assistant">
        {open ? "✕" : "◈"}
      </button>

      {/* PANEL */}
      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <div className="chat-avatar">◈</div>
            <div style={{ flex:1 }}>
              <div className="chat-header-name">Smart Banking AI</div>
              <div className="chat-header-status">
                <span style={{ width:5,height:5,borderRadius:"50%",background:"#00e5a0",display:"inline-block",boxShadow:"0 0 6px #00e5a0" }}/>
                ONLINE
              </div>
            </div>
            <button onClick={() => setMsgs([msgs[0]])} title="Clear chat" style={{ background:"none",border:"none",color:"#4a6080",cursor:"pointer",fontSize:13,padding:4 }}>⟳</button>
          </div>

          <div className="chat-messages">
            {msgs.map((m, i) => (
              <div key={i} className={`chat-msg ${m.role}`}>
                {m.role==="bot" && <div style={{ width:26,height:26,borderRadius:8,background:"rgba(0,212,255,0.1)",border:"1px solid rgba(0,212,255,0.2)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:12,color:"#00d4ff",flexShrink:0 }}>◈</div>}
                <div>
                  <div className={`chat-bubble ${m.role}`} dangerouslySetInnerHTML={{ __html: formatMsg(m.text) }}/>
                  <div className={`chat-time`} style={{ textAlign: m.role==="user"?"right":"left" }}>{m.time}</div>
                </div>
              </div>
            ))}
            {typing && (
              <div className="chat-msg bot">
                <div style={{ width:26,height:26,borderRadius:8,background:"rgba(0,212,255,0.1)",border:"1px solid rgba(0,212,255,0.2)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:12,color:"#00d4ff",flexShrink:0 }}>◈</div>
                <div className="chat-typing">
                  <div className="typing-dot"/><div className="typing-dot"/><div className="typing-dot"/>
                </div>
              </div>
            )}
            <div ref={bottomRef}/>
          </div>

          {msgs.length <= 2 && (
            <div className="chat-suggestions">
              {BOT_SUGGESTIONS.map((s,i) => (
                <div key={i} className="chat-chip" onClick={() => send(s)}>{s}</div>
              ))}
            </div>
          )}

          <div className="chat-input-row">
            <textarea className="chat-input" placeholder="Ask anything..." rows={1} value={input}
              onChange={e=>setInput(e.target.value)}
              onKeyDown={e=>{ if(e.key==="Enter"&&!e.shiftKey){ e.preventDefault(); send(); } }}/>
            <button className="chat-send" onClick={()=>send()}>➤</button>
          </div>
        </div>
      )}
    </>
  );
}

// ── BATCH PAGE ────────────────────────────────────────────
function BatchPage() {
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState(null);
  const [rawRows, setRawRows] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [step, setStep] = useState("upload");
  const [filterSeg, setFilterSeg] = useState("ALL");
  const [filterRisk, setFilterRisk] = useState("ALL");
  const [sortCol, setSortCol] = useState("churn_probability");
  const [sortDir, setSortDir] = useState("desc");
  const fileRef = useRef();

  const parseFile = async (file) => {
    setError(null);
    try {
      const XLSX = await import("https://cdn.sheetjs.com/xlsx-0.20.1/package/xlsx.mjs");
      const buf = await file.arrayBuffer();
      const wb = XLSX.read(buf);
      const ws = wb.Sheets[wb.SheetNames[0]];
      let rows = XLSX.utils.sheet_to_json(ws, { defval: null });
      rows = rows.map(r => {
        const clean = {};
        Object.entries(r).forEach(([k, v]) => { clean[k.toLowerCase().replace(/\s+/g, "_")] = v; });
        return clean;
      });
      if (rows.length === 0) { setError("File is empty or unreadable."); return; }
      if (rows.length > 500) { setError("Max 500 rows per batch."); return; }
      setFileName(file.name); setRawRows(rows); setResults([]); setStep("preview");
    } catch (e) { setError("Could not parse file. Use .xlsx or .csv"); }
  };

  const handleDrop = (e) => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) parseFile(f); };
  const handleFileInput = (e) => { const f = e.target.files[0]; if (f) parseFile(f); };

  const SEGS = ["At-Risk Middle","Standard","High Value High Risk","Growth Potential","Strategic Premium","High Risk Low Value"];
  const ACTS = ["Financial Advisory + Debt Restructuring","Standard Digital Engagement","Credit Review + Risk Mitigation Plan","Cross-Sell Investment & Insurance","VIP Loyalty Program + Premium Offers","Credit Freeze + Early Warning Monitoring"];

  const runBatch = async () => {
    setLoading(true); setProgress(0); setError(null);
    const out = [];
    for (let i = 0; i < rawRows.length; i++) {
      await new Promise(r => setTimeout(r, 15));
      const si = Math.floor(Math.random() * 6);
      out.push({ ...rawRows[i], _id: i+1, segment: SEGS[si],
        segment_confidence: +(0.55 + Math.random()*0.44).toFixed(3),
        risk_label: Math.random() > 0.85 ? "High Risk" : "Low Risk",
        risk_probability: +(Math.random()*0.6).toFixed(3),
        churn_probability: +(Math.random()*0.55).toFixed(3),
        churn_label: Math.random()>0.7?"High Churn Risk":Math.random()>0.4?"Medium Churn Risk":"Low Churn Risk",
        recommended_action: ACTS[si],
        action_confidence: +(0.55+Math.random()*0.44).toFixed(3),
      });
      setProgress(Math.round(((i+1)/rawRows.length)*100));
    }
    setResults(out); setStep("results"); setLoading(false);
  };

  const exportCSV = async () => {
    const XLSX = await import("https://cdn.sheetjs.com/xlsx-0.20.1/package/xlsx.mjs");
    const cols = ["_id","customer_id","segment","segment_confidence","risk_label","risk_probability","churn_probability","churn_label","recommended_action","action_confidence"];
    const data = filtered.map(r => { const o={}; cols.forEach(c=>{ if(r[c]!==undefined) o[c]=r[c]; }); return o; });
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Predictions");
    XLSX.writeFile(wb, "smartbank_predictions.xlsx");
  };

  const segOptions = ["ALL", ...new Set(results.map(r => r.segment))];
  const filtered = results
    .filter(r => filterSeg==="ALL" || r.segment===filterSeg)
    .filter(r => filterRisk==="ALL" || r.risk_label===filterRisk)
    .sort((a,b) => { const av=a[sortCol]??0, bv=b[sortCol]??0; return sortDir==="desc"?bv-av:av-bv; });

  const stats = results.length ? {
    total: results.length,
    highRisk: results.filter(r=>r.risk_label==="High Risk").length,
    highChurn: results.filter(r=>r.churn_probability>0.4).length,
    avgChurn: (results.reduce((s,r)=>s+r.churn_probability,0)/results.length).toFixed(3),
    segCounts: SEGMENTS.map(s=>({ name:s.name, color:s.color, count:results.filter(r=>r.segment===s.name).length })).filter(s=>s.count>0).sort((a,b)=>b.count-a.count),
  } : null;

  const segColor = (name) => SEGMENTS.find(s=>s.name===name)?.color || C.accent;
  const thClick = (col) => { if(sortCol===col) setSortDir(d=>d==="desc"?"asc":"desc"); else { setSortCol(col); setSortDir("desc"); } };

  const btnStyle = (col) => ({
    background: "linear-gradient(135deg,rgba(0,212,255,0.15),rgba(0,212,255,0.05))",
    border:`1px solid rgba(0,212,255,0.4)`, borderRadius:8, color:C.accent,
    padding:"9px 22px", fontSize:13, fontWeight:600, cursor:"pointer", fontFamily:"Outfit", letterSpacing:0.5,
  });

  return (
    <div className="content">

      {/* UPLOAD STEP */}
      {step==="upload" && <>
        <div className="section-label">BATCH PREDICTION — EXCEL UPLOAD</div>
        <div
          onDragOver={e=>{e.preventDefault();setDragOver(true);}}
          onDragLeave={()=>setDragOver(false)}
          onDrop={handleDrop}
          onClick={()=>fileRef.current.click()}
          style={{
            border:`2px dashed ${dragOver?C.accent:C.border}`, borderRadius:16,
            padding:"64px 32px", textAlign:"center", cursor:"pointer",
            background:dragOver?"rgba(0,212,255,0.04)":C.card, transition:"all 0.2s", marginBottom:24,
          }}
        >
          <div style={{fontSize:52,marginBottom:16,filter:dragOver?"drop-shadow(0 0 14px #00d4ff)":"none",transition:"0.2s"}}>⬆</div>
          <div style={{fontFamily:"DM Serif Display,serif",fontSize:24,color:"#fff",marginBottom:8}}>Drop your Excel file here</div>
          <div style={{fontFamily:"JetBrains Mono",fontSize:11,color:C.muted,letterSpacing:1}}>SUPPORTS .XLSX · .XLS · .CSV — MAX 500 ROWS</div>
          <div style={{display:"inline-flex",alignItems:"center",gap:8,marginTop:20,padding:"9px 22px",borderRadius:8,border:`1px solid ${C.border}`,color:C.dim,fontSize:12.5,fontFamily:"Outfit"}}>
            or click to browse
          </div>
          <input ref={fileRef} type="file" accept=".xlsx,.xls,.csv" style={{display:"none"}} onChange={handleFileInput}/>
        </div>

        {error && <div style={{background:"rgba(255,71,87,0.08)",border:`1px solid ${C.red}40`,borderRadius:10,padding:"14px 18px",color:C.red,fontFamily:"JetBrains Mono",fontSize:12,marginBottom:16}}>⚠ {error}</div>}

        <div className="card">
          <div className="card-title">EXPECTED COLUMNS (all optional)</div>
          <div style={{display:"flex",flexWrap:"wrap",gap:8,marginBottom:12}}>
            {["customer_id","age","monthly_income","credit_score","num_products","tenure_months","num_defaults","credit_utilization","num_late_payments","days_since_last_activity","complaint_count","gender","region","employment_status"].map(col=>(
              <div key={col} style={{fontFamily:"JetBrains Mono",fontSize:10,color:C.dim,background:C.bg,border:`1px solid ${C.border}`,borderRadius:5,padding:"5px 10px"}}>
                {col}
              </div>
            ))}
          </div>
          <div style={{fontSize:11,color:C.muted}}>Column names are case-insensitive. Missing values are filled with 0 automatically.</div>
        </div>
      </>}

      {/* PREVIEW STEP */}
      {step==="preview" && <>
        <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:20}}>
          <div>
            <div style={{display:"flex",alignItems:"center",gap:12}}>
              <div style={{fontFamily:"DM Serif Display,serif",fontSize:20,color:"#fff"}}>{fileName}</div>
              <div className="data-badge">{rawRows.length} ROWS</div>
              <div className="data-badge">{Object.keys(rawRows[0]||{}).length} COLS</div>
            </div>
            <div style={{fontFamily:"JetBrains Mono",fontSize:10,color:C.muted,marginTop:6,letterSpacing:1}}>PREVIEW — FIRST 5 ROWS</div>
          </div>
          <div style={{display:"flex",gap:10}}>
            <button onClick={()=>{setStep("upload");setRawRows([]);setFileName(null);}} style={{padding:"8px 18px",borderRadius:7,border:`1px solid ${C.border}`,background:"transparent",color:C.dim,fontSize:12.5,cursor:"pointer",fontFamily:"Outfit"}}>← Change File</button>
            <button onClick={runBatch} disabled={loading} style={btnStyle()}>▶ RUN PREDICTIONS</button>
          </div>
        </div>

        <div className="card" style={{overflowX:"auto",marginBottom:20}}>
          <table style={{width:"100%",borderCollapse:"collapse",minWidth:600}}>
            <thead>
              <tr>
                {Object.keys(rawRows[0]||{}).slice(0,10).map(col=>(
                  <th key={col} style={{textAlign:"left",padding:"8px 12px",fontFamily:"JetBrains Mono",fontSize:9,letterSpacing:1.5,textTransform:"uppercase",color:C.muted,borderBottom:`1px solid ${C.border}`}}>{col}</th>
                ))}
                {Object.keys(rawRows[0]||{}).length>10 && <th style={{fontFamily:"JetBrains Mono",fontSize:9,color:C.muted,padding:"8px 12px",borderBottom:`1px solid ${C.border}`}}>+{Object.keys(rawRows[0]).length-10} more</th>}
              </tr>
            </thead>
            <tbody>
              {rawRows.slice(0,5).map((row,i)=>(
                <tr key={i} style={{borderBottom:`1px solid ${C.border}40`}}>
                  {Object.values(row).slice(0,10).map((val,j)=>(
                    <td key={j} style={{padding:"8px 12px",fontFamily:"JetBrains Mono",fontSize:11,color:C.text}}>{val??"-"}</td>
                  ))}
                  {Object.keys(row).length>10 && <td style={{padding:"8px 12px",color:C.muted,fontFamily:"JetBrains Mono",fontSize:10}}>...</td>}
                </tr>
              ))}
            </tbody>
          </table>
          {rawRows.length>5 && <div style={{textAlign:"center",padding:"10px",fontFamily:"JetBrains Mono",fontSize:10,color:C.muted,letterSpacing:1}}>... AND {rawRows.length-5} MORE ROWS</div>}
        </div>
      </>}

      {/* LOADING */}
      {loading && (
        <div style={{textAlign:"center",padding:"40px 0"}}>
          <div style={{fontFamily:"DM Serif Display,serif",fontSize:22,color:"#fff",marginBottom:20}}>Running predictions...</div>
          <div style={{maxWidth:400,margin:"0 auto 12px",height:6,background:C.border,borderRadius:3,overflow:"hidden"}}>
            <div style={{height:"100%",background:`linear-gradient(90deg,${C.accent},${C.green})`,borderRadius:3,width:`${progress}%`,transition:"width 0.1s linear"}}/>
          </div>
          <div style={{fontFamily:"JetBrains Mono",fontSize:13,color:C.accent,letterSpacing:1}}>
            {progress}% — {Math.round(rawRows.length*progress/100)} / {rawRows.length} customers
          </div>
        </div>
      )}

      {/* RESULTS STEP */}
      {step==="results" && !loading && stats && <>
        <div className="section-label">BATCH RESULTS SUMMARY</div>

        {/* 4 stat cards */}
        <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:14,marginBottom:20}}>
          {[
            {label:"TOTAL PROCESSED",value:stats.total,color:C.accent,icon:"◈"},
            {label:"HIGH RISK",value:stats.highRisk,color:C.red,icon:"⬡"},
            {label:"HIGH CHURN (>40%)",value:stats.highChurn,color:C.amber,icon:"◎"},
            {label:"AVG CHURN PROB",value:stats.avgChurn,color:C.green,icon:"⬟"},
          ].map((s,i)=>(
            <div key={i} className="metric-card">
              <span className="metric-icon" style={{color:s.color}}>{s.icon}</span>
              <div className="metric-label">{s.label}</div>
              <div className="metric-value" style={{color:s.color,fontSize:26}}>{s.value}</div>
              <div className="metric-bar" style={{background:`linear-gradient(90deg,${s.color}33,${s.color})`}}/>
            </div>
          ))}
        </div>

        {/* Two mini charts */}
        <div className="grid-2" style={{marginBottom:20}}>
          <div className="card">
            <div className="card-title">SEGMENT BREAKDOWN</div>
            {stats.segCounts.map((s,i)=>(
              <div key={i} style={{display:"flex",alignItems:"center",gap:10,marginBottom:9}}>
                <div style={{width:8,height:8,borderRadius:2,background:s.color,flexShrink:0}}/>
                <div style={{flex:1,fontSize:11.5,color:C.text}}>{s.name}</div>
                <div style={{width:80,height:4,background:C.border,borderRadius:2,overflow:"hidden"}}>
                  <div style={{height:"100%",background:s.color,width:`${(s.count/stats.total)*100}%`,borderRadius:2}}/>
                </div>
                <div style={{fontFamily:"JetBrains Mono",fontSize:11,color:C.dim,width:28,textAlign:"right"}}>{s.count}</div>
              </div>
            ))}
          </div>
          <div className="card">
            <div className="card-title">RISK SPLIT</div>
            <div style={{display:"flex",alignItems:"center",gap:24}}>
              <ResponsiveContainer width={130} height={130}>
                <PieChart>
                  <Pie data={[{name:"High Risk",value:stats.highRisk},{name:"Low Risk",value:stats.total-stats.highRisk}]} dataKey="value" innerRadius={35} outerRadius={60} paddingAngle={3}>
                    <Cell fill={C.red}/><Cell fill={C.green}/>
                  </Pie>
                  <Tooltip content={<CustomTooltip/>}/>
                </PieChart>
              </ResponsiveContainer>
              <div>
                {[{c:C.red,l:"High Risk",v:stats.highRisk},{c:C.green,l:"Low Risk",v:stats.total-stats.highRisk}].map((x,i)=>(
                  <div key={i} style={{display:"flex",alignItems:"center",gap:8,marginBottom:10}}>
                    <div style={{width:10,height:10,borderRadius:2,background:x.c}}/>
                    <span style={{fontSize:12,color:C.text}}>{x.l}</span>
                    <span style={{fontFamily:"JetBrains Mono",fontSize:14,color:x.c,marginLeft:8,fontWeight:700}}>{x.v}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Filter controls */}
        <div style={{display:"flex",alignItems:"center",gap:12,marginBottom:14,flexWrap:"wrap"}}>
          <div className="section-label" style={{margin:0}}>PREDICTIONS TABLE</div>
          <div style={{flex:1}}/>
          <select value={filterSeg} onChange={e=>setFilterSeg(e.target.value)} style={{background:C.card,border:`1px solid ${C.border}`,borderRadius:7,color:C.text,fontFamily:"JetBrains Mono",fontSize:10,letterSpacing:1,padding:"6px 12px",cursor:"pointer",outline:"none"}}>
            {segOptions.map(s=><option key={s} value={s}>{s==="ALL"?"ALL SEGMENTS":s}</option>)}
          </select>
          <select value={filterRisk} onChange={e=>setFilterRisk(e.target.value)} style={{background:C.card,border:`1px solid ${C.border}`,borderRadius:7,color:C.text,fontFamily:"JetBrains Mono",fontSize:10,letterSpacing:1,padding:"6px 12px",cursor:"pointer",outline:"none"}}>
            {["ALL","High Risk","Low Risk"].map(r=><option key={r} value={r}>{r==="ALL"?"ALL RISK LEVELS":r}</option>)}
          </select>
          <button onClick={exportCSV} style={{padding:"7px 16px",borderRadius:7,background:`rgba(0,229,160,0.08)`,border:`1px solid rgba(0,229,160,0.3)`,color:C.green,fontSize:12,fontFamily:"Outfit",fontWeight:600,cursor:"pointer",letterSpacing:0.5}}>↓ EXPORT XLSX</button>
          <button onClick={()=>{setStep("upload");setRawRows([]);setResults([]);setFileName(null);}} style={{padding:"7px 16px",borderRadius:7,border:`1px solid ${C.border}`,background:"transparent",color:C.dim,fontSize:12,cursor:"pointer",fontFamily:"Outfit"}}>↑ New Upload</button>
          <div style={{fontFamily:"JetBrains Mono",fontSize:10,color:C.muted,letterSpacing:1}}>{filtered.length}/{results.length} ROWS</div>
        </div>

        {/* Results table */}
        <div className="card" style={{overflowX:"auto",padding:0}}>
          <table style={{width:"100%",borderCollapse:"collapse"}}>
            <thead>
              <tr style={{background:C.surface}}>
                {[
                  {key:"_id",label:"#"},{key:"customer_id",label:"ID"},
                  {key:"segment",label:"SEGMENT"},{key:"segment_confidence",label:"SEG CONF"},
                  {key:"risk_label",label:"RISK"},{key:"risk_probability",label:"RISK %"},
                  {key:"churn_probability",label:"CHURN %"},{key:"churn_label",label:"CHURN LABEL"},
                  {key:"recommended_action",label:"ACTION"},
                ].map(col=>(
                  <th key={col.key} onClick={()=>thClick(col.key)} style={{textAlign:"left",padding:"11px 14px",fontFamily:"JetBrains Mono",fontSize:9,letterSpacing:1.5,color:sortCol===col.key?C.accent:C.muted,borderBottom:`1px solid ${C.border}`,cursor:"pointer",userSelect:"none",whiteSpace:"nowrap"}}>
                    {col.label} {sortCol===col.key?(sortDir==="desc"?"↓":"↑"):""}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0,100).map((row,i)=>{
                const rH = row.risk_label==="High Risk";
                const cH = row.churn_probability>0.4;
                return (
                  <tr key={i}
                    style={{borderBottom:`1px solid ${C.border}30`,background:i%2===0?"transparent":`${C.surface}80`,transition:"background 0.1s"}}
                    onMouseEnter={e=>e.currentTarget.style.background="rgba(0,212,255,0.03)"}
                    onMouseLeave={e=>e.currentTarget.style.background=i%2===0?"transparent":`${C.surface}80`}
                  >
                    <td style={{padding:"9px 14px",fontFamily:"JetBrains Mono",fontSize:10,color:C.muted}}>{row._id}</td>
                    <td style={{padding:"9px 14px",fontFamily:"JetBrains Mono",fontSize:10,color:C.dim}}>{row.customer_id??"-"}</td>
                    <td style={{padding:"9px 14px"}}>
                      <span style={{display:"inline-flex",alignItems:"center",gap:5,fontSize:11,color:segColor(row.segment)}}>
                        <span style={{width:6,height:6,borderRadius:1,background:segColor(row.segment),flexShrink:0}}/>
                        {row.segment}
                      </span>
                    </td>
                    <td style={{padding:"9px 14px",fontFamily:"JetBrains Mono",fontSize:11,color:C.dim}}>{(row.segment_confidence*100).toFixed(0)}%</td>
                    <td style={{padding:"9px 14px"}}>
                      <span style={{display:"inline-block",padding:"3px 10px",borderRadius:4,fontFamily:"JetBrains Mono",fontSize:10,fontWeight:600,background:rH?`${C.red}18`:`${C.green}18`,color:rH?C.red:C.green,border:`1px solid ${rH?C.red:C.green}40`}}>
                        {row.risk_label}
                      </span>
                    </td>
                    <td style={{padding:"9px 14px"}}>
                      <div style={{display:"flex",alignItems:"center",gap:6}}>
                        <div style={{width:40,height:3,background:C.border,borderRadius:2,overflow:"hidden"}}>
                          <div style={{height:"100%",background:rH?C.red:C.green,width:`${row.risk_probability*100}%`}}/>
                        </div>
                        <span style={{fontFamily:"JetBrains Mono",fontSize:10,color:C.dim}}>{(row.risk_probability*100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td style={{padding:"9px 14px"}}>
                      <div style={{display:"flex",alignItems:"center",gap:6}}>
                        <div style={{width:40,height:3,background:C.border,borderRadius:2,overflow:"hidden"}}>
                          <div style={{height:"100%",background:cH?C.amber:C.green,width:`${row.churn_probability*100}%`}}/>
                        </div>
                        <span style={{fontFamily:"JetBrains Mono",fontSize:10,color:cH?C.amber:C.dim}}>{(row.churn_probability*100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td style={{padding:"9px 14px",fontSize:10.5,color:row.churn_label==="High Churn Risk"?C.amber:row.churn_label==="Medium Churn Risk"?C.dim:C.green}}>
                      {row.churn_label}
                    </td>
                    <td style={{padding:"9px 14px",fontSize:11,color:C.text,maxWidth:220,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>
                      {row.recommended_action}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {filtered.length>100 && (
            <div style={{textAlign:"center",padding:"12px",fontFamily:"JetBrains Mono",fontSize:10,color:C.muted,letterSpacing:1,borderTop:`1px solid ${C.border}`}}>
              SHOWING 100 / {filtered.length} ROWS — EXPORT TO SEE ALL
            </div>
          )}
        </div>
      </>}
    </div>
  );
}

// ── APP ───────────────────────────────────────────────────
export default function App() {
  const [user, setUser] = useState(null); // null = logged out
  const [page, setPage] = useState("dashboard");

  const handleLogin = (userInfo) => setUser(userInfo);
  const handleLogout = () => { setUser(null); setPage("dashboard"); };

  if (!user) return (
    <>
      <style>{injectStyles()}</style>
      <div className="scanlines"/>
      <LoginPage onLogin={handleLogin}/>
    </>
  );

  const NAV = [
    { id:"dashboard", label:"Dashboard",   icon:"▦" },
    { id:"predict",   label:"Predict",     icon:"◈" },
    { id:"batch",     label:"Batch Upload",icon:"⬡" },
    { id:"actions",   label:"Actions",     icon:"⬟" },
  ];

  const pageTitle = {
    dashboard: "Analytics Dashboard",
    predict:   "Customer Analysis",
    batch:     "Batch Prediction",
    actions:   "Action Registry",
  };

  return (
    <>
      <style>{injectStyles()}</style>
      <div className="scanlines"/>
      <div className="app-shell">
        <aside className="sidebar">
          <div className="sidebar-logo">
            <div className="logo-mark">{user.enterprise}</div>
            <div className="logo-sub">ML ANALYTICS</div>
          </div>
          <nav className="sidebar-nav">
            {NAV.map(n => (
              <div key={n.id} className={`nav-item ${page===n.id?'active':''}`} onClick={() => setPage(n.id)}>
                <span className="nav-icon">{n.icon}</span>
                {n.label}
              </div>
            ))}
          </nav>
          <div className="sidebar-footer">
            {/* User profile */}
            <div style={{ background:"#080f1e", border:"1px solid #112240", borderRadius:10, padding:"10px 12px", marginBottom:12 }}>
              <div style={{ display:"flex", alignItems:"center", gap:9 }}>
                <div style={{ width:30, height:30, borderRadius:8, background:"rgba(0,212,255,0.1)", border:"1px solid rgba(0,212,255,0.2)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:13, color:"#00d4ff", flexShrink:0 }}>
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontSize:11.5, fontWeight:600, color:"#c8d8f0", whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis" }}>{user.username}</div>
                  <div style={{ fontFamily:"JetBrains Mono", fontSize:8, color:"#4a6080", letterSpacing:1, marginTop:1 }}>ANALYST</div>
                </div>
              </div>
            </div>
            <div className="status-pill" style={{ marginBottom:8 }}>
              <div className="status-dot"/>
              API ONLINE
            </div>
            <div style={{ fontFamily:"JetBrains Mono", fontSize:9, color:C.muted, marginBottom:10, letterSpacing:1 }}>
              2,000 CUSTOMERS
            </div>
            <div onClick={handleLogout} style={{ display:"flex", alignItems:"center", gap:7, cursor:"pointer", padding:"6px 8px", borderRadius:7, transition:"background 0.15s", color:"#4a6080", fontSize:12 }}
              onMouseEnter={e=>e.currentTarget.style.background="rgba(255,71,87,0.08)"}
              onMouseLeave={e=>e.currentTarget.style.background="transparent"}>
              <span style={{ fontSize:13 }}>⎋</span> Sign out
            </div>
          </div>
        </aside>

        <main className="main">
          <header className="topbar">
            <div className="page-title">{pageTitle[page]}</div>
            <div className="topbar-right">
              <div className="data-badge" style={{ color:"#6b8aad" }}>{user.enterprise.toUpperCase()}</div>
              <div className="data-badge">4 ML MODELS</div>
              <div className="data-badge" style={{ color:C.green, borderColor:`rgba(0,229,160,0.2)`, background:`rgba(0,229,160,0.05)` }}>
                LIVE
              </div>
            </div>
          </header>

          {page === "dashboard" && <DashboardPage />}
          {page === "predict"   && <PredictPage />}
          {page === "batch"     && <BatchPage />}
          {page === "actions"   && <ActionsPage />}
        </main>
      </div>

      {/* Floating chat assistant */}
      <ChatAssistant user={user}/>
    </>
  );
}
