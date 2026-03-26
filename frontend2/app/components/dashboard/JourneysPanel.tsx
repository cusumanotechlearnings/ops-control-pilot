"use client";

import { useState } from "react";

type Journey = {
  journey_id: string;
  journey_name: string;
  business_unit: string;
  status: string;
  target_audience: string | null;
  department: string | null;
  last_send_date: string | null;
  first_send_date: string | null;
  schedule_frequency: string | null;
  schedule_start_time: string | null;
  schedule_end_time: string | null;
};

type JourneysPanelProps = {
  journeys: Journey[];
  loading?: boolean;
};

const STATUS_COLORS: Record<string, string> = {
  Active:   "#2d7d57",
  Stopped:  "#b91c1c",
  Paused:   "#c2820a",
  Draft:    "#6b7280",
  Complete: "#2c5f8a",
};

function StatusBadge({ status }: { status: string }) {
  const color = STATUS_COLORS[status] ?? "#6b7280";
  return (
    <span className="journey-status-badge" style={{ background: color + "22", color }}>
      {status}
    </span>
  );
}

function fmtDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export function JourneysPanel({ journeys, loading }: JourneysPanelProps) {
  const [statusFilter, setStatusFilter] = useState<string>("Active");
  const [search, setSearch] = useState("");

  const filtered = journeys.filter((j) => {
    const matchStatus = statusFilter === "All" || j.status === statusFilter;
    const matchSearch = !search || j.journey_name.toLowerCase().includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  const statuses = ["All", "Active", "Stopped", "Draft"];

  return (
    <div className="journeys-panel">
      <div className="journeys-filters">
        <div className="journey-status-tabs">
          {statuses.map((s) => (
            <button
              key={s}
              type="button"
              className={`journey-tab ${statusFilter === s ? "active" : ""}`}
              onClick={() => setStatusFilter(s)}
            >
              {s}
            </button>
          ))}
        </div>
        <input
          type="text"
          className="journey-search"
          placeholder="Search journeys…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="journeys-loading">Loading journeys…</div>
      ) : (
        <div className="journeys-table-wrap">
          <table className="journeys-table">
            <thead>
              <tr>
                <th>Journey Name</th>
                <th>BU</th>
                <th>Status</th>
                <th>Audience</th>
                <th>Frequency</th>
                <th>Last Send</th>
                <th>Schedule End</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="journeys-empty">No journeys match your filters.</td>
                </tr>
              ) : (
                filtered.map((j) => (
                  <tr key={j.journey_id}>
                    <td className="journey-name-cell" title={j.journey_name}>{j.journey_name}</td>
                    <td><span className="bu-badge">{j.business_unit}</span></td>
                    <td><StatusBadge status={j.status} /></td>
                    <td>{j.target_audience ?? "—"}</td>
                    <td>{j.schedule_frequency ?? "—"}</td>
                    <td>{fmtDate(j.last_send_date)}</td>
                    <td>{fmtDate(j.schedule_end_time)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      <p className="journeys-count">
        {loading ? "" : `${filtered.length} of ${journeys.length} journeys`}
      </p>
    </div>
  );
}
