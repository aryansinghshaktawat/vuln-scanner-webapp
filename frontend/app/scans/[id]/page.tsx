"use client";

import { useCallback, useEffect, useState, use } from "react";
import Link from "next/link";
import Sidebar from "../../components/Sidebar";
import Topbar from "../../components/Topbar";
import { SeverityBadge, StatusBadge } from "../../components/Badges";
import RiskGauge from "../../components/RiskGauge";
import DiffViewer from "../../components/DiffViewer";
import { apiFetch, ScanRecord, DiffResult, getApiBase } from "../../lib/api";

export default function ScanDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const [scan, setScan] = useState<ScanRecord | null>(null);
  const [diff, setDiff] = useState<DiffResult | null>(null);
  const [activeTab, setActiveTab] = useState<"findings" | "ports" | "diff" | "raw">("findings");
  const [loading, setLoading] = useState(true);
  const [livePhase, setLivePhase] = useState<string>("");

  const fetchScan = useCallback(async () => {
    try {
      const data = await apiFetch<ScanRecord>(`/api/scans/${id}`);
      setScan(data);
      setLivePhase(data.progress_phase);

      if (data.status === "COMPLETED") {
        apiFetch<DiffResult>(`/api/scans/${id}/diff`)
          .then((d) => setDiff(d))
          .catch(() => {});
      }
    } catch (err) {
      console.error("Failed to fetch scan:", err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchScan();

    // Connect to Server-Sent Events (SSE) live progress stream
    const apiBase = getApiBase();
    const eventSource = new EventSource(`${apiBase}/api/scans/${id}/stream`);

    eventSource.onmessage = (event) => {
      try {
        const update = JSON.parse(event.data);
        if (update.progress_phase) setLivePhase(update.progress_phase);
        if (update.status && ["COMPLETED", "FAILED", "TIMEOUT", "CANCELLED"].includes(update.status)) {
          fetchScan();
          eventSource.close();
        }
      } catch {
        // Keepalive or parse error
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [id, fetchScan]);

  if (loading && !scan) {
    return (
      <div className="app-shell">
        <Sidebar />
        <main className="main-content" style={{ padding: "40px", textAlign: "center" }}>
          Loading assessment results...
        </main>
      </div>
    );
  }

  if (!scan) {
    return (
      <div className="app-shell">
        <Sidebar />
        <main className="main-content" style={{ padding: "40px" }}>
          <h2>Scan record not found</h2>
          <Link href="/scans" className="btn btn-outline" style={{ marginTop: "16px" }}>
            ← Back to Scans
          </Link>
        </main>
      </div>
    );
  }

  const isRunning = scan.status === "RUNNING" || scan.status === "QUEUED";
  const apiBase = getApiBase();

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <Topbar breadcrumbs={["Scan Management", `Scan ${scan.target}`]} />

        {/* Scan Header */}
        <section className="page-heading">
          <div>
            <div style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "8px" }}>
              <StatusBadge status={scan.status} />
              <span className="badge badge-info" style={{ textTransform: "capitalize" }}>
                {scan.profile} assessment
              </span>
              <span className="mono" style={{ color: "#64748b", fontSize: "11px" }}>ID: {scan.id.slice(0, 8)}</span>
            </div>
            <h1 className="mono">{scan.target}<span>.</span></h1>
            <p className="muted">
              {isRunning
                ? `Active phase: ${livePhase || scan.progress_phase}`
                : `Executed on ${scan.started_at ? new Date(scan.started_at).toLocaleString() : ""} in ${scan.duration_seconds}s`}
            </p>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <a
              href={`${apiBase}/api/reports/scans/${scan.id}?format=html`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-outline"
            >
              Print / HTML Report ↗
            </a>
            <a
              href={`${apiBase}/api/reports/scans/${scan.id}?format=csv`}
              download
              className="btn btn-outline"
            >
              Export CSV ↓
            </a>
          </div>
        </section>

        {/* Running banner if in progress */}
        {isRunning && (
          <div
            style={{
              padding: "16px 20px",
              background: "#eff6ff",
              border: "1px solid #bfdbfe",
              borderRadius: "6px",
              marginBottom: "20px",
              display: "flex",
              alignItems: "center",
              gap: "12px",
            }}
          >
            <span className="status-badge status-running"><i /></span>
            <div style={{ flex: 1 }}>
              <strong style={{ display: "block", fontSize: "12px", color: "#1e3a8a" }}>
                Scan in Progress: {livePhase || scan.progress_phase}
              </strong>
              <small style={{ color: "#3b82f6" }}>
                Live events connected. Port probing and vulnerability signatures executing in isolated worker.
              </small>
            </div>
          </div>
        )}

        {/* Failed or timeout error message */}
        {scan.error_message && (
          <div className="error-message" style={{ marginBottom: "20px" }}>
            <strong>Scan Execution Failed:</strong> {scan.error_message}
          </div>
        )}

        {/* Score & Factors Grid */}
        <div className="content-grid" style={{ marginBottom: "24px" }}>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">AUDIT ASSESSMENT</p>
                <h2>Scan Risk Score</h2>
              </div>
            </div>
            <RiskGauge score={scan.risk_score} reasons={scan.risk_reasons} />
          </section>

          <section className="panel" style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <div className="panel-heading" style={{ marginBottom: "0" }}>
              <div>
                <p className="eyebrow">SUMMARY STATS</p>
                <h2>Discovered Metrics</h2>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px", fontSize: "12px" }}>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>OPEN PORTS</span>
                <strong>{scan.open_ports.length} listening</strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>VULNERABILITIES</span>
                <strong style={{ color: scan.findings.length > 0 ? "var(--coral)" : "var(--green)" }}>
                  {scan.findings.length} detected
                </strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>SCAN DURATION</span>
                <span>{scan.duration_seconds} seconds</span>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>INITIATED BY</span>
                <span>{scan.created_by}</span>
              </div>
            </div>

            {scan.asset_id && (
              <div style={{ marginTop: "auto", borderTop: "1px solid var(--line)", paddingTop: "12px" }}>
                <Link href={`/assets/${scan.asset_id}`} className="text-link" style={{ fontWeight: 600 }}>
                  View Full Asset Posture Profile →
                </Link>
              </div>
            )}
          </section>
        </div>

        {/* Tab Navigation */}
        <div className="tab-nav">
          <button
            className={`tab-btn ${activeTab === "findings" ? "active" : ""}`}
            onClick={() => setActiveTab("findings")}
          >
            Vulnerability Findings ({scan.findings.length})
          </button>
          <button
            className={`tab-btn ${activeTab === "ports" ? "active" : ""}`}
            onClick={() => setActiveTab("ports")}
          >
            Open Ports ({scan.open_ports.length})
          </button>
          <button
            className={`tab-btn ${activeTab === "diff" ? "active" : ""}`}
            onClick={() => setActiveTab("diff")}
          >
            Differential Comparison
          </button>
          <button
            className={`tab-btn ${activeTab === "raw" ? "active" : ""}`}
            onClick={() => setActiveTab("raw")}
          >
            Raw Nmap Output
          </button>
        </div>

        {/* TAB 1: Findings */}
        {activeTab === "findings" && (
          <section className="panel" style={{ padding: "0" }}>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Severity</th>
                    <th>CVE ID</th>
                    <th>Vulnerability Title</th>
                    <th>Affected Port</th>
                    <th>CISA KEV</th>
                    <th>Detection Source</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {scan.findings.length === 0 ? (
                    <tr>
                      <td colSpan={8} style={{ textAlign: "center", padding: "30px", color: "#64748b" }}>
                        ✓ No potential vulnerabilities identified in this scan execution.
                      </td>
                    </tr>
                  ) : (
                    scan.findings.map((f) => (
                      <tr key={f.id}>
                        <td>
                          <SeverityBadge severity={f.severity} />
                        </td>
                        <td className="mono font-bold">
                          <Link href={`/vulnerabilities/${f.id}`} style={{ color: "var(--coral)", textDecoration: "none" }}>
                            {f.cve_id}
                          </Link>
                        </td>
                        <td>{f.title}</td>
                        <td className="mono">{f.affected_port ? `${f.affected_port}/${f.service || "tcp"}` : "-"}</td>
                        <td>
                          {f.is_known_exploit === "YES" ? (
                            <span className="badge badge-cisa">EXPLOITED</span>
                          ) : (
                            <span style={{ color: "#94a3b8", fontSize: "10px" }}>No KEV match</span>
                          )}
                        </td>
                        <td style={{ color: "#64748b", fontSize: "10px" }}>{f.detection_source}</td>
                        <td>
                          <span className={`badge ${f.status === "RESOLVED" ? "badge-success" : "badge-info"}`}>
                            {f.status}
                          </span>
                        </td>
                        <td>
                          <Link href={`/vulnerabilities/${f.id}`} className="text-link">
                            Track Fix →
                          </Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* TAB 2: Open Ports */}
        {activeTab === "ports" && (
          <section className="panel" style={{ padding: "0" }}>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Port</th>
                    <th>Protocol</th>
                    <th>State</th>
                    <th>Service Fingerprint</th>
                    <th>Version Details</th>
                  </tr>
                </thead>
                <tbody>
                  {scan.open_ports.length === 0 ? (
                    <tr>
                      <td colSpan={5} style={{ textAlign: "center", padding: "30px", color: "#64748b" }}>
                        No open ports detected.
                      </td>
                    </tr>
                  ) : (
                    scan.open_ports.map((p, idx) => (
                      <tr key={idx}>
                        <td className="mono font-bold">{p.port}</td>
                        <td className="mono">{p.protocol.toUpperCase()}</td>
                        <td>
                          <span className="badge badge-success">{p.state}</span>
                        </td>
                        <td>{p.service}</td>
                        <td style={{ color: "#64748b" }}>{p.version || "-"}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* TAB 3: Diff Viewer */}
        {activeTab === "diff" && (
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">SCAN COMPARISON</p>
                <h2>Changes Compared to Previous Scan</h2>
              </div>
            </div>
            <DiffViewer diff={diff} />
          </section>
        )}

        {/* TAB 4: Raw Output */}
        {activeTab === "raw" && (
          <section className="panel">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
              <span className="eyebrow">NMAP STDOUT RAW STREAM</span>
              <button
                className="btn btn-outline btn-sm"
                onClick={() => {
                  if (scan.raw_output) {
                    navigator.clipboard.writeText(scan.raw_output);
                    alert("Raw Nmap output copied to clipboard");
                  }
                }}
              >
                Copy Output
              </button>
            </div>
            <pre className="code-box">
              {scan.raw_output || "No stdout output recorded for this scan."}
            </pre>
          </section>
        )}
      </main>
    </div>
  );
}
