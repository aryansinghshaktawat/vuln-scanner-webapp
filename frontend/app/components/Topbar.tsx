"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { apiFetch, NotificationItem } from "../lib/api";

interface TopbarProps {
  breadcrumbs: string[];
  onOpenNewScan?: () => void;
}

export default function Topbar({ breadcrumbs }: TopbarProps) {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [showNotif, setShowNotif] = useState(false);
  const [nmapOnline, setNmapOnline] = useState<boolean | null>(null);

  useEffect(() => {
    // Check health
    apiFetch<{ nmap: boolean; api: boolean }>("/health")
      .then((data) => setNmapOnline(data.nmap))
      .catch(() => setNmapOnline(false));

    // Fetch notifications
    apiFetch<NotificationItem[]>("/api/notifications")
      .then((data) => setNotifications(data || []))
      .catch(() => setNotifications([]));
  }, []);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const markAllRead = async () => {
    try {
      await apiFetch("/api/notifications/read-all", { method: "POST" });
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch {
      // Ignore
    }
  };

  return (
    <header className="topbar">
      <div className="breadcrumbs">
        {breadcrumbs.map((b, i) => (
          <span key={i}>
            {i > 0 && " / "}
            {i === breadcrumbs.length - 1 ? <strong>{b}</strong> : b}
          </span>
        ))}
      </div>

      <div className="top-actions" style={{ position: "relative" }}>
        <span className="system-status">
          <i style={{ background: nmapOnline ? "#10b981" : "#ef4444" }} />
          {nmapOnline ? "Nmap engine ready" : "Nmap engine unavailable"}
        </span>

        <button
          className="icon-button"
          aria-label="Notifications"
          onClick={() => setShowNotif(!showNotif)}
          style={{ position: "relative", cursor: "pointer", fontSize: "16px" }}
        >
          🔔
          {unreadCount > 0 && (
            <span
              style={{
                position: "absolute",
                top: "-4px",
                right: "-6px",
                background: "#ef4444",
                color: "#fff",
                borderRadius: "50%",
                fontSize: "9px",
                fontWeight: 700,
                width: "14px",
                height: "14px",
                display: "grid",
                placeItems: "center",
              }}
            >
              {unreadCount}
            </span>
          )}
        </button>

        {showNotif && (
          <div className="notification-popup">
            <div className="notif-header">
              <span>SECURITY ALERTS</span>
              {unreadCount > 0 && (
                <button
                  onClick={markAllRead}
                  style={{ border: 0, background: "transparent", color: "var(--teal)", fontSize: "9px", cursor: "pointer" }}
                >
                  Mark all read
                </button>
              )}
            </div>
            <div className="notif-list">
              {notifications.length === 0 ? (
                <div style={{ padding: "16px", textAlign: "center", color: "#94a3b8", fontSize: "11px" }}>
                  No recent security alerts.
                </div>
              ) : (
                notifications.slice(0, 5).map((n) => (
                  <div key={n.id} className="notif-item">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <strong>{n.title}</strong>
                      <span className={`badge badge-${n.severity.toLowerCase()}`} style={{ fontSize: "8px" }}>
                        {n.severity}
                      </span>
                    </div>
                    <p>{n.message}</p>
                    <small>{new Date(n.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</small>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        <Link href="/settings" className="outline-button" style={{ textDecoration: "none" }}>
          Target Safety Notice ↗
        </Link>
      </div>
    </header>
  );
}
