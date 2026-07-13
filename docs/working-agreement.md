# Working Agreement

## Workflow

- Start work from a GitHub issue.
- Create a short-lived branch from an updated `main`.
- Keep pull requests focused enough to review in one sitting.
- Prefer several meaningful commits over one large final commit.
- Merge only after the other person has reviewed the change.

## Branch and commit naming

```text
feature/de-001-customer-ingestion
fix/de-004-duplicate-facts
docs/de-002-document-grain
```

```text
DE-001 add customer CSV reader
DE-001 validate required customer fields
DE-001 add ingestion tests
```

## Pairing approach

Rotate roles:

- **Driver:** writes code and explains choices.
- **Navigator:** asks questions, checks requirements, and watches for edge cases.

Change roles regularly. The more experienced person should avoid taking over the keyboard whenever progress slows.

## Review style

Review the code, not the person. Distinguish between:

- required changes for correctness;
- suggestions for maintainability;
- questions intended to understand the decision;
- optional ideas for later issues.

## Learning journal

For each pull request, record at least one thing learned and one unresolved question. Unresolved questions can become new issues instead of expanding the current pull request indefinitely.
