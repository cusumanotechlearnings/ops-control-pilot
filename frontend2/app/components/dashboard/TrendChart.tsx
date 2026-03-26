"use client";

import { useMemo, useState } from "react";

type TrendRow = {
  send_date: string;
  business_unit: string;
  total_sends: number;
  deliveries: number;
  total_opens: number;
  total_clicks: number;
  avg_open_rate: number;
  avg_click_rate: number;
  avg_sentiment: number | null;
};

type Metric = "deliveries" | "avg_open_rate" | "avg_click_rate" | "avg_sentiment";

type MetricConfig = {
  label: string;
  isRate: boolean;
  fixedMax?: number;
  fixedMin?: number;
  formatTick?: (v: number) => string;
};

const METRIC_CONFIG: Record<Metric, MetricConfig> = {
  deliveries:     { label: "Deliveries",     isRate: false },
  avg_open_rate:  { label: "Open Rate",      isRate: true,  fixedMax: 0.5 },
  avg_click_rate: { label: "Click Rate",     isRate: true,  fixedMax: 0.05 },
  avg_sentiment:  {
    label: "VOC Sentiment",
    isRate: false,
    fixedMin: -1,
    fixedMax:  1,
    formatTick: (v) => v.toFixed(2),
  },
};

const BU_ORDER = ["UC", "GC", "INTL", "MIL", "OL"];

const BU_LABELS: Record<string, string> = {
  UC:   "Undergraduate",
  GC:   "Graduate",
  INTL: "International",
  MIL:  "Military",
  OL:   "Online",
};

const BU_COLORS: Record<string, string> = {
  UC:   "#2c5f8a",
  GC:   "#3d8b8b",
  INTL: "#2d7d57",
  MIL:  "#c2820a",
  OL:   "#7a3d8b",
};

const FALLBACK_COLORS = ["#2c5f8a", "#3d8b8b", "#2d7d57", "#c2820a", "#7a3d8b", "#8a2c5f"];

type TrendChartProps = {
  data: TrendRow[];
  loading?: boolean;
};

const WIDTH  = 600;
const HEIGHT = 210;
const PAD = { top: 16, right: 16, bottom: 36, left: 52 };

function formatDate(iso: string) {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function formatNum(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)     return `${(n / 1_000).toFixed(0)}k`;
  return String(n);
}

function buColor(bu: string, fallbackIdx: number) {
  return BU_COLORS[bu] ?? FALLBACK_COLORS[fallbackIdx % FALLBACK_COLORS.length];
}

