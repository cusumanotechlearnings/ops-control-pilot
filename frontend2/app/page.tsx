"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  fetchMetricsSummary,
  fetchMetricsTrend,
  fetchJourneys,
  fetchUpcomingCalendar,
  fetchEmailSearch,
  type MetricsOverall,
  type TrendRow,
  type Journey,
  type CalendarDay,
  type EmailSearchResult,
} from "./lib/api";
import {
  MetricCard,
  TrendChart,
  SendsCalendar,
  JourneysPanel,
  EmailSearchPanel,
  DashboardChatBar,
} from "./components/dashboard";

function fmtNum(n: number | null | undefined) {
  if (n == null) return "—";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(n);
}

function fmtPct(r: number | null | undefined) {
  if (r == null) return "—";
  return `${(Number(r) * 100).toFixed(1)}%`;
}

function fmtSentiment(v: number | null | undefined) {
  if (v == null) return "—";
  const n = Number(v);
  return `${n >= 0 ? "+" : ""}${n.toFixed(2)}`;
}

export default function DashboardPage() {
  const [calYear, setCalYear] = useState<number | null>(null);
  const [calMonth, setCalMonth] = useState<number | null>(null);

  // Data state
  const [overall, setOverall] = useState<MetricsOverall | null>(null);
  const [trend, setTrend] = useState<TrendRow[]>([]);
  const [journeys, setJourneys] = useState<Journey[]>([]);
  const [calDays, setCalDays] = useState<CalendarDay[]>([]);
  const [searchResults, setSearchResults] = useState<EmailSearchResult[]>([]);

  // Loading state
  const [loadingMetrics, setLoadingMetrics] = useState(true);
  const [loadingTrend, setLoadingTrend] = useState(true);
  const [loadingJourneys, setLoadingJourneys] = useState(true);
  const [loadingCal, setLoadingCal] = useState(true);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [searched, setSearched] = useState(false);

  // Error state (non-fatal: shown inline per section)
  const [metricsError, setMetricsError] = useState(false);

  // Initial data load
  useEffect(() => {
    fetchMetricsSummary(365)
      .then((d) => { setOverall(d.overall); setLoadingMetrics(false); })
      .catch(() => { setLoadingMetrics(false); setMetricsError(true); });

    fetchMetricsTrend(90)
      .then((d) => { setTrend(d.trend); setLoadingTrend(false); })
      .catch(() => setLoadingTrend(false));

    fetchJourneys()
      .then((d) => { setJourneys(d.journeys); setLoadingJourneys(false); })
      .catch(() => setLoadingJourneys(false));
  }, []);

  // Calendar reload on month change; first load defaults to current month
  useEffect(() => {
    setLoadingCal(true);
    fetchUpcomingCalendar(calYear ?? undefined, calMonth ?? undefined)
      .then((d) => {
        setCalDays(d.days);
        setCalYear(d.year);
        setCalMonth(d.month);
        setLoadingCal(false);
      })
      .catch(() => setLoadingCal(false));
  }, [calYear, calMonth]);

  const handleMonthChange = useCallback((y: number, m: number) => {
    setCalYear(y);
    setCalMonth(m);
  }, []);

  const handleSearch = useCallback(async (params: {
    copy: string;
    business_unit: string;
    date_from: string;
    date_to: string;
    sender: string;
  }) => {
    setLoadingSearch(true);
    setSearched(true);
    try {
      const data = await fetchEmailSearch(params);
      setSearchResults(data.results);
    } catch {
      setSearchResults([]);
    } finally {
      setLoadingSearch(false);
    }
  }, []);

  return (
    <div className="dashboard-shell">
      {/* Sidebar */}
      <aside className="sidebar-root">
        <div className="sidebar-header">
          <h1 className="sidebar-app-name">Marketing Ops AI</h1>
          <p className="sidebar-powered-by">Powered by Claude</p>
        </div>

        <nav className="sidebar-nav-links">
          <span className="sidebar-nav-item active">Dashboard</span>
          <Link href="/chat" className="sidebar-nav-item">
            AI Chat →
          </Link>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-footer-divider" />
          <p>Marketing Ops · Internal Tool</p>
        </div>
      </aside>

      {/* Main content */}
      <div className="dashboard-main">
        <header className="topbar dashboard-topbar">
          <h2>Marketing Ops Dashboard</h2>
          <span className="topbar-period">
            {overall?.earliest_date && overall?.latest_date
              ? `${new Date(overall.earliest_date).toLocaleDateString("en-US", { month: "short", year: "numeric" })} – ${new Date(overall.latest_date).toLocaleDateString("en-US", { month: "short", year: "numeric" })}`
              : "Last 12 months"}
          </span>
        </header>

        <div className="dashboard-scroll">

          {/* ── KPI Cards ── */}
          <section className="dashboard-section">
            <h3 className="section-title">Send Performance</h3>
            {metricsError ? (
              <p className="section-error">Could not load metrics — check backend connection.</p>
            ) : (
              <div className="kpi-grid">
                <MetricCard
                  title="Total Sends"
                  value={fmtNum(overall?.total_sends)}
                  loading={loadingMetrics}
                />
                <MetricCard
                  title="Deliveries"
                  value={fmtNum(overall?.deliveries)}
                  sub={`${fmtPct(overall?.avg_delivery_rate)} delivery rate`}
                  loading={loadingMetrics}
                />
                <MetricCard
                  title="Avg Open Rate"
                  value={fmtPct(overall?.avg_open_rate)}
                  loading={loadingMetrics}
                />
                <MetricCard
                  title="Avg Click Rate"
                  value={fmtPct(overall?.avg_click_rate)}
                  loading={loadingMetrics}
                />
                <MetricCard
                  title="Click-to-Open"
                  value={fmtPct(overall?.avg_ctor)}
                  loading={loadingMetrics}
                />
                <MetricCard
                  title="VOC Sentiment"
                  value={fmtSentiment(overall?.avg_sentiment)}
                  sub="avg score (−1 to +1)"
                  loading={loadingMetrics}
                />
              </div>
            )}
          </section>

          {/* ── Trend Chart ── */}
          <section className="dashboard-section">
            <div className="dashboard-card">
              <h3 className="section-title">Daily Trend</h3>
              <TrendChart data={trend} loading={loadingTrend} />
            </div>
          </section>

          {/* ── Journeys ── */}
          <section className="dashboard-section">
            <div className="dashboard-card journeys-card">
              <h3 className="section-title">Automated Sends</h3>
              <JourneysPanel journeys={journeys} loading={loadingJourneys} />
            </div>
          </section>

          {/* ── Sends Calendar ── */}
          <section className="dashboard-section">
            <div className="dashboard-card">
              <h3 className="section-title">Upcoming Sends</h3>
              {calYear && calMonth ? (
                <SendsCalendar
                  data={calDays}
                  year={calYear}
                  month={calMonth}
                  onMonthChange={handleMonthChange}
                  loading={loadingCal}
                />
              ) : (
                <p className="section-subtitle">Loading calendar…</p>
              )}
            </div>
          </section>

          {/* ── Email Asset Search ── */}
          <section className="dashboard-section">
            <div className="dashboard-card">
              <h3 className="section-title">Email Asset Search</h3>
              <p className="section-subtitle">
                Search by email copy, subject line, business unit, sender, or send date range.
              </p>
              <EmailSearchPanel
                onSearch={handleSearch}
                results={searchResults}
                loading={loadingSearch}
                searched={searched}
              />
            </div>
          </section>

          {/* ── AI Chat Bar ── */}
          <DashboardChatBar />

        </div>
      </div>
    </div>
  );
}
