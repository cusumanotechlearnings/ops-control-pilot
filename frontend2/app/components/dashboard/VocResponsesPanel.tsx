"use client";

import { useState } from "react";
import type { VocResponse } from "../../lib/api";

type VocResponsesPanelProps = {
  responses: VocResponse[];
  loading?: boolean;
};

type SentimentFilter = "All" | "positive" | "neutral" | "negative";

function normalizeSentiment(raw: string | null): "positive" | "neutral" | "negative" | null {
  if (raw == null) return null;
  const v = raw.toString().toLowerCase().trim();
  if (v === "positive" || v === "1") return "positive";
  if (v === "negative" || v === "-1") return "negative";
  if (v === "neutral" || v === "0") return "neutral";
  return null;
}

function SentimentBadge({ sentiment }: { sentiment: string | null }) {
  const norm = normalizeSentiment(sentiment);
  const labels: Record<string, string> = {
    positive: "Positive",
    neutral: "Neutral",
    negative: "Negative",
  };
  const colors: Record<string, { bg: string; text: string }> = {
    positive: { bg: "#dcfce7", text: "#166534" },
    neutral:  { bg: "#f3f4f6", text: "#6b7280" },
    negative: { bg: "#fee2e2", text: "#991b1b" },
  };
  const c = norm ? colors[norm] : { bg: "#f3f4f6", text: "#6b7280" };
  return (
    <span
      className="voc-sentiment-badge"
      style={{ background: c.bg, color: c.text }}
    >
      {norm ? labels[norm] : (sentiment ?? "—")}
    </span>
  );
}

function rowClass(sentiment: string | null): string {
  const norm = normalizeSentiment(sentiment);
  if (norm === "positive") return "voc-row-positive";
  if (norm === "negative") return "voc-row-negative";
  return "voc-row-neutral";
}

function fmtDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

const SENTIMENT_TABS: SentimentFilter[] = ["All", "positive", "neutral", "negative"];
const TAB_LABELS: Record<SentimentFilter, string> = {
  All: "All",
  positive: "Positive",
  neutral: "Neutral",
  negative: "Negative",
};

const PAGE_SIZE = 15;

export function VocResponsesPanel({ responses, loading }: VocResponsesPanelProps) {
  const [sentimentFilter, setSentimentFilter] = useState<SentimentFilter>("All");
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const filtered = responses.filter((r) => {
    const norm = normalizeSentiment(r.sentiment);
    const matchSentiment =
      sentimentFilter === "All" || norm === sentimentFilter;
    const matchSearch =
      !search ||
      (r.response_text ?? "").toLowerCase().includes(search.toLowerCase()) ||
      (r.subscriber_email ?? "").toLowerCase().includes(search.toLowerCase()) ||
      (r.target_audience ?? "").toLowerCase().includes(search.toLowerCase());
    return matchSentiment && matchSearch;
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(currentPage, totalPages);
  const pageStart = (safePage - 1) * PAGE_SIZE;
  const paginated = filtered.slice(pageStart, pageStart + PAGE_SIZE);

  function handleSentimentFilter(s: SentimentFilter) {
    setSentimentFilter(s);
    setCurrentPage(1);
  }

  function handleSearch(value: string) {
    setSearch(value);
    setCurrentPage(1);
  }

  return (
    <div className="voc-panel">
      <div className="voc-filters">
        <div className="voc-tab-group">
          {SENTIMENT_TABS.map((s) => (
            <button
              key={s}
              type="button"
              className={`voc-tab${sentimentFilter === s ? " active" : ""}${s !== "All" ? ` voc-tab-${s}` : ""}`}
              onClick={() => handleSentimentFilter(s)}
            >
              {TAB_LABELS[s]}
            </button>
          ))}
        </div>
        <input
          type="text"
          className="voc-search"
          placeholder="Search feedback, email, audience…"
          value={search}
          onChange={(e) => handleSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="voc-loading">Loading VOC responses…</div>
      ) : (
        <div className="voc-table-wrap">
          <table className="voc-table">
            <thead>
              <tr>
                <th>Feedback</th>
                <th>Date</th>
                <th>Sentiment</th>
                <th>Email</th>
                <th>Audience</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="voc-empty">
                    No VOC responses match the current filters.
                  </td>
                </tr>
              ) : (
                paginated.map((r) => (
                  <tr key={r.id} className={rowClass(r.sentiment)}>
                    <td className="voc-feedback-cell" title={r.response_text ?? ""}>
                      {r.response_text ?? "—"}
                    </td>
                    <td className="voc-date-cell">{fmtDate(r.response_date)}</td>
                    <td><SentimentBadge sentiment={r.sentiment} /></td>
                    <td className="voc-email-cell">{r.subscriber_email ?? "—"}</td>
                    <td>{r.target_audience ?? "—"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="voc-footer">
        <p className="voc-count">
          {loading ? "" : `${filtered.length} of ${responses.length} responses`}
        </p>
        {!loading && totalPages > 1 && (
          <div className="voc-pagination">
            <button
              type="button"
              className="voc-page-btn"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={safePage === 1}
            >
              ‹
            </button>
            <span className="voc-page-label">
              Page {safePage} of {totalPages}
            </span>
            <button
              type="button"
              className="voc-page-btn"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={safePage === totalPages}
            >
              ›
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
