"use client";

export function SkeletonMessage({ loadingLabel }: { loadingLabel: string }) {
  return (
    <div className="message-row agent">
      <article className="agent-card loading-card">
        <p className="loading-label">{loadingLabel}</p>
        <div className="skeleton-line w-70" />
        <div className="skeleton-line w-90" />
        <div className="skeleton-line w-60" />
      </article>
    </div>
  );
}
