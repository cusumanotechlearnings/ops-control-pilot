const API_BASE =
  typeof window !== "undefined"
    ? (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
    : "http://localhost:8000";

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------

export type ChatResponse = {
  response: string;
  response_type: "clarification" | "answer";
};

export async function sendChatMessage(
  message: string,
  sessionId: string,
  userId = "user"
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId, user_id: userId }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }

  return res.json();
}

// ---------------------------------------------------------------------------
// Dashboard types
// ---------------------------------------------------------------------------

export type MetricsByBU = {
  business_unit: string;
  total_sends: number;
  deliveries: number;
  total_opens: number;
  total_clicks: number;
  avg_open_rate: number;
  avg_click_rate: number;
  avg_delivery_rate: number;
  avg_ctor: number;
};

export type MetricsOverall = {
  total_sends: number;
  deliveries: number;
  total_opens: number;
  total_clicks: number;
  avg_open_rate: number;
  avg_click_rate: number;
  avg_delivery_rate: number;
  avg_ctor: number;
  avg_sentiment: number | null;
  latest_date?: string;
  earliest_date?: string;
};

export type MetricsSummaryResponse = {
  by_bu: MetricsByBU[];
  overall: MetricsOverall;
};

export type TrendRow = {
  send_date: string;
  business_unit: string;
  total_sends: number;
  deliveries: number;
  total_opens: number;
  total_clicks: number;
  avg_open_rate: number;
  avg_click_rate: number;
  avg_sentiment: number | null;
};

export type TrendResponse = { trend: TrendRow[] };

export type Journey = {
  journey_id: string;
  journey_name: string;
  business_unit: string;
  status: string;
  target_audience: string | null;
  department: string | null;
  last_send_date: string | null;
  first_send_date: string | null;
  schedule_frequency: string | null;
  schedule_start_time: string | null;
  schedule_end_time: string | null;
};

export type JourneysResponse = { journeys: Journey[] };

export type CalendarDay = {
  send_date: string;
  send_count: number;
  total_sends: number;
  deliveries: number;
  avg_open_rate: number | null;
  avg_click_rate: number | null;
  has_planned: boolean;
  has_actual: boolean;
  email_names: string[];
  journey_names: string[];
};

export type CalendarResponse = {
  year: number;
  month: number;
  days: CalendarDay[];
};

export type EmailSearchResult = {
  asset_id: string;
  business_unit: string;
  email_name: string;
  subject_line: string | null;
  pre_header: string | null;
  sender_address: string | null;
  folder: string | null;
  department_code: string | null;
  created_time: string | null;
  last_modified_date: string | null;
  total_sends: number | null;
  deliveries: number | null;
  avg_open_rate: number | null;
  avg_click_rate: number | null;
  last_send_date: string | null;
  send_count: number | null;
};

export type EmailSearchResponse = { results: EmailSearchResult[]; count: number };

// ---------------------------------------------------------------------------
// Dashboard fetch helpers
// ---------------------------------------------------------------------------

async function apiFetch<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchMetricsSummary(days = 365): Promise<MetricsSummaryResponse> {
  return apiFetch(`${API_BASE}/api/metrics/summary?days=${days}`);
}

export async function fetchMetricsTrend(days = 30): Promise<TrendResponse> {
  return apiFetch(`${API_BASE}/api/metrics/trend?days=${days}`);
}

export async function fetchJourneys(status?: string): Promise<JourneysResponse> {
  const qs = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiFetch(`${API_BASE}/api/journeys${qs}`);
}

export async function fetchCalendar(year?: number, month?: number): Promise<CalendarResponse> {
  const qs = new URLSearchParams();
  if (year != null) qs.set("year", String(year));
  if (month != null) qs.set("month", String(month));
  const query = qs.toString() ? `?${qs.toString()}` : "";
  return apiFetch(`${API_BASE}/api/sends/calendar${query}`);
}

export async function fetchUpcomingCalendar(year?: number, month?: number): Promise<CalendarResponse> {
  const qs = new URLSearchParams();
  if (year != null) qs.set("year", String(year));
  if (month != null) qs.set("month", String(month));
  const query = qs.toString() ? `?${qs.toString()}` : "";
  return apiFetch(`${API_BASE}/api/sends/upcoming-calendar${query}`);
}

export async function fetchEmailSearch(params: {
  copy?: string;
  business_unit?: string;
  date_from?: string;
  date_to?: string;
  sender?: string;
}): Promise<EmailSearchResponse> {
  const qs = new URLSearchParams();
  if (params.copy) qs.set("copy", params.copy);
  if (params.business_unit) qs.set("business_unit", params.business_unit);
  if (params.date_from) qs.set("date_from", params.date_from);
  if (params.date_to) qs.set("date_to", params.date_to);
  if (params.sender) qs.set("sender", params.sender);
  return apiFetch(`${API_BASE}/api/search/emails?${qs.toString()}`);
}
