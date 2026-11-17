---
document_type: prd
level: L3
version: "0.2.1"
status: draft
producer: product-owner
timestamp: 2026-11-17T16:30:00Z
phase: 1a
stage: "3 of 3 (integration)"
inputs:
  - product-brief.md
  - domain-spec/L2-INDEX.md
  - domain-spec/capabilities.md
  - domain-spec/invariants.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md
  - owner-decisions-log-2026-11-14.md
  - docs/PLAN.md
input-hash: "d23a0b0"
traces_to: domain-spec/L2-INDEX.md
supplements:
  - prd-supplements/interface-definitions.md
  - prd-supplements/error-taxonomy.md
  - prd-supplements/test-vectors.md
  - prd-supplements/nfr-catalog.md
  - prd-supplements/module-criticality.md
  - prd-supplements/assumptions-register.md
  - prd-supplements/risk-register.md
---

# Product Requirements Document: hylo P1 — Status Line

> **BC Index Model.** This PRD is an index document. Each Behavioral Contract lives in
> its own file under `behavioral-contracts/ss-NN/` (one shard per subsystem). Section 2
> provides one-line summaries linking to the individual BC files. Full contract detail
> is never inlined here.
>
> **Integration stage (3 of 3).** Stage 1 produced the subsystem breakdown and the
> authoritative allocation (`behavioral-contracts/BC-ALLOCATION.md`); stage 2 wrote all
> 138 BC files (verified: 138/138 match the register; frontmatter carries legacy_id,
> parity_class, confidence); stage 3 built `behavioral-contracts/BC-INDEX.md`,
> reconciled cross-group differences, and fills the sections below. The BC files and
> `BC-INDEX.md` are the contract detail; this document indexes them. Revised 2026-11-15
> by the owner rulings OD-132..OD-145 on §10 (seven contracts added; 145 total).
>
> **Scope ruling (OD-115).** The brief and L2 spec are product-level; this PRD specifies
> **P1 (`hylo statusline`) only**. Later phases enter via Feature Mode.
> **Subsystem breakdown** approved by the owner 2026-11-15; to be recorded as OD-131
> (pending recording in the owner decision log).

## 1. Product Overview

> Sections 1.1-1.5 are human-audience context; agents consume the structured tables in
> Sections 2-7. The Subsystems table (1.6) is machine-consumed for shard layout.

### 1.1 Problem Statement

A Claude Code subscriber with local inference hardware must either repoint the client at
a base-URL gateway (losing Remote Control since Claude Code 2.1.196) or run a hand-built
Python/mitmproxy stack. The prototype's status line is the daily cockpit — lane, session,
context, limits, cost and backend telemetry — and it is the lowest-risk, highest-value
first slice of the port: a pure function of stdin + transcript + metrics + caches (DI-007).

### 1.2 Solution Vision (P1)

`hylo statusline`: a Go port of `legacy/dgx_statusline.py` that renders byte-identical
output against the CPython 3.11.x oracle over the synthetic fixture corpus and the
owner's recorded real inputs, on all three OSes (D4 parity is the definition of done).
Rendering never fails: faults produce the degraded ladder — one-line output, exit 0
(DI-008). Approved deviations ride only the named exclusion list (D4-EX-1/2/3 + OD-110
entries; DI-012). Configuration in P1 is typed `HYLO_*` env over built-in defaults
(file layer arrives P4, OD-107); invalid config renders the D4-EX-3 one-line error and
exits 0.

### 1.3 Key Differentiators (P1-visible)

| ID | Differentiator | Description |
|----|---------------|-------------|
| KD-001 | Backend telemetry strip | Health/queue/KV/throughput/TTFT/power/idle from the metrics store with a freshness ladder — unique among surveyed peers (CAP-010) |
| KD-002 | Owned-hardware `⛏` cost with percentile colors | Per-lane p75/p95-from-history coloring of `$` and `$/h` (CAP-011, CAP-009) |
| KD-003 | Composition and window-age widgets | `▤❙◈` composition bars and `⌂` process window age (CAP-009) |

### 1.4 Target Users

| Persona | Description | Volume | Pain Level |
|---------|-------------|--------|------------|
| PRIMARY | The owner: Claude Code subscriber with a dedicated vLLM-class server on the LAN | 1 | Daily-production cockpit; parity and p95 <= 25 ms render |
| SECONDARY (P6) | Other Claude Code users with local inference (llama.cpp, Ollama, LM Studio, SGLang) | community | Wants hybrid routing without losing Remote Control |

### 1.5 Out of Scope (P1)

> Machine-consumed: no story AC may implement these in the P1 cycle.

- `--subagent` / custom agent-panel rows (OD-14; legacy BC-SL-097 not ported)
- Exporter (P2), proxy & routing (P3), ledger (P3, D7), launcher/Stop hook/doctor/CA (P4), web/terminal UIs (P4/P6), multi-backend fleet (P6)
- Config-file layer and its YAML dependency (P4; P1 is `HYLO_*` env + built-in defaults, OD-107)
- GPU-serving side (vLLM/LMCache launchers, dashboards) — private home-lab repo
- Reading the Claude.ai OAuth token for usage widgets (market-intel R7)
- No backend/GPU behavior changes of any kind — P1 renders from the metrics store exactly as legacy does

### 1.6 Subsystems

Owner-approved breakdown (2026-11-15, to be recorded as OD-131). BC numbering:
`BC-S.SS.NNN` = subsystem S, subsection SS, sequential within subsection. Shards:
`behavioral-contracts/ss-NN/` keyed by subsystem.

| Subsystem | Name | Priority | Governing L2 (CAP / DI) | BCs this cycle |
|-----------|------|----------|------------------------|----------------|
| S1 | Status line | CRITICAL | CAP-009, CAP-010, CAP-011; DI-007, DI-008 | 93 |
| S2 | Configuration | HIGH | CAP-015; DI-010, DI-008 | 13 |
| S3 | Platform | MEDIUM | CAP-009 (render path support); DI-008 | 3 |
| S4 | CLI | MEDIUM | CAP-009, CAP-015; DI-008 | 3 |
| S5 | Python-compatible formatting (`internal/pyfmt`) | CRITICAL | Enables CAP-009 byte parity (OD-103) | 19 |
| S6 | Parity harness | HIGH | CAP-009 (parity verification); DI-012 machinery; D4 exit criterion | 14 |
| S7 | Exporter | — | CAP-008 | **Reserved — no BCs this cycle (P2)** |
| S8 | Proxy & routing | — | CAP-001..005 | **Reserved — no BCs this cycle (P3)** |
| S9 | Ledger | — | CAP-006, CAP-007; DI-005, DI-006 | **Reserved — no BCs this cycle (P3, D7)** |
| S10 | Launcher / hook / doctor / CA | — | CAP-012, CAP-014, CAP-017 | **Reserved — no BCs this cycle (P4)** |
| S11 | UIs (web + TUI) | — | CAP-016; DI-016 | **Reserved — no BCs this cycle (P4/P6)** |
| S12 | Multi-backend | — | CAP-018 | **Reserved — no BCs this cycle (P6)** |