export function TrendChart({ data, loading }: TrendChartProps) {
  const [metric, setMetric] = useState<Metric>("deliveries");

  const cfg    = METRIC_CONFIG[metric];
  const chartW = WIDTH  - PAD.left - PAD.right;
  const chartH = HEIGHT - PAD.top  - PAD.bottom;

  const dates = useMemo(
    () => Array.from(new Set(data.map((d) => d.send_date))).sort(),
    [data],
  );

  const bus = useMemo(() => {
    const all = Array.from(new Set(data.map((d) => d.business_unit)));
    return [
      ...BU_ORDER.filter((b) => all.includes(b)),
      ...all.filter((b) => !BU_ORDER.includes(b)).sort(),
    ];
  }, [data]);

  // lookup[bu][date] = value for current metric
  const lookup = useMemo(() => {
    const map: Record<string, Record<string, number | null>> = {};
    for (const row of data) {
      if (!map[row.business_unit]) map[row.business_unit] = {};
      const raw = row[metric as keyof TrendRow];
      map[row.business_unit][row.send_date] =
        raw != null ? Number(raw) : null;
    }
    return map;
  }, [data, metric]);

  // Max stacked total (deliveries only)
  const maxStackTotal = useMemo(() => {
    let max = 1;
    for (const date of dates) {
      const total = bus.reduce((sum, bu) => sum + ((lookup[bu]?.[date] as number) ?? 0), 0);
      if (total > max) max = total;
    }
    return max;
  }, [dates, bus, lookup]);

  // Max individual BU value fallback for line charts without fixedMax
  const maxVal = useMemo(() => {
    let max = 1;
    for (const buMap of Object.values(lookup)) {
      for (const v of Object.values(buMap)) {
        if (v != null && v > max) max = v;
      }
    }
    return max;
  }, [lookup]);

  const axisMin: number = cfg.fixedMin ?? 0;
  const axisMax: number =
    metric === "deliveries" ? maxStackTotal : (cfg.fixedMax ?? maxVal);
  const axisRange = axisMax - axisMin;

  const isSentiment = metric === "avg_sentiment";

  const tickStep = Math.ceil(dates.length / 12);

  function toX(i: number) {
    return PAD.left + (i / Math.max(dates.length - 1, 1)) * chartW;
  }

  // Convert a data value → SVG y coordinate
  function toY(val: number) {
    return PAD.top + chartH - ((val - axisMin) / axisRange) * chartH;
  }

  // ── Stacked bars (deliveries only) ────────────────────────────────────────
  const stackedBars = useMemo(() => {
    if (metric !== "deliveries") return [];
    const gap  = chartW / Math.max(dates.length, 1);
    const barW = Math.max(2, gap * 0.72);
    return dates.map((date, i) => {
      const x = PAD.left + i * gap + (gap - barW) / 2;
      let cumH = 0;
      const segments = bus.map((bu, bi) => {
        const val  = (lookup[bu]?.[date] as number) ?? 0;
        const segH = (val / axisMax) * chartH;
        const y    = PAD.top + chartH - cumH - segH;
        cumH += segH;
        return { bu, color: buColor(bu, bi), x, y, width: barW, height: segH };
      });
      return { date, i, segments };
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [metric, dates, bus, lookup, axisMax, chartW, chartH]);

  // ── Lines (rate metrics, per-BU) ─────────────────────────────────────────
  const lines = useMemo(() => {
    if (metric === "deliveries" || metric === "avg_sentiment") return [];
    return bus.map((bu, bi) => {
      const color = buColor(bu, bi);

      const segments: string[] = [];
      let current: string[] = [];

      dates.forEach((date, i) => {
        const raw = lookup[bu]?.[date];
        if (raw == null) {
          if (current.length > 1) segments.push(current.join(" "));
          current = [];
          return;
        }
        const val = Math.max(axisMin, Math.min(axisMax, raw));
        const x   = PAD.left + (i / Math.max(dates.length - 1, 1)) * chartW;
        const y   = toY(val);
        current.push(`${x},${y}`);
      });
      if (current.length > 1) segments.push(current.join(" "));

      return { bu, color, label: BU_LABELS[bu] ?? bu, segments };
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [metric, bus, dates, lookup, axisMin, axisMax, chartW, chartH]);

  // ── Single aggregated line (sentiment only) ───────────────────────────────
  const sentimentSegments = useMemo(() => {
    if (metric !== "avg_sentiment") return [];
    const segments: string[] = [];
    let current: string[] = [];

    dates.forEach((date, i) => {
      // Average across all BUs that have a non-null value for this date
      const vals = bus
        .map((bu) => lookup[bu]?.[date])
        .filter((v): v is number => v != null);

      if (vals.length === 0) {
        if (current.length > 1) segments.push(current.join(" "));
        current = [];
        return;
      }
      const avg = vals.reduce((s, v) => s + v, 0) / vals.length;
      const val = Math.max(axisMin, Math.min(axisMax, avg));
      const x   = PAD.left + (i / Math.max(dates.length - 1, 1)) * chartW;
      const y   = toY(val);
      current.push(`${x},${y}`);
    });
    if (current.length > 1) segments.push(current.join(" "));
    return segments;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [metric, bus, dates, lookup, axisMin, axisMax, chartW, chartH]);

  // ── Y-axis ticks ──────────────────────────────────────────────────────────
  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((t) => {
    const val = axisMin + t * axisRange;
    let label: string;
    if (cfg.formatTick) {
      label = cfg.formatTick(val);
    } else if (cfg.isRate) {
      label = `${(val * 100).toFixed(1)}%`;
    } else {
      label = formatNum(Math.round(val));
    }
    return { y: PAD.top + chartH - t * chartH, val, label };
  });

  // Zero reference line for sentiment (y=0 maps to middle when range is -1…1)
  const zeroY = isSentiment ? toY(0) : null;

  const legendItems = bus.map((bu, bi) => ({
    bu,
    color: buColor(bu, bi),
    label: BU_LABELS[bu] ?? bu,
  }));

  if (loading) {
    return <div className="trend-chart-loading">Loading trend data…</div>;
  }
  if (!data.length) {
    return <div className="trend-chart-empty">No trend data available for this period.</div>;
  }

  return (
    <div className="trend-chart-wrap">
      {/* Metric selector */}
      <div className="trend-chart-controls">
        {(Object.keys(METRIC_CONFIG) as Metric[]).map((m) => (
          <button
            key={m}
            type="button"
            className={`trend-series-btn ${metric === m ? "active" : ""}`}
            onClick={() => setMetric(m)}
          >
            {METRIC_CONFIG[m].label}
          </button>
        ))}
      </div>

      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className="trend-chart-svg"
        aria-label={`${cfg.label} trend by audience`}
      >
        {/* Y grid lines + labels */}
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

        {/* Zero reference line for sentiment */}
        {isSentiment && zeroY != null && (
          <line
            x1={PAD.left} y1={zeroY}
            x2={WIDTH - PAD.right} y2={zeroY}
            stroke="#9ca3af" strokeWidth="1" strokeDasharray="4 3"
          />
        )}

        {/* Stacked bars — deliveries */}
        {stackedBars.map(({ date, segments }) =>
          segments.map((seg) =>
            seg.height > 0 ? (
              <rect
                key={`${date}-${seg.bu}`}
                x={seg.x} y={seg.y}
                width={seg.width} height={seg.height}
                fill={seg.color}
                opacity={0.88}
              />
            ) : null,
          ),
        )}

        {/* Lines — rate metrics (per-BU) */}
        {lines.map((line) =>
          line.segments.map((pts, si) => (
            <polyline
              key={`${line.bu}-${si}`}
              points={pts}
              fill="none"
              stroke={line.color}
              strokeWidth="1.5"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          )),
        )}

        {/* Single aggregated line — sentiment */}
        {sentimentSegments.map((pts, si) => (
          <polyline
            key={`sentiment-${si}`}
            points={pts}
            fill="none"
            stroke="#3d8b8b"
            strokeWidth="2"
            strokeLinejoin="round"
            strokeLinecap="round"
          />
        ))}

        {/* X-axis date labels */}
        {dates.map((date, i) =>
          i % tickStep === 0 ? (
            <text
              key={date}
              x={metric === "deliveries"
                ? PAD.left + (i + 0.5) * (chartW / Math.max(dates.length, 1))
                : toX(i)}
              y={HEIGHT - PAD.bottom + 14}
              textAnchor="middle"
              fontSize="9"
              fill="#6b7280"
            >
              {formatDate(date)}
            </text>
          ) : null,
        )}

        {/* X baseline */}
        <line
          x1={PAD.left}          y1={PAD.top + chartH}
          x2={WIDTH - PAD.right} y2={PAD.top + chartH}
          stroke="#e2e0db" strokeWidth="1"
        />
      </svg>

      {/* Legend — hidden for sentiment (single aggregated line) */}
      {!isSentiment && (
        <div className="trend-chart-legend">
          {legendItems.map((item) => (
            <span key={item.bu} className="trend-legend-item">
              {metric === "deliveries" ? (
                <span
                  className="trend-legend-square"
                  style={{ background: item.color }}
                />
              ) : (
                <span
                  className="trend-legend-swatch"
                  style={{ background: item.color }}
                />
              )}
              {item.label}
            </span>
          ))}
        </div>
      )}

      {/* Sentiment hint */}
      {isSentiment && (
        <p className="trend-sentiment-hint">
          Scores are averaged from VOC responses (−1 negative · 0 neutral · +1 positive)
        </p>
      )}
    </div>
  );
}
