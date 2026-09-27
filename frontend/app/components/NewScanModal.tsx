"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, Asset, ScanRecord } from "../lib/api";

interface NewScanModalProps {
  isOpen: boolean;
  onClose: () => void;
  assets?: Asset[];
  defaultTarget?: string;
  defaultAssetId?: string;
}

export default function NewScanModal({
  isOpen,
  onClose,
  assets = [],
  defaultTarget = "",
  defaultAssetId = "",
}: NewScanModalProps) {
  const router = useRouter();
  const [selectedAssetId, setSelectedAssetId] = useState(defaultAssetId);
  const [target, setTarget] = useState(defaultTarget);
  const [profile, setProfile] = useState("full");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAssetSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setSelectedAssetId(val);
    if (val) {
      const match = assets.find((a) => a.id === val);
      if (match) setTarget(match.target);
    }
  };

  const handleLaunch = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanTarget = target.trim();
    if (!cleanTarget && !selectedAssetId) {
      setError("Please specify a target or select an asset from inventory.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const scan = await apiFetch<ScanRecord>("/api/scans", {
        method: "POST",
        body: JSON.stringify({
          target: cleanTarget || undefined,
          asset_id: selectedAssetId || undefined,
          profile,
        }),
      });
      onClose();
      router.push(`/scans/${scan.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to launch scan");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-box">
        <div className="modal-header">
          <h3>Launch Network Scan</h3>
          <button className="icon-button" onClick={onClose} style={{ cursor: "pointer", fontSize: "16px" }}>✕</button>
        </div>

        <form onSubmit={handleLaunch}>
          <div className="modal-body">
            {error && (
              <div className="error-message" style={{ marginBottom: "16px" }}>
                {error}
              </div>
            )}

            {assets.length > 0 && (
              <div className="form-group">
                <label>Select Monitored Asset <small>(optional)</small></label>
                <select className="form-control" value={selectedAssetId} onChange={handleAssetSelect}>
                  <option value="">-- Choose registered asset or enter custom target below --</option>
                  {assets.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({a.target}) - {a.environment}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="form-group">
              <label>Target IP, Domain, or Subnet</label>
              <input
                className="form-control mono"
                placeholder="e.g. 10.24.18.0/24 or api.company.com"
                value={target}
                onChange={(e) => {
                  setTarget(e.target.value);
                  setSelectedAssetId("");
                }}
                required
              />
            </div>

            <div className="form-group">
              <label>Scan Assessment Profile</label>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginTop: "6px" }}>
                <div
                  onClick={() => setProfile("quick")}
                  style={{
                    border: `1px solid ${profile === "quick" ? "var(--teal)" : "var(--line)"}`,
                    background: profile === "quick" ? "#e5f2ef" : "#fff",
                    borderRadius: "6px",
                    padding: "12px",
                    cursor: "pointer",
                  }}
                >
                  <strong style={{ display: "block", fontSize: "12px", color: profile === "quick" ? "#0b5f5b" : "var(--ink)" }}>
                    Quick Discovery
                  </strong>
                  <small style={{ color: "#64748b", fontSize: "10px" }}>Port scan & service probing (~2 min)</small>
                </div>

                <div
                  onClick={() => setProfile("full")}
                  style={{
                    border: `1px solid ${profile === "full" ? "var(--teal)" : "var(--line)"}`,
                    background: profile === "full" ? "#e5f2ef" : "#fff",
                    borderRadius: "6px",
                    padding: "12px",
                    cursor: "pointer",
                  }}
                >
                  <strong style={{ display: "block", fontSize: "12px", color: profile === "full" ? "#0b5f5b" : "var(--ink)" }}>
                    Full Vulnerability Audit
                  </strong>
                  <small style={{ color: "#64748b", fontSize: "10px" }}>TCP + Version detection + NSE Vuln scripts</small>
                </div>
              </div>
            </div>

            <div style={{ fontSize: "10px", color: "#64748b", background: "#f8fafc", padding: "10px", borderRadius: "5px", marginTop: "16px" }}>
              🛡️ Scans run in an isolated background worker. Live progress will stream via Server-Sent Events.
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Queueing..." : "Start Scan →"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