**Total new BCs: 145** (101 mapped from legacy BC-SL-001..103 + 44 new contracts; see
`behavioral-contracts/BC-ALLOCATION.md` for the authoritative mapping). Priority labels
amended by OD-135: S1 and S5 are module-critical (coverage >= 95%, per
`prd-supplements/module-criticality.md`); the 2026-11-15 owner rulings OD-132..OD-145
added seven contracts (BC-2.02.006; the six pyfmt helper BCs, OD-140/OD-141).

## 2. Behavioral Contracts Index

> Each BC lives at the linked path under `behavioral-contracts/` (created in stage 2).
> "Legacy" is the source contract BC-SL-nnn from
> `../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md` (§7.3);
> "new" = no legacy counterpart. Parity class and translation confidence per BC are in
> `behavioral-contracts/BC-ALLOCATION.md`.

### 2.1 S1 — Status line (CAP-009/010/11)

#### S1.01 Input/output contract (writer group A)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-1.01.001](behavioral-contracts/ss-01/BC-1.01.001.md) | Guard prints the 29-byte degraded line and exits 0 | BC-SL-001 | P0 |
| [BC-1.01.002](behavioral-contracts/ss-01/BC-1.01.002.md) | Non-JSON or non-object stdin decodes to an empty object | BC-SL-002 | P0 |
| [BC-1.01.003](behavioral-contracts/ss-01/BC-1.01.003.md) | Rows join with LF; row 2 shown only when width permits | BC-SL-003 | P0 |
| [BC-1.01.004](behavioral-contracts/ss-01/BC-1.01.004.md) | Visible width counts code points after stripping SGR | BC-SL-004 | P0 |
| [BC-1.01.005](behavioral-contracts/ss-01/BC-1.01.005.md) | COLUMNS parses with the Python int grammar, else 0 | BC-SL-005 | P0 |
| [BC-1.01.006](behavioral-contracts/ss-01/BC-1.01.006.md) | trim_to_fit double-resets; single reset on the recycle row | BC-SL-054 | P0 |
| [BC-1.01.007](behavioral-contracts/ss-01/BC-1.01.007.md) | Negative COLUMNS disables trim and hides row 2 | BC-SL-055 | P0 |
| [BC-1.01.008](behavioral-contracts/ss-01/BC-1.01.008.md) | Strict UTF-8 stdio; invalid stdin UTF-8 renders from {} | BC-SL-076 | P0 |
| [BC-1.01.009](behavioral-contracts/ss-01/BC-1.01.009.md) | Side effects run in legacy order; a degrade keeps earlier writes | BC-SL-077 | P0 |
| [BC-1.01.010](behavioral-contracts/ss-01/BC-1.01.010.md) | Trim breakpoint matrix across widths | BC-SL-090 | P0 |

#### S1.02 Row-1 widgets (writer groups B1 = .001-.015, B2 = .016-.030)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-1.02.001](behavioral-contracts/ss-01/BC-1.02.001.md) | Lane pill derives from model-prefix startswith match | BC-SL-006 | P0 |
| [BC-1.02.002](behavioral-contracts/ss-01/BC-1.02.002.md) | Model label falls back display_name → id → "?" | BC-SL-007 | P0 |
| [BC-1.02.003](behavioral-contracts/ss-01/BC-1.02.003.md) | Project label is basename(normpath(cwd)) | BC-SL-008 | P0 |
| [BC-1.02.004](behavioral-contracts/ss-01/BC-1.02.004.md) | Branch walk reads .git dir or file and HEAD | BC-SL-009 | P0 |
| [BC-1.02.005](behavioral-contracts/ss-01/BC-1.02.005.md) | Branch segment cached with a 5 s TTL | BC-SL-010 | P0 |
| [BC-1.02.006](behavioral-contracts/ss-01/BC-1.02.006.md) | Context thermometer and its denominator | BC-SL-011 | P0 |
| [BC-1.02.007](behavioral-contracts/ss-01/BC-1.02.007.md) | Composition percentage rounds half-even | BC-SL-012 | P0 |
| [BC-1.02.008](behavioral-contracts/ss-01/BC-1.02.008.md) | Cache-hit segment | BC-SL-013 | P0 |
| [BC-1.02.009](behavioral-contracts/ss-01/BC-1.02.009.md) | Limits segment hidden on reroute-all prefixes | BC-SL-014 | P0 |
| [BC-1.02.010](behavioral-contracts/ss-01/BC-1.02.010.md) | Expired rate-limit window is unreported | BC-SL-015 | P0 |
| [BC-1.02.011](behavioral-contracts/ss-01/BC-1.02.011.md) | Pace and absolute colour bands | BC-SL-016 | P0 |
| [BC-1.02.012](behavioral-contracts/ss-01/BC-1.02.012.md) | Countdown format and the 1.15 gate | BC-SL-017 | P0 |
| [BC-1.02.013](behavioral-contracts/ss-01/BC-1.02.013.md) | Rate-limit smoothing over 1800 s | BC-SL-018 | P0 |
| [BC-1.02.014](behavioral-contracts/ss-01/BC-1.02.014.md) | Lines segment formats via _fmt_lines | BC-SL-019 | P0 |
| [BC-1.02.015](behavioral-contracts/ss-01/BC-1.02.015.md) | Timer segment formats via _hm | BC-SL-020 | P0 |
| [BC-1.02.016](behavioral-contracts/ss-01/BC-1.02.016.md) | API-time suffix | BC-SL-021 | P0 |
| [BC-1.02.017](behavioral-contracts/ss-01/BC-1.02.017.md) | Window-age suffix (⌂) with its visibility gate | BC-SL-022 | P0 |
| [BC-1.02.018](behavioral-contracts/ss-01/BC-1.02.018.md) | Token segment formats via _fmt_tok_c | BC-SL-024 | P0 |
| [BC-1.02.019](behavioral-contracts/ss-01/BC-1.02.019.md) | heat() HSV cell colours | BC-SL-056 | P0 |
| [BC-1.02.020](behavioral-contracts/ss-01/BC-1.02.020.md) | Thermometer quirks (/0K, /1000K, NaN crash) | BC-SL-057 | P0 |
| [BC-1.02.021](behavioral-contracts/ss-01/BC-1.02.021.md) | Model label str() of a non-str value | BC-SL-058 | P0 |
| [BC-1.02.022](behavioral-contracts/ss-01/BC-1.02.022.md) | POSIX normpath keeps // | BC-SL-059 | P0 |
| [BC-1.02.023](behavioral-contracts/ss-01/BC-1.02.023.md) | Cache-hit NaN/inf rendering | BC-SL-060 | P0 |
| [BC-1.02.024](behavioral-contracts/ss-01/BC-1.02.024.md) | Pace band boundary at rem = 0.9 × length | BC-SL-061 | P0 |
| [BC-1.02.025](behavioral-contracts/ss-01/BC-1.02.025.md) | _fmt_tok_c performs no unit promotion | BC-SL-062 | P0 |
| [BC-1.02.026](behavioral-contracts/ss-01/BC-1.02.026.md) | _fmt_lines OverflowError on inf degrades (CP-S11) | BC-SL-063 | P0 |
| [BC-1.02.027](behavioral-contracts/ss-01/BC-1.02.027.md) | _hm ValueError on inf degrades (CP-S12/S13) | BC-SL-064 | P0 |
| [BC-1.02.028](behavioral-contracts/ss-01/BC-1.02.028.md) | Window-age duration format | BC-SL-081 | P0 |
| [BC-1.02.029](behavioral-contracts/ss-01/BC-1.02.029.md) | Pick eq threshold 0.005 | BC-SL-083 | P0 |
| [BC-1.02.030](behavioral-contracts/ss-01/BC-1.02.030.md) | effective_rl sequence with sticky CP-S09 | BC-SL-093 | P0 |

