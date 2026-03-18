# Technical Decisions

## Agent framework: Agno (not LangChain/LangGraph)
Rationale: LangGraph requires understanding graph theory and state
machines, which adds unnecessary complexity for a beginner-built POC.
Agno's mental model (agent + tools + instructions) maps directly to
the architecture we designed. Migration path to LangGraph exists if
complexity grows.

## NL-to-SQL: Hybrid approach
Rationale: Pure dynamic SQL generation risks hallucinated column names
and silent wrong answers. Pure pre-defined queries are too rigid.
Hybrid: schema context embedded in agent system prompt (so Claude knows
exact column names) + validated SQL execution with error handling.

## Database: Neon (Postgres) read-only
Rationale: Free tier sufficient for POC. Postgres dialect familiar.
Read-only constraint eliminates entire class of data integrity bugs.

## Frontend: Next.js on Vercel boilerplate
Rationale: Fastest path to a deployed, shareable URL. Vercel's
deployment is one-click from GitHub.

## Model: Claude claude-opus-4-5
Rationale: Best performance on multi-step reasoning and SQL generation
among available models. Consistent with the rest of the stack.

