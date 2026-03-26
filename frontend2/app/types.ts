export type MessageRole = "user" | "agent";

export type ResponseType = "answer" | "info";

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
  imageBase64?: string | null;
  imageMimeType?: string | null;
  imageAlt?: string | null;
  agentChain?: string[] | null;
  responseType?: ResponseType;
};

export type Conversation = {
  id: string;
  title: string;
  updatedAt: string;
  messages: Message[];
};
