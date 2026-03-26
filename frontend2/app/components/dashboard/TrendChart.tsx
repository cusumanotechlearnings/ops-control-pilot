"use client";

import { useMemo, useState } from "react";

type TrendRow = {
  send_date: string;
  total_sends: number;
  deliveries: number;
  total_opens: number;
  total_clicks: number;
  avg_open_rate: number;
  avg_click_rate: number;
};

type Series = "deliveries" | "total_opens" | "total_clicks";

const SERIES_CONFIG: Record<Series, { label: string; color: string }> = {
  deliveries:   { label: "Deliveries",  color: "#2c5f8a" },
  total_opens:  { label: "Opens",       color: "#3d8b8b" },
  total_clicks: { label: "Clicks",      color: "#2d7d57" },
};

type TrendChartProps = {
  data: TrendRow[];
  loading?: boolean;
};

const WIDTH = 600;
const HEIGHT = 180;
const PAD = { top: 12, right: 16, bottom: 32, left: 52 };

function formatDate(iso: string) {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function formatNum(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}k`;
  return String(n);
}

export function TrendChart({ data, loading }: TrendChartProps) {
  const [active, setActive] = useState<Series>("deliveries");

  const chartW = WIDTH - PAD.left - PAD.right;
  const chartH = HEIGHT - PAD.top - PAD.bottom;

  const values = useMemo(() => data.map((d) => Number(d[active]) || 0), [data, active]);
  const maxVal = useMemo(() => Math.max(...values, 1), [values]);

  // Show at most ~15 x-axis labels
  const tickStep = Math.ceil(data.length / 12);

  const bars = useMemo(() => {
    if (!data.length) return [];
    const barW = Math.max(2, (chartW / data.length) * 0.7);
    const gap = chartW / data.length;
    return data.map((row, i) => {
      const val = Number(row[active]) || 0;
      const barH = (val / maxVal) * chartH;
      const x = PAD.left + i * gap + (gap - barW) / 2;
      const y = PAD.top + chartH - barH;
      return { x, y, width: barW, height: barH, val, date: row.send_date };
    });
  }, [data, active, chartW, chartH, maxVal]);

  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((t) => ({
    y: PAD.top + chartH - t * chartH,
    label: formatNum(Math.round(t * maxVal)),
  }));

  if (loading) {
    return <div className="trend-chart-loading">Loading trend data…</div>;
  }

  if (!data.length) {
    return <div className="trend-chart-empty">No trend data available for this period.</div>;
  }

  const color = SERIES_CONFIG[active].color;

  return (
    <div className="trend-chart-wrap">
      <div className="trend-chart-controls">
        {(Object.keys(SERIES_CONFIG) as Series[]).map((s) => (
          <button
            key={s}
            type="button"
            className={`trend-series-btn ${active === s ? "active" : ""}`}
            style={active === s ? { borderColor: SERIES_CONFIG[s].color, color: SERIES_CONFIG[s].color } : {}}
            onClick={() => setActive(s)}
          >
            {SERIES_CONFIG[s].label}
          </button>
        ))}
      </div>

      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className="trend-chart-svg"
        aria-label={`${SERIES_CONFIG[active].label} trend chart`}
      >
        {/* Y grid lines */}
        {yTicks.map((tick) => (
          <g key={tick.y}>
            <line
              x1={PAD.left} y1={tick.y}
              x2={WIDTH - PAD.right} y2={tick.y}
              stroke="#e2e0db" strokeWidth="1"
            />
            <text
              x={PAD.left - 6} y={tick.y + 4}
              textAnchor="end" fontSize="9" fill="#6b7280"
            >
              {tick.label}
            </text>
          </g>
        ))}

        {/* Bars */}
        {bars.map((bar, i) => (
          <rect
            key={i}
            x={bar.x} y={bar.y}
            width={bar.width} height={bar.height}
            fill={color}
            opacity={0.85}
            rx="2"
          />
        ))}

        {/* X-axis labels */}
        {bars.map((bar, i) =>
          i % tickStep === 0 ? (
            <text
              key={i}
              x={bar.x + bar.width / 2}
              y={HEIGHT - PAD.bottom + 14}
              textAnchor="middle"
              fontSize="9"
              fill="#6b7280"
            >
              {formatDate(bar.date)}
            </text>
          ) : null,
        )}

        {/* X baseline */}
        <line
          x1={PAD.left} y1={PAD.top + chartH}
          x2={WIDTH - PAD.right} y2={PAD.top + chartH}
          stroke="#e2e0db" strokeWidth="1"
        />
      </svg>
    </div>
  );
}