#### S1.03 Transcript parsing (writer group C)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-1.03.001](behavioral-contracts/ss-01/BC-1.03.001.md) | No transcript path yields no transcript state | BC-SL-030 | P0 |
| [BC-1.03.002](behavioral-contracts/ss-01/BC-1.03.002.md) | Mix cache name and mixv6 reset rules | BC-SL-031 | P0 |
| [BC-1.03.003](behavioral-contracts/ss-01/BC-1.03.003.md) | 512 KB read step with long-line completion | BC-SL-032 | P0 |
| [BC-1.03.004](behavioral-contracts/ss-01/BC-1.03.004.md) | bytes.splitlines + per-line json.loads | BC-SL-033 | P0 |
| [BC-1.03.005](behavioral-contracts/ss-01/BC-1.03.005.md) | Usage dedup per message id (memory 256) | BC-SL-034 | P0 |
| [BC-1.03.006](behavioral-contracts/ss-01/BC-1.03.006.md) | Usage accumulation across int/float/big-int | BC-SL-035 | P0 |
| [BC-1.03.007](behavioral-contracts/ss-01/BC-1.03.007.md) | Rebuild rule at 20,000 excess input tokens | BC-SL-036 | P0 |
| [BC-1.03.008](behavioral-contracts/ss-01/BC-1.03.008.md) | compact_boundary resets composition and pp | BC-SL-037 | P0 |
| [BC-1.03.009](behavioral-contracts/ss-01/BC-1.03.009.md) | Composition per block from json.dumps lengths | BC-SL-038 | P0 |
| [BC-1.03.010](behavioral-contracts/ss-01/BC-1.03.010.md) | Last-turn rate machine | BC-SL-039 | P0 |
| [BC-1.03.011](behavioral-contracts/ss-01/BC-1.03.011.md) | First line of a message supplies its usage | BC-SL-065 | P0 |
| [BC-1.03.012](behavioral-contracts/ss-01/BC-1.03.012.md) | Short + long line completes over two refreshes | BC-SL-066 | P0 |
| [BC-1.03.013](behavioral-contracts/ss-01/BC-1.03.013.md) | Mix cache sid sanitized per code point | BC-SL-070 | P0 |
| [BC-1.03.014](behavioral-contracts/ss-01/BC-1.03.014.md) | text/thinking block value types | BC-SL-072 | P0 |
| [BC-1.03.015](behavioral-contracts/ss-01/BC-1.03.015.md) | transcript_path type semantics (int = fd) | BC-SL-088 | P0 |
| [BC-1.03.016](behavioral-contracts/ss-01/BC-1.03.016.md) | Turn-machine exhaustive table (20 rows) | BC-SL-094 | P0 |
| [BC-1.03.017](behavioral-contracts/ss-01/BC-1.03.017.md) | Turn identity ignores seen_ids | BC-SL-095 | P0 |
| [BC-1.03.018](behavioral-contracts/ss-01/BC-1.03.018.md) | D4-EX-2 wrong-shape line W-predicates (skip, no partial mutation) | BC-SL-098 | P0 |
| [BC-1.03.019](behavioral-contracts/ss-01/BC-1.03.019.md) | D4-EX-2 table tests (21 rows, exact expected caches) | BC-SL-099 | P0 |
| [BC-1.03.020](behavioral-contracts/ss-01/BC-1.03.020.md) | Legacy-poisoned cur.out reader rule (OD-32) | BC-SL-100 | P0 |
| [BC-1.03.021](behavioral-contracts/ss-01/BC-1.03.021.md) | cur with t0 null and non-numeric out kept verbatim | BC-SL-103 | P0 |

#### S1.04 Row-2 telemetry, metrics client, freshness (writer group D)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-1.04.001](behavioral-contracts/ss-01/BC-1.04.001.md) | fetch_sample: query, 1.5 s timeout, first-wins | BC-SL-040 | P0 |
| [BC-1.04.002](behavioral-contracts/ss-01/BC-1.04.002.md) | get_sample TTL / KEEP_DEAD state machine | BC-SL-041 | P0 |
| [BC-1.04.003](behavioral-contracts/ss-01/BC-1.04.003.md) | History point rules (90 s cap, 2 s gap) | BC-SL-042 | P0 |
| [BC-1.04.004](behavioral-contracts/ss-01/BC-1.04.004.md) | Freshness ladder + stale suffix | BC-SL-043 | P0 |
| [BC-1.04.005](behavioral-contracts/ss-01/BC-1.04.005.md) | Health dot | BC-SL-044 | P0 |
| [BC-1.04.006](behavioral-contracts/ss-01/BC-1.04.006.md) | Queue segment | BC-SL-045 | P0 |
| [BC-1.04.007](behavioral-contracts/ss-01/BC-1.04.007.md) | KV segment | BC-SL-046 | P0 |
| [BC-1.04.008](behavioral-contracts/ss-01/BC-1.04.008.md) | Throughput segments | BC-SL-047 | P0 |
| [BC-1.04.009](behavioral-contracts/ss-01/BC-1.04.009.md) | Sparkline glyphs, scale and colors | BC-SL-048 | P0 |
| [BC-1.04.010](behavioral-contracts/ss-01/BC-1.04.010.md) | TTFT segment | BC-SL-049 | P0 |
| [BC-1.04.011](behavioral-contracts/ss-01/BC-1.04.011.md) | Power segment | BC-SL-050 | P0 |
| [BC-1.04.012](behavioral-contracts/ss-01/BC-1.04.012.md) | Idle segment | BC-SL-051 | P0 |
| [BC-1.04.013](behavioral-contracts/ss-01/BC-1.04.013.md) | VM fetch whenever ROWS >= 2 | BC-SL-053 | P0 |
| [BC-1.04.014](behavioral-contracts/ss-01/BC-1.04.014.md) | Sparkline NaN/+Inf crash path (CP-N02) | BC-SL-073 | P0 |
| [BC-1.04.015](behavioral-contracts/ss-01/BC-1.04.015.md) | KV NaN crash path (CP-N01) and cell math | BC-SL-074 | P0 |
| [BC-1.04.016](behavioral-contracts/ss-01/BC-1.04.016.md) | Row-2 NaN/inf rendering; wall-colour mismatch | BC-SL-075 | P0 |
| [BC-1.04.017](behavioral-contracts/ss-01/BC-1.04.017.md) | Idle strict > 300 and age format | BC-SL-084 | P0 |
| [BC-1.04.018](behavioral-contracts/ss-01/BC-1.04.018.md) | Mine (last-turn) segment | BC-SL-085 | P0 |
| [BC-1.04.019](behavioral-contracts/ss-01/BC-1.04.019.md) | TTFT format boundaries | BC-SL-086 | P0 |
| [BC-1.04.020](behavioral-contracts/ss-01/BC-1.04.020.md) | get_sample pinned sequence and cache key order | BC-SL-091 | P0 |
| [BC-1.04.021](behavioral-contracts/ss-01/BC-1.04.021.md) | HIST_MIN_GAP reachability (seeded) | BC-SL-092 | P0 |

