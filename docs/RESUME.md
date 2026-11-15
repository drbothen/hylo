# RESUME — hylo state snapshot

Read this first in a new session, then `docs/PLAN.md`. Machine-specific context (where the
live prototype runs, paths, endpoints) is in the git-ignored `CLAUDE.local.md`.

## Where things stand (2026-11-14)

- **P0 done** — this repository was created from the prototype's history: 18 commits carried
  over with `git filter-repo`, scrubbed (private IP → `192.0.2.10`, usernames/paths/labels,
  client project name, region-revealing utility name, private session links removed, author
  email → GitHub no-reply), verified with gitleaks, trufflehog and a pattern scan (all clean),
  plus LICENSE (Apache-2.0), README, `docs/PLAN.md`, and removal of the visible-mode router (D6).
- **The prototype is still the production path** on the owner's machine (`legacy/` is a frozen
  copy of it). Nothing in hylo replaces it until cutover (P5).
- **No Go code yet.** Next phase: **P1 — Go skeleton + `hylo statusline` at parity.**

## How we got here (context worth keeping)

- The prototype was built as `claude-dgx` for one GPU server (an NVIDIA DGX Station running
  vLLM, later with LMCache). Hence the `dgx_*` file names and `DGX_*` env vars in `legacy/`.
- On 2026-11-13/14 every status line widget was reviewed one at a time with the owner; ~30
  defects were fixed in the prototype *before* the freeze (wrong timer math, token totals
  counted 3×, a cache-hit ratio reading 0% under LMCache, cost basis exploding after a quiet
  day, a parser that froze on long transcript lines, …). **`legacy/dgx_statusline.py` is the
  post-review version** — port it, not an earlier one. The rationale for every rule is in
  `docs/STATUSLINE-REVIEW-2026-11-13.md`; the behavior spec is `docs/STATUSLINE-WIDGETS.md`.
- A first `anth_ratelimit` header capture showed Anthropic sends only the 7-day plan window for
  the owner's account, so the 5-hour window is hidden until it appears.
- Claude Code 2.1.323 removed `subagentStatusLine` (agent-panel rows): the `--subagent` mode is
  **not** ported.

## P1 — next steps (in order)

1. **Skeleton.** `go mod init github.com/drbothen/hylo`; `cmd/hylo/main.go` with subcommand
   dispatch (stdlib `flag`): `hylo statusline`, `hylo version`. Layout per `docs/PLAN.md` §6.
2. **CI.** `.github/workflows/ci.yml`: matrix ubuntu / macos / windows — `gofmt -l`, `go vet`,
   `go test ./...`; plus a gitleaks job.
3. **Determinism hooks for the parity harness.** The prototype reads the wall clock
   (countdowns, idle, ages), the network (VictoriaMetrics), the process tree (`⌂`) and a cache
   directory. The harness must pin all four:
   - clock: a test-only env var (e.g. `HYLO_TEST_NOW`) honored by the Go code, and injected into
     the Python run via a `sitecustomize.py` shim that patches `time.time` (the shim lives in the
     harness, so `legacy/` stays unmodified; the shim must freeze `time.strftime`/`localtime`/
     `gmtime` as well as `time.time`, and run the Python side with `-s` so user site-packages
     cannot interfere);
   - metrics: a local fake VictoriaMetrics HTTP server returning canned query results;
   - process tree / window age: an injected start time in tests;
   - cache: a fresh temp directory per case (`HOME`/cache dir override).
4. **Fixtures (synthetic only — public repo).** `testdata/statusline/`: stdin JSON cases and a
   small generator for synthetic transcripts covering the review's edge cases — assistant
   messages split across lines with repeated `usage`, a `compact_boundary`, a line > 512 KB,
   tool results interleaved inside a message, a cache rebuild, empty thinking blocks, images in
   tool results; canned metrics for healthy / vLLM down / LMCache down / stale.
5. **Port, in this order:** formatting helpers → row-1 widgets (lane, model, branch, project,
   thermometer, composition, cache, lines, timer, tokens, cost, limits) → transcript parser
   (incremental, message-id dedup, compaction reset, last-turn rate, rebuild counter) → row-2
   widgets and the metrics client/cache → cost history (dynamic p75/p95 colors) → window age
   (`internal/platform`: macOS / Linux / Windows process ancestry).
6. **Exit criterion (P1):** byte-identical output, Python vs Go, across the whole fixture
   corpus on all three OSes in CI; a table test for every rule in the review doc.

After P1: P2 exporter, P3 proxy (replay; no shadow week), P4 run/hook/doctor/ca, P5 full cutover, P6
generalize, P7 ledger/metrics redesign — see `docs/PLAN.md` §7.

## Open questions for the owner

Phase 0 (analysis of `legacy/` with the private VSDD factory) is complete and the owner
decided every open item on 2026-11-14 (no `DGX_*` aliases; no shadow week, full cutover;
`--subagent` not ported; config under `~/.config/hylo`). Next: Phase 1 specification, then
the P1 steps above. (Release tooling — GitHub Releases first, per D12 — is set up when there
is something to release.)
