"use client";

import Image from "next/image";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ResponseType } from "../types";

type AgentMessageCardProps = {
  content: string;
  imageBase64: string | null;
  imageMimeType: string | null;
  imageAlt: string | null;
  agentChain: string[] | null;
  responseType: ResponseType;
};

export function AgentMessageCard({
  content,
  imageBase64,
  imageMimeType,
  imageAlt,
  agentChain,
  responseType,
}: AgentMessageCardProps) {
  const imageSrc =
    imageBase64 && imageMimeType ? `data:${imageMimeType};base64,${imageBase64}` : null;

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
        {imageSrc ? (
          <div className="agent-inline-image-wrap">
            <Image
              src={imageSrc}
              alt={imageAlt ?? "Generated image"}
              className="agent-inline-image"
              width={1200}
              height={630}
              unoptimized
              loading="lazy"
            />
          </div>
        ) : null}
      </article>
    </div>
  );
}
