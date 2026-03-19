# Marketing Ops AI — Project Spec

## What this is
An internal chat application that lets marketing team members query
SFMC marketing asset data and trigger actions using plain English.
Built as a POC for an AI Engineering course.

## The "money" feature
Natural language querying of a Neon Postgres database that mirrors
SFMC data extensions. Users can ask questions like:
- "What emails were sent to campus students last month?"
- "What automated journeys are currently running?"
- "What lift did we get from SMS in the last 30 days?"
- "How did SMS lift compare between Freshman and Senior students?"
- "How do I improve email performance for graduate students?"
  (this triggers: data agent + creative agent + project manager agent)

## Agents
1. Orchestrator — reads every message, decides which agents to call
2. Data Query Agent — translates NL to SQL, queries Neon, returns results
3. Campaign Analyst Agent — interprets query results, calculates lift/trends
4. Creative Agent — generates campaign ideas based on performance data
5. Audience Segmentation Agent — profiles and compares student segments
6. Brand Standards Agent — checks ideas against brand guidelines
7. Image Analysis Agent — predicts image performance based on history
8. Ops/PM Agent — creates Airtable project tickets and tasks

## Tech stack
- Framework: Agno (agent framework)
- Database: Neon (Postgres) — read-only SFMC dummy data
- Backend: Python + FastAPI
- Frontend: Next.js (Vercel boilerplate)
- IDE: Cursor
- Project management: Airtable

## Business Units in the data
UC (University Campus), GC (Graduate Campus), OL (Online),
MIL (Military), INTL (International)

## Key tables in Neon
- dod_metrics — daily email performance (primary fact table)
- email_assets — email template definitions
- journeys — journey/automation flow definitions
- journey_activities — individual send steps within journeys
- automations — scheduled automations feeding journeys
- subscribers — student contact records
- opportunities — downstream funnel data (enrollment, registration)
- landing_page_assets, content_block_assets, sms_assets, image_assets

## Response formats expected
- Plain text answers
- Data tables
- Charts and visualizations
- Actionable next steps / recommendations


# Feature Specification: Conversational Email Insights Chat

**Feature Branch**: `001-email-insights-chat`  
**Created**: 2026-03-17  
**Status**: Draft  
**Input**: User description: "Build a conversational chat application that allows marketing team members and the CMO at an education company to ask natural language questions about their email marketing assets and performance data. All users have the same level of access. No login or authentication is required in this initial phase."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask and explore email performance (Priority: P1)

Marketing team members and the CMO can ask natural language questions about email performance (e.g., lift from SMS,
image performance, segment performance by term) and receive clear answers with tables, narrative analysis, and
suggested next steps — without needing technical or SQL knowledge.

**Why this priority**: This is the core value of the application; if users cannot reliably ask and understand performance
questions, the product does not deliver value.

**Independent Test**: A non-technical marketing user can start a new session, ask any of the representative questions
listed in the spec, and receive a correct, comprehensible response that includes data and explanation without needing
additional setup.

**Acceptance Scenarios**:

1. **Given** a marketing user in the chat interface, **When** they ask "What emails were sent to Military students last
   month", **Then** the system returns a table listing relevant emails filtered to the last calendar month and Military
   segment, with key performance metrics and a short narrative summary.
2. **Given** a marketing user in the chat interface, **When** they ask "What lift did we get from SMS campaigns",
   **Then** the system returns a comparison of journeys with versus without SMS activities, including clearly labeled
   lift metrics and a concise explanation of how the comparison was computed.

---

### User Story 2 - Clarification-first conversational experience (Priority: P2)

The system behaves like a knowledgeable marketing analyst: it asks focused clarifying questions when a request is
ambiguous, builds shared understanding over multiple turns, and avoids guessing or taking silent shortcuts.

**Why this priority**: Clarification-first behavior is essential for trust and accuracy; it differentiates the product
from generic dashboards and prevents misleading answers when intent is unclear.

**Independent Test**: Testers can craft ambiguous or underspecified questions and observe that the system responds with
one clear follow-up question at a time instead of executing potentially-wrong queries or guessing silently.

**Acceptance Scenarios**:

