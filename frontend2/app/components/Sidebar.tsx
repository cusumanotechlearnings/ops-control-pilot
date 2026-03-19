"use client";

import type { Conversation } from "../types";
import { truncateTitle, formatRelativeTime } from "../lib/utils";

type SidebarProps = {
  conversations: Conversation[];
  activeConversationId: string;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
};

export function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
}: SidebarProps) {
  return (
    <aside className="sidebar-root">
      <div className="sidebar-header">
        <h1 className="sidebar-app-name">Marketing Ops AI</h1>
        <p className="sidebar-powered-by">Powered by Claude</p>
      </div>

      <button type="button" className="sidebar-new-conversation" onClick={onNewConversation}>
        + New conversation
      </button>

      <nav className="sidebar-conversation-list" aria-label="Past conversations">
        {conversations.map((conversation) => {
          const isActive = conversation.id === activeConversationId;
          return (
            <button
              key={conversation.id}
              type="button"
              onClick={() => onSelectConversation(conversation.id)}
              className={`sidebar-conversation-item ${isActive ? "active" : ""}`}
            >
              <p className="sidebar-conversation-title">{truncateTitle(conversation.title, 45)}</p>
              <p className="sidebar-conversation-time">{formatRelativeTime(conversation.updatedAt)}</p>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-footer-divider" />
        <p>Marketing Ops · Internal Tool</p>
      </div>
    </aside>
  );
}
