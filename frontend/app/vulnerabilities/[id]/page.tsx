"use client";

import { useCallback, useEffect, useState, use } from "react";
import Link from "next/link";
import Sidebar from "../../components/Sidebar";
import Topbar from "../../components/Topbar";
import { SeverityBadge } from "../../components/Badges";
import { apiFetch, VulnerabilityFinding } from "../../lib/api";

export default function VulnerabilityDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const [finding, setFinding] = useState<VulnerabilityFinding | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);

  // Form states
  const [status, setStatus] = useState("OPEN");
  const [owner, setOwner] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  const loadFinding = useCallback(async () => {
    try {
      const data = await apiFetch<VulnerabilityFinding>(`/api/vulnerabilities/${id}`);
      setFinding(data);
      setStatus(data.status);
      setOwner(data.remediation_owner || "");
      setNotes(data.remediation_notes || "");
    } catch (err) {
      console.error("Failed to load finding details:", err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadFinding();
  }, [loadFinding]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await apiFetch<VulnerabilityFinding>(`/api/vulnerabilities/${id}`, {
        method: "PUT",
        body: JSON.stringify({
          status,
          remediation_owner: owner.trim() || undefined,
          remediation_notes: notes.trim() || undefined,
        }),
      });
      setFinding(updated);
      alert("Finding updated successfully");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update finding");
    } finally {
      setSaving(false);
    }
  };

  const handleVerify = async () => {
    if (!finding) return;
    setVerifying(true);
    try {
      const res = await apiFetch<{ status: string; message: string; scan_id?: string }>(
        `/api/vulnerabilities/${finding.id}/verify`,
        { method: "POST" }
      );
      alert(res.message);
      loadFinding();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to trigger verification");
    } finally {
      setVerifying(false);
    }
  };

  if (loading) {
    return (
      <div className="app-shell">
        <Sidebar />
        <main className="main-content" style={{ padding: "40px", textAlign: "center" }}>
          Loading vulnerability dossier...
        </main>
      </div>
    );
  }

  if (!finding) {
    return (
      <div className="app-shell">
        <Sidebar />
        <main className="main-content" style={{ padding: "40px" }}>
          <h2>Finding not found</h2>
          <Link href="/vulnerabilities" className="btn btn-outline" style={{ marginTop: "16px" }}>
            ← Back to Findings
          </Link>
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <Topbar breadcrumbs={["Vulnerabilities", finding.cve_id]} />

        {/* Heading */}
        <section className="page-heading">
          <div>
            <div style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "8px" }}>
              <SeverityBadge severity={finding.severity} />
              <span className={`badge ${finding.status === "RESOLVED" ? "badge-success" : "badge-info"}`}>
                {finding.status}
              </span>
              {finding.is_known_exploit === "YES" && (
                <span className="badge badge-cisa">CISA KEV ACTIVE EXPLOIT</span>
              )}
            </div>
            <h1 className="mono">{finding.cve_id}<span>.</span></h1>
            <p className="muted" style={{ fontSize: "14px", fontWeight: 600 }}>{finding.title}</p>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <button className="btn btn-primary" onClick={handleVerify} disabled={verifying}>
              {verifying ? "Triggering..." : "Verify Fix (Rescan) ↗"}
            </button>
          </div>
        </section>

        {/* Grid: Context & Evidence */}
        <div className="content-grid" style={{ marginBottom: "24px" }}>
          {/* Finding Details */}
          <section className="panel" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div className="panel-heading" style={{ marginBottom: 0 }}>
              <div>
                <p className="eyebrow">AFFECTED SURFACE</p>
                <h2>Vulnerability Context</h2>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", fontSize: "12px" }}>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>AFFECTED HOST</span>
                <strong className="mono">{finding.affected_host}</strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>AFFECTED PORT & SERVICE</span>
                <strong className="mono">
                  {finding.affected_port ? `Port ${finding.affected_port}` : "Host / Perimeter"} ({finding.service || "unknown"})
                </strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>DETECTION ENGINE</span>
                <span>{finding.detection_source}</span>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>CVSS SCORE</span>
                <strong>{finding.cvss_score ? `${finding.cvss_score} / 10.0` : "N/A - NSE Heuristic"}</strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>FIRST DETECTED</span>
                <span>{new Date(finding.first_seen).toLocaleString()}</span>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>LAST OBSERVED</span>
                <span>{new Date(finding.last_seen).toLocaleString()}</span>
              </div>
            </div>

            <div style={{ borderTop: "1px solid var(--line)", paddingTop: "14px" }}>
              <span style={{ color: "#94a3b8", display: "block", fontSize: "10px", marginBottom: "4px" }}>DESCRIPTION</span>
              <p style={{ margin: 0, fontSize: "12px", color: "#334155", lineHeight: 1.5 }}>
                {finding.description || "Potential vulnerability detected during Nmap NSE script evaluation."}
              </p>
            </div>

            {/* External Intelligence links */}
            <div style={{ display: "flex", gap: "10px", marginTop: "auto", paddingTop: "12px", borderTop: "1px solid var(--line)" }}>
              <a
                href={`https://nvd.nist.gov/vuln/detail/${finding.cve_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline btn-sm"
              >
                NVD NIST Database ↗
              </a>
              <a
                href={`https://cve.mitre.org/cgi-bin/cvename.cgi?name=${finding.cve_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline btn-sm"
              >
                MITRE CVE Record ↗
              </a>
            </div>
          </section>

          {/* Remediation Management Form */}
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">REMEDIATION WORKFLOW</p>
                <h2>Mitigation & Tracking</h2>
              </div>
            </div>

            <form onSubmit={handleUpdate}>
              <div className="form-group">
                <label>Finding Lifecycle State</label>
                <select className="form-control" value={status} onChange={(e) => setStatus(e.target.value)}>
                  <option value="OPEN">OPEN (Vulnerability active)</option>
                  <option value="IN_PROGRESS">IN_PROGRESS (Remediation active)</option>
                  <option value="ACKNOWLEDGED">ACKNOWLEDGED (Accepted risk)</option>
                  <option value="RESOLVED">RESOLVED (Fix applied)</option>
                  <option value="FALSE_POSITIVE">FALSE_POSITIVE (Non-applicable)</option>
                </select>
              </div>

              <div className="form-group">
                <label>Assigned Lead / Team</label>
                <input
                  className="form-control"
                  placeholder="e.g. Infrastructure, Application Sec"
                  value={owner}
                  onChange={(e) => setOwner(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Analyst Notes</label>
                <textarea
                  className="form-control"
                  placeholder="Record patch versions applied, configuration adjustments, or verification results..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={4}
                />
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: "100%" }} disabled={saving}>
                {saving ? "Updating..." : "Save Remediation Record"}
              </button>
            </form>
          </section>
        </div>

        {/* Evidence Block */}
        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">OBSERVED EVIDENCE</p>
              <h2>Scanner Output Evidence</h2>
            </div>
          </div>
          <pre className="code-box">
            {finding.evidence || "No raw evidence snippet attached."}
          </pre>
        </section>
      </main>
    </div>
  );
}
