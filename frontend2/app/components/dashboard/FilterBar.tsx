"use client";

import { useEffect, useRef, useState } from "react";

export type GlobalFilters = {
  dateFrom: string;
  dateTo: string;
  audience: string;
  subjectLine: string;
};

const EMPTY_FILTERS: GlobalFilters = { dateFrom: "", dateTo: "", audience: "", subjectLine: "" };

const BU_OPTIONS: { value: string; label: string; short: string }[] = [
  { value: "",     label: "All Audiences", short: "All" },
  { value: "UC",   label: "Undergraduate", short: "UC" },
  { value: "GC",   label: "Graduate",      short: "GC" },
  { value: "INTL", label: "International", short: "INTL" },
  { value: "MIL",  label: "Military",      short: "MIL" },
  { value: "OL",   label: "Online",        short: "OL" },
];

type FilterBarProps = {
  filters: GlobalFilters;
  onApply: (filters: GlobalFilters) => void;
};

function fmtPillDate(iso: string) {
  const [y, m, d] = iso.split("-");
  return `${m}/${d}/${y.slice(2)}`;
}

export function FilterBar({ filters, onApply }: FilterBarProps) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<GlobalFilters>(filters);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => { setDraft(filters); }, [filters]);

  useEffect(() => {
    if (!open) return;
    function handleOutside(e: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, [open]);

  const isActive = !!(filters.dateFrom || filters.dateTo || filters.audience || filters.subjectLine);

  const pillLabel = (() => {
    if (!isActive) return "All Time · All Audiences";
    const parts: string[] = [];
    if (filters.dateFrom || filters.dateTo) {
      const from = filters.dateFrom ? fmtPillDate(filters.dateFrom) : "…";
      const to   = filters.dateTo   ? fmtPillDate(filters.dateTo)   : "…";
      parts.push(`${from} – ${to}`);
    }
    if (filters.audience) {
      const opt = BU_OPTIONS.find((o) => o.value === filters.audience);
      parts.push(opt?.short ?? filters.audience);
    }
    if (filters.subjectLine) {
      parts.push(`"${filters.subjectLine}"`);
    }
    return parts.join(" · ");
  })();

  function handleApply() {
    onApply({ ...draft });
    setOpen(false);
  }

  function handleClear() {
    setDraft(EMPTY_FILTERS);
    onApply(EMPTY_FILTERS);
    setOpen(false);
  }

  return (
    <div className="filter-bar-wrap" ref={wrapRef}>
      <button
        type="button"
        className={`filter-pill${isActive ? " active" : ""}`}
        onClick={() => { setDraft(filters); setOpen((v) => !v); }}
        aria-expanded={open}
      >
        <svg className="filter-pill-icon" viewBox="0 0 16 16" fill="none" aria-hidden>
          <path d="M2 4h12M4 8h8M6 12h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
        <span className="filter-pill-label">{pillLabel}</span>
        <span className="filter-pill-caret" aria-hidden>{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="filter-popover" role="dialog" aria-label="Dashboard filters">
          <p className="filter-popover-heading">Filter Dashboard</p>

          {/* Date range */}
          <div className="filter-section">
            <span className="filter-section-label">Date Range</span>
            <div className="filter-date-row">
              <div className="filter-date-field">
                <label className="filter-date-hint" htmlFor="fb-date-from">From</label>
                <input
                  id="fb-date-from"
                  type="date"
                  className="filter-date-input"
                  value={draft.dateFrom}
                  max={draft.dateTo || undefined}
                  onChange={(e) => setDraft((d) => ({ ...d, dateFrom: e.target.value }))}
                />
              </div>
              <span className="filter-date-arrow" aria-hidden>→</span>
              <div className="filter-date-field">
                <label className="filter-date-hint" htmlFor="fb-date-to">To</label>
                <input
                  id="fb-date-to"
                  type="date"
                  className="filter-date-input"
                  value={draft.dateTo}
                  min={draft.dateFrom || undefined}
                  onChange={(e) => setDraft((d) => ({ ...d, dateTo: e.target.value }))}
                />
              </div>
            </div>
          </div>

          {/* Audience */}
          <div className="filter-section">
            <span className="filter-section-label">Audience</span>
            <div className="filter-audience-grid">
              {BU_OPTIONS.map((o) => (
                <button
                  key={o.value}
                  type="button"
                  className={`filter-audience-btn${draft.audience === o.value ? " active" : ""}`}
                  onClick={() => setDraft((d) => ({ ...d, audience: o.value }))}
                >
                  {o.label}
                </button>
              ))}
            </div>
          </div>

          {/* Subject Line */}
          <div className="filter-section">
            <label className="filter-section-label" htmlFor="fb-subject-line">
              Subject Line Contains
            </label>
            <input
              id="fb-subject-line"
              type="text"
              className="filter-date-input"
              placeholder="e.g. graduation"
              value={draft.subjectLine}
              onChange={(e) => setDraft((d) => ({ ...d, subjectLine: e.target.value }))}
            />
          </div>

          {/* Actions */}
          <div className="filter-popover-actions">
            <button type="button" className="filter-clear-btn" onClick={handleClear}>
              Clear filters
            </button>
            <button type="button" className="filter-apply-btn" onClick={handleApply}>
              Apply
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
