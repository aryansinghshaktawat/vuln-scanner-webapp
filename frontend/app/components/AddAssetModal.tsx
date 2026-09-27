"use client";

import { useState } from "react";
import { apiFetch, Asset } from "../lib/api";

interface AddAssetModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAssetAdded: (asset: Asset) => void;
}

export default function AddAssetModal({ isOpen, onClose, onAssetAdded }: AddAssetModalProps) {
  const [name, setName] = useState("");
  const [target, setTarget] = useState("");
  const [description, setDescription] = useState("");
  const [environment, setEnvironment] = useState<"production" | "staging" | "development" | "internal">("production");
  const [criticality, setCriticality] = useState<"critical" | "high" | "medium" | "low">("high");
  const [owner, setOwner] = useState("SecOps");
  const [tags, setTags] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !target.trim()) {
      setError("Asset name and target IP/domain are required.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const created = await apiFetch<Asset>("/api/assets", {
        method: "POST",
        body: JSON.stringify({
          name: name.trim(),
          target: target.trim(),
          description: description.trim() || undefined,
          environment,
          criticality,
          owner: owner.trim() || "SecOps",
          tags: tags.trim(),
        }),
      });
      onAssetAdded(created);
      onClose();
      setName("");
      setTarget("");
      setDescription("");
      setTags("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add asset");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-box">
        <div className="modal-header">
          <h3>Add Authorized Asset</h3>
          <button className="icon-button" onClick={onClose} style={{ cursor: "pointer", fontSize: "16px" }}>✕</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && (
              <div className="error-message" style={{ marginBottom: "16px" }}>
                {error}
              </div>
            )}

            <div className="form-group">
              <label>Asset Name <small>(e.g. Primary Edge Gateway)</small></label>
              <input
                className="form-control"
                placeholder="e.g. Production Web Cluster"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Target IP, Domain, or CIDR <small>(max /24 range)</small></label>
              <input
                className="form-control mono"
                placeholder="e.g. 192.168.1.20 or api.company.com"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                required
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div className="form-group">
                <label>Environment</label>
                <select
                  className="form-control"
                  value={environment}
                  onChange={(e) => setEnvironment(e.target.value as "production" | "staging" | "development" | "internal")}
                >
                  <option value="production">Production</option>
                  <option value="staging">Staging</option>
                  <option value="development">Development</option>
                  <option value="internal">Internal Network</option>
                </select>
              </div>

              <div className="form-group">
                <label>Criticality</label>
                <select
                  className="form-control"
                  value={criticality}
                  onChange={(e) => setCriticality(e.target.value as "critical" | "high" | "medium" | "low")}
                >
                  <option value="critical">Critical (Tier 1)</option>
                  <option value="high">High (Tier 2)</option>
                  <option value="medium">Medium (Tier 3)</option>
                  <option value="low">Low (Tier 4)</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Owner / Responsible Team</label>
              <input
                className="form-control"
                placeholder="e.g. Infrastructure, Payments Team"
                value={owner}
                onChange={(e) => setOwner(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Tags <small>(comma-separated: e.g. web, dmz, public-facing)</small></label>
              <input
                className="form-control"
                placeholder="e.g. dmz, public-facing, payments"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                className="form-control"
                placeholder="Purpose of this host or service..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
              />
            </div>

            <div style={{ fontSize: "10px", color: "#64748b", background: "#f8fafc", padding: "10px", borderRadius: "5px" }}>
              🛡️ <b>Authorization Notice:</b> Only register assets you own or have explicit, documented permission to test.
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Registering..." : "Add to Inventory"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
