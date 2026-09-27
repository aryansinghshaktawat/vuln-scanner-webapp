"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { SeverityBadge } from "../components/Badges";
import { apiFetch, VulnerabilityFinding } from "../lib/api";

export default function VulnerabilitiesPage() {
  const [findings, setFindings] = useState<VulnerabilityFinding[]>([]);
  const [severityFilter, setSeverityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  // Edit Remediation Modal
  const [editingFinding, setEditingFinding] = useState<VulnerabilityFinding | null>(null);
  const [editStatus, setEditStatus] = useState("");
  const [editOwner, setEditOwner] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [editDue, setEditDue] = useState("");
  const [saving, setSaving] = useState(false);

  const fetchFindings = useCallback(async () => {
    try {
      let query = "/api/vulnerabilities?limit=100&";
      if (severityFilter) query += `severity=${encodeURIComponent(severityFilter)}&`;
      if (statusFilter) query += `status=${encodeURIComponent(statusFilter)}&`;
      if (search) query += `search=${encodeURIComponent(search)}&`;

      const data = await apiFetch<VulnerabilityFinding[]>(query);
      setFindings(data || []);
    } catch (err) {
      console.error("Failed to load vulnerabilities:", err);
    } finally {
      setLoading(false);
    }
  }, [severityFilter, statusFilter, search]);

  useEffect(() => {
    fetchFindings();
  }, [fetchFindings]);

  const handleOpenEdit = (f: VulnerabilityFinding) => {
    setEditingFinding(f);
    setEditStatus(f.status);
    setEditOwner(f.remediation_owner || "");
    setEditNotes(f.remediation_notes || "");
    setEditDue(f.due_date ? f.due_date.slice(0, 10) : "");
  };

  const handleSaveRemediation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingFinding) return;

    setSaving(true);
    try {
      const updated = await apiFetch<VulnerabilityFinding>(`/api/vulnerabilities/${editingFinding.id}`, {
        method: "PUT",
        body: JSON.stringify({
          status: editStatus,
          remediation_owner: editOwner.trim() || undefined,
          remediation_notes: editNotes.trim() || undefined,
          due_date: editDue ? new Date(editDue).toISOString() : undefined,
        }),
      });

      setFindings((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      setEditingFinding(null);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update remediation record");
    } finally {
      setSaving(false);
    }
  };

  const handleVerifyFix = async (f: VulnerabilityFinding) => {
    if (!confirm(`Trigger an automated verification scan for ${f.cve_id} on ${f.affected_host}?`)) {
      return;
    }
    try {
      const res = await apiFetch<{ status: string; message: string; scan_id?: string }>(
        `/api/vulnerabilities/${f.id}/verify`,
        { method: "POST" }
      );
      alert(res.message);
      fetchFindings();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to trigger verification");
    }
  };

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <Topbar breadcrumbs={["Security Operations", "Vulnerabilities & Remediation"]} />

        <section className="page-heading">
          <div>
            <p className="eyebrow">DEFENSIVE FINDINGS LIFECYCLE</p>
            <h1>Vulnerability Remediation Tracker<span>.</span></h1>
            <p className="muted">Track, assign, and verify network exposure findings detected across authorized infrastructure.</p>
          </div>
        </section>

        {/* Filter Bar */}
        <div className="filter-bar">
          <div className="search-input">
            <span>⌕</span>
            <input
              placeholder="Search by CVE ID, title, or target host..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <select className="select-input" value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select className="select-input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="RESOLVED">Resolved</option>
            <option value="FALSE_POSITIVE">False Positive</option>
          </select>
        </div>

        {/* Vulnerabilities Table */}
        <section className="panel" style={{ padding: "0" }}>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Severity</th>
                  <th>CVE ID</th>
                  <th>Title & Description</th>
                  <th>Affected Host & Port</th>
                  <th>Status</th>
                  <th>Assigned Owner</th>
                  <th>Remediation Target</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading && findings.length === 0 ? (
                  <tr>
                    <td colSpan={8} style={{ textAlign: "center", padding: "30px", color: "#64748b" }}>
                      Loading findings...
                    </td>
                  </tr>
                ) : findings.length === 0 ? (
                  <tr>
                    <td colSpan={8} style={{ textAlign: "center", padding: "40px", color: "#94a3b8" }}>
                      No vulnerability findings match the selected filters.
                    </td>
                  </tr>
                ) : (
                  findings.map((f) => (
                    <tr key={f.id}>
                      <td>
                        <SeverityBadge severity={f.severity} />
                      </td>
                      <td>
                        <Link href={`/vulnerabilities/${f.id}`} className="mono font-bold" style={{ color: "var(--coral)", textDecoration: "none" }}>
                          {f.cve_id}
                        </Link>
                        {f.is_known_exploit === "YES" && (
                          <span className="badge badge-cisa" style={{ display: "block", width: "fit-content", marginTop: "4px" }}>
                            KEV EXPLOIT
                          </span>
                        )}
                      </td>
                      <td>
                        <strong style={{ display: "block", color: "var(--ink)", fontSize: "11px" }}>{f.title}</strong>
                        {f.description && (
                          <p style={{ margin: "2px 0 0", color: "#64748b", fontSize: "10px", maxWidth: "340px" }}>
                            {f.description.slice(0, 90)}...
                          </p>
                        )}
                      </td>
                      <td className="mono">
                        {f.affected_host}
                        {f.affected_port ? ` · Port ${f.affected_port}` : ""}
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            f.status === "RESOLVED"
                              ? "badge-success"
                              : f.status === "IN_PROGRESS"
                              ? "badge-high"
                              : "badge-info"
                          }`}
                        >
                          {f.status.replace("_", " ")}
                        </span>
                      </td>
                      <td>{f.remediation_owner || "Unassigned"}</td>
                      <td>{f.due_date ? new Date(f.due_date).toLocaleDateString() : "-"}</td>
                      <td>
                        <div style={{ display: "flex", gap: "6px" }}>
                          <button className="btn btn-outline btn-sm" onClick={() => handleOpenEdit(f)}>
                            Edit Status
                          </button>
                          <button
                            className="btn btn-outline btn-sm"
                            title="Rescan to verify if vulnerability was patched"
                            onClick={() => handleVerifyFix(f)}
                          >
                            Verify Fix
                          </button>
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

      {/* Edit Remediation Modal */}
      {editingFinding && (
        <div className="modal-backdrop">
          <div className="modal-box">
            <div className="modal-header">
              <h3>Remediation: {editingFinding.cve_id}</h3>
              <button className="icon-button" onClick={() => setEditingFinding(null)} style={{ cursor: "pointer", fontSize: "16px" }}>✕</button>
            </div>

            <form onSubmit={handleSaveRemediation}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Remediation Lifecycle Status</label>
                  <select
                    className="form-control"
                    value={editStatus}
                    onChange={(e) => setEditStatus(e.target.value)}
                  >
                    <option value="OPEN">OPEN (Unaddressed finding)</option>
                    <option value="IN_PROGRESS">IN_PROGRESS (Patch or configuration underway)</option>
                    <option value="ACKNOWLEDGED">ACKNOWLEDGED (Accepted operational risk)</option>
                    <option value="RESOLVED">RESOLVED (Mitigation implemented)</option>
                    <option value="FALSE_POSITIVE">FALSE_POSITIVE (Verified non-issue)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Assigned Lead / Team</label>
                  <input
                    className="form-control"
                    placeholder="e.g. Infrastructure, Security Team"
                    value={editOwner}
                    onChange={(e) => setEditOwner(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>Target Resolution Date</label>
                  <input
                    type="date"
                    className="form-control"
                    value={editDue}
                    onChange={(e) => setEditDue(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>Analyst Remediation Notes</label>
                  <textarea
                    className="form-control"
                    placeholder="Document patch version, firewall rule reference, or mitigation rationale..."
                    value={editNotes}
                    onChange={(e) => setEditNotes(e.target.value)}
                    rows={3}
                  />
                </div>

                {editingFinding.recommendation && (
                  <div style={{ fontSize: "11px", color: "#64748b", background: "#f8fafc", padding: "10px", borderRadius: "5px" }}>
                    <b>Scanner Guidance:</b> {editingFinding.recommendation}
                  </div>
                )}
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={() => setEditingFinding(null)} disabled={saving}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? "Saving..." : "Update Finding"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
