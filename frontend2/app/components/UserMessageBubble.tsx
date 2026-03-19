"use client";

export function UserMessageBubble({ content }: { content: string }) {
  return (
    <div className="message-row user">
      <div className="user-bubble">{content}</div>
    </div>
  );
}
