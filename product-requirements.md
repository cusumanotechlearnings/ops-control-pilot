# Product Requirements — Marketing Ops AI

## Problem statement
The marketing team at an education company spends significant time
manually querying SFMC data extensions to answer basic performance
questions. There is no natural language interface to the data, and
cross-agent tasks (get data → analyze → generate ideas → create ticket)
require switching between multiple tools manually.

## Solution
A chat interface backed by a multi-agent AI system that can answer
natural language questions about marketing assets and performance,
generate campaign recommendations, and take actions like creating
project tickets — all from a single conversation.

## Users
Marketing team members (non-technical). Primary persona: a campaign
manager who wants to understand performance without writing SQL.

## Success criteria
- User can ask any question from DEMO_QUESTIONS.md and get a correct,
  well-formatted answer
- Multi-agent questions (data + creative + PM) complete end to end
- Airtable ticket creation works from a chat message
- Response time under 15 seconds for single-agent queries
- Professor can clone repo and run locally with one command

## Out of scope
- User authentication
- Real SFMC connection (using dummy data)
- Mobile optimization
- Multi-user sessions

