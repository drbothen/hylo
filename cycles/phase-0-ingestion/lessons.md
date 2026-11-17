# Cycle lessons — phase-0-ingestion (active cycle)

Process and hygiene lessons recorded during the cycle. Each entry carries a tag;
[process-gap] entries are also listed in STATE.md's Drift Items table with their
remediation target.

## L-PG-01 [process-gap] — Verify the merge commit GitHub creates

- **Lesson:** The PR process must verify the author/committer of the commit
  GitHub creates at merge. PR #1's squash commit carried the owner's personal
  email as author even though every authored commit in the branch used the
  GitHub no-reply identity; the rewrite had to be approved and run post-merge
  (570a0fc -> fd031da, force-push, OD-151).
- **Remedy:** Merge checklist gains a post-merge step: inspect `git log
  --format='%an <%ae> | %cn <%ce>' -1 <merge-sha>` on main before any follow-up
  work.

## L-PG-02 [process-gap] — CI guard for committer identity on main

- **Lesson:** CI must check that every author and committer on main is the
  GitHub no-reply address. Detection should be automatic, not a human
  post-merge catch.
- **Remedy:** Add a CI job (or extend the lint job) that walks main's tip
  commits and fails on any author/committer email other than the no-reply
  address.

## L-PG-03 [process-gap] — Describe scanner false positives, never quote them

- **Lesson:** Documents that explain a scanner false positive must describe,
  never quote, the flagged text. Quoting the flagged text re-triggers the
  scanner on the explanation itself (the hit is synthetic, but the noise and
  the review burden are real).
- **Remedy:** False-positive write-ups paraphrase the pattern (shape, length,
  where it came from) and point at the flagged artifact instead of embedding
  the matching text.
