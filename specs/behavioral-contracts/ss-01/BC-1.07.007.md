---
document_type: behavioral-contract
level: L3
version: "1.1.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T06:25:00Z
phase: 1a
inputs: [behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r8.md, semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions.md]
input-hash: "55afa1e"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_fmt_tokens + token/elapsed branches (SL:909-921, 876-885)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-097
parity_class: byte-exact
confidence: H
priority: P0
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.0.1 2026-11-18T03:00:00Z: VP citation reconciliation: no-VP-yet rows replaced with VP-009 (dense grid) + VP-039 (clock ulp)"
  - "1.0.2 2026-11-18T07:00:00Z: adv-p3 remediation: huge-int overflow paths catalogued as CP-A04 (float(n), SL:878) and CP-A05 (now_ms - start, SL:919) (ADV-P3-C04); threshold/format order wording fixed (ADV-P3-C19); tok suffix and thresholds sourced from statusline.subagent.tokens.* config keys (ADV-P3-C05)"
  - "1.0.3 2026-11-18T08:00:00Z: pass-4 remediation: tokens.suffix key minted (Text, default ` tok`, design call 3); k_from/m_from defined as display thresholds only with the 1e3/1e6 divisors ruled format constants, not config (ADV-P4-C05)"
  - "1.0.4 2026-11-18T23:00:00Z: pass-5 remediation (ADV-P5-C07/C03) — clock base is the injected Env.Now() float seconds with the time.time()*1000 float-product rule (call 7); UnixMilli guidance removed; theme keys named for the token/clock colours"
  - "1.0.5 2026-11-18: pass-5 residual sweep (ADV-P5-A2-11/C15 reciprocal) — VP-001 row added to Verification Properties and VP Anchors (the CP-A04/A05 legs ride the never-blank ladder); no behavioral change"
  - "1.0.6 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C12) — frontmatter template conformance: priority P0 added (prd.md S1.07), introduced normalized to the sibling \"0.1\" format"
  - "1.0.7 2026-11-19T18:30:00Z: pass-7 remediation (ADV-P7-C04/C14) — EC-010/EC-011 added and oracle-pinned: tokenCount Infinity/1e400 renders infM tok (Python float-repr spelling, not Go's +Inf); startTime Infinity clamps to 00:00; PC1's misplaced <suffix> clause reattached to the token-bit sentence (ADV-P7-C14)"
  - "1.0.8 2026-11-19T23:59:00Z: pass-8 remediation (ADV-P8-C01) — Infinity-row expected content re-pinned to the pure-ASCII wire form with the glyphs escaped (oracle byte-exact) + CTV byte-notation note added"
  - "1.0.9 2026-11-20T12:00:00Z: pass-8 residual sweep (task 9) — ASSUMP-107-1 capture timing respelled per OD-192: 'before Phase 3' -> 'before Phase 2 writes the S1.07 stories'; body wording only"
  - "1.1.0 2026-11-20T18:00:00Z: pass-9 remediation (ADV-P9-C01/C02) — CTV Expected Output column uniform pure-ASCII wire notation, ESC spelled as the ensure_ascii escape; the Infinity row's raw U+2714/U+00B7 replaced by their escapes (oracle re-run 2026-11-18); frontmatter modified list repaired to block style"
  - "1.1.1 2026-11-23T12:00:00Z: pass-12 remediation (ADV-P12-C02/C06/C08) — Description/PC6/PC7 bound the CP-A04/A05 trigger envelope to 309..4300-digit decimal literals (4,301+ digits raise ValueError at the stdin json.load, absorbed to {} per BC-1.07.003, zero bytes; oracle-measured on CPython 3.11.7, the oracle interpreter); the k_from/m_from rationale restated as the helper's own unit-boundary convention, the approved-mockup docstring cite returned to _fmt_tok_c (SL:864); oracle provenance respelled without an install path"
  - "1.1.2 pass-12 residual sweep (orchestrator pass-12 residual call 4): the VP-039 closure row and the decisions-list entry state VP-039's operative claim (elapsed-clock floats match CPython-derived goldens bit-exactly), retiring the retired ulp-tolerance reading; no behavioral change; 2026-11-23T14:00:00Z"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.07.007: Token segment (_fmt_tokens) and running-only elapsed clock

## Description

