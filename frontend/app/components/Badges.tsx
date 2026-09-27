export function SeverityBadge({ severity }: { severity: string }) {
  const sev = (severity || "INFO").toUpperCase();
  let badgeClass = "badge-info";
  if (sev === "CRITICAL") badgeClass = "badge-critical";
  else if (sev === "HIGH") badgeClass = "badge-high";
  else if (sev === "MEDIUM") badgeClass = "badge-medium";
  else if (sev === "LOW") badgeClass = "badge-low";

  return <span className={`badge ${badgeClass}`}>{sev}</span>;
}

export function StatusBadge({ status }: { status: string }) {
  const st = (status || "QUEUED").toUpperCase();
  let statusClass = "status-queued";
  if (st === "COMPLETED" || st === "COMPLETE" || st === "RESOLVED") statusClass = "status-completed";
  else if (st === "RUNNING" || st === "IN_PROGRESS") statusClass = "status-running";
  else if (st === "FAILED") statusClass = "status-failed";
  else if (st === "TIMEOUT") statusClass = "status-timeout";
  else if (st === "CANCELLED") statusClass = "status-cancelled";

  return (
    <span className={`status-badge ${statusClass}`}>
      <i />
      {st.replace("_", " ")}
    </span>
  );
}

export function EnvironmentPill({ environment }: { environment: string }) {
  const env = (environment || "production").toLowerCase();
  let pillClass = "env-prod";
  if (env === "staging") pillClass = "env-staging";
  else if (env === "development") pillClass = "env-dev";
  else if (env === "internal") pillClass = "env-internal";

  return <span className={`env-pill ${pillClass}`}>{env}</span>;
}