#### S1.05 Cost history + dynamic colors (writer group E)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-1.05.001](behavioral-contracts/ss-01/BC-1.05.001.md) | $ colours from lane percentile thresholds | BC-SL-025 | P0 |
| [BC-1.05.002](behavioral-contracts/ss-01/BC-1.05.002.md) | $/h segment with threshold colouring | BC-SL-026 | P0 |
| [BC-1.05.003](behavioral-contracts/ss-01/BC-1.05.003.md) | ⛏ pick inside the $ block (basis threshold) | BC-SL-027 | P0 |
| [BC-1.05.004](behavioral-contracts/ss-01/BC-1.05.004.md) | record_cost throttled write | BC-SL-028 | P0 |
| [BC-1.05.005](behavioral-contracts/ss-01/BC-1.05.005.md) | cost_thresholds p75/p95 percentiles | BC-SL-029 | P0 |
| [BC-1.05.006](behavioral-contracts/ss-01/BC-1.05.006.md) | Numeric sid: throttle and self-exclusion fail (single string-form key) | BC-SL-079 | P0 |
| [BC-1.05.007](behavioral-contracts/ss-01/BC-1.05.007.md) | $ and $/h number formatting | BC-SL-082 | P0 |
| [BC-1.05.008](behavioral-contracts/ss-01/BC-1.05.008.md) | Cost colouring goldens (20 seeded sessions) | BC-SL-101 | P0 |
| [BC-1.05.009](behavioral-contracts/ss-01/BC-1.05.009.md) | record_cost write contract (exact JSON format) | BC-SL-102 | P0 |

#### S1.06 Session caches (writer group E)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-1.06.001](behavioral-contracts/ss-01/BC-1.06.001.md) | Cache load/save: never-raise, raw sid in file names | BC-SL-052 | P0 |
| [BC-1.06.002](behavioral-contracts/ss-01/BC-1.06.002.md) | Sid with / : failed replace persists nothing; temp handling | BC-SL-078 | P0 |

### 2.2 S2 — Configuration (CAP-015)

#### S2.01 Schema + resolution (writer group F)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-2.01.001](behavioral-contracts/ss-02/BC-2.01.001.md) | P1 resolution: HYLO_* env over built-in defaults; no file layer; DGX_* never read | new | P0 |
| [BC-2.01.002](behavioral-contracts/ss-02/BC-2.01.002.md) | backends array: exactly one entry validated until P6; backends[0].metrics_url / backends[0].model_prefixes; default prefixes claude-sonnet | new | P0 |
| [BC-2.01.003](behavioral-contracts/ss-02/BC-2.01.003.md) | statusline.theme.* keys for SGR palette, pill codes and separator, legacy defaults | new | P0 |
| [BC-2.01.004](behavioral-contracts/ss-02/BC-2.01.004.md) | Key registry: every key declares type, range/operator, default and rationale | new | P1 |
| [BC-2.01.005](behavioral-contracts/ss-02/BC-2.01.005.md) | HYLO_* value grammars: typed bool, comma lists, ~ path expansion; COLUMNS excluded as protocol input | new | P1 |

#### S2.02 Validation + config-error line (writer group F)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-2.02.001](behavioral-contracts/ss-02/BC-2.02.001.md) | D4-EX-3 config-error line: exact format, exit 0, stderr detail, no cache writes | BC-SL-087 | P0 |
| [BC-2.02.002](behavioral-contracts/ss-02/BC-2.02.002.md) | Number-range class: non-finite/negative durations are config errors; TTL 0 stays valid | new | P0 |
| [BC-2.02.003](behavioral-contracts/ss-02/BC-2.02.003.md) | Number-grammar class: underscore and Unicode-digit numerals are config errors | new | P0 |
| [BC-2.02.004](behavioral-contracts/ss-02/BC-2.02.004.md) | Enum class: unknown sparkline trace value is a config error | new | P0 |
| [BC-2.02.005](behavioral-contracts/ss-02/BC-2.02.005.md) | URL class: non-http(s) metrics URL is a config error | new | P0 |
| [BC-2.02.006](behavioral-contracts/ss-02/BC-2.02.006.md) | Boolean class: a non-typed-boolean value is a config error (true\|false\|1\|0\|yes\|no) | new | P0 |

#### S2.03 Config subcommands (writer group F)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-2.03.001](behavioral-contracts/ss-02/BC-2.03.001.md) | hylo config validate exits non-zero on the same errors as D4-EX-3 | new | P1 |
| [BC-2.03.002](behavioral-contracts/ss-02/BC-2.03.002.md) | hylo config path prints the config, cache and state paths (OD-132) | new | P2 |

### 2.3 S3 — Platform

#### S3.01 Per-OS paths (writer group G)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-3.01.001](behavioral-contracts/ss-03/BC-3.01.001.md) | Per-OS cache/config/state dirs; hylo cache dir from P1 (XDG/hylo, LOCALAPPDATA) | new | P0 |

#### S3.02 Process start / window age (writer group G)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-3.02.001](behavioral-contracts/ss-03/BC-3.02.001.md) | Window start via native per-OS ancestor probe; whole-second truncation; proc_start key first | BC-SL-023 | P0 |
| [BC-3.02.002](behavioral-contracts/ss-03/BC-3.02.002.md) | ps-parse replacement: named per-OS edge differences (macOS/Linux) | BC-SL-080 | P0 |

### 2.4 S4 — CLI

#### S4.01 Subcommand dispatch (writer group F)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-4.01.001](behavioral-contracts/ss-04/BC-4.01.001.md) | Dispatch statusline / version / config; statusline exits 0 for any argv | new | P0 |
| [BC-4.01.002](behavioral-contracts/ss-04/BC-4.01.002.md) | Unknown flag renders one-line error, exit 0, never blank (incl. leftover --subagent) | new | P0 |
| [BC-4.01.003](behavioral-contracts/ss-04/BC-4.01.003.md) | hylo version prints the version string | new | P2 |

### 2.5 S5 — Python-compatible formatting (`internal/pyfmt`, OD-103)