Two conditional bits close the row. Tokens: a positive numeric `tokenCount` renders
`<CYAN><_fmt_tokens(tok)> tok<RESET>` with `_fmt_tokens` = `.0f` below 1000, `.1f`k to 999,999, `.2f`M
above (display unit-boundary convention: the thresholds are where the K and M units switch — legacy
records no rationale for this helper at SL:876-885; the approved-mockup docstring belongs to
`_fmt_tok_c`, SL:864, a different helper). The "?" fallback is reached only on TypeError/ValueError
coercions; a huge int (|n| >= 2**1024 - 2**970 — the trigger envelope is bounded to 309..4300-digit
decimal literals, ADV-P12-C02) raises OverflowError at `float(n)`, which the helper
does not catch, degrading via the guard (CP-A04, BC-1.07.008). Clock: only a `running` row with
numeric `startTime > 0` gets `MM:SS` elapsed (`max(now_ms - start, 0)/1000`, minute-second split) — a
settled row's clock must not keep counting (review #21.2), a huge-int `startTime` overflows the same
way at `now_ms - start` (CP-A05), and the PR-15 FMA pitfall binds the float port (explicit `float64`
per product, operation order preserved; FMA detector test on darwin/arm64 only, CONV-ABS-77).

## Preconditions

1. ASSUMPTION (ASSUMP-107-1): the Claude Code 2.1.326 `subagentStatusLine` stdin payload is assumed
   compatible with the 2.1.322 contract legacy parsed; to be verified by a capture before Phase 2 writes the S1.07 stories (OD-192).
2. Wall clock read once per render (`now_ms = time.time() * 1000`, SL:889 — a PR-15 site).
3. `tokenCount` and `startTime` taken from the eligible task dict.

## Postconditions

1. Token bit: only when `tokenCount` is int/float/bool with value > 0; bytes
   `\e[36m<fmt><suffix>\e[0m`, where `<suffix>` is the configured
   `statusline.subagent.tokens.suffix` (Text, default ` tok`) and the `36` is the shared theme
   colour key `statusline.theme.cyan` (OD-113); the settled-row status suffix and the elapsed
   clock use `statusline.theme.grey` (default `90`); fmt = `f"{n:.0f}"` (n < k_from), `f"{n/1e3:.1f}k"` (n < m_from),
   `f"{n/1e6:.2f}M"` (n >= m_from) after `float(n)` — `k_from`/`m_from` (defaults 1000/1e6) are display
   thresholds only (the PC branch points); the 1e3/1e6 divisors are format constants that do NOT
   follow the thresholds (Inv5); the threshold compares the float value first, then the
   format rounds (round-half-to-even applied by CPython `format()` to the exact binary double) —
   EC-003.
2. Clock bit: only when `status == "running"` AND `startTime` is int/float/bool AND `startTime > 0`;
   bytes `\e[90m{int(secs//60):02d}:{int(secs%60):02d}\e[0m`, `secs = max(now_ms - start, 0)/1000`.
3. Future startTime (start > now) clamps to `00:00` — the max(..., 0) floor.
4. Settled rows (completed/failed/killed/unknown) show no clock even when `startTime` is set.
5. Non-numeric `tokenCount`/`startTime` (string, null, list, dict) → the bit is silently omitted.
6. Huge-int `tokenCount` (value > 0, |n| >= 2**1024 - 2**970): passes the gate, raises OverflowError
   at `_fmt_tokens`'s `float(n)` (SL:878); the helper catches only TypeError/ValueError, so the fault
   propagates to the guard — the degraded line (CP-A04, BC-1.07.008). The trigger envelope is bounded
   to 309..4300-digit decimal literals (ADV-P12-C02, oracle-measured 2026-11-18 on CPython 3.11.7, the
   oracle interpreter): a literal of 308 digits or fewer sits below the gate, and a literal of 4,301+
   digits exceeds CPython's `sys.int_max_str_digits` = 4300, so `json.load` at SL:930 raises ValueError
   at the stdin decode — absorbed to `{}` per BC-1.07.003, stdout zero bytes, NOT the degraded line.
7. Huge-int `startTime` (running, value > 0, |n| >= 2**1024 - 2**970): raises OverflowError at
   `now_ms - start` (SL:919) — the degraded line (CP-A05, BC-1.07.008); same 309..4300-digit literal
   envelope as PC6 (longer literals fail the stdin decode instead, BC-1.07.003).

## Invariants

1. `_fmt_tokens` thresholds compare AFTER `float(n)`: 1000 → `1.0k`, 999.5 → `1000`
   (threshold-then-format: 999.5 fails the `>= 1000` test, then the `.0f` format rounds
   half-to-even to `1000`), 999,999 → `1000.0k` (verified).
2. Bool `tokenCount=True` passes the isinstance gate and > 0 test and renders `1 tok`
   (Python bool-as-int quirk, pinned).
3. PR-15 remedy: every float product (notably `time.time() * 1000`) ports with an explicit `float64`
   conversion and Python operation order; Go must not fuse `x*y + z` across statements on arm64.
   Detector test placed on darwin/arm64 CI only (GOAMD64=v3; v1 never fuses — CONV-ABS-77).
