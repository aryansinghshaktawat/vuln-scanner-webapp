"use client";

import { useCallback, useEffect, useState, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import { SeverityBadge, StatusBadge } from "./components/Badges";
import RiskGauge from "./components/RiskGauge";
import NewScanModal from "./components/NewScanModal";
import AddAssetModal from "./components/AddAssetModal";
import { apiFetch, DashboardData, ScanRecord, Asset, VulnerabilityFinding } from "./lib/api";

export default function Home() {
  const router = useRouter();
  const [metrics, setMetrics] = useState<DashboardData | null>(null);
  const [recentScans, setRecentScans] = useState<ScanRecord[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [priorityFindings, setPriorityFindings] = useState<VulnerabilityFinding[]>([]);
  
  // Quick launcher state
  const [target, setTarget] = useState("");
  const [mode, setMode] = useState<"quick" | "full">("full");
  const [launching, setLaunching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modals
  const [isScanModalOpen, setIsScanModalOpen] = useState(false);
  const [isAssetModalOpen, setIsAssetModalOpen] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [dashData, scansData, assetsData, findingsData] = await Promise.all([
        apiFetch<DashboardData>("/api/dashboard"),
        apiFetch<ScanRecord[]>("/api/scans?limit=5"),
        apiFetch<Asset[]>("/api/assets"),
        apiFetch<VulnerabilityFinding[]>("/api/vulnerabilities?limit=5&status=OPEN"),
      ]);
      setMetrics(dashData);
      setRecentScans(scansData || []);
      setAssets(assetsData || []);
      setPriorityFindings(findingsData || []);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleLaunchScan = async (e: FormEvent) => {
    e.preventDefault();
    const cleanTarget = target.trim();
    if (!cleanTarget) {
      setError("Please enter an IP address, hostname, or authorized CIDR range.");
      return;
    }

    setLaunching(true);
    setError(null);
    try {
      const scan = await apiFetch<ScanRecord>("/api/scans", {
        method: "POST",
        body: JSON.stringify({
          target: cleanTarget,
          profile: mode,
        }),
      });
      setTarget("");
      router.push(`/scans/${scan.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to initiate scan.");
    } finally {
      setLaunching(false);
    }
  };

  const totalAssets = metrics?.total_assets ?? assets.length;
  const openVulns = metrics?.open_vulnerabilities ?? priorityFindings.length;
  const critVulns = metrics?.critical_vulnerabilities ?? 0;
  const highVulns = metrics?.high_vulnerabilities ?? 0;
  const medVulns = metrics?.severity_breakdown.medium ?? 0;

  // Environment risk score (weighted based on active vulns)
  const envScore = Math.min(100, Math.max(12, critVulns * 25 + highVulns * 15 + medVulns * 6 + (totalAssets > 0 ? 10 : 0)));

  return (
    <div className="app-shell">
      <Sidebar assetCount={totalAssets} />

      <main className="main-content" id="overview">
        <Topbar breadcrumbs={["Security Operations", "Overview"]} />

        <section className="page-heading">
          <div>
            <p className="eyebrow">DEFENSIVE THREAT & EXPOSURE PLATFORM</p>
            <h1>Security Posture Overview<span>.</span></h1>
            <p className="muted">Continuous perimeter asset inventory, Nmap audit history, and vulnerability remediation.</p>
          </div>
          <div style={{ display: "flex", gap: "10px" }}>
            <button className="btn btn-outline" onClick={() => setIsAssetModalOpen(true)}>
              + Add Asset
            </button>
            <button className="btn btn-primary" onClick={() => setIsScanModalOpen(true)}>
              New Scan ↗
            </button>
          </div>
        </section>

        {/* Top Key Metrics */}
        <section className="stats-grid" aria-label="Security overview metrics">
          <div className="stat-card">
            <div className="stat-top">
              <span>Monitored Assets</span>
              <span className="stat-icon blue">◈</span>
            </div>
            <strong>{totalAssets}</strong>
            <small className="trend neutral">
              {metrics?.scanned_recently ?? 0} <i>audited recently</i>
            </small>
            <div className="sparkline blue-line" />
          </div>

          <div className="stat-card">
            <div className="stat-top">
              <span>Open Findings</span>
              <span className="stat-icon coral">!</span>
            </div>
            <strong>{openVulns}</strong>
            <small className="trend down">
              ↓ {metrics?.resolved_vulnerabilities_7d ?? 0} <i>resolved this week</i>
            </small>
            <div className="sparkline coral-line" />
          </div>

          <div className="stat-card">
            <div className="stat-top">
              <span>Critical Severity</span>
              <span className="stat-icon amber">⌁</span>
            </div>
            <strong style={{ color: critVulns > 0 ? "var(--coral)" : "inherit" }}>
              {String(critVulns).padStart(2, "0")}
            </strong>
            <small className="trend up">
              +{metrics?.new_vulnerabilities_7d ?? 0} <i>new in 7 days</i>
            </small>
            <div className="sparkline amber-line" />
          </div>

          <div className="stat-card">
            <div className="stat-top">
              <span>Asset Coverage</span>
              <span className="stat-icon green">✓</span>
            </div>
            <strong>
              {totalAssets > 0 ? Math.round(((metrics?.scanned_recently || 0) / totalAssets) * 100) : 100}
              <small>%</small>
            </strong>
            <small className="trend up">
              Active Nmap worker
            </small>
            <div className="sparkline green-line" />
          </div>
        </section>

        {/* Main Content Grid: Scanner Panel + Environment Risk Posture */}
        <div className="content-grid">
          <section className="panel scan-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">AUTHORIZED NETWORK AUDIT</p>
                <h2>Start an automated scan</h2>
              </div>
              <span className="live-pill">
                <i /> NMAP ENGINE READY
              </span>
            </div>

            <form onSubmit={handleLaunchScan}>
              <label htmlFor="target">
                Target <span>IP, domain, or subnet range (max /24)</span>
              </label>
              <div className="target-input">
                <span>⌕</span>
                <input
                  id="target"
                  className="mono"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  placeholder="e.g. 10.24.18.0/24 or api.staging.northstar.io"
                  disabled={launching}
                />
              </div>

              <div className="scan-options">
                <div>
                  <label>Scan profile</label>
                  <div className="segmented">
                    <button
                      type="button"
                      className={mode === "quick" ? "selected" : ""}
                      onClick={() => setMode("quick")}
                      disabled={launching}
                    >
                      Quick discovery <small>Port discovery</small>
                    </button>
                    <button
                      type="button"
                      className={mode === "full" ? "selected" : ""}
                      onClick={() => setMode("full")}
                      disabled={launching}
                    >
                      Full assessment <small>NSE vuln scripts</small>
                    </button>
                  </div>
                </div>

                <button className="primary-button" type="submit" disabled={launching}>
                  {launching ? "Queueing scan..." : "Run scan →"}
                </button>
              </div>
            </form>

            <div className="scan-note">
              <span>🛡️</span>
              <p>
                Only scan systems you own or have explicit authorization to test. Subprocess isolation,
                SSRF filtering, and rate bounds are enforced server-side.
              </p>
            </div>

            {error && (
              <div className="error-message" role="alert">
                {error}
              </div>
            )}
          </section>

          {/* Risk Posture Panel */}
          <section className="panel posture-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">POSTURE & PRIORITIZATION</p>
                <h2>Environment Risk</h2>
              </div>
              <Link href="/vulnerabilities" className="text-link">Manage →</Link>
            </div>

            <RiskGauge
              score={envScore}
              showReasons={false}
            />

            <div className="risk-breakdown" style={{ marginTop: "auto" }}>
              <span>
                <i className="dot coral" />
                Critical <b>{critVulns}</b>
              </span>
              <span>
                <i className="dot amber" />
                High <b>{highVulns}</b>
              </span>
              <span>
                <i className="dot blue-dot" />
                Medium <b>{medVulns}</b>
              </span>
            </div>
          </section>
        </div>

        {/* Recent Scans Activity */}
        <section className="panel activity-panel" id="scans">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">ACTIVITY TRAIL</p>
              <h2>Recent Scans</h2>
            </div>
            <Link className="text-link" href="/scans">View all scans →</Link>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Target</th>
                  <th>Profile</th>
                  <th>Status</th>
                  <th>Duration</th>
                  <th>Risk Score</th>
                  <th>Discovered Findings</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentScans.length === 0 ? (
                  <tr>
                    <td colSpan={7} style={{ textAlign: "center", padding: "24px", color: "#94a3b8" }}>
                      No scan records yet. Run your first scan above or add an asset to inventory.
                    </td>
                  </tr>
                ) : (
                  recentScans.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <span className="target-dot" />
                        <Link href={`/scans/${item.id}`} style={{ color: "var(--ink)", fontWeight: 600, textDecoration: "none" }}>
                          {item.target}
                        </Link>
                      </td>
                      <td style={{ textTransform: "capitalize" }}>{item.profile}</td>
                      <td>
                        <StatusBadge status={item.status} />
                      </td>
                      <td>{item.duration_seconds ? `${item.duration_seconds}s` : "-"}</td>
                      <td>
                        <span style={{ fontWeight: 700, color: item.risk_score >= 60 ? "var(--coral)" : "var(--teal)" }}>
                          {item.risk_score} / 100
                        </span>
                      </td>
                      <td>{item.findings?.length || 0} findings</td>
                      <td>
                        <Link href={`/scans/${item.id}`} className="text-link" style={{ fontWeight: 600 }}>
                          Inspect →
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Priority Findings / Action Items */}
        <section className="panel findings-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">REMEDIATION PRIORITY QUEUE</p>
              <h2>Active Vulnerability Findings</h2>
            </div>
            <Link className="text-link" href="/vulnerabilities">
              Full Remediation Tracker →
            </Link>
          </div>

          {priorityFindings.length === 0 ? (
            <div style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>
              ✓ No critical or high unaddressed findings across the monitored attack surface.
            </div>
          ) : (
            <div className="finding-list">
              {priorityFindings.map((finding) => (
                <div key={finding.id} className="finding-row">
                  <SeverityBadge severity={finding.severity} />
                  <div>
                    <strong style={{ fontSize: "12px" }}>
                      <Link href={`/vulnerabilities/${finding.id}`} style={{ color: "inherit", textDecoration: "none" }}>
                        {finding.cve_id}: {finding.title}
                      </Link>
                    </strong>
                    <small>
                      {finding.affected_host} {finding.affected_port ? `· Port ${finding.affected_port}` : ""} · {finding.service || "network"}
                    </small>
                  </div>
                  <span className="finding-age">
                    {finding.status}
                  </span>
                  <Link href={`/vulnerabilities/${finding.id}`} className="text-link" style={{ fontSize: "11px" }}>
                    Details
                  </Link>
                </div>
              ))}
            </div>
          )}
        </section>

        <footer>
          <span>Northstar Security Platform &bull; Professional Network Vulnerability Management</span>
          <span>Defensive Security Architecture &bull; Nmap Scanning Engine</span>
        </footer>
      </main>

      {/* Modals */}
      <NewScanModal
        isOpen={isScanModalOpen}
        onClose={() => setIsScanModalOpen(false)}
        assets={assets}
      />
      <AddAssetModal
        isOpen={isAssetModalOpen}
        onClose={() => setIsAssetModalOpen(false)}
        onAssetAdded={(newAsset) => {
          setAssets((prev) => [newAsset, ...prev]);
          loadData();
        }}
      />
    </div>
  );
}
