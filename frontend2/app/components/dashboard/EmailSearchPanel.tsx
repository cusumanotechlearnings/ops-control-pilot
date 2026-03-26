"use client";

import { FormEvent, useState } from "react";
import type { EmailSearchResult } from "../../lib/api";

type EmailSearchPanelProps = {
  onSearch: (params: {
    copy: string;
    business_unit: string;
    date_from: string;
    date_to: string;
    sender: string;
  }) => Promise<void>;
  results: EmailSearchResult[];
  loading?: boolean;
  searched?: boolean;
};

const BU_OPTIONS = ["", "UC", "GC", "OL", "MIL", "INTL"];

function fmtDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function fmtNum(n: number | null) {
  if (n == null) return "—";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}k`;
  return String(n);
}

function fmtRate(r: number | null) {
  if (r == null) return "—";
  return `${(Number(r) * 100).toFixed(1)}%`;
}

export function EmailSearchPanel({ onSearch, results, loading, searched }: EmailSearchPanelProps) {
  const [copy, setCopy] = useState("");
  const [bu, setBu] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sender, setSender] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await onSearch({ copy, business_unit: bu, date_from: dateFrom, date_to: dateTo, sender });
  }

  function handleReset() {
    setCopy(""); setBu(""); setDateFrom(""); setDateTo(""); setSender("");
  }

  return (
    <div className="search-panel">
      <form className="search-filter-bar" onSubmit={handleSubmit}>
        <div className="search-filter-row">
          <div className="search-field">
            <label className="search-label">Email copy / name / subject</label>
            <input
              type="text"
              className="search-input"
              placeholder="e.g. FAFSA, Welcome, Deadline"
              value={copy}
              onChange={(e) => setCopy(e.target.value)}
            />
          </div>

          <div className="search-field search-field-sm">
            <label className="search-label">Business Unit</label>
            <select className="search-select" value={bu} onChange={(e) => setBu(e.target.value)}>
              {BU_OPTIONS.map((o) => (
                <option key={o} value={o}>{o || "All BUs"}</option>
              ))}
            </select>
          </div>

          <div className="search-field search-field-sm">
            <label className="search-label">Sender address</label>
            <input
              type="text"
              className="search-input"
              placeholder="e.g. admissions"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
            />
          </div>
        </div>

        <div className="search-filter-row">
          <div className="search-field search-field-sm">
            <label className="search-label">Send date from</label>
            <input
              type="date"
              className="search-input"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
          </div>

          <div className="search-field search-field-sm">
            <label className="search-label">Send date to</label>
            <input
              type="date"
              className="search-input"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </div>

          <div className="search-field search-field-actions">
            <button type="submit" className="search-btn-primary" disabled={loading}>
              {loading ? "Searching…" : "Search"}
            </button>
            <button type="button" className="search-btn-secondary" onClick={handleReset}>
              Reset
            </button>
          </div>
        </div>
      </form>

      {searched && (
        <div className="search-results-wrap">
          {results.length === 0 && !loading ? (
            <p className="search-empty">No emails match your filters.</p>
          ) : (
            <>
              <p className="search-results-count">{results.length} email{results.length !== 1 ? "s" : ""} found</p>
              <div className="search-table-scroll">
                <table className="search-table">
                  <thead>
                    <tr>
                      <th>Email Name</th>
                      <th>BU</th>
                      <th>Subject Line</th>
                      <th>Sender</th>
                      <th>Deliveries</th>
                      <th>Open Rate</th>
                      <th>Click Rate</th>
                      <th>Last Send</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((r) => (
                      <tr key={r.asset_id}>
                        <td className="search-name-cell" title={r.email_name}>{r.email_name}</td>
                        <td><span className="bu-badge">{r.business_unit}</span></td>
                        <td className="search-subject-cell" title={r.subject_line ?? ""}>{r.subject_line ?? "—"}</td>
                        <td className="search-sender-cell">{r.sender_address ?? "—"}</td>
                        <td>{fmtNum(r.deliveries)}</td>
                        <td>{fmtRate(r.avg_open_rate)}</td>
                        <td>{fmtRate(r.avg_click_rate)}</td>
                        <td>{fmtDate(r.last_send_date)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
