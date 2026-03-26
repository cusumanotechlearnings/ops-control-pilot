type MetricCardProps = {
  title: string;
  value: string | number;
  sub?: string;
  delta?: number | null;
  loading?: boolean;
};

export function MetricCard({ title, value, sub, delta, loading }: MetricCardProps) {
  const deltaPositive = delta != null && delta >= 0;

  return (
    <div className="metric-card">
      <p className="metric-card-title">{title}</p>
      {loading ? (
        <div className="metric-card-skeleton" />
      ) : (
        <>
          <p className="metric-card-value">{value}</p>
          {sub && <p className="metric-card-sub">{sub}</p>}
          {delta != null && (
            <p className={`metric-card-delta ${deltaPositive ? "positive" : "negative"}`}>
              {deltaPositive ? "▲" : "▼"} {Math.abs(delta).toFixed(1)}% vs prior period
            </p>
          )}
        </>
      )}
    </div>
  );
}
