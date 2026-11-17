---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/ubiquitous-language.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, semport/hylo-legacy/hylo-legacy-pass-4-deep-nfr-r7.md, owner-decisions-log-2026-11-14.md]
input-hash: "db7abf8"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-093"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.030: effective_rl sequence with sticky CP-S09

> Byte notation used below: `\e` = ESC (0x1B); `\n` = LF (0x0A). All other characters are literal UTF-8.

## Description

`effective_rl` smooths the plan windows across refreshes: a non-empty object in stdin `rate_limits` is written to
the session cache (`rl`, `rl_ts = now`) and used; any other input (absent, `{}`, `null`, a string) leaves the cache
untouched and serves the cached `rl` while `now - rl_ts < 1800`. Because the cache stores whatever object stdin sent,
a malformed window (truthy, not an object) is cached before the render crashes on it (CP-S09), so the degraded line
repeats on every refresh until stdin sends a good object or 1800 s pass. This contract pins that multi-step sequence.

## Preconditions

1. Session cache file `<cache_dir>/statusline-<sid>.json`, where `<cache_dir>` is `paths.cache_dir` (OD-101: hylo's
   cache location, not the legacy literal) and `<sid>` is stdin `session_id` or `nosession` (BC-1.06.001 owns load/save
   and file naming, BC-1.06.002 temp handling, BC-3.01.001 the cache directory).