#### S5.01 Numbers/rounding (writer group G)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-5.01.001](behavioral-contracts/ss-05/BC-5.01.001.md) | Round/RoundN/F: half-even, decimal re-round, 'f' format incl. -0; nan/inf/-inf spellings | new | P0 |
| [BC-5.01.002](behavioral-contracts/ss-05/BC-5.01.002.md) | ParseInt/ParseFloat Python grammar: underscores, Unicode digits, signs, 4,300-digit limit, nan/inf/1e400 | new | P0 |
| [BC-5.01.003](behavioral-contracts/ss-05/BC-5.01.003.md) | CPython float divmod/mod; Int/Ceil typed NaN/Overflow errors; Max/Min NaN argument order | new | P0 |
| [BC-5.01.004](behavioral-contracts/ss-05/BC-5.01.004.md) | pyfmt.D: {:d} decimal formatting with width and zero-pad | new | P0 |
| [BC-5.01.005](behavioral-contracts/ss-05/BC-5.01.005.md) | pyfmt.Repr: CPython float repr (shortest round-trip, .0 suffix, inf/nan spellings) | new | P0 |
| [BC-5.01.006](behavioral-contracts/ss-05/BC-5.01.006.md) | pyfmt.MaxSeq: Python max() over a sequence with first-maximal-wins NaN order | new | P0 |

#### S5.02 JSON byte semantics (writer group G)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-5.02.001](behavioral-contracts/ss-05/BC-5.02.001.md) | json.dumps length rules (escaping, float repr, inner-null 0) | BC-SL-071 | P0 |
| [BC-5.02.002](behavioral-contracts/ss-05/BC-5.02.002.md) | json.dumps length oracle (63 cases) | BC-SL-096 | P0 |
| [BC-5.02.003](behavioral-contracts/ss-05/BC-5.02.003.md) | json.loads(bytes) acceptance set: BOM/UTF-16/32, invalid UTF-8, depth, NaN, duplicates | BC-SL-067 | P0 |
| [BC-5.02.004](behavioral-contracts/ss-05/BC-5.02.004.md) | Ordered object Value: insertion order, last-wins keeps position, Delete; WTF-8 strings | new | P0 |
| [BC-5.02.005](behavioral-contracts/ss-05/BC-5.02.005.md) | pyfmt.Str: Python str() of values (str unchanged, non-str via repr) | new | P0 |
| [BC-5.02.006](behavioral-contracts/ss-05/BC-5.02.006.md) | pyfmt.Dumps: json.dump cache-file bytes (separators, ensure_ascii, float repr, order) | new | P0 |

#### S5.03 Code-point string ops (writer group G)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-5.03.001](behavioral-contracts/ss-05/BC-5.03.001.md) | Len/Truncate/HasSurrogate: code points, surrogate = 1, not terminal cells | new | P0 |
| [BC-5.03.002](behavioral-contracts/ss-05/BC-5.03.002.md) | Strip/RStrip/RSplit1/SplitLinesBytes: Python whitespace; \n \r\n \r only | new | P0 |
| [BC-5.03.003](behavioral-contracts/ss-05/BC-5.03.003.md) | SubNonWord per code point before truncation; EncodeUTF8Replace lone surrogate → ? | new | P0 |
| [BC-5.03.004](behavioral-contracts/ss-05/BC-5.03.004.md) | PosixNormpath/NtNormpath/Basename per-OS selection (ntpath on Windows) | new | P0 |

#### S5.04 Time semantics (writer group G)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-5.04.001](behavioral-contracts/ss-05/BC-5.04.001.md) | FromISOFormat: 3.11 grammar, naive = local, fraction truncation beyond µs | BC-SL-069 | P0 |
| [BC-5.04.002](behavioral-contracts/ss-05/BC-5.04.002.md) | LocalToUnix: CPython _mktime port, gap/overlap semantics, TZ injection, embedded tzdata | new | P0 |
| [BC-5.04.003](behavioral-contracts/ss-05/BC-5.04.003.md) | pyfmt.TimeFloat: Python time.time() value discipline (ns→s float, once per render) | new | P0 |

### 2.6 S6 — Parity harness

#### S6.01 Oracle execution (writer group H)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-6.01.001](behavioral-contracts/ss-06/BC-6.01.001.md) | Oracle runs via explicit absolute CPython 3.11.x path, never PATH; invoked with -s, never -I/-E | new | P0 |
| [BC-6.01.002](behavioral-contracts/ss-06/BC-6.01.002.md) | Child environment constructed from scratch: no *_proxy, fixed HOME/TMPDIR/locale | new | P0 |
| [BC-6.01.003](behavioral-contracts/ss-06/BC-6.01.003.md) | Clock shim freezes time functions from HYLO_TEST_NOW, stepped per refresh; canary fails if shim absent | new | P0 |

#### S6.02 Fixture corpus (writer group H)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-6.02.001](behavioral-contracts/ss-06/BC-6.02.001.md) | Committed corpus synthetic-only; owner real inputs replayed from git-ignored captures/ | new | P0 |
| [BC-6.02.002](behavioral-contracts/ss-06/BC-6.02.002.md) | stdin-sequence replay of captured sessions: ordered snapshots, clock advanced per step | new | P0 |
| [BC-6.02.003](behavioral-contracts/ss-06/BC-6.02.003.md) | Case model: stdin template + translated settings + metrics mode + seeds + steps | new | P0 |
| [BC-6.02.004](behavioral-contracts/ss-06/BC-6.02.004.md) | Cache-swap coverage: Python-writes/Go-reads and reverse, all four caches | new | P1 |

#### S6.03 Comparison + exclusions (writer group H)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-6.03.001](behavioral-contracts/ss-06/BC-6.03.001.md) | Row goldens A/B/C (Tier B, Python-written, OS-specific variants) | BC-SL-089 | P0 |
| [BC-6.03.002](behavioral-contracts/ss-06/BC-6.03.002.md) | Comparison = stdout bytes + exit code per step; named caches byte-for-byte by file name; stderr never compared | new | P0 |
| [BC-6.03.003](behavioral-contracts/ss-06/BC-6.03.003.md) | mkstemp temp names excluded from comparison; Go temp-cleanup difference covered | new | P0 |
| [BC-6.03.004](behavioral-contracts/ss-06/BC-6.03.004.md) | Exclusion-list machinery: per-case entries, expected files, table tests, no globs | new | P0 |

#### S6.04 CI matrix + timing (writer group H)

| BC ID | Title | Legacy | Priority |
|-------|-------|--------|----------|
| [BC-6.04.001](behavioral-contracts/ss-06/BC-6.04.001.md) | CI matrix: ubuntu-24.04 / macos-15 arm64 / windows-2025; Go 1.26.x leg; -race; gitleaks | new | P0 |
| [BC-6.04.002](behavioral-contracts/ss-06/BC-6.04.002.md) | Per-OS timing report; p95 <= 25 ms binds on the owner's Mac target | new | P1 |
| [BC-6.04.003](behavioral-contracts/ss-06/BC-6.04.003.md) | Tier C differential fuzz: nightly Linux, non-gating, random valid inputs to both sides | new | P1 |

### 2.7 Reserved subsystems (no BCs this cycle)

S7 exporter (P2), S8 proxy & routing (P3), S9 ledger (P3, D7), S10 launcher/hook/doctor/CA
(P4), S11 UIs (P4/P6), S12 multi-backend (P6). See Section 1.6.


## 3. Interface Definition

> Supplement: `prd-supplements/interface-definitions.md` (full help text, exit codes,
> stdin JSON contract, `HYLO_*` key schema with types/ranges/defaults/rationales per
> D15 + OD-101/111/113/114/123, flag interactions, output byte contract). Essentials:

