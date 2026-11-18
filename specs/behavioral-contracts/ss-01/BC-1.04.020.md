---
document_type: behavioral-contract
level: L3
version: "1.3.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T12:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md]
input-hash: "73d2913"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:get_sample (SL:315-359)"
subsystem: "SS-01"
capability: "CAP-010"
legacy_id: "BC-SL-091"
parity_class: byte-exact
confidence: M
lifecycle_status: active
introduced: v0.1.0
modified: ["1.3 2026-11-18: pass-4 residual sweep — D4-EX-3 table-test name canonicalized to TestD4EX3_* (ADV-P4-D22)", "1.3.1 2026-11-18: pass-6 metadata alignment (ADV-P6-C2-15) — D22 sweep entry redated to the pass-4 burst date (2026-11-18) and timestamp raised above the last modified entry; no behavioral change", "1.3.2 2026-11-18: pass-11 OD-194 sibling sweep (note added after the exact row bytes — the label bytes in the table are the default spellings of the statusline.labels.* keys named in the forming contracts BC-1.04.004/006/007/008)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.04.020: get_sample pinned sequence and cache key order

## Description

An 11-step multi-refresh sequence pins `get_sample`'s returned tuple, the rendered row 2 and
the **exact session-cache bytes** after every step, including key order inherited from the
file read earlier (`entry = dict(c)`) followed by `fetch_ts, up, ts, sample, hist`. The Go
writer must mutate the loaded ordered `Value` and serialize it with `json.dump` defaults
(`", "` / `": "`, float repr, `NaN`/`Infinity` tokens, no trailing newline). Notation: `\e`
is byte 0x1B; `·` in row text is the separator `\e[2m · \e[0m`.

## Preconditions

1. TTL 4 (default), frozen clock stepped per row, fetch outcome injected by the fake
   metrics store; row 2 rendered plain (no width trim); sparkline on, trace `rate`.
2. Seed file `statusline-<sid>.json` = `{"hist": [[900.0, 50.0], [990.0, 60.0], [998.5, 70.0]], "sess_state": {"x": 1}}`.
3. S1 = `{"vllm:num_requests_running": 1.0, "vllm:kv_cache_usage_perc": 0.5, "dgx_sl:gen_rate1m": 80.0}`;
   S2 = `{"vllm:num_requests_running": 0.0, "dgx_tokens:gen_rate5m": 12.5, "dgx_ttft:p95_30m": 2.0, "dgx_preempt:rate5m": 0.01}`.

## Postconditions

Let SMP1 = `"sample": {"vllm:num_requests_running": 1.0, "vllm:kv_cache_usage_perc": 0.5, "dgx_sl:gen_rate1m": 80.0}`
and H0 = `"hist": [{"t": 990.0, "v": 60.0}, {"t": 998.5, "v": 70.0}]`.

| # | t | Fetch | Returned / row 2 | Cache after (exact bytes) |
|---|---|---|---|---|
| 0 | 1000 | yes, S1 | `(S1, 0.0, true)`; `◉ · r1·q0 · KV▰▰▱▱ 50% · ▣80t/s ▇█` (80 not plotted: newest point 1.5 s old) | `{H0, "fetch_ts": 1000.0, "up": true, "ts": 1000.0, SMP1}` |
| 1 | 1002 | no (`1000 > 998`) | `(S1, 2.0, true)`, same row | unchanged |
| 2 | 1004 | yes (strict: `1000 > 1000` false), fails | `(S1, 4.0, false)`; yellow dot, grey `▣80t/s`, no sparkline, `(~4s old)` | `{H0, "fetch_ts": 1004.0, "up": false, "ts": 1000.0, SMP1}` |
| 3 | 1006 | no | `(S1, 6.0, false)`, `(~6s old)` | unchanged |
| 4 | 1020 | yes, fails | `(S1, 20.0, false)`, `(~20s old)` | `fetch_ts` 1020.0 |
| 5 | 1300 | yes, fails (age 300, `< 300` false) | `(none, 300.0, false, [])` → `\e[31m◌ DGX ?\e[0m` | `fetch_ts` 1300.0; sample still stored |
| 6 | 1302 | no (cached) | `(S1, 302.0, false)` → stale row `(~302s old)` (KEEP_DEAD not applied) | unchanged |
| 7 | 1305 | yes, fails | `◌ DGX ?` | `fetch_ts` 1305.0 |
| 8 | 1310 | yes, S2 | `◉ · r0·q0 (yellow: preempt) · ▣12t/s · ◔2.0s` (1 point, no sparkline) | `{"hist": [{"t": 1310.0, "f": 2.0, "v": 12.5, "p": 1}], "fetch_ts": 1310.0, "up": true, "ts": 1310.0, "sample": {"vllm:num_requests_running": 0.0, "dgx_tokens:gen_rate5m": 12.5, "dgx_ttft:p95_30m": 2.0, "dgx_preempt:rate5m": 0.01}}` |
| 9 | 1314.5 | yes, S1 | `… ▣80t/s` + `\e[38;2;220;170;60m▂\e[38;2;140;235;255m█\e[0m` | `{"hist": [{"t": 1310.0, "f": 2.0, "v": 12.5, "p": 1}, {"t": 1314.5, "v": 80.0, "k": 0.5}], "fetch_ts": 1314.5, "up": true, "ts": 1314.5, SMP1}` |
| 10 | 1316.5 | no | same as 9 | unchanged |

Exact step-0 row bytes:
`\e[32m◉\e[0m\e[2m · \e[0m\e[32mr1·q0\e[0m\e[2m · \e[0m\e[36mKV▰▰▱▱ 50%\e[0m\e[2m · \e[0m\e[90m▣\e[0m\e[97m80\e[0m\e[90mt/s\e[0m \e[38;2;38;93;104m▇\e[38;2;140;235;255m█\e[0m`.
Exact step-2 row bytes:
`\e[33m◉\e[0m\e[2m · \e[0m\e[32mr1·q0\e[0m\e[2m · \e[0m\e[36mKV▰▰▱▱ 50%\e[0m\e[2m · \e[0m\e[90m▣\e[0m\e[90m80\e[0m\e[90mt/s\e[0m\e[2m · \e[0m\e[2m(~4s old)\e[0m`.

The label bytes in the table and exact rows (`r`/`q` with the `·` between them, `KV`,
`t/s`, the `(~Ns old)` suffix) are the default spellings of the `statusline.labels.*`
keys named in the forming contracts — `labels.rate`/`labels.queue` (defaults `r`/`q`,
BC-1.04.006 PC3), `labels.kv`/`labels.host` (defaults `KV`/`host`, BC-1.04.007 PC5),
`labels.tps` (default `t/s`, BC-1.04.008 PC1/PC2) and `labels.old` (default `old`,
BC-1.04.004 PC2); OD-194.

## Invariants

1. Key order: keys already in the file keep their position; `sess_state` is deleted on
   any fetch; new keys append in the order `fetch_ts, up, ts, sample, hist` (step 0 shows
   `hist` first because the seed had it first).
2. Legacy `[t, v]` list points are normalized only on a successful fetch; the failure
   path writes them back verbatim.
3. Floats serialize as Python `repr` (`1000.0`, `1314.5`); ints stay ints.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Seed `{"hist": [[900.0, 50.0]]}`, first fetch fails at 1000 | file `{"hist": [[900.0, 50.0]], "fetch_ts": 1000.0, "up": false}` |
| EC-002 | No file, first fetch fails at 1000 | `{"fetch_ts": 1000.0, "up": false}`; age `now - 0` |
| EC-003 | Empty file `{}`, fetch S with no plottable series, preempt 0 | `{"fetch_ts": 1000.0, "up": true, "ts": 1000.0, "sample": {…}, "hist": [{"t": 1000.0}]}` |
| EC-004 | Legacy `DGX_SL_TTL=nan` (fetch every refresh) / `inf` (never fetch, age `now - 9999`) | **not reproduced**: approved deviation D4-EX-3 — a non-finite TTL is a config error line with no cache writes (BC-2.02.002); OD-105 exclusion entry `D4-EX-3`, dedicated test `TestD4EX3_Number` |
| EC-005 | Temp file names (`statusline-<sid>.json.<random>`) | excluded from cache comparison: OD-110 `temp-file` entry (BC-6.03.003); not an output difference |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| step 0 above | step-0 row bytes and cache bytes | happy-path |
| step 6 above | `(~302s old)` stale row from the cached path | edge-case |
| step 5 above | `\e[31m◌ DGX ?\e[0m`; sample retained in the file | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-030, VP-019 (swap byte equality) | Go and legacy session-cache bytes are identical after each of the 11 steps | manual (multi-step parity case, Tier A) |
| VP-030, VP-019 (swap byte equality) | Cache-swap: a legacy-written file read by Go (and reverse) yields the same next state | manual (BC-6.02.004) |

## Traceability

| Field | Value |
|-------|-------|
| Source | legacy/dgx_statusline.py:get_sample (SL:315-359); save_cache (SL:198-206); _norm_pt (SL:652-656) |
| Legacy contract | BC-SL-091 (P3 r2 §A2; ruling (b) Go-writer format obligation) |
| L2 Capability | CAP-010 |
| L2 Domain Invariants | DI-012 (TTL nan/inf D4-EX-3 deviation, EC-004) |
| Decisions | P3 r2 ruling (b); OD-105/OD-110 (exclusions named in EC-004/EC-005); OD-114 |
| Architecture Module | `internal/statusline/sample.go`, `internal/pyfmt` (json) |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.04.002 — refines: state machine
- BC-1.04.003 — refines: history rules
- BC-5.02.004 — depends on: ordered `Value`
- BC-1.06.001 — depends on: cache I/O
- BC-6.02.004 — related to: cache-swap tests

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#effect-step-script-design-doc-31-normative` — internal/statusline/sample.go (11-step pinned seq) (cache format obligation) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — row 2 + metrics client (design §4 step S5)

## VP Anchors (Recommended)

- VP-030, VP-019 — pinned sequence parity

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:315-359) |
| **Confidence** | medium — inherited key order requires the ordered `Value` (design §8 row 091); sequence re-executed on CPython 3.11.7 (2026-11-15) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **inferred**: `entry = dict(c)` + `entry.update({...})` ordering (SL:327, 349); `json.dump` defaults (SL:203)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads + writes, network call |
| **Global state access** | reads config |
| **Deterministic** | yes given seams |
| **Thread safety** | not thread-safe |
| **Overall classification** | mixed |

#### Refactoring Notes

Never build the cache from a Go struct with `encoding/json` (reorders keys, reformats
floats). Mutate the loaded `pyfmt.Value` and serialize with `pyfmt.Dumps`.
