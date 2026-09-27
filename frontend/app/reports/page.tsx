"use client";

import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { apiFetch, ScanHistoryItem, getApiBase } from "../lib/api";

export default function ReportsPage() {
  const [scans, setScans] = useState<ScanHistoryItem[]>([]);
  const [selectedScanId, setSelectedScanId] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<ScanHistoryItem[]>("/api/scans?limit=50")
      .then((data) => {
        setScans(data || []);
        if (data && data.length > 0) setSelectedScanId(data[0].id);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const apiBase = getApiBase();
  const selectedScan = scans.find((s) => s.id === selectedScanId);

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <Topbar breadcrumbs={["Security Operations", "Reports & Export Center"]} />

        <section className="page-heading">
          <div>
            <p className="eyebrow">AUDIT DELIVERABLES</p>
            <h1>Security Assessment Reports<span>.</span></h1>
            <p className="muted">Generate and export compliance reports, CSV spreadsheets, and printable executive summaries.</p>
          </div>
        </section>

        {/* Report Generator Card */}
        <section className="panel" style={{ maxWidth: "720px", marginBottom: "32px" }}>
          <div className="panel-heading">
            <div>
              <p className="eyebrow">EXPORT GENERATOR</p>
              <h2>Select Assessment Run</h2>
            </div>
          </div>

          <div className="form-group">
            <label>Scan Assessment Record</label>
            <select
              className="form-control mono"
              value={selectedScanId}
              onChange={(e) => setSelectedScanId(e.target.value)}
              disabled={loading}
            >
              {scans.length === 0 ? (
                <option value="">No completed scans found</option>
              ) : (
                scans.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.target} - {s.profile} ({s.started_at ? new Date(s.started_at).toLocaleDateString() : ""}) - Risk: {s.risk_score}/100
                  </option>
                ))
              )}
            </select>
          </div>

          {selectedScan && (
            <div style={{ background: "#f8fafc", padding: "16px", borderRadius: "6px", margin: "16px 0", fontSize: "12px" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <div>Target Host: <b>{selectedScan.target}</b></div>
                <div>Risk Posture: <b>{selectedScan.risk_score} / 100</b></div>
                <div>Open Ports: <b>{selectedScan.open_ports_count}</b></div>
                <div>Detected Findings: <b>{selectedScan.vulnerabilities_count}</b></div>
              </div>
            </div>
          )}

          <div style={{ display: "flex", gap: "12px", marginTop: "20px" }}>
            <a
              href={`${apiBase}/api/reports/scans/${selectedScanId}?format=html`}
              target="_blank"
              rel="noopener noreferrer"
              className={`btn btn-primary ${!selectedScanId ? "disabled" : ""}`}
              style={{ flex: 1, textAlign: "center" }}
            >
              📄 Printable HTML Report (Print to PDF) ↗
            </a>

            <a
              href={`${apiBase}/api/reports/scans/${selectedScanId}?format=csv`}
              download
              className={`btn btn-outline ${!selectedScanId ? "disabled" : ""}`}
              style={{ flex: 1, textAlign: "center" }}
            >
              📊 Export CSV Spreadsheet ↓
            </a>

            <a
              href={`${apiBase}/api/reports/scans/${selectedScanId}?format=json`}
              target="_blank"
              rel="noopener noreferrer"
              className={`btn btn-outline ${!selectedScanId ? "disabled" : ""}`}
              style={{ flex: 1, textAlign: "center" }}
            >
              {`{ }`} Raw JSON Payload ↗
            </a>
          </div>
        </section>

        {/* Standards & Guidelines Info */}
        <section className="panel" style={{ maxWidth: "720px" }}>
          <div className="panel-heading">
            <div>
              <p className="eyebrow">DEFENSIVE COMPLIANCE & PRIVACY</p>
              <h2>Report Integrity & Content Standards</h2>
            </div>
          </div>
          <p style={{ fontSize: "12px", color: "#64748b", lineHeight: 1.5, margin: 0 }}>
            Reports contain discovered port numbers, identified service banners, CVE mappings, and scanner
            evidence. Internal credentials, database connection strings, and infrastructure secret keys are
            strictly excluded from generated artifacts.
          </p>
        </section>
      </main>
    </div>
  );
}
