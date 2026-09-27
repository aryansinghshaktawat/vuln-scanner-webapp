"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { StatusBadge } from "../components/Badges";
import NewScanModal from "../components/NewScanModal";
import { apiFetch, ScanHistoryItem, Asset } from "../lib/api";

export default function ScansPage() {
  const [scans, setScans] = useState<ScanHistoryItem[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [targetFilter, setTargetFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [isScanModalOpen, setIsScanModalOpen] = useState(false);

  const fetchScans = useCallback(async () => {
    try {
      let query = "/api/scans?limit=50&";
      if (statusFilter) query += `status=${encodeURIComponent(statusFilter)}&`;
      if (targetFilter) query += `target=${encodeURIComponent(targetFilter)}&`;

      const [scansData, assetsData] = await Promise.all([
        apiFetch<ScanHistoryItem[]>(query),
        apiFetch<Asset[]>("/api/assets"),
      ]);
      setScans(scansData || []);
      setAssets(assetsData || []);
    } catch (err) {
      console.error("Failed to load scans:", err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, targetFilter]);

  useEffect(() => {
    fetchScans();
    const interval = setInterval(fetchScans, 8000);
    return () => clearInterval(interval);
  }, [fetchScans]);

  const handleCancelScan = async (scanId: string) => {
    try {
      await apiFetch(`/api/scans/${scanId}/cancel`, { method: "POST" });
      fetchScans();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to cancel scan");
    }
  };

  return (
    <div className="app-shell">
      <Sidebar assetCount={assets.length} />

      <main className="main-content">
        <Topbar breadcrumbs={["Security Operations", "Scan Management & History"]} />

        <section className="page-heading">
          <div>
            <p className="eyebrow">AUDIT & ASSESSMENT RUNS</p>
            <h1>Scan Execution History<span>.</span></h1>
            <p className="muted">Orchestrate and review automated network port discovery and NSE vulnerability script runs.</p>
          </div>
          <button className="btn btn-primary" onClick={() => setIsScanModalOpen(true)}>
            + Launch New Scan
          </button>
        </section>

        {/* Filter Bar */}
        <div className="filter-bar">
          <div className="search-input">
            <span>⌕</span>
            <input
              placeholder="Search by target host or IP..."
              value={targetFilter}
              onChange={(e) => setTargetFilter(e.target.value)}
            />
          </div>

          <select className="select-input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="RUNNING">Running</option>
            <option value="QUEUED">Queued</option>
            <option value="COMPLETED">Completed</option>
            <option value="FAILED">Failed</option>
            <option value="CANCELLED">Cancelled</option>
            <option value="TIMEOUT">Timeout</option>
          </select>
        </div>

        {/* Scans Table */}
        <section className="panel" style={{ padding: "0" }}>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Target Host</th>
                  <th>Profile</th>
                  <th>Execution State</th>
                  <th>Start Time</th>
                  <th>Duration</th>
                  <th>Open Ports</th>
                  <th>Findings</th>
                  <th>Risk Score</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading && scans.length === 0 ? (
                  <tr>
                    <td colSpan={9} style={{ textAlign: "center", padding: "30px", color: "#64748b" }}>
                      Loading scan runs...
                    </td>
                  </tr>
                ) : scans.length === 0 ? (
                  <tr>
                    <td colSpan={9} style={{ textAlign: "center", padding: "40px", color: "#94a3b8" }}>
                      No scan runs recorded yet.
                    </td>
                  </tr>
                ) : (
                  scans.map((scan) => (
                    <tr key={scan.id}>
                      <td>
                        <span className="target-dot" />
                        <Link
                          href={`/scans/${scan.id}`}
                          className="mono"
                          style={{ color: "var(--ink)", fontWeight: 700, textDecoration: "none" }}
                        >
                          {scan.target}
                        </Link>
                      </td>
                      <td style={{ textTransform: "capitalize" }}>{scan.profile}</td>
                      <td>
                        <StatusBadge status={scan.status} />
                      </td>
                      <td>{scan.started_at ? new Date(scan.started_at).toLocaleString() : "Queued"}</td>
                      <td>{scan.duration_seconds > 0 ? `${scan.duration_seconds}s` : "-"}</td>
                      <td>{scan.open_ports_count}</td>
                      <td>
                        <span style={{ fontWeight: scan.vulnerabilities_count ? 700 : 400, color: scan.vulnerabilities_count ? "var(--coral)" : "inherit" }}>
                          {scan.vulnerabilities_count}
                        </span>
                      </td>
                      <td>
                        <span
                          style={{
                            fontWeight: 700,
                            color: scan.risk_score >= 70 ? "var(--coral)" : (scan.risk_score >= 40 ? "var(--amber)" : "var(--teal)"),
                          }}
                        >
                          {scan.risk_score} / 100
                        </span>
                      </td>
                      <td>
                        <div style={{ display: "flex", gap: "6px" }}>
                          <Link href={`/scans/${scan.id}`} className="btn btn-outline btn-sm">
                            Inspect
                          </Link>
                          {(scan.status === "RUNNING" || scan.status === "QUEUED") && (
                            <button
                              className="btn btn-outline btn-sm"
                              style={{ color: "#ef4444" }}
                              onClick={() => handleCancelScan(scan.id)}
                            >
                              Cancel
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      <NewScanModal
        isOpen={isScanModalOpen}
        onClose={() => setIsScanModalOpen(false)}
        assets={assets}
      />
    </div>
  );
}
