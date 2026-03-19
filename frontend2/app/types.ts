export type MessageRole = "user" | "agent";

export type ResponseType = "answer" | "info";

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
  agentChain?: string[] | null;
  responseType?: ResponseType;
};

export type Conversation = {
  id: string;
  title: string;
  updatedAt: string;
  messages: Message[];
};