2. `now` = the single per-render clock value (design IM-14), frozen by the harness.
3. Config `statusline.limits.keep_s` default 1800 (T-010; owner group A judgment: "30 min of plan limits between Claude
   Code reports"). `backends[0].model_prefixes` controls reroute-all (BC-1.02.009).
4. `effective_rl` runs before the row-1 render (legacy step order, BC-1.01.009).

## Postconditions

1. If stdin `rate_limits` is an object with at least one key: load the cache, set `rl` = that object verbatim and
   `rl_ts = now`, save the cache, return the object. This happens even when reroute-all hides the widget.
2. Otherwise: load the cache; return `rl` if `rl` is an object and `now - rl_ts < keep_s` (strict), where a missing
   `rl_ts` counts as 0; else return `None` (widget hidden). The cache is not modified and a stale `rl` is never
   deleted.
3. The cache file content after a write is the Python `json.dump` default form (`", "` and `": "` separators, keys in
   insertion order, floats in Python `repr`) of the whole cache object, byte-exact (S5.02).
4. The returned value replaces `d["rate_limits"]` for the limits widget (BC-1.02.009..012). A returned window value
   that is truthy and not an object (string, non-empty list, non-zero number, `true`) makes the limits loop raise at
   SL:503 (CP-S09) → whole stdout is `\e[90mstatusline degraded\e[0m\n`, with the cache write of step 1 already done.

## Invariants

1. The cache is replaced wholesale by each good stdin object (no merge of windows).
2. No lower bound on `rl_ts`: a future `rl_ts` is served.
3. `keep_s` comparison is `<`; exactly 1800 s after `rl_ts` the cached value is no longer served.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | stdin `rate_limits` = `{}`, `null` or `"x"` | treated as absent; not written; cached value served |
| EC-002 | exactly `rl_ts + 1800` | hidden; cache unchanged |
| EC-003 | stdin `{five_hour: "x"}` | cached, then degraded; degraded again on every refresh with absent `rate_limits` until `rl_ts + 1800`, then hidden |
| EC-004 | bad cached window, then a good stdin object | recovers at once (stdin overwrites the cache) |
| EC-005 | `{five_hour: 0, seven_day: {…}}` | saved verbatim; `0` counts as an absent window |
| EC-006 | `{seven_day: {}}` | saved; widget hidden (no percentage) |
| EC-007 | reroute-all (`backends[0].model_prefixes` contains bare `claude`) | still written to the cache; widget hidden |
| EC-008 | foreign cache with `rl` but no `rl_ts` | hidden (`ts` defaults to 0) |
| EC-009 | cache `rl_ts` in the future | shown |

## Canonical Test Vectors

T0 = 1794600000; good = `{"seven_day": {"used_percentage": 44, "resets_at": 1794615480.0}}`. Each step runs
`effective_rl` then the row-1 render. "Shown" is the limits segment with SGR stripped; "Cache" is the exact file
content (no trailing newline).

| Input (t − T0, stdin `rate_limits`) | Expected Output (shown; cache after) | Category |
|-------|----------------|----------|
| 0, good | `7d44% ->4h18m`; `{"rl": {"seven_day": {"used_percentage": 44, "resets_at": 1794615480.0}}, "rl_ts": 1794600000.0}` | happy-path |
| 100, absent | `7d44% ->4h16m` (countdown from cached `resets_at`); unchanged | happy-path |
| 200 / 300 / 400, `{}` / `null` / `"x"` | `7d44% ->4h14m` / `->4h13m` / `->4h11m`; unchanged | edge-case |
| 1799.999, absent | `7d44% ->3h48m`; unchanged | edge-case |
| 1800, absent | hidden; unchanged (stale `rl` kept) | edge-case |
| 1900, `{"five_hour": {"used_percentage": 90, "resets_at": 1794601900.0}, "seven_day": {"used_percentage": 50, "resets_at": 1794615480.0}}` | `7d50% ->3h46m` (5h expired, `resets_at <= now`); cache replaced wholesale with that object and `"rl_ts": 1794601900.0` | happy-path |
| 2000, absent | `7d50% ->3h44m` | happy-path |
| 15480, absent | hidden | edge-case |
| sticky: 0, `{"five_hour": "x"}` | degraded line; `{"rl": {"five_hour": "x"}, "rl_ts": 1794600000.0}` written before the crash | error (CP-S09) |
| sticky: 10 and 1799, absent | degraded line; unchanged | error |
| sticky: 1800, absent | recovers (hidden); unchanged | edge-case |
| recover: 0 `{"five_hour": [1]}`, then 5 good | degraded, then `7d44% ->4h17m` with `"rl_ts": 1794600005.0` | edge-case |
| 0, `{"five_hour": true}` | degraded; cache `{"rl": {"five_hour": true}, "rl_ts": 1794600000.0}` | error |
| 0, good with reroute-all | hidden; cache written as in row 1 | edge-case |
| cache `{"rl": good}` (no `rl_ts`), absent | hidden | edge-case |
| cache `{"rl": good, "rl_ts": 1794600500.0}`, t = 0, absent | `7d44% ->4h18m` | edge-case |

Unstripped form of the first row: `\e[90m7d44%\e[0m \e[90m->4h18m\e[0m`. Pinned 2026-11-15 by running the legacy
`effective_rl` + `render_lane` sequence under CPython 3.11 (oracle, OD-104); identical to deep pass-3 round 2 §A3.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028, VP-019 | For any interleaving of good/absent/malformed stdin, Go's shown output and cache bytes equal the oracle's at every step | multi-step (M) sequence harness vs oracle |
| VP-028, VP-019 | A malformed window is cached before the degrade | multi-step table test |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` (design §8 home `sl/limits.go`; BC-COMPONENT-MAP: internal/statusline/limits.go (effective_rl, sticky CP-S09) — ARCH-03) |
| Stories | S-N.MM (filled by story-writer) |
| Source | legacy/dgx_statusline.py:effective_rl (SL:298-312); call site legacy/dgx_statusline.py:main (SL:1216); crash site legacy/dgx_statusline.py:render_lane (SL:502-503) |
| Legacy contract | BC-SL-093 (deep pass-3 round 2 §A3) |
| Config keys | `statusline.limits.keep_s` (T-010), `paths.cache_dir` (OD-101), `backends[0].model_prefixes` (OD-123) |
| Parity | byte-exact for stdout and cache content. Go temp-file cleanup on a failed replace (legacy leaks the temp file) is the OD-110 temp-file exclusion entry (owned by BC-1.06.002 with its own table tests), applied to the cache-directory comparison only; it does not affect any vector here |

## Related BCs (Recommended)

- BC-1.02.013 — refines (rate-limit smoothing over 1800 s)
- BC-1.02.009 — composes with (reroute-all hides the widget)
- BC-1.02.010 — composes with (expired window unreported)
- BC-1.01.009 — depends on (legacy step order; earlier writes kept)
- BC-5.02.001..004 — depends on (JSON byte semantics of the cache file)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md` — internal/statusline/limits.go (effective_rl, sticky CP-S09) (session cache, side-effect order) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-N.MM — filled by story-writer

## VP Anchors (Recommended)

- VP-028, VP-019 — sequence equality

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (effective_rl SL:298-312; main SL:1216) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `isinstance(rl_stdin, dict) and rl_stdin` (SL:305); `isinstance(rl, dict) and now - ts < RL_KEEP` (SL:312)
- **documentation**: SL:299-303 docstring (no blinking; show unless never seen or stale)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads + writes (session cache file) |
| **Global state access** | none |
| **Deterministic** | yes given `now` and the cache content |
| **Thread safety** | not thread-safe (file read-modify-write; one process per refresh) |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Split into a pure decision `(stdin, cached, now) -> (shown, newCache?)` and the cache I/O shell, so the sequence is
table-testable without files; the harness still compares the real cache bytes.
