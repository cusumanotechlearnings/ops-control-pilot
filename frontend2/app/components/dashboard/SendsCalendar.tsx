"use client";

import { useMemo, useState } from "react";

type CalendarDay = {
  send_date: string;
  send_count: number;
  total_sends: number;
  deliveries: number;
  avg_open_rate: number | null;
  avg_click_rate: number | null;
  has_planned: boolean;
  has_actual: boolean;
  email_names: string[];
  journey_names: string[];
};

type SendsCalendarProps = {
  data: CalendarDay[];
  year: number;
  month: number;
  onMonthChange: (year: number, month: number) => void;
  loading?: boolean;
};

const MONTH_NAMES = [
  "January","February","March","April","May","June",
  "July","August","September","October","November","December",
];
const DOW = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];

function fmt(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}k`;
  return String(n);
}

function pct(rate: number | null) {
  if (rate == null) return "—";
  return `${(Number(rate) * 100).toFixed(1)}%`;
}

export function SendsCalendar({ data, year, month, onMonthChange, loading }: SendsCalendarProps) {
  const [tooltip, setTooltip] = useState<CalendarDay | null>(null);

  const dayMap = useMemo(() => {
    const m: Record<string, CalendarDay> = {};
    for (const d of data) m[d.send_date] = d;
    return m;
  }, [data]);

  const maxSends = useMemo(() => Math.max(...data.map((d) => d.send_count), 1), [data]);

  // Build the grid cells: pad with nulls for the first week
  const cells = useMemo(() => {
    const firstDay = new Date(year, month - 1, 1).getDay();
    const daysInMonth = new Date(year, month, 0).getDate();
    const result: (number | null)[] = [];
    for (let i = 0; i < firstDay; i++) result.push(null);
    for (let d = 1; d <= daysInMonth; d++) result.push(d);
    return result;
  }, [year, month]);

  function prevMonth() {
    if (month === 1) onMonthChange(year - 1, 12);
    else onMonthChange(year, month - 1);
  }
  function nextMonth() {
    if (month === 12) onMonthChange(year + 1, 1);
    else onMonthChange(year, month + 1);
  }

  function dateKey(day: number) {
    return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
  }

  function heatOpacity(sendCount: number) {
    return 0.15 + (sendCount / maxSends) * 0.75;
  }

  return (
    <div className="sends-calendar">
      <div className="calendar-nav">
        <button type="button" className="cal-nav-btn" onClick={prevMonth}>‹</button>
        <span className="calendar-month-label">{MONTH_NAMES[month - 1]} {year}</span>
        <button type="button" className="cal-nav-btn" onClick={nextMonth}>›</button>
        <div className="calendar-legend">
          <span className="legend-item legend-planned">◎ Journey launch</span>
        </div>
      </div>

      <div className="calendar-grid">
        {DOW.map((d) => (
          <div key={d} className="calendar-dow">{d}</div>
        ))}

        {cells.map((day, i) => {
          if (day === null) return <div key={`pad-${i}`} className="calendar-cell empty" />;
          const key = dateKey(day);
          const info = dayMap[key];
          const hasSend = !!info;
          const isPlannedOnly = hasSend && info.has_planned && !info.has_actual;
          const isMixed = hasSend && info.has_planned && info.has_actual;

          return (
            <div
              key={key}
              className={`calendar-cell ${hasSend ? "has-send" : ""} ${isPlannedOnly ? "planned-only" : ""} ${isMixed ? "mixed-send" : ""}`}
              onMouseEnter={() => hasSend && setTooltip(info)}
              onMouseLeave={() => setTooltip(null)}
            >
              <span className="calendar-day-num">{day}</span>
              {hasSend && (
                <span
                  className={`calendar-dot ${isPlannedOnly ? "dot-planned" : ""}`}
                  style={{ opacity: heatOpacity(info.send_count) }}
                />
              )}
              {hasSend && info.send_count > 0 && (
                <span className="calendar-count">{info.send_count}</span>
              )}
            </div>
          );
        })}
      </div>

      {loading && <div className="calendar-loading">Loading…</div>}

      {tooltip && (
        <div className="calendar-tooltip">
          <p className="tooltip-date">
            {tooltip.send_date}
            {tooltip.has_planned && !tooltip.has_actual && (
              <span className="tooltip-planned-badge"> Scheduled</span>
            )}
            {tooltip.has_planned && tooltip.has_actual && (
              <span className="tooltip-planned-badge"> Partial schedule</span>
            )}
          </p>
          <p>
            <strong>{tooltip.send_count}</strong> journey{tooltip.send_count !== 1 ? "s" : ""} launching
            {tooltip.total_sends > 0 && (
              <> · {tooltip.has_planned && !tooltip.has_actual ? "Projected: " : ""}<strong>{fmt(tooltip.total_sends)}</strong> recipients</>
            )}
          </p>
          {tooltip.has_actual && (
            <p>Open rate: {pct(tooltip.avg_open_rate)} · Click rate: {pct(tooltip.avg_click_rate)}</p>
          )}
          {tooltip.journey_names?.length > 0 && (
            <p className="tooltip-journeys">
              {tooltip.journey_names.slice(0, 5).join(", ")}
              {tooltip.journey_names.length > 5 ? ` +${tooltip.journey_names.length - 5} more` : ""}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
