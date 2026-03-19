"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ResponseType } from "../types";

type AgentMessageCardProps = {
  content: string;
  agentChain: string[] | null;
  responseType: ResponseType;
};

export function AgentMessageCard({ content, agentChain, responseType }: AgentMessageCardProps) {
  return (
    <div className="message-row agent">
      <article className="agent-card">
        {agentChain && responseType === "answer" ? (
          <div className="agent-chain" aria-label="Agent chain">
            {agentChain.map((agent, idx) => (
              <div className="agent-chain-link" key={`${agent}-${idx}`}>
                <span className="agent-pill">{agent}</span>
                {idx < agentChain.length - 1 ? <span className="agent-arrow">→</span> : null}
              </div>
            ))}
          </div>
        ) : null}

        <div className="markdown-render">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        </div>
      </article>
    </div>
  );
}