1. **Given** a user asks "How did our campaigns do", **When** the scope (timeframe, segment, channel) is ambiguous,
   **Then** the system responds with a single, focused clarifying question (e.g., "Do you mean all students or a
   specific segment?") instead of returning a broad, noisy report.

---

### User Story 3 - Turn insights into Airtable projects (Priority: P3)

When insights suggest clear follow-up work (e.g., test new campaigns, optimize segments, try new images), the system can
help users turn those insights into structured Airtable project tickets — only after explicit confirmation.

**Why this priority**: This closes the loop from insight to action, aligning with the Marketing Operations AI
constitution's project management agent behavior without requiring users to leave the chat.

**Independent Test**: A tester can run a query that reveals an opportunity, accept a suggestion to create a project, and
see a correctly populated Airtable ticket created only after confirming a preview, with no ticket created when the
confirmation is missing or ambiguous.

**Acceptance Scenarios**:

1. **Given** a user asks "How do I improve performance for graduate students" and the system identifies specific
   underperforming segments, **When** the system suggests creating a project ticket and shows a full preview of the
   ticket fields, **Then** no Airtable ticket is created until the user explicitly confirms in the current thread.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- User asks for segments or terms that do not exist in the underlying data (e.g., misspelled segment names or invalid
  academic terms).
- User issues compound or multi-part questions that would require multiple separate queries or visualizations; the
  system should either decompose them explicitly or ask clarifying questions.
- Database is temporarily unavailable or a query fails; the system must surface a clear error message instead of a
  broken or empty response.
- Context window is near capacity; the orchestrator must summarize and start a new thread while preserving current
  focus and recent filters.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST provide a conversational chat interface where marketing users and the CMO can submit natural
  language questions about email marketing performance and assets.
- **FR-002**: System MUST translate natural language performance and asset questions into read-only SQL `SELECT`
  queries against the Neon Postgres database, never using `INSERT`, `UPDATE`, `DELETE`, `DROP`, or other write
  operations.
- **FR-003**: System MUST correctly map semantic phrases (e.g., "Military students", "graduate campaigns", "last
  semester", "first gen") to the appropriate fields and filters in tables such as `dod_metrics`, `subscribers`,
  `academic_terms`, and `image_assets`.
- **FR-004**: System MUST support the example questions listed in this spec, returning correct data and analysis for
  each:
  - "What emails were sent to Military students last month"
  - "What lift did we get from SMS campaigns"
  - "How did images of people perform compared to images of buildings"
  - "How did undergraduate campaigns perform this past semester amongst first gen students"
  - "How many students who received the FAFSA email ended up enrolling"
  - "How do I improve performance for graduate students"
- **FR-005**: System MUST return responses that may include: data tables, plain text analysis, visualizations, and
  actionable next steps, choosing appropriate formats based on the question type and results size.
- **FR-006**: System MUST implement a clarification-first behavior: when a user's request is ambiguous, it asks one
  focused clarifying question at a time before calling specialist agents, and never guesses silently.
- **FR-007**: System MUST preserve context (user intent, segments, time ranges, prior answers) within a session so that
  follow-up questions can build on previous queries.
- **FR-008**: System MUST manage context window limits by summarizing key facts and starting a new thread with the
  summary injected as initial context when necessary, while notifying the user that a new session has begun.
- **FR-009**: System MUST support a project management flow where, when insights are actionable, it can propose creating
  an Airtable project ticket, show a full preview, and only create the ticket after explicit confirmation from the user
  in the current thread.
- **FR-010**: System MUST treat all users in this initial phase as having the same access level, with no login or
  authentication required.
- **FR-011**: System MUST never ask users to re-enter information already provided in the current session.
- **FR-012**: System MUST attribute responses to the appropriate agent role (e.g., Data, Visualization, Project
  Management, Orchestrator) in the UI, while maintaining a single consistent product voice.

### Key Entities *(include if feature involves data)*

- **dod_metrics**: Fact table representing email performance by email and send date; includes metrics such as
  `open_rate`, `click_rate`, `delivery_rate`, `click_to_open_rate`, `bounce_rate`, `total_sends`, `unique_opens`,
  `unique_clicks`, and segmentation fields like `target_segment`, `department_code`, and `business_unit`.
- **image_assets**: Metadata for image assets used in campaigns; includes flags such as `has_people`, `subject_matter`,
  and average engagement metrics (e.g., `avg_click_rate`, `avg_open_rate`) used for creative performance comparisons.
- **subscribers**: Represents individual students or subscribers with attributes like `student_type`, `student_level`,
  `student_stage`, and `business_unit`, enabling segmentation and funnel analysis.
- **academic_terms**: Reference data for academic terms (e.g., `term_code`, `term_start_date`, `term_end_date`) used to
  translate natural language timeframes like "last semester" or "this past semester" into concrete date ranges.
- **opportunities**: Funnel table with downstream enrollment-related fields (e.g., `stage_name`, `enrolled_term`,
  `registered_next_term`, `withdrew`) used to connect campaign exposure to enrollment outcomes.
- **journeys and journey_activities**: Represent multi-step marketing journeys and their activities (e.g., EMAIL, SMS,
  WAIT), allowing the system to compare journeys with and without SMS activities when computing lift.
- **project_tickets (Airtable)**: Conceptual entity representing Airtable records created by the project management
  agent, including fields such as `title`, `project_description`, `relevant_assets`, `notes`, `assignee`, `due_date`,
  and `priority_level`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 80% of test users (marketing team members and CMO) can successfully obtain a correct answer to a
  representative performance question (from the example list) within two conversational turns or fewer.
- **SC-002**: For the curated set of example questions, system answers match expected benchmark results (computed via
  offline SQL) with 100% accuracy in filters and aggregations.
- **SC-003**: At least 70% of qualifying sessions (where a clear optimization opportunity exists) result in the system
  proactively suggesting an actionable next step, such as experimentation ideas or Airtable project creation.
- **SC-004**: In usability testing, at least 85% of users rate the system's explanations and recommendations as "clear"
  or "very clear" on a standardized survey.