### 3.1 CLI

| Verb | Output | Exit | Contract |
|---|---|---|---|
| `hylo statusline` | 1 or 2 rendered lines on stdout (LF-joined); faults degrade to the 29-byte grey line, never blank | always 0 | BC-4.01.001, BC-1.01.001/.003 |
| `hylo version` | `hylo <version>` (build info fallback, then `dev`) | 0 | BC-4.01.003 |
| `hylo config validate` | `hylo: config ok` or plain reason lines | 0 / 1 | BC-2.03.001 |
| `hylo config path` | config, cache and state paths, one per line, fixed labels/order (OD-132) | 0 | BC-2.03.002 |

Usage errors (bad args/flags on non-statusline verbs) print the golden usage text and
exit 2 (`cmd/hylo/testdata/usage.golden`). `hylo statusline` takes no flags: any flag is
an unknown-flag one-line error, exit 0 (OD-112), checked before config resolution.

### 3.2 stdin protocol (statusline)

One JSON object on stdin (Claude Code statusLine payload): text-mode
`json.load` semantics — a BOM or invalid UTF-8 decodes to `{}` and the render continues
(BC-1.01.002, BC-1.01.008); NaN/Infinity tokens accepted; nesting budget is a per-call-site
constant (993 accepted / 994 rejected at stdin, BC-1.01.002). Objects read: `model`,
`workspace`, `transcript_path`, `session_id`, `cost`, `rate_limits`, `version`, and the
newer optional fields (`output_style.name`, `pr.kind`, `workspace.repo.*`,
`prompt_cache.*`, `rate_limits.spend_limit` with and without its dollar fields;
market-intel §6.1) — all tolerated absent or null. Wrong inner types degrade per the
crash-path register (CP-S01..S17), never fail.

### 3.3 Configuration

P1 resolution: built-in defaults, overridden by `HYLO_*` env only (no file layer, OD-107;
`DGX_*` never read). Key = dotted lower-snake (`statusline.rows`, `backends[0].metrics_url`,
`statusline.theme.*`); env name = `HYLO_` + upper snake with separators collapsed
(`backends[0].metrics_url` → `HYLO_BACKENDS_0_METRICS_URL`). Every key declares type,
range, default, rationale and rationale code (D15, OD-57); two documented default
exceptions: `paths.cache_dir` (OD-101) and `backends[0].model_prefixes` = `claude-sonnet`
(OD-111/OD-123). `COLUMNS` is a Claude Code protocol input, not a hylo key (BC-1.01.005,
BC-2.01.005). Full P1 subset with ranges and rationale codes: BC-2.01.004 (registry) and
the supplement.

## 4. Non-Functional Requirements

> Supplement: `prd-supplements/nfr-catalog.md` (targets, validation methods, risk
> sources). Headline targets:

| ID | Requirement | Target | Validation | Contract |
|---|---|---|---|---|
| NFR-001 | Render latency, steady state | p95 <= 25 ms on the owner's Mac over the fixture corpus, excluding the metrics HTTP wait (OD-117). Measured legacy baseline 2026-11-15: median 84.5 ms, p90 101 ms (~25 ms interpreter start removed by the port) | per-OS timing report; gate binds only with `HYLO_TIMING_GATE=1` | BC-6.04.002 |
| NFR-002 | Never-blank, exit-0 rendering | 100% of fault-injection and crash-path triggers (CP-S01..S17, CP-T01..T07, CP-N01/N02) produce >= 1 output byte and exit 0 | fault-injection table tests | BC-1.01.001, BC-1.01.002, register per BC |
| NFR-003 | Byte parity (D4 exit criterion) | 0 unexplained stdout/exit diffs over the corpus; every explained diff rides a named exclusion entry with its own table test | parity harness per step: stdout bytes + exit code + named caches | BC-6.03.002, BC-6.03.004, DI-012 |
| NFR-004 | Cross-platform (D5) | CI green on ubuntu-24.04, macos-15 (arm64), windows-2025 for every change; Go 1.26.x; -race clean | CI matrix | BC-6.04.001 |
| NFR-005 | Memory/CPU envelope | bounded state: 256-entry dedup memory, 32-point histories, 1000-line identity window, 512 KB read steps | table tests | BC-1.03.003/.005, BC-1.04.002 |
| NFR-006 | Repo hygiene (public repo) | synthetic-only committed fixtures; gitleaks + pattern scan clean on CI | CI leg + TestCorpusHygiene | BC-6.02.001, BC-6.04.001 |

## 5. Error Taxonomy

> Supplement: `prd-supplements/error-taxonomy.md` (full catalog with severity, exit code
> and exact message format per entry). Two observable error surfaces exist in P1, both
> one-line grey on stdout, both exit 0 (DI-008); non-zero exits occur only in validate /
> usage / harness contexts.

| Code | Surface | Observable | Exit | Contract |
|---|---|---|---|---|
| E-REN-001 | Panic guard (any crash path) | `\e[90mstatusline degraded\e[0m\n` (29 bytes: `1b 5b 39 30 6d` + `statusline degraded` + `1b 5b 30 6d 0a`) | 0 | BC-1.01.001 |
| E-REN-002 | Typed degrade (OverflowError/ValueError/NaN per CP-*) | same 29-byte line; earlier side-effect writes are kept | 0 | BC-1.02.026/.027, BC-1.02.020, BC-1.04.014/.015, BC-1.03.015 |
| E-CFG-001 | D4-EX-3 config error (six classes, register closed: number-range, number-grammar, enum, URL — OD-114; boolean — OD-140; theme/SGR — OD-134) | `\e[90mhylo: config error: <key>=<value> (<reason>)\e[0m\n`, first error in registry order; full list to stderr; no cache writes | 0 | BC-2.02.001..006, BC-2.01.003/.005 |
| E-CLI-001 | Unknown flag on `statusline` | `\e[90mhylo: unknown flag <flag>\e[0m\n` (first flag, no colon after "flag"); stderr detail per flag; precedes config errors | 0 | BC-4.01.002 |
| E-CLI-002 | Usage error (non-statusline verbs) | golden usage text on stderr | 2 | BC-4.01.001, BC-2.03.001 |
| E-VAL-001 | `config validate` on invalid config | plain reason lines (no SGR) on stdout | 1 | BC-2.03.001 |
| E-NET-001 | Metrics unreachable / 500 / garbage | freshness ladder down to the stale suffix; render never fails | 0 | BC-1.04.001/.004 |
| E-FS-001 | Cache load/save faults | never-raise; render continues from defaults; failed replace persists nothing | 0 | BC-1.06.001/.002 |
| E-HAR-001 | Harness integrity (canary, missing table test, glob entry, id outside closed set) | harness run FAILs with a named reason | non-zero (harness only) | BC-6.01.003, BC-6.03.004 |

Severity model: `broken` = cannot render (E-REN-001/002 — observable is the degraded
line); `degraded` = partial widget output with stated fallback (E-CFG-001, E-CLI-001,
E-NET-001, E-FS-001); `cosmetic` = stderr-only detail (stderr is never compared by the
harness). Non-zero exits: E-CLI-002 and E-VAL-001 by ruler TOM side (OD-102); E-HAR-001
in the harness process only.

