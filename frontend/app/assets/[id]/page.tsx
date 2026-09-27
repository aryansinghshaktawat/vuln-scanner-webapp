"use client";

import { useCallback, useEffect, useState, use } from "react";
import Link from "next/link";
import Sidebar from "../../components/Sidebar";
import Topbar from "../../components/Topbar";
import { SeverityBadge, StatusBadge, EnvironmentPill } from "../../components/Badges";
import RiskGauge from "../../components/RiskGauge";
import DiffViewer from "../../components/DiffViewer";
import NewScanModal from "../../components/NewScanModal";
import {
  apiFetch,
  Asset,
  ScanRecord,
  ScanHistoryItem,
  VulnerabilityFinding,
  DiffResult,
} from "../../lib/api";

export default function AssetDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const [asset, setAsset] = useState<Asset | null>(null);
  const [scans, setScans] = useState<ScanHistoryItem[]>([]);
  const [latestScan, setLatestScan] = useState<ScanRecord | null>(null);
  const [findings, setFindings] = useState<VulnerabilityFinding[]>([]);
  const [diff, setDiff] = useState<DiffResult | null>(null);
  const [activeTab, setActiveTab] = useState<"ports" | "vulns" | "diff" | "history">("vulns");
  const [loading, setLoading] = useState(true);
  const [isScanOpen, setIsScanOpen] = useState(false);

  const loadAssetDetails = useCallback(async () => {
    try {
      const [assetData, scansData, vulnsData, diffData] = await Promise.all([
        apiFetch<Asset>(`/api/assets/${id}`),
        apiFetch<ScanHistoryItem[]>(`/api/assets/${id}/scans`),
        apiFetch<VulnerabilityFinding[]>(`/api/assets/${id}/vulnerabilities`),
        apiFetch<DiffResult>(`/api/assets/${id}/diff`),
      ]);

      setAsset(assetData);
      setScans(scansData || []);
      setFindings(vulnsData || []);
      setDiff(diffData);

      if (scansData && scansData.length > 0) {
        const fullScan = await apiFetch<ScanRecord>(`/api/scans/${scansData[0].id}`);
        setLatestScan(fullScan);
      }
    } catch (err) {
      console.error("Failed to load asset details:", err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadAssetDetails();
  }, [loadAssetDetails]);

  if (loading) {
    return (
      <div className="app-shell">
        <Sidebar />
        <main className="main-content" style={{ padding: "40px", textAlign: "center" }}>
          Loading asset profile...
        </main>
      </div>
    );
  }

  if (!asset) {
    return (
      <div className="app-shell">
        <Sidebar />
        <main className="main-content" style={{ padding: "40px" }}>
          <h2>Asset not found</h2>
          <Link href="/assets" className="btn btn-outline" style={{ marginTop: "16px" }}>
            ← Back to Inventory
          </Link>
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <Topbar breadcrumbs={["Asset Inventory", asset.name]} />

        {/* Asset Header */}
        <section className="page-heading">
          <div>
            <div style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "8px" }}>
              <EnvironmentPill environment={asset.environment} />
              <span className={`badge ${asset.criticality === "critical" ? "badge-critical" : "badge-medium"}`}>
                {asset.criticality}
              </span>
              <span className="mono" style={{ color: "#64748b", fontSize: "11px" }}>{asset.target}</span>
            </div>
            <h1>{asset.name}<span>.</span></h1>
            <p className="muted">{asset.description || "Perimeter network asset under continuous assessment."}</p>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            {latestScan && (
              <a
                href={`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/reports/scans/${latestScan.id}?format=html`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline"
              >
                Export Report ↗
              </a>
            )}
            <button className="btn btn-primary" onClick={() => setIsScanOpen(true)}>
              Run Scan ↗
            </button>
          </div>
        </section>

        {/* Posture Summary Grid */}
        <div className="content-grid" style={{ marginBottom: "24px" }}>
          {/* Risk Gauge Card */}
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">RISK & ATTACK SURFACE</p>
                <h2>Asset Risk Score</h2>
              </div>
              <span className="status-badge status-completed">
                <i /> {asset.scan_status}
              </span>
            </div>

            <RiskGauge
              score={asset.current_risk_score}
              reasons={latestScan?.risk_reasons || []}
            />
          </section>

          {/* Quick Stats Card */}
          <section className="panel" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div className="panel-heading" style={{ marginBottom: "0" }}>
              <div>
                <p className="eyebrow">OPERATIONAL CONTEXT</p>
                <h2>Asset Metadata</h2>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px", fontSize: "12px" }}>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>RESPONSIBLE OWNER</span>
                <strong>{asset.owner}</strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>TARGET DESTINATION</span>
                <strong className="mono">{asset.target}</strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>OPEN PORTS DETECTED</span>
                <strong>{latestScan ? latestScan.open_ports.length : 0} ports</strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>ACTIVE CVEs</span>
                <strong style={{ color: findings.length > 0 ? "var(--coral)" : "var(--green)" }}>
                  {findings.length} findings
                </strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>LAST AUDITED</span>
                <span>{asset.last_scanned_at ? new Date(asset.last_scanned_at).toLocaleString() : "Never"}</span>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>TAGS</span>
                <span>{asset.tags || "None"}</span>
              </div>
            </div>
          </section>
        </div>

        {/* Tab Navigation */}
        <div className="tab-nav">
          <button
            className={`tab-btn ${activeTab === "vulns" ? "active" : ""}`}
            onClick={() => setActiveTab("vulns")}
          >
            Vulnerabilities ({findings.length})
          </button>
          <button
            className={`tab-btn ${activeTab === "diff" ? "active" : ""}`}
            onClick={() => setActiveTab("diff")}
          >
            Vulnerability Diff (Scan vs Scan)
          </button>
          <button
            className={`tab-btn ${activeTab === "ports" ? "active" : ""}`}
            onClick={() => setActiveTab("ports")}
          >
            Open Ports & Services ({latestScan?.open_ports.length || 0})
          </button>
          <button
            className={`tab-btn ${activeTab === "history" ? "active" : ""}`}
            onClick={() => setActiveTab("history")}
          >
            Scan History ({scans.length})
          </button>
        </div>

        {/* TAB 1: Vulnerabilities */}
        {activeTab === "vulns" && (
          <section className="panel" style={{ padding: "0" }}>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Severity</th>
                    <th>CVE Identifier</th>
                    <th>Vulnerability Title</th>
                    <th>Affected Port</th>
                    <th>Status</th>
                    <th>First Seen</th>
                    <th>Remediation Owner</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {findings.length === 0 ? (
                    <tr>
                      <td colSpan={8} style={{ textAlign: "center", padding: "30px", color: "#64748b" }}>
                        ✓ No active vulnerabilities currently detected on this asset.
                      </td>
                    </tr>
                  ) : (
                    findings.map((f) => (
                      <tr key={f.id}>
                        <td>
                          <SeverityBadge severity={f.severity} />
                        </td>
                        <td className="mono font-bold">
                          <Link href={`/vulnerabilities/${f.id}`} style={{ color: "var(--coral)", textDecoration: "none" }}>
                            {f.cve_id}
                          </Link>
                          {f.is_known_exploit === "YES" && (
                            <span className="badge badge-cisa" style={{ marginLeft: "6px" }}>
                              KEV
                            </span>
                          )}
                        </td>
                        <td>{f.title}</td>
                        <td className="mono">{f.affected_port ? `${f.affected_port}/${f.service || "tcp"}` : "-"}</td>
                        <td>
                          <span className={`badge ${f.status === "RESOLVED" ? "badge-success" : "badge-info"}`}>
                            {f.status}
                          </span>
                        </td>
                        <td>{new Date(f.first_seen).toLocaleDateString()}</td>
                        <td>{f.remediation_owner || "Unassigned"}</td>
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

        {/* TAB 2: Vulnerability Diff */}
        {activeTab === "diff" && (
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">DIFFERENTIAL ANALYSIS</p>
                <h2>Latest Scan vs Previous Scan</h2>
              </div>
            </div>
            <DiffViewer diff={diff} />
          </section>
        )}

        {/* TAB 3: Ports & Services */}
        {activeTab === "ports" && (
          <section className="panel" style={{ padding: "0" }}>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Port Number</th>
                    <th>Protocol</th>
                    <th>State</th>
                    <th>Service Fingerprint</th>
                    <th>Detected Version</th>
                  </tr>
                </thead>
                <tbody>
                  {!latestScan || latestScan.open_ports.length === 0 ? (
                    <tr>
                      <td colSpan={5} style={{ textAlign: "center", padding: "30px", color: "#64748b" }}>
                        No listening ports detected in the most recent assessment.
                      </td>
                    </tr>
                  ) : (
                    latestScan.open_ports.map((p, idx) => (
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

        {/* TAB 4: Scan History */}
        {activeTab === "history" && (
          <section className="panel" style={{ padding: "0" }}>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Profile</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Open Ports</th>
                    <th>Findings</th>
                    <th>Risk Score</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {scans.length === 0 ? (
                    <tr>
                      <td colSpan={8} style={{ textAlign: "center", padding: "30px", color: "#64748b" }}>
                        No scans recorded for this asset yet.
                      </td>
                    </tr>
                  ) : (
                    scans.map((s) => (
                      <tr key={s.id}>
                        <td>{s.started_at ? new Date(s.started_at).toLocaleString() : "Pending"}</td>
                        <td style={{ textTransform: "capitalize" }}>{s.profile}</td>
                        <td>
                          <StatusBadge status={s.status} />
                        </td>
                        <td>{s.duration_seconds}s</td>
                        <td>{s.open_ports_count}</td>
                        <td>{s.vulnerabilities_count}</td>
                        <td>
                          <span style={{ fontWeight: 700, color: s.risk_score >= 60 ? "var(--coral)" : "var(--teal)" }}>
                            {s.risk_score} / 100
                          </span>
                        </td>
                        <td>
                          <Link href={`/scans/${s.id}`} className="text-link">
                            View Results →
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
      </main>

      <NewScanModal
        isOpen={isScanOpen}
        onClose={() => setIsScanOpen(false)}
        assets={[asset]}
        defaultTarget={asset.target}
        defaultAssetId={asset.id}
      />
    </div>
  );
}
