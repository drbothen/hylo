---
document_type: remediation-plan
phase: 1d
pass: 4
date: 2026-11-17
source: adversarial-reviews/pass-4.md, adversarial-reviews/ADV-P4-INDEX.md
---

# Pass-4 remediation plan (canonical rulings and minted IDs)

Every fix agent in the pass-4 burst reads this file first. Values here are binding; do not re-derive or re-mint them.

## Owner rulings (2026-11-17; owner chose the recommended option each time)

| ID | Ruling | Source finding |
|---|---|---|
| OD-169 | OD-166's cost-history divergence gets its own closed-set exclusion id `OD-166`. The closed set becomes 11 ids: D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161, OD-166. Scope: cost-history bytes written after a refresh whose `usd` or `api_ms` could not convert to float; nothing else. It needs its own table test and a VP-012 closure row. Remove every "rides D4-EX-2" and "named deviation under OD-156" wording for this case. | A16, A2-04, C2-03 |
| OD-170 | hylo carries its own Unicode 14.0 tables (decimal digit Nd, printable, whitespace, and any other class pyfmt consults), generated from CPython 3.11.7 `unicodedata` by a committed generator script run under `go generate`. pyfmt never consults Go's `unicode` package for these classes. A version constant (`14.0.0`) and a test pin the tables to the oracle; CI fails if the generated file is stale. P6 may move to current Unicode. | D14 |
| OD-171 | hylo resolves its local zone through `internal/platform`, honouring `TZ` on every OS (load the named zone; fall back to the OS zone when `TZ` is unset or unparseable). The parity harness pins `TZ=UTC` for both binaries; the Windows leg runs the naive local-time cases with no skip (remove VP-026's `posix-only` tag). Table test: TZ unset / `UTC` / IANA name / unparseable. Documented limitation: POSIX-style TZ strings (e.g. `EST5EDT`) may differ from MSVC on Windows; parity cases use `TZ=UTC` only. | A2-06, D21 |
| OD-172 | `cp-x03` extends to `--subagent` row writes: a stdout write failure while printing rows stops writing and exits 0 (no degraded line attempt). No new id. | C13 |
| OD-173 | The lane-pill words become config keys `statusline.pill.label_local` (default `DGX`), `statusline.pill.label_cloud` (default `ANTH`), `statusline.pill.label_unknown` (default `?`). Drop the D7 citation. Range: non-empty, no control bytes, display width 1..16 (judgment call: keeps the pill short). | B16 |
| OD-174 | Rename `cost.basis_min_shown_usd` to `statusline.cost.display_floor_usd`; delete the disclaimers. | B21 |
| OD-175 | `statusline.queue.yellow` is ratified as a P1 Bool key, default `true` = legacy rule (yellow when queue > 0 or preempt > 0); `false` = never yellow. Replace the phantom "2026-11-18 owner ruling" citation with OD-175. | D26 |

Next free OD: OD-176.

## Orchestrator design calls (low-stakes, binding for this burst)

1. **Composite-type env grammar (A04, D19):** a key whose registry type is composite (Float pair, Float triple, Int map, RGB triples + Float, any list of numbers) takes its env value as strict JSON of the declared shape, e.g. `HYLO_STATUSLINE_COST_PERCENTILES='[50,90]'`, map `'{"cc":1,"other":2}'`. Reason strings: `<key>=<value> (expected JSON <shape>)` where `<shape>` is e.g. `array of 2 numbers`, `object {cc,other} of integers`. Range checks apply after the shape check. Add these types to the BC-2.01.004 Type enum.
2. **Glyph registry (A05, B15):** BC-2.01.004 enumerates every `statusline.glyphs.*` and `statusline.subagent.glyphs.*` member with env names. Every glyph member is exactly 1 code point and 1 column (OD-02). The two-character `in` label is NOT a glyph: it becomes the Text key `statusline.labels.input` (default `in`).
3. **Subagent token keys (C05):** add `statusline.subagent.tokens.suffix` (Text, default ` tok`). `k_from`/`m_from` are display thresholds only; the divisors 1e3/1e6 are format constants (named constants with a "why not config" comment: they define the K/M units).
4. **Unknown subagent status (C07):** new key `statusline.subagent.glyphs.unknown` (default `◍`, colour = `statusline.theme.grey`). It does not follow `glyphs.killed`.
5. **History `p` marker (C2-13):** new key `statusline.sparkline.preempt_marker_above` (Int, default 0, range `>= 0`): the `p` marker shows when preempt > value. Independent of `statusline.queue.yellow`.
6. **Heat triple (B01, A12):** `statusline.theme.heat` is default-only (BC-1.02.019 stands); fix the registry. `units.context` is default-only because the M/K divisors are fixed (B10 rationale).
7. **plain_max / red_from (B08):** type Float, "any finite number" (matches BC-1.02.006). `statusline.context.cells` gets range 1..100 like `kv.cells` (B09).
8. **git.ttl_s (A03):** legacy admits negatives (SL:99-100). BC-2.02.002 gets an explicit per-key exception list: `statusline.git.ttl_s` admits any finite value; negative = never fresh. Registry row stays.
9. **Parity case argv (A15, D09, D05):** a case's `argv` is the handler-relative argument list (after the `statusline` verb), default `[]`. In P1 the corpus validator admits only `[]` and `["--subagent"]`; the oracle receives `[python, -s, script]` plus the same list. Other argv shapes are covered by Go table tests (BC-4.01.002), never parity.
10. **Corpus layout (D10) — CORRECTED after the burst:** the first version of this call moved the corpus root to `internal/parity/testdata/cases/`, which contradicts the settled owner decision OD-148 (parity fixtures stay with the subject package; the runner `internal/parity` is generic; AD-13). Binding layout: corpus root `internal/statusline/testdata/parity/cases/`, exclusions file `internal/statusline/testdata/parity/exclusions.json`; the generic runner and the `-update` flag live in `./internal/parity` and read the fixtures from the subject package; `steps` live inside `case.json`.
11. **Harness Bool translation (D11):** settings of Bool type are translated to the legacy env by value: true → `1`, false → `0`.
12. **Captures (D12):** replays from `captures/` use a git-ignored `captures/exclusions.json` validated by the same closed-set rule; CI never runs captures.
13. **D4-EX-3 test names (D22):** canonical set `TestD4EX3_Boolean`, `TestD4EX3_Enum`, `TestD4EX3_URL`, `TestD4EX3_Number`. No Theme member (theme settings are rejected by the corpus validator).
14. **Timing p95 (D23):** per case, never pooled, 20 timed runs after 1 warm-up; the gate applies to every case's p95.
15. **Captured stdin (D25):** a capture stores stdin byte-exact in a sibling file `stdin.bin`, never as a JSON member of session.json.
16. **Empty `HYLO_PATHS_CACHE_DIR` (D20):** `config path` reports the same `empty path` error the status line does; it does not fall back to the platform default.
17. **New crash id (C2-12):** `CP-N03` = metrics-borne degrade: a numeric `__name__` key sorts ahead of every `vllm:` key and `k.startswith` raises AttributeError (SL:717).
18. **New VP (B03):** `VP-041` = S1.02 for-all property legs split from VP-028 (as VP-040 was split from VP-027 in pass 3). VP-028 keeps the bounded golden tables. VP count becomes 41.
19. **Float division by zero (D15):** CPython raises ZeroDivisionError for any division by a zero float or int divisor; `TrueDiv` returns an error in every such case and the calling site degrades exactly as legacy does.

## Rules for every agent in this burst

- Read the verbatim finding in `adversarial-reviews/pass-4.md` before fixing it. If a finding is wrong, do not fix it; report it as rejected with evidence.
- **Sibling sweep (lesson L-PG-09..12):** for every fact you change, grep the whole `specs/` tree for the old fact. Fix every hit inside your file set; list hits outside your file set in your report (file:line) so the orchestrator routes them.
- Python claims: verify with `python3 -I` (CPython 3.11.7). Any legacy run uses an isolated temporary HOME and cwd; never touch the real HOME, real caches, the live proxies or the DGX.
- Public-repo hygiene: no real IPs (use 192.0.2.x), no usernames, home paths, hostnames, emails or session links; never quote a hygiene-flagged string.
- English only. Do not commit; the state-manager commits last.
- Bump `version`/`modified` in the frontmatter of every file you change, without duplicating keys.