## 5b. Test Vectors

> Supplement: `prd-supplements/test-vectors.md` maps each canonical golden table to its
> owning contract. The tables and owners:

| Canonical table | Owner |
|---|---|
| 29-byte degraded line (bytes, exit) | BC-1.01.001 |
| COLUMNS grammar table (unset, 0, 71, 72, -5, -0, 10, unicode, underscore, 4,300-digit) | BC-1.01.005, BC-5.01.002 |
| ROWS x COLUMNS trim-breakpoint matrix | BC-1.01.010, BC-1.01.003 |
| Turn machine (20 rows, incl. the added T13 row) | BC-1.03.016 |
| D4-EX-2 wrong-shape table (21 rows, exact expected caches) | BC-1.03.019 |
| json.dumps length oracle (63 cases; row 53 script-generated, OD-142) | BC-5.02.002, BC-5.02.001 |
| json.loads(bytes) acceptance set (BOM/UTF-16/32, depth, NaN, duplicates) | BC-5.02.003 |
| get_sample 11-step pinned sequence + exact cache JSON | BC-1.04.020 |
| Cost colouring goldens (20 seeded sessions, 12 outputs + 5 scenarios) | BC-1.05.008 |
| heat() HSV cell colours; trim; ladder thresholds | BC-1.02.019, BC-1.01.010, BC-1.04.004 |
| Row goldens A/B/C (Tier B, Python-written, per-OS variants) | BC-6.03.001 |
| CPython-generated pyfmt expectation tables | BC-5.01.001..003, BC-5.03.x, BC-5.04.x |

## 6. Competitive Differentiator Traceability

Maps Section 1.3 differentiators to the BCs that implement them (seeds:
domain-spec/capabilities.md differentiator trace table; market-intel §4; OD-97 honesty
rules — a peer capability is claimed as differentiated only where the survey shows no
lane-split peer).

| Differentiator | Implementing BCs | Claim basis |
|---|---|---|
| KD-001 Backend telemetry strip (health/queue/KV/throughput/TTFT/power/idle + freshness ladder) | BC-1.04.001 (client), BC-1.04.002/.003/.020/.021 (store, history, TTL), BC-1.04.004 (freshness ladder), BC-1.04.005..012, .017, .018, .019 (segments), BC-1.04.013 (ROWS >= 2 fetch), BC-1.02.009 (limits segment) | CAP-010; market-intel §4: no surveyed peer renders local-backend telemetry in the status line |
| KD-002 Owned-hardware `⛏` cost with percentile colors | BC-1.05.003 (⛏ pick inside the $ block), BC-1.05.001/.002 (percentile thresholds), BC-1.05.005 (p75/p95 from history), BC-1.05.004/.006/.009 (record throttle, numeric sid, write format), BC-1.05.007 (number formats), BC-1.05.008 (goldens), BC-1.02.029 (basis threshold) | CAP-011, CAP-009; lane-split cost coloring absent from peers (§4) |
| KD-003 Composition and window-age widgets | composition: BC-1.02.007 (half-even percentage), BC-1.03.008/.009 (state from transcript), BC-1.02.019 (heat cells); window age: BC-1.02.017 (gate), BC-1.02.028 (duration format), BC-3.02.001/.002 (native per-OS probe, D4-EX-1/OD-76) | CAP-009; `▤❙◈` and ancestor-probe age unique among surveyed peers (§4) |

## 7. Requirements Traceability Matrix

Full per-BC detail lives in `BC-INDEX.md` and `BC-ALLOCATION.md` (legacy id, parity
class, confidence, writer). Per-subsection rollup (CAP = governing L2 capability;
priority = the P0/P1/P2 mix in Section 2; test type per the design §8 test column):

| BC range | Source CAP | Module | Priority | Test type |
|---|---|---|---|---|
| BC-1.01.001..010 | CAP-009 | `internal/statusline` (frame, guard, width, trim) | P0 | oracle-pinned table tests |
| BC-1.02.001..030 | CAP-009 | `internal/statusline` (widgets) + `internal/pyfmt` | P0 | oracle-pinned table tests |
| BC-1.03.001..021 | CAP-009 | `internal/statusline` (transcript parser) | P0 | oracle-pinned table tests, D4-EX-2 table |
| BC-1.04.001..021 | CAP-009, CAP-010 | `internal/statusline` (row 2, metrics client) | P0 | table tests + fake-server integration |
| BC-1.05.001..009 | CAP-011, CAP-009 | `internal/statusline` + `internal/cost` (cost history, colors) | P0 | seeded goldens, table tests |
| BC-1.06.001..002 | CAP-009 | `internal/statusline` (cache store) | P0 | table tests, temp-file exclusion test |
| BC-2.01.001..005 | CAP-015 | `internal/config` | P0/P1 | build-time table tests |
| BC-2.02.001..006 | CAP-015 | `internal/config` | P0 | D4-EX-3 class tests |
| BC-2.03.001..002 | CAP-015 | `cmd/hylo` | P1/P2 | CLI integration tests |
| BC-3.01.001 | CAP-009 | `internal/platform` | P0 | per-OS table tests |
| BC-3.02.001..002 | CAP-009 | `internal/platform` | P0 | per-OS probe tests (D4-EX-1/OD-76 tables) |
| BC-4.01.001..003 | CAP-009, CAP-015 | `cmd/hylo` | P0/P2 | CLI integration, usage golden |
| BC-5.01.001..006 | CAP-009 (enabler, OD-103) | `internal/pyfmt` (num) | P0 | CPython oracle tables + fuzz |
| BC-5.02.001..006 | CAP-009 (enabler) | `internal/pyfmt` (json) | P0 | oracle tables (63-case dump oracle) + fuzz |
| BC-5.03.001..004 | CAP-009 (enabler) | `internal/pyfmt` (str) | P0 | proptest + oracle tables |
| BC-5.04.001..003 | CAP-009 (enabler) | `internal/pyfmt` (time) | P0 | oracle tables, TZ-matrix tests |
| BC-6.01.001..003 | DI-012 machinery | `internal/parity` (oracle exec) | P0 | harness integration tests |
| BC-6.02.001..004 | DI-012 machinery | `internal/parity` (corpus) | P0/P1 | harness integration tests |
| BC-6.03.001..004 | DI-012 machinery | `internal/parity` (comparison, exclusions) | P0 | golden compares, machinery tests |
| BC-6.04.001..003 | DI-012 machinery | `internal/parity` (CI, timing, fuzz) | P0/P1 | CI matrix, timing report, nightly fuzz |

## 8. Cross-Cutting Concerns

- **DI-007 — read scope.** The status line reads only stdin, the transcript, the metrics
  store and its own caches — never the ledger (P3). Enforced by the frame BCs (BC-1.01.x)
  and the purity classifications in each BC file.
- **DI-008 — rendering never fails.** Any fault lands on the degraded ladder (E-REN-*) or
  a stated fallback; exit 0 always for `statusline`; config errors and unknown flags are
  themselves one-line outputs (E-CFG-001, E-CLI-001). Includes D4-EX-3 and OD-112.
