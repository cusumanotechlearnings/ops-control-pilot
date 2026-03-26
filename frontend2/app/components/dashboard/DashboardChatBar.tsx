"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export function DashboardChatBar() {
  const router = useRouter();
  const [draft, setDraft] = useState("");

  function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const text = draft.trim();
    if (!text) return;
    router.push(`/chat?q=${encodeURIComponent(text)}`);
  }

  return (
    <div className="dashboard-chat-bar">
      <div className="dashboard-chat-inner">
        <p className="dashboard-chat-label">Ask the AI assistant anything</p>
        <form className="dashboard-chat-form" onSubmit={onSubmit}>
          <input
            type="text"
            className="chat-input"
            placeholder="e.g. How did GC perform last month? Which journeys have the highest click rate?"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
          />
          <button type="submit" className="send-button" disabled={!draft.trim()}>
            Ask →
          </button>
        </form>
        <div className="dashboard-chat-chips">
          {[
            "What lift did we get from SMS last month?",
            "Compare Fall 2025 vs Fall 2024 open rates",
            "Show active automations and when they last ran",
          ].map((chip) => (
            <button
              key={chip}
              type="button"
              className="suggestion-chip"
              onClick={() => router.push(`/chat?q=${encodeURIComponent(chip)}`)}
            >
              {chip}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
