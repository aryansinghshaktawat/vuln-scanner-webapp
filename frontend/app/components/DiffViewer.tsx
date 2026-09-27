"use client";

import { DiffResult } from "../lib/api";
import { SeverityBadge } from "./Badges";

interface DiffViewerProps {
  diff: DiffResult | null;
  loading?: boolean;
}

export default function DiffViewer({ diff, loading = false }: DiffViewerProps) {
  if (loading) {
    return <div style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>Calculating differential changes...</div>;
  }

  if (!diff) {
    return <div style={{ padding: "24px", textAlign: "center", color: "#94a3b8" }}>No differential data available. Run at least two scans on this target to compare.</div>;
  }

  const {
    new_vulnerabilities,
    resolved_vulnerabilities,
    persisting_vulnerabilities,
    new_ports,
    closed_ports,
    version_changes,
  } = diff;

  const totalChanges =
    new_vulnerabilities.length +
    resolved_vulnerabilities.length +
    new_ports.length +
    closed_ports.length +
    version_changes.length;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Diff Stat Pills */}
      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <span className="diff-item diff-new" style={{ padding: "6px 12px", fontWeight: 700 }}>
          + {new_vulnerabilities.length} NEW Vulnerabilities
        </span>
        <span className="diff-item diff-resolved" style={{ padding: "6px 12px", fontWeight: 700 }}>
          ✓ {resolved_vulnerabilities.length} RESOLVED
        </span>
        <span className="diff-item diff-persisting" style={{ padding: "6px 12px", fontWeight: 700 }}>
          ⚠ {persisting_vulnerabilities.length} PERSISTING
        </span>
        <span className="diff-item diff-port-new" style={{ padding: "6px 12px", fontWeight: 700 }}>
          + {new_ports.length} NEW Ports
        </span>
        <span className="diff-item diff-port-closed" style={{ padding: "6px 12px", fontWeight: 700 }}>
          - {closed_ports.length} CLOSED Ports
        </span>
      </div>

      {totalChanges === 0 && persisting_vulnerabilities.length === 0 ? (
        <div style={{ padding: "20px", background: "#f8fafc", borderRadius: "6px", textAlign: "center", color: "#64748b", fontSize: "12px" }}>
          No changes detected between consecutive assessments. Network attack surface remains static.
        </div>
      ) : null}

      {/* NEW VULNERABILITIES */}
      {new_vulnerabilities.length > 0 && (
        <div className="diff-section">
          <h4 style={{ color: "#065f46" }}>
            <span style={{ background: "#ecfdf5", padding: "2px 6px", borderRadius: "3px" }}>+</span>
            NEW Potential Vulnerabilities Detected
          </h4>
          {new_vulnerabilities.map((v) => (
            <div key={v.cve_id} className="diff-item diff-new">
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <strong className="mono">{v.cve_id}</strong>
                <SeverityBadge severity={v.severity} />
                <span>{v.title}</span>
              </div>
              <small>{v.affected_port ? `Port ${v.affected_port}` : "Host service"}</small>
            </div>
          ))}
        </div>
      )}

      {/* RESOLVED VULNERABILITIES */}
      {resolved_vulnerabilities.length > 0 && (
        <div className="diff-section">
          <h4 style={{ color: "#0f766e" }}>
            <span style={{ background: "#f0fdfa", padding: "2px 6px", borderRadius: "3px" }}>✓</span>
            RESOLVED Vulnerabilities (Fixed since previous scan)
          </h4>
          {resolved_vulnerabilities.map((v) => (
            <div key={v.cve_id} className="diff-item diff-resolved">
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <strong className="mono" style={{ textDecoration: "line-through" }}>{v.cve_id}</strong>
                <SeverityBadge severity={v.severity} />
                <span>{v.title}</span>
              </div>
              <span className="badge badge-success">FIX VERIFIED</span>
            </div>
          ))}
        </div>
      )}

      {/* PERSISTING VULNERABILITIES */}
      {persisting_vulnerabilities.length > 0 && (
        <div className="diff-section">
          <h4 style={{ color: "#854d0e" }}>
            <span style={{ background: "#fefce8", padding: "2px 6px", borderRadius: "3px" }}>⚠</span>
            PERSISTING Vulnerabilities (Remains unresolved)
          </h4>
          {persisting_vulnerabilities.map((v) => (
            <div key={v.cve_id} className="diff-item diff-persisting">
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <strong className="mono">{v.cve_id}</strong>
                <SeverityBadge severity={v.severity} />
                <span>{v.title}</span>
              </div>
              <small style={{ color: "#854d0e", fontWeight: 600 }}>Action Pending</small>
            </div>
          ))}
        </div>
      )}

      {/* PORT CHANGES */}
      {(new_ports.length > 0 || closed_ports.length > 0) && (
        <div className="diff-section">
          <h4>Network Port State Changes</h4>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
            <div>
              <strong style={{ fontSize: "11px", color: "#1e40af", display: "block", marginBottom: "6px" }}>NEW OPEN PORTS:</strong>
              {new_ports.length === 0 ? (
                <div style={{ fontSize: "11px", color: "#94a3b8" }}>No newly exposed ports.</div>
              ) : (
                new_ports.map((p) => (
                  <div key={p.port} className="diff-item diff-port-new">
                    <span className="mono font-bold">Port {p.port}/{p.protocol}</span>
                    <span>{p.service} {p.version}</span>
                  </div>
                ))
              )}
            </div>
            <div>
              <strong style={{ fontSize: "11px", color: "#991b1b", display: "block", marginBottom: "6px" }}>CLOSED PORTS:</strong>
              {closed_ports.length === 0 ? (
                <div style={{ fontSize: "11px", color: "#94a3b8" }}>No closed ports.</div>
              ) : (
                closed_ports.map((p) => (
                  <div key={p.port} className="diff-item diff-port-closed">
                    <span className="mono font-bold">Port {p.port}/{p.protocol}</span>
                    <span style={{ textDecoration: "line-through" }}>{p.service}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* SERVICE VERSION CHANGES */}
      {version_changes.length > 0 && (
        <div className="diff-section">
          <h4>Service Fingerprint / Version Changes</h4>
          {version_changes.map((vc) => (
            <div key={vc.port} className="diff-item" style={{ background: "#f8fafc", border: "1px solid #e2e8f0" }}>
              <span className="mono font-bold">Port {vc.port}/{vc.protocol} ({vc.service})</span>
              <span>
                <span style={{ color: "#ef4444", textDecoration: "line-through", marginRight: "8px" }}>{vc.old_version}</span>
                ➔
                <span style={{ color: "#10b981", fontWeight: 600, marginLeft: "8px" }}>{vc.new_version}</span>
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
