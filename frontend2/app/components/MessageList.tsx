"use client";

import { useEffect, useRef } from "react";
import type { Message } from "../types";
import { UserMessageBubble } from "./UserMessageBubble";
import { AgentMessageCard } from "./AgentMessageCard";
import { SkeletonMessage } from "./SkeletonMessage";

type MessageListProps = {
  messages: Message[];
  isLoading: boolean;
  loadingLabel: string;
};

export function MessageList({ messages, isLoading, loadingLabel }: MessageListProps) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="message-list">
      {messages.map((message) =>
        message.role === "user" ? (
          <UserMessageBubble key={message.id} content={message.content} />
        ) : (
          <AgentMessageCard
            key={message.id}
            content={message.content}
            imageBase64={message.imageBase64 ?? null}
            imageMimeType={message.imageMimeType ?? null}
            imageAlt={message.imageAlt ?? null}
            agentChain={message.agentChain ?? null}
            responseType={message.responseType ?? "answer"}
          />
        ),
      )}
      {isLoading ? <SkeletonMessage loadingLabel={loadingLabel} /> : null}
      <div ref={endRef} />
    </div>
  );
}