4. The clock base `now_ms` is captured once per render, not per row (SL:889).
5. The ` tok` suffix comes from `statusline.subagent.tokens.suffix` (Text, default ` tok`); the
   `k_from`/`m_from` keys (defaults 1000/1e6) are display thresholds only — they move the PC1 branch
   points, nothing else. The 1e3/1e6 divisors are format constants, NOT config: named constants with a
   "why not config" comment (they define the K/M units, the iron rule's format-constant carve-out), so
   a non-default `k_from` never changes the divisor. Leaf spellings registered in the BC-2.01.004
   registry (per the ADV-P3-C05 ruling); with defaults the bytes are exactly legacy's (SL:909-911) and
   no hard-coded literals own them in logic (D15).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `tokenCount = 0`, `-5`, `False`, `""`, `"500"`, null | Bit omitted (gate: numeric AND > 0) |
| EC-002 | `tokenCount = True` | Bit renders `1 tok` (bool-is-int quirk) |
| EC-003 | `tokenCount = 999.5` | Renders `1000 tok` (threshold-then-format order) |
| EC-004 | Completed row with `startTime` set | No clock; grey status suffix only |
| EC-005 | `startTime = true` (bool) | Clock computed from epoch-1ms — a huge valid MM:SS; exact bytes time-dependent (not pinned) |
| EC-006 | Very large tokenCount (1e9) | `1000.00M` (>=".2f"M of 1000.0) |
| EC-007 | startTime exactly 0 | No clock (gate is `> 0`) |
| EC-008 | `tokenCount = 2**1024 - 2**970` (huge int) | OverflowError at `float(n)` → exactly the degraded line, exit 0 (CP-A04) |
| EC-009 | `startTime = 2**1024 - 2**970`, running | OverflowError at `now_ms - start` → exactly the degraded line, exit 0 (CP-A05) |
| EC-010 | `tokenCount` = `Infinity` (or `1e400`) — the stdin decode yields float `inf`, which passes the numeric `> 0` gate; `_fmt_tokens` divides and formats `f"{inf/1e6:.2f}M"` → `infM` (ADV-P7-C04, oracle-pinned 2026-11-18) | renders `\e[36minfM tok\e[0m` — legacy's Python float-repr spelling; a naive Go port prints `+Inf` (fmt/strconv) and would break byte parity, so hylo renders `infM` |
| EC-011 | `startTime` = `Infinity`, running — `start > 0` passes; `secs = max(now_ms - inf, 0)/1000 = 0` | renders `\e[90m00:00\e[0m` (clamp floor; ADV-P7-C04, oracle-pinned 2026-11-18) |

## Canonical Test Vectors

(Byte notation: expected outputs are wire forms — pure ASCII, `ensure_ascii`-escaped per
BC-1.07.004 PC3/Inv 2. ESC is spelled `\u001b` on the wire and non-ASCII characters never appear
raw; one notation throughout this table.)

| Input (task fields) | Expected Output | Category |
|---|---|---|
| `tokenCount=12345`, running, `startTime=<now-125000>` | `\u001b[36m12.3k tok\u001b[0m \u00b7 \u001b[90m02:05\u001b[0m` (content bits within the BC-1.07.004 pinned row) | happy-path |
| `tokenCount=2500000`, completed | `\u001b[36m2.50M tok\u001b[0m`, no clock | happy-path |
| `tokenCount=500`, running | `\u001b[36m500 tok\u001b[0m` | happy-path |
| `_fmt_tokens` direct: 12345 / 2500000 / 500 / 999.5 / 1000 / 999999 / True / "abc" / None | `12.3k` / `2.50M` / `500` / `1000` / `1.0k` / `1000.0k` / `1` / `?` / `?` | table |
| running, `startTime=<now+60000>` | `\u001b[90m00:00\u001b[0m` (floor) | edge-case |
| `tokenCount = 2**1024 - 2**970`, running, `startTime=<now-125000>` | exactly `\u001b[90mstatusline degraded\u001b[0m\n` (29 bytes), exit 0 (CP-A04) | error |
| `tokenCount = 2**1024 - 2**970 - 1`, running (largest convertible int) | renders; `float` value is the IEEE-754 maximum; tok bit present, no degrade | edge-case |
| `startTime = 2**1024 - 2**970`, running | exactly `\u001b[90mstatusline degraded\u001b[0m\n` (29 bytes), exit 0 (CP-A05) | error |
| `tokenCount=Infinity`, completed (stdin token `Infinity` or `1e400` — both decode to float `inf`) | one line, content `"\u001b[32m\u2714 n\u001b[0m \u00b7 \u001b[36minfM tok\u001b[0m \u00b7 \u001b[90mcompleted\u001b[0m"` (pure-ASCII wire, oracle byte-exact re-run pass-9 2026-11-18; the raw glyph spellings of ADV-P8-C01 corrected per BC-1.07.004 PC3) | edge-case |
| `startTime=Infinity`, running | one line, content `"\u001b[33m\u00bb n\u001b[0m \u00b7 \u001b[90m00:00\u001b[0m"` (pure-ASCII wire, oracle 2026-11-18) | edge-case |

Verified 2026-11-18 against CPython 3.11.7 (`python3 -I`): every cell above reproduced, including the
999.5 → `1000` and True → `1` quirks and the `02:05` split at 125 s; the overflow threshold confirmed
empirically — `float(2**1024 - 2**970)` raises OverflowError, `float(2**1024 - 2**970 - 1)` converts
(CP-A04/A05, adv-p3). The Infinity rows (EC-010/EC-011) were re-pinned 2026-11-18 through
`render_subagent_rows` under CPython 3.11.7 (the oracle interpreter) with an isolated HOME
(ADV-P7-C04) — `infM tok` and the `00:00` clamp reproduced byte-for-byte.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-009 | `_fmt_tokens` equals CPython format over a dense grid incl. threshold boundaries (rides the Tier A T-family corpus rows) | manual corpus comparison (Tier A) |
| VP-039 | PR-15: fused vs unfused elapsed-clock floats match CPython-derived goldens bit-exactly (VP-039 1.4); rendered MM:SS byte-identical across regimes | FMA detector test, darwin/arm64 only (CONV-ABS-77) |
| VP-001 | The promised output set holds under the fault ladder incl. the subagent regime: render output, the 29-byte degraded line, subagent JSON rows or zero bytes — never blank, exit 0 (CP-A04/A05 legs ride this ladder) | fault-injection ladder (assertPromisedOutputSet, DI-008) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 (gates never raise), DI-012 (quirks pinned, no silent normalization) |
| Architecture Module | `internal/statusline` (token/clock bits); float ops per `internal/pyfmt` Num conventions |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py: token bit (SL:909-911), clock (SL:913-921), `_fmt_tokens` (SL:876-885; `float(n)` SL:878), now_ms (SL:889), `now_ms - start` (SL:919) |
| Legacy contract | BC-SL-097 (P3r2 §A7; `_fmt_tokens` home r8; CP-A04/A05 enumerated adv-p3); pitfall PR-15 (P5r1 §292, r2 §A.2) |
| Decisions | OD-155; D4; adv-p3: OD-156 + new CP ids (ADV-P3-C04), ADV-P3-C05 token config keys; review 2026-11-13 #21.2 (clock gate), #8.1 analog (compact scales); CONV-ABS-77 (FMA test placement) |

## Related BCs (Recommended)

- BC-1.07.004 — composes with (framing)
- BC-1.07.005 — composes with (suffix interplay: settled rows)
- BC-1.07.008 — related to (CP-A04/A05 overflow sites degrade to the 29-byte line)
- BC-5.01.* — related to (Python number-formatting semantics family)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — segment builder; PR-15 float discipline in the elapsed-clock
  helper

## Story Anchor (Recommended)

TBD — filled by story-writer

## VP Anchors (Recommended)

- VP-009 (T-family `_fmt_tokens` dense grid)
- VP-039 (PR-15 fused/unfused elapsed clock, bit-exact against CPython-derived goldens)
- VP-001 (never-blank/exit-0 ladder; the CP-A04/A05 legs of this contract ride it)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:909-921, 876-885, 889) |
| **Confidence** | high (dense pinned grid 2026-11-18) |
| **Extraction Date** | 2026-11-18 |

#### Evidence Types Used

- **assertion**: 9-cell `_fmt_tokens` table + clock clamp/bool quirks, all pinned under CPython 3.11.7
- **guard clause**: isinstance+(>0) gates (SL:909, 917-918)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | wall clock (once per render) |
| **Deterministic** | yes modulo wall clock |
| **Thread safety** | safe for concurrent use |
| **Overall classification** | pure (given now_ms) |

#### Refactoring Notes

Go: keep `_fmt_tokens` as a pure `func(n any) string` mirroring float64(everything)-then-branch order;
inject `now_ms` for testability. The clock base comes from the injected `Env.Now()` as **float64 seconds** (the
`time.time()` value; `HYLO_TEST_NOW` pins that same float — orchestrator call 7), and the millisecond product is
`nowMs := nowSecs * 1000` — a single float64 product, never a fused multiply-add chain. **Never**
`float64(time.Now().UnixMilli())`: it truncates below 1 ms and bypasses the injected clock, so when the true
elapsed time is under 1 ms past a whole second legacy shows N s and Go would show N−1 s — the MM:SS bytes differ
(ADV-P5-C07).
