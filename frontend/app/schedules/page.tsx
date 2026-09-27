"use client";

import { useCallback, useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { apiFetch, ScanSchedule, Asset } from "../lib/api";

export default function SchedulesPage() {
  const [schedules, setSchedules] = useState<ScanSchedule[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);

  // New Schedule Modal
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [assetId, setAssetId] = useState("");
  const [profile, setProfile] = useState("full");
  const [cadence, setCadence] = useState("Every 24 hours");
  const [intervalHours, setIntervalHours] = useState(24);
  const [creating, setCreating] = useState(false);

  const fetchSchedules = useCallback(async () => {
    try {
      const [schedulesData, assetsData] = await Promise.all([
        apiFetch<ScanSchedule[]>("/api/schedules"),
        apiFetch<Asset[]>("/api/assets"),
      ]);
      setSchedules(schedulesData || []);
      setAssets(assetsData || []);
      if (assetsData && assetsData.length > 0) {
        setAssetId((prev) => prev || assetsData[0].id);
      }
    } catch (err) {
      console.error("Failed to load schedules:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSchedules();
  }, [fetchSchedules]);

  const handleToggle = async (schedule: ScanSchedule) => {
    try {
      const updated = await apiFetch<ScanSchedule>(`/api/schedules/${schedule.id}`, {
        method: "PUT",
        body: JSON.stringify({ enabled: !schedule.enabled }),
      });
      setSchedules((prev) => prev.map((s) => (s.id === updated.id ? updated : s)));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to toggle schedule");
    }
  };

  const handleDelete = async (scheduleId: string) => {
    if (!confirm("Are you sure you want to remove this recurring schedule?")) return;
    try {
      await apiFetch(`/api/schedules/${scheduleId}`, { method: "DELETE" });
      setSchedules((prev) => prev.filter((s) => s.id !== scheduleId));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete schedule");
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assetId) {
      alert("Please select an asset for this recurring schedule.");
      return;
    }
    setCreating(true);
    try {
      const created = await apiFetch<ScanSchedule>("/api/schedules", {
        method: "POST",
        body: JSON.stringify({
          asset_id: assetId,
          profile,
          cadence,
          interval_hours: Number(intervalHours),
          enabled: true,
        }),
      });
      setSchedules((prev) => [...prev, created]);
      setIsAddOpen(false);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to create schedule");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar scheduleCount={schedules.length} />

      <main className="main-content">
        <Topbar breadcrumbs={["Security Operations", "Scheduled Scanning"]} />

        <section className="page-heading">
          <div>
            <p className="eyebrow">AUTOMATED CADENCE</p>
            <h1>Recurring Scan Schedules<span>.</span></h1>
            <p className="muted">Configure background vulnerability assessments executed periodically by APScheduler.</p>
          </div>
          <button className="btn btn-primary" onClick={() => setIsAddOpen(true)}>
            + Add Schedule
          </button>
        </section>

        {/* Schedules Table */}
        <section className="panel" style={{ padding: "0" }}>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Target Asset</th>
                  <th>Target Destination</th>
                  <th>Scan Profile</th>
                  <th>Cadence</th>
                  <th>Next Execution</th>
                  <th>Last Execution</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={8} style={{ textAlign: "center", padding: "30px", color: "#64748b" }}>
                      Loading automated schedules...
                    </td>
                  </tr>
                ) : schedules.length === 0 ? (
                  <tr>
                    <td colSpan={8} style={{ textAlign: "center", padding: "40px", color: "#94a3b8" }}>
                      No recurring schedules configured. Click &quot;+ Add Schedule&quot; to automate your perimeter assessments.
                    </td>
                  </tr>
                ) : (
                  schedules.map((s) => (
                    <tr key={s.id}>
                      <td>
                        <strong>{s.asset_name}</strong>
                      </td>
                      <td className="mono">{s.asset_target}</td>
                      <td style={{ textTransform: "capitalize" }}>{s.profile}</td>
                      <td>{s.cadence}</td>
                      <td>{new Date(s.next_run).toLocaleString()}</td>
                      <td>{s.last_run ? new Date(s.last_run).toLocaleString() : "Never"}</td>
                      <td>
                        <span className={`badge ${s.enabled ? "badge-success" : "badge-info"}`}>
                          {s.enabled ? "ACTIVE" : "PAUSED"}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: "flex", gap: "6px" }}>
                          <button
                            className="btn btn-outline btn-sm"
                            onClick={() => handleToggle(s)}
                          >
                            {s.enabled ? "Pause" : "Resume"}
                          </button>
                          <button
                            className="btn btn-outline btn-sm"
                            style={{ color: "#ef4444" }}
                            onClick={() => handleDelete(s.id)}
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

      {/* Add Schedule Modal */}
      {isAddOpen && (
        <div className="modal-backdrop">
          <div className="modal-box">
            <div className="modal-header">
              <h3>Create Recurring Scan Schedule</h3>
              <button className="icon-button" onClick={() => setIsAddOpen(false)} style={{ cursor: "pointer", fontSize: "16px" }}>✕</button>
            </div>

            <form onSubmit={handleCreate}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Target Asset</label>
                  <select
                    className="form-control"
                    value={assetId}
                    onChange={(e) => setAssetId(e.target.value)}
                    required
                  >
                    {assets.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.name} ({a.target})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Scan Profile</label>
                  <select
                    className="form-control"
                    value={profile}
                    onChange={(e) => setProfile(e.target.value)}
                  >
                    <option value="full">Full Vulnerability Assessment</option>
                    <option value="quick">Quick Discovery (Port scan only)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Cadence Interval</label>
                  <select
                    className="form-control"
                    value={intervalHours}
                    onChange={(e) => {
                      const val = Number(e.target.value);
                      setIntervalHours(val);
                      if (val === 24) setCadence("Every 24 hours");
                      else if (val === 168) setCadence("Every 7 days");
                      else setCadence(`Every ${val} hours`);
                    }}
                  >
                    <option value={24}>Daily (Every 24 hours)</option>
                    <option value={168}>Weekly (Every 7 days)</option>
                    <option value={12}>Twice Daily (Every 12 hours)</option>
                    <option value={720}>Monthly (Every 30 days)</option>
                  </select>
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={() => setIsAddOpen(false)} disabled={creating}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? "Scheduling..." : "Create Schedule"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