- **DI-010 — typed, validated config.** Every key is registry-declared with a rationale
  (D15); invalid values render the D4-EX-3 line and continue (BC-2.01.004, BC-2.02.x).
- **DI-012 — closed deviation set.** Behavior may differ from the oracle only via named,
  tested exclusions (D4-EX-1/2/3, OD-30, OD-76, temp-file). The id set is closed
  (BC-6.03.004); a new class needs an owner decision.
- **Cache-format ownership (ruling b).** Go is byte-exact cache writer and reader across
  Python/Go swaps for all four caches (BC-1.02.013, BC-1.03.002, BC-1.05.009,
  BC-1.06.001/.002, BC-6.02.004).
- **Per-call-site resources.** JSON recursion budget (stdin 993/994; transcript 995/1000)
  and whitespace sets (int/float vs str.isspace) are stated per site, never globally
  (BC-1.01.002, BC-5.02.003, BC-5.01.002, BC-5.03.002).
- **Public-repo hygiene (policy 21).** Repo-relative paths only; synthetic fixtures;
  real inputs replayed from git-ignored captures/ (BC-6.02.001); the placeholder IP
  192.0.2.x is the only address literal in fixtures.

## 9. Assumptions

The canonical register is
[prd-supplements/assumptions-register.md](prd-supplements/assumptions-register.md)
(minted 2026-11-17 per OD-152), which carries Status, Validation Method and Impact per
ASM-NNN. Itemized from the Phase 0 semport registers and resolved by the owner rulings
OD-118..OD-130 (owner-validation-list.md); none reopened here. Operating assumptions this
cycle relies on:

- **ASM-001 — Oracle pin.** CPython 3.11.7 with a strict UTF-8 locale is the parity
  oracle (OD-104) — validated.
- **ASM-002 — Client surface stability.** Claude Code 2.1.325 is the tested statusLine
  surface; the stdin field list is unchanged since 2026-11-14 (BC-1.01.002) — validated.
- **ASM-003 — Settings translation.** Legacy `DGX_SL_*`/`LOCAL_MODEL_PREFIXES` translate
  to typed `HYLO_*` per case (OD-05, BC-1.02.005 EC-011) — validated.
- **ASM-004 — Binding latency target.** The p95 <= 25 ms target binds on the owner's Mac
  (darwin/arm64) only; CI legs report without gating (OD-117, BC-6.04.002) — validated.
- **ASM-005 — Pending CI-leg verification.** Windows edge cases (BC-1.06.001 EC-008,
  BC-1.06.002 EC-003/EC-005) and the CPython 3.11 sitecustomize shim are marked
  "not executed", pinned on the windows-2025 CI leg / harness canary — open, disclosed.
- **ASM-006 — Timeout ruling.** OD-56 replaces the per-socket timeout with a total fetch
  deadline (BC-1.04.001); output-identical on the corpus — validated.

The companion R-NNN risk register is minted in `prd-supplements/risk-register.md` (R-001..R-007).

## 10. Open Questions

All fourteen were disposed by the owner on 2026-11-15 (rulings OD-132..OD-145, recorded in
the owner decision log); OQ-3 is deferred by design. Original questions and alternatives
remain in git history and in the BCs' edge-case registers.

| # | OD | Disposition |
|---|---|---|
| OQ-1 | OD-136 | Resolved: CP-X03 — when the degraded-line write itself fails, Go swallows the error and exits 0 (DI-008); named exclusion `cp-x03` in the OD-105/OD-110 closed set with its own table test (BC-1.01.001 EC-005, BC-6.03.004) |
| OQ-2 | OD-137 | Resolved: durations beyond int64 stay byte-exact using `math/big` at the two duration-format sites (BC-1.02.027 EC-005, BC-1.02.028 EC-007; IM-07 note in the BC); no exclusion |
| OQ-3 | OD-139 | **Deferred:** the per-OS probe test measures the symlinked-binary case (native `P_comm`/`/proc` comm vs `ps comm`); it becomes an owner ruling only if the measured names differ (BC-3.02.002 EC-003) |
| OQ-4 | OD-138 | Resolved: NaN `usd` in the cost history pinned byte-for-byte; expected bytes generated from the CPython 3.11 oracle (frozen clock, temp HOME, synthetic history; both file orders pinned in BC-1.05.005 EC-009) |
| OQ-5 | OD-143 | Resolved: T13 confirmed real legacy behavior by the CPython 3.11 oracle run (exact golden reproduction, 2026-11-15); the row stays and BC-1.03.016 remains "20 rows" |
| OQ-6 | OD-134 | Resolved: OD-114's config-error classes extended with the theme class, reason string `not an SGR parameter list` (BC-2.01.003, error-taxonomy.md); class register closed at six |
| OQ-7 | OD-140 | Resolved: dedicated boolean-parsing contract stood up in S2.02 (BC-2.02.006); one behavior — typed booleans `true\|false\|1\|0\|yes\|no` per OD-05, anything else is a config error |
| OQ-8 | OD-132 | Resolved: `hylo config path` prints all three paths — config, cache, state — one per line in that fixed order with those fixed labels (BC-2.03.002; interface-definitions.md) |
| OQ-9 | OD-145 | Resolved: harness flag names, timing method and remaining spec details delegated to the architect in create-architecture (subject to adversarial review); marked "names provisional — architect (OD-145)" in BC-6.x; no behavior change |
| OQ-10 | OD-145 | Resolved: proposed test names and seed paths likewise delegated to the architect (marked provisional in BC-1.06.002, BC-3.02.001/.002, BC-6.03.004, BC-1.05.008); no behavior change |
| OQ-11 | OD-144 | Resolved: relative/empty `XDG_*` values are ignored (XDG spec); on Windows `%LOCALAPPDATA%\hylo\cache` and `%LOCALAPPDATA%\hylo\state` are separate subdirectories (BC-3.01.001; interface-definitions.md) |
| OQ-12 | OD-133 | Resolved: the process name becomes the config key `statusline.window_age.process_name`, default `claude`, type/range and D15 rationale registered (BC-3.02.001/.002; interface-definitions.md) |
| OQ-13 | OD-141 | Resolved: one helper-level contract each for the six pyfmt helpers `D` (BC-5.01.004), `Repr` (BC-5.01.005), `MaxSeq` (BC-5.01.006), `Str` (BC-5.02.005), `Dumps` (BC-5.02.006), `TimeFloat` (BC-5.04.003); S5 is module-critical (OD-135); cycle total 145 BCs |
| OQ-14 | OD-142 | Resolved: the whole json.dumps oracle table for BC-5.02.002 regenerated by script from CPython 3.11 (no hand-recorded literals); the generating script is recorded inline in the BC; row 53 = 38 (generated) |

Carried, closed by spec decision (no owner action needed): RK-5 (HYLO_TEST_NOW stderr
warning outside the harness), RK-6 (`statusline.window_age.ps_timeout_s` — removed by
OD-147 (owner, 2026-11-16); setting it is now an ordinary unknown-key config error),
T9 follow-through (theme key registry rows — delivered in BC-2.01.003), and the recording
of OD-131 (subsystem breakdown approved 2026-11-15).
