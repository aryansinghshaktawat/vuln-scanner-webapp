"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface SidebarProps {
  assetCount?: number;
  scheduleCount?: number;
}

export default function Sidebar({ assetCount = 0, scheduleCount = 0 }: SidebarProps) {
  const pathname = usePathname();

  const navItems = [
    { href: "/", label: "Overview", icon: "⊞" },
    { href: "/assets", label: "Assets", icon: "◈", count: assetCount },
    { href: "/scans", label: "Scan History", icon: "◌" },
    { href: "/vulnerabilities", label: "Vulnerabilities", icon: "!" },
    { href: "/schedules", label: "Schedules", icon: "◷", count: scheduleCount },
    { href: "/reports", label: "Reports", icon: "↓" },
    { href: "/settings", label: "Settings", icon: "⚙" },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">N</span>
        <span>Northstar <b>Security</b></span>
      </div>
      <div className="workspace-label">
        PLATFORM <span>ENTERPRISE</span>
      </div>
      <nav className="nav-list" aria-label="Primary navigation">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-item ${isActive ? "active" : ""}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
              {item.count !== undefined && item.count > 0 && <em>{item.count}</em>}
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <div className="help-card">
          <span className="help-icon">?</span>
          <div>
            <strong>Authorized Testing</strong>
            <small>Defense policy active</small>
          </div>
        </div>
        <div className="user-row">
          <span className="avatar">SO</span>
          <span>
            <strong>SecOps Lead</strong>
            <small>Auditor & Operator</small>
          </span>
        </div>
      </div>
    </aside>
  );
}
