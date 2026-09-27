"use client";

import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { apiFetch } from "../lib/api";

interface SystemHealth {
  status?: string;
  api?: boolean;
  nmap?: boolean;
  database?: boolean;
  version?: string;
}

export default function SettingsPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);

  useEffect(() => {
    apiFetch<SystemHealth>("/health").then(setHealth).catch(() => {});
  }, []);

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <Topbar breadcrumbs={["Security Operations", "Settings & Target Safety Policy"]} />

        <section className="page-heading">
          <div>
            <p className="eyebrow">GOVERNANCE & SAFEGUARDS</p>
            <h1>Platform Policies & Settings<span>.</span></h1>
            <p className="muted">Target safety authorization policies, scanner security controls, and operational limits.</p>
          </div>
        </section>

        {/* Authorization & Legal Warning */}
        <section
          className="panel"
          style={{
            borderColor: "#fecaca",
            background: "#fff5f5",
            marginBottom: "24px",
          }}
        >
          <div style={{ display: "flex", gap: "14px", alignItems: "flex-start" }}>
            <span style={{ fontSize: "28px" }}>🛡️</span>
            <div>
              <h3 style={{ margin: "0 0 6px 0", color: "#991b1b", font: "500 18px Georgia, serif" }}>
                Defensive Security Notice & Authorization Requirement
              </h3>
              <p style={{ margin: "0 0 8px 0", fontSize: "12px", color: "#7f1d1d", lineHeight: 1.5 }}>
                The Northstar Vulnerability Management Platform is engineered strictly for authorized defensive security
                audits, asset posture monitoring, and remediation tracking. Users must only initiate scans against systems,
                domains, or IP spaces that they own or for which they hold prior written authorization.
              </p>
              <p style={{ margin: 0, fontSize: "11px", color: "#991b1b" }}>
                Unauthorized port scanning or exploitation attempts may violate the Computer Fraud and Abuse Act (CFAA),
                GDPR, and local telecommunications laws.
              </p>
            </div>
          </div>
        </section>

        {/* Security Controls Grid */}
        <div className="content-grid" style={{ marginBottom: "24px" }}>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">CONTROLS</p>
                <h2>Subprocess & SSRF Defenses</h2>
              </div>
            </div>

            <ul className="reasons-list">
              <li>
                <strong>Command Injection Prevention:</strong> Nmap arguments are passed exclusively as isolated subprocess arrays with <code>shell=False</code>. Shell command concatenation is prohibited.
              </li>
              <li>
                <strong>SSRF & Cloud Metadata Filtering:</strong> Target inputs resolving to <code>169.254.169.254</code> (AWS/GCP/Azure instance metadata), link-local addresses, or multicast subnets are blocked server-side.
              </li>
              <li>
                <strong>Subnet Concurrency Bounds:</strong> CIDR ranges are restricted to a maximum of 256 addresses (/24) per scan to prevent denial of service.
              </li>
              <li>
                <strong>Execution Watchdog Timers:</strong> Scans enforce strict profile timeouts (180s for Quick, 600s for Deep). Runaway processes are forcibly terminated.
              </li>
            </ul>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">SYSTEM ENVIRONMENT</p>
                <h2>Engine Health & Status</h2>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", fontSize: "12px" }}>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>BACKEND API</span>
                <strong style={{ color: health?.api ? "var(--green)" : "var(--coral)" }}>
                  {health?.api ? "Operational" : "Unavailable"}
                </strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>NMAP SCANNER</span>
                <strong style={{ color: health?.nmap ? "var(--green)" : "var(--coral)" }}>
                  {health?.nmap ? "Installed & Executable" : "Not Found"}
                </strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>DATABASE</span>
                <strong style={{ color: health?.database ? "var(--green)" : "var(--coral)" }}>
                  {health?.database ? "Connected (SQLAlchemy)" : "Disconnected"}
                </strong>
              </div>
              <div>
                <span style={{ color: "#94a3b8", display: "block", fontSize: "10px" }}>PLATFORM VERSION</span>
                <span>{health?.version || "2.0.0"}</span>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
