"use client";

import { FormEvent, Suspense, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import type { Conversation, Message } from "../types";
import { truncateTitle } from "../lib/utils";
import { sendChatMessage } from "../lib/api";
import { Sidebar, MessageList } from "../components";

const nowIso = new Date().toISOString();

const starterConversations: Conversation[] = [
  {
    id: "conv-1",
    title: "How did Fall 2025 performance compare to Fall 2024?",
    updatedAt: nowIso,
    messages: [
      {
        id: "m-1",
        role: "user",
        content: "How did Fall 2025 performance compare to Fall 2024?",
      },
      {
        id: "m-2",
        role: "agent",
        responseType: "answer",
        agentChain: ["Data Query", "Analyst"],
        content: [
          "Fall 2025 outperformed Fall 2024 on the core engagement metrics.",
          "",
          "| term | avg_open_rate | avg_click_rate | total_sends |",
          "| --- | ---: | ---: | ---: |",
          "| Fall 2024 | 30.2% | 4.8% | 142,230 |",
          "| Fall 2025 | 33.9% | 5.6% | 151,992 |",
          "",
          "The strongest gain came from military and online segments.",
        ].join("\n"),
      },
    ],
  },
  {
    id: "conv-2",
    title: "What automated journeys are currently active?",
    updatedAt: "2026-03-16T20:00:00.000Z",
    messages: [
      {
        id: "m-3",
        role: "user",
        content: "What automated journeys are currently active?",
      },
    ],
  },
];

const demoSuggestionChips = [
  "What lift did we get from SMS campaigns last month?",
  "What images perform best with Graduate students?",
  "How many FAFSA email recipients ended up enrolling?",
  "Show me all active automations and when they last ran.",
];

const ERROR_MESSAGE =
  "Something went wrong. Please check that the backend is running at the configured API URL and try again.";

function ChatPageInner() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") ?? "";
  const didAutoSubmit = useRef(false);

  const [conversations, setConversations] = useState<Conversation[]>(starterConversations);
  const [activeConversationId, setActiveConversationId] = useState<string>(starterConversations[0].id);
  const [draft, setDraft] = useState(initialQuery);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingLabel, setLoadingLabel] = useState("Thinking");

  const activeConversation = useMemo(
    () => conversations.find((c) => c.id === activeConversationId) ?? conversations[0],
    [conversations, activeConversationId],
  );

  const topBarTitle = useMemo(
    () => truncateTitle(activeConversation?.title ?? "New conversation", 60),
    [activeConversation],
  );

  function onNewConversation() {
    const newId = `conv-${Date.now()}`;
    const newConversation: Conversation = {
      id: newId,
      title: "New conversation",
      updatedAt: new Date().toISOString(),
      messages: [],
    };
    setConversations((prev) => [newConversation, ...prev]);
    setActiveConversationId(newId);
  }

  function onSuggestionClick(text: string) {
    setDraft(text);
  }

  function appendMessage(conversationId: string, message: Message) {
    setConversations((prev) =>
      prev.map((conversation) => {
        if (conversation.id !== conversationId) return conversation;
        const nextMessages = [...conversation.messages, message];
        const firstUserMessage = nextMessages.find((msg) => msg.role === "user");
        return {
          ...conversation,
          messages: nextMessages,
          title: firstUserMessage ? firstUserMessage.content : conversation.title,
          updatedAt: new Date().toISOString(),
        };
      }),
    );
  }

  async function submitMessage(text: string, conversationId: string) {
    if (!text.trim()) return;

    appendMessage(conversationId, {
      id: `m-${Date.now()}-user`,
      role: "user",
      content: text.trim(),
    });

    setLoadingLabel("Thinking");
    setIsLoading(true);

    try {
      const data = await sendChatMessage(text.trim(), conversationId);
      const agentMessage: Message = {
        id: `m-${Date.now()}-agent`,
        role: "agent",
        responseType: data.response_type === "clarification" ? "info" : "answer",
        agentChain: null,
        content: data.response,
      };
      appendMessage(conversationId, agentMessage);
    } catch {
      appendMessage(conversationId, {
        id: `m-${Date.now()}-agent`,
        role: "agent",
        responseType: "info",
        content: ERROR_MESSAGE,
      });
    } finally {
      setIsLoading(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!draft.trim() || !activeConversation) return;
    const text = draft.trim();
    setDraft("");
    await submitMessage(text, activeConversation.id);
  }

  // Auto-submit if navigated here with ?q= from the dashboard
  useEffect(() => {
    if (initialQuery && !didAutoSubmit.current) {
      didAutoSubmit.current = true;

      // Create a fresh conversation for the inbound query
      const newId = `conv-${Date.now()}`;
      const newConversation: Conversation = {
        id: newId,
        title: "New conversation",
        updatedAt: new Date().toISOString(),
        messages: [],
      };
      setConversations((prev) => [newConversation, ...prev]);
      setActiveConversationId(newId);
      setDraft("");
      submitMessage(initialQuery, newId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const hasNoMessages = (activeConversation?.messages.length ?? 0) === 0;

  return (
    <div className="app-shell">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={setActiveConversationId}
        onNewConversation={onNewConversation}
        extraTopLink={
          <Link href="/" className="sidebar-dashboard-link">
            ← Dashboard
          </Link>
        }
      />

      <main className="main-area">
        <header className="topbar">
          <h2>{topBarTitle}</h2>
        </header>

        <section className="chat-scroll-area">
          <div className="chat-max-width">
            {hasNoMessages ? (
              <div className="chip-wrap">
                {demoSuggestionChips.map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    className="suggestion-chip"
                    onClick={() => onSuggestionClick(chip)}
                  >
                    {chip}
                  </button>
                ))}
              </div>
            ) : null}
            <MessageList
              messages={activeConversation?.messages ?? []}
              isLoading={isLoading}
              loadingLabel={loadingLabel}
            />
          </div>
        </section>

        <footer className="input-bar">
          <form className="input-form" onSubmit={onSubmit}>
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask about campaign performance, assets, or next steps..."
              className="chat-input"
              disabled={isLoading}
            />
            <button type="submit" className="send-button" disabled={isLoading || !draft.trim()}>
              Send
            </button>
          </form>
        </footer>
      </main>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="app-shell" />}>
      <ChatPageInner />
    </Suspense>
  );
}
