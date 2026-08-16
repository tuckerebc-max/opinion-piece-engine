# Workflow Artifacts

Use only the artifacts needed for the requested operating mode. Do not make the user read the engine's entire internal apparatus for a simple revision.

## Assignment brief

```markdown
# Opinion-Piece Brief

- Purpose:
- Target audience:
- Target venue/form:
- Target length:
- Author standing:
- Desired reader movement:
- Why now / news peg (optional unless venue-dependent):
- Controlling question:
- Candidate answer:
- Stakes:
- Evidence supplied:
- Research still needed:
- Voice constraints:
- Release status:
- Non-goals:
- Assumptions:
```

## Thesis slate

| Candidate | Claim type | What is arguable | Stakes | Evidence fit | Distinctiveness | Main vulnerability |
| --- | --- | --- | --- | --- | --- | --- |

Select by argument quality, not rhetorical heat. State the chosen thesis in plain language, then in publication-ready language.

## Argument map

| ID | Claim | Role | Evidence/source | Warrant | Qualification | Strongest objection | Response/adjustment | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 |  | Thesis / reason / implication |  |  |  |  |  | Supported / verify / cut |

Add relationships when useful:

- `supports`: evidence or reason supports a claim;
- `depends_on`: claim fails if another claim fails;
- `qualifies`: limits scope or certainty;
- `rebuts`: answers an objection;
- `illustrates`: makes concrete but does not prove.

## Audience-resistance map

| Audience belief/resistance | Why it is reasonable or durable | What could move it | What will backfire |
| --- | --- | --- | --- |

## Stakes ladder

| Affected people | Concrete consequence | Magnitude/time horizon | Available decision | Value in conflict | Cost of action | Cost of inaction | Reversibility | Support |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Reject stakes language that is more certain, universal, urgent, or catastrophic than its support.

## Component plan

| Component | Include? | Rhetorical job | Material available | Risk |
| --- | --- | --- | --- | --- |

Never answer “include” merely because the component appears in a standard op-ed template.

## Paragraph job map

| Paragraph | Dominant job | Claim or movement | Evidence/example | Transition function | Reader state after | Cut if absent? |
| --- | --- | --- | --- | --- | --- | --- |

Each paragraph should change what the reader knows, believes, feels, doubts, or anticipates.

## First-screen contract

| Opening move | Essential context | Why this author | Particular-to-public bridge | Thesis/promise | Reader's expected question | Risk |
| --- | --- | --- | --- | --- | --- | --- |

## Voice brief

| Dimension | Evidence from samples | Preserve | Avoid | Confidence |
| --- | --- | --- | --- | --- |

Include stance toward reader, cadence, abstraction, humor, emotional temperature, moral vocabulary, certainty, evidence/analogy habits, first-person authority, and language the author would not use.

## Editorial query log

| ID | Location | Query | Why it matters | Owner | Status |
| --- | --- | --- | --- | --- | --- |

Use queries for unresolved author intent, permissions, factual support, venue constraints, or voice choices. Do not silently resolve consequential ambiguities.

## Full-package manifest

```yaml
engine: opinion-piece-engine
engine_version: read-from-VERSION
date: YYYY-MM-DD
mode: discover|develop|draft|revise|pitch|evaluate
venue: unknown
word_target: null
artifacts:
  brief: true
  thesis_slate: true
  argument_map: true
  component_plan: true
  opening_slate: true
  draft: true
  headline_slate: true
  scorecard: true
  verification_ledger: true
unresolved_queries: 0
release_status: blocked|research_needed|editorial_queries_open|venue_check_needed|ready_for_editorial_review
```
