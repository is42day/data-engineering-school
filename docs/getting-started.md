# Getting Started

## First session together

Do the setup side by side. Avoid one person sharing a finished environment.

1. Install Git, Python 3.12+, and `uv`.
2. Clone the repository.
3. Run `uv sync --dev`.
4. Run `uv run pytest`.
5. Run `uv run python -m de_school.pipeline` and discuss why it fails intentionally.
6. Create the first GitHub issue from `docs/learning-path.md`.
7. Create a branch named `feature/de-001-customer-ingestion`.

## Useful Git commands

```bash
git status
git switch main
git pull
git switch -c feature/de-001-customer-ingestion
git add <specific-files>
git commit -m "DE-001 add customer source data"
git push --set-upstream origin feature/de-001-customer-ingestion
```

Do not use `git add .` automatically at first. Review what is being staged.

## Definition of done

A learning task is done when:

- acceptance criteria are met;
- tests cover the important behaviour;
- generated data and secrets are not committed;
- documentation is updated when assumptions change;
- another person can run the change;
- the pull request explains decisions and limitations.

## Questions to ask during review

- What is the grain of the output?
- What happens when the input is empty or malformed?
- Can the step be run twice safely?
- Which assumptions are business rules?
- How do we know the result is correct?
- What should be logged when it fails?
