"use client";

import React from "react";

interface RiskGaugeProps {
  score: number;
  reasons?: string[];
  showReasons?: boolean;
}

export default function RiskGauge({ score, reasons = [], showReasons = true }: RiskGaugeProps) {
  const safeScore = Math.max(0, Math.min(100, Math.round(score)));
  
  let label = "Healthy & Hardened";
  let color = "var(--green)";
  if (safeScore >= 80) {
    label = "Critical Exposure";
    color = "var(--coral)";
  } else if (safeScore >= 60) {
    label = "High Risk - Needs Attention";
    color = "var(--amber)";
  } else if (safeScore >= 30) {
    label = "Moderate Posture";
    color = "#457b8c";
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
        <div
          className="risk-ring"
          style={
            {
              "--score": `${safeScore * 3.6}deg`,
              background: `conic-gradient(${color} ${safeScore * 3.6}deg, #edf0ee 0)`,
            } as React.CSSProperties
          }
        >
          <div>
            <strong>{safeScore}</strong>
            <small>/ 100</small>
          </div>
        </div>

        <div>
          <span className="risk-label">RISK POSTURE</span>
          <h3 style={{ margin: "4px 0 6px", fontSize: "16px" }}>{label}</h3>
          <p style={{ margin: 0, color: "#64748b", fontSize: "11px", maxWidth: "240px" }}>
            Network risk score derived from CVE severities, CISA KEV exploitation, asset criticality, and open services.
          </p>
        </div>
      </div>

      {showReasons && reasons && reasons.length > 0 && (
        <div style={{ borderTop: "1px solid var(--line)", paddingTop: "12px" }}>
          <strong style={{ fontSize: "10px", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.8px" }}>
            Explainable Risk Factors:
          </strong>
          <ul className="reasons-list">
            {reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
