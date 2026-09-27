"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { EnvironmentPill, StatusBadge } from "../components/Badges";
import AddAssetModal from "../components/AddAssetModal";
import NewScanModal from "../components/NewScanModal";
import { apiFetch, Asset } from "../lib/api";

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [search, setSearch] = useState("");
  const [envFilter, setEnvFilter] = useState("");
  const [critFilter, setCritFilter] = useState("");
  const [loading, setLoading] = useState(true);

  // Modals
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isScanOpen, setIsScanOpen] = useState(false);
  const [scanTargetAsset, setScanTargetAsset] = useState<Asset | null>(null);

  const fetchAssets = useCallback(async () => {
    try {
      let query = "/api/assets?";
      if (search) query += `search=${encodeURIComponent(search)}&`;
      if (envFilter) query += `environment=${encodeURIComponent(envFilter)}&`;
      if (critFilter) query += `criticality=${encodeURIComponent(critFilter)}&`;
      const data = await apiFetch<Asset[]>(query);
      setAssets(data || []);
    } catch (err) {
      console.error("Failed to load assets:", err);
    } finally {
      setLoading(false);
    }
  }, [search, envFilter, critFilter]);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  const handleDelete = async (asset: Asset) => {
    if (!confirm(`Are you sure you want to remove "${asset.name}" (${asset.target}) from inventory?`)) {
      return;
    }
    try {
      await apiFetch(`/api/assets/${asset.id}`, { method: "DELETE" });
      setAssets((prev) => prev.filter((a) => a.id !== asset.id));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete asset");
    }
  };

  const handleQuickScan = (asset: Asset) => {
    setScanTargetAsset(asset);
    setIsScanOpen(true);
  };

  return (
    <div className="app-shell">
      <Sidebar assetCount={assets.length} />

      <main className="main-content">
        <Topbar breadcrumbs={["Security Operations", "Asset Inventory"]} />

        <section className="page-heading">
          <div>
            <p className="eyebrow">ATTACK SURFACE INVENTORY</p>
            <h1>Monitored Assets<span>.</span></h1>
            <p className="muted">Authorized hosts, domain boundaries, and perimeter subnets tracked for vulnerabilities.</p>
          </div>
          <button className="btn btn-primary" onClick={() => setIsAddOpen(true)}>
            + Add Authorized Asset
          </button>
        </section>

        {/* Filter Bar */}
        <div className="filter-bar">
          <div className="search-input">
            <span>⌕</span>
            <input
              placeholder="Search by asset name, target IP, or owner..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <select className="select-input" value={envFilter} onChange={(e) => setEnvFilter(e.target.value)}>
            <option value="">All Environments</option>
            <option value="production">Production</option>
            <option value="staging">Staging</option>
            <option value="development">Development</option>
            <option value="internal">Internal</option>
          </select>

          <select className="select-input" value={critFilter} onChange={(e) => setCritFilter(e.target.value)}>
            <option value="">All Criticalities</option>
            <option value="critical">Critical (Tier 1)</option>
            <option value="high">High (Tier 2)</option>
            <option value="medium">Medium (Tier 3)</option>
            <option value="low">Low (Tier 4)</option>
          </select>
        </div>

        {/* Assets Table */}
        <section className="panel" style={{ padding: "0" }}>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Asset Name</th>
                  <th>Target Host</th>
                  <th>Environment</th>
                  <th>Criticality</th>
                  <th>Owner</th>
                  <th>Open Ports</th>
                  <th>Active Vulns</th>
                  <th>Risk Score</th>
                  <th>Scan Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={10} style={{ textAlign: "center", padding: "30px", color: "#64748b" }}>
                      Loading assets...
                    </td>
                  </tr>
                ) : assets.length === 0 ? (
                  <tr>
                    <td colSpan={10} style={{ textAlign: "center", padding: "40px", color: "#94a3b8" }}>
                      No assets found matching criteria. Click &quot;+ Add Authorized Asset&quot; to register one.
                    </td>
                  </tr>
                ) : (
                  assets.map((asset) => (
                    <tr key={asset.id}>
                      <td>
                        <Link
                          href={`/assets/${asset.id}`}
                          style={{ color: "var(--ink)", fontWeight: 600, textDecoration: "none" }}
                        >
                          {asset.name}
                        </Link>
                        {asset.description && (
                          <small style={{ display: "block", color: "#94a3b8", fontSize: "10px" }}>
                            {asset.description.slice(0, 45)}...
                          </small>
                        )}
                      </td>
                      <td className="mono font-bold">{asset.target}</td>
                      <td>
                        <EnvironmentPill environment={asset.environment} />
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            asset.criticality === "critical"
                              ? "badge-critical"
                              : asset.criticality === "high"
                              ? "badge-high"
                              : "badge-medium"
                          }`}
                        >
                          {asset.criticality}
                        </span>
                      </td>
                      <td>{asset.owner}</td>
                      <td>{asset.open_ports_count ?? 0}</td>
                      <td>
                        <span style={{ fontWeight: asset.vulnerabilities_count ? 700 : 400, color: asset.vulnerabilities_count ? "var(--coral)" : "inherit" }}>
                          {asset.vulnerabilities_count ?? 0}
                        </span>
                      </td>
                      <td>
                        <span
                          style={{
                            fontWeight: 700,
                            color: asset.current_risk_score >= 70 ? "var(--coral)" : (asset.current_risk_score >= 40 ? "var(--amber)" : "var(--teal)"),
                          }}
                        >
                          {asset.current_risk_score} / 100
                        </span>
                      </td>
                      <td>
                        <StatusBadge status={asset.scan_status} />
                      </td>
                      <td>
                        <div style={{ display: "flex", gap: "6px" }}>
                          <button
                            className="btn btn-outline btn-sm"
                            title="Run Scan"
                            onClick={() => handleQuickScan(asset)}
                          >
                            Scan ↗
                          </button>
                          <Link href={`/assets/${asset.id}`} className="btn btn-outline btn-sm">
                            View
                          </Link>
                          <button
                            className="btn btn-outline btn-sm"
                            title="Delete Asset"
                            style={{ color: "#ef4444" }}
                            onClick={() => handleDelete(asset)}
                          >
                            ✕
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

      <AddAssetModal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        onAssetAdded={(newAsset) => setAssets((prev) => [newAsset, ...prev])}
      />

      <NewScanModal
        isOpen={isScanOpen}
        onClose={() => setIsScanOpen(false)}
        assets={assets}
        defaultTarget={scanTargetAsset?.target}
        defaultAssetId={scanTargetAsset?.id}
      />
    </div>
  );
}
