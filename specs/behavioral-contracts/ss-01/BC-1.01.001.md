---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T17:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "7d75fbc"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-001"
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

# Behavioral Contract BC-1.01.001: Guard prints the 29-byte degraded line and exits 0

> Byte notation used below: `\e` = ESC (0x1B); `\n` = LF (0x0A). All other characters are literal UTF-8.

## Description

Any fault raised while rendering one status-line refresh (after configuration has resolved) is caught by one
top-level guard, which writes exactly the 29-byte degraded line to stdout and exits 0. The status line is never
blank and never non-zero (DI-008). This is the outermost rung of the degraded ladder; config errors (D4-EX-3) and
unknown flags (OD-112) use their own one-line formats and are not this contract.

## Preconditions

1. `hylo statusline` is invoked with any argv that BC-4.01.001 routes to the main render (no unknown flag; that
   case is BC-4.01.002).
2. Configuration resolved without error (an invalid value renders the D4-EX-3 line instead, BC-2.02.001).
3. During the refresh a fault occurs at any guarded site: a crash-path site CP-S01..S17 (stdin type confusion,
   lone surrogate at output), CP-N01/N02 (row-2 NaN paths, BC-1.04.014/015), or any unexpected Go panic.

## Postconditions

1. stdout receives exactly these 29 bytes and nothing else (no partial row output precedes them):
   `\e[90mstatusline degraded\e[0m\n` — hex `1b 5b 39 30 6d` + ASCII `statusline degraded` (19 bytes) +
   `1b 5b 30 6d 0a`.
2. The process exit code is 0.
3. Cache writes performed by steps that completed before the fault persist unchanged (BC-1.01.009); no write
   planned after the fault point happens.
4. Diagnostic detail, if any, goes to stderr only; stderr is never compared for parity (design §5.3).

## Invariants

1. The degraded line is pure ASCII plus ESC; it cannot fail to encode.
2. The line terminator is LF on every OS, including Windows (design IM-22; the harness pins legacy to
   `newline="\n"`).
3. Exactly one write to stdout per refresh: Go builds the output in a buffer and either writes the rendered rows
   or the degraded line, never both (design IM-15/IM-22).
4. The color code `\e[90m` and reset `\e[0m` are the legacy defaults of `statusline.theme.*` (OD-113); the bytes
   above are the default-config output.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Fault inside the row-1 widgets after the git-cache write (e.g. thermometer, CP-S06) | Degraded line; git cache and earlier writes kept (BC-1.01.009) |
| EC-002 | Fault at the final print: a rendered str holds a lone surrogate (CP-S17) | Degraded line after every cache write of the refresh (BC-1.01.008) |
| EC-003 | Go panic not mapped to any CP site (programming error) | `recover()` backstop prints the same 29 bytes, exit 0; the parity diff still flags it because legacy would not degrade on that input |
| EC-004 | Legacy import-time env crash (CP-X01/X02: unparseable TTL/ROWS -> empty stdout, exit 1) | Not reachable in Go: invalid settings are config errors, approved deviation **D4-EX-3** (OD-102, OD-114) rendered by BC-2.02.001; excluded from the parity diff via the OD-105 exclusion entry `D4-EX-3` with dedicated tests `TestConfigError_D4EX3_{Number,Boolean,URL,Enum}` |
| EC-005 | Writing the degraded line itself fails (stdout closed / EPIPE; legacy CP-X03 exits 1 with no stdout) | Ruled OD-136: Go swallows the write error and still returns exit 0 (DI-008). This is the named exclusion `cp-x03` in the OD-105/OD-110 closed set, with its own dedicated table test (name provisional — architect (OD-145)). Not observable by Claude Code (the consumer is gone); out of parity comparison (P3r1 §B marks CP-X03 not parity-relevant) |
| EC-006 | SIGINT/SIGTERM (legacy CP-X04) | Out of scope; no output contract |
| EC-007 | argv contains `--subagent` | Not this contract: OD-14 drops the subagent path; OD-112 renders `hylo: unknown flag ...`, exit 0 (BC-4.01.002) |

## Canonical Test Vectors

Config: defaults with `HYLO_STATUSLINE_ROWS=1`, `HYLO_STATUSLINE_GIT_ENABLED=0`, COLUMNS unset, empty cache dir.

| Input | Expected Output | Category |
|-------|----------------|----------|
| stdin `{"model":{"display_name":"Opus 5.5"}}` | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97mOpus 5.5\e[0m\n`, exit 0 (no degrade) | happy-path |
| stdin `{"model":"x"}` (CP-S01: `.get` on a str) | exactly `\e[90mstatusline degraded\e[0m\n` (29 bytes), exit 0 | error |
| stdin `{"session_id":"s1","model":{"display_name":"\ud800"},"rate_limits":{"five_hour":{"used_percentage":1,"resets_at":9999999999}}}` (JSON escape, CP-S17) | degraded 29 bytes, exit 0; `statusline-s1.json` exists holding `rl`/`rl_ts` (written before the fault) | edge-case |
| injected panic in a widget (Go unit test) | degraded 29 bytes, exit 0 | error |

Verified 2026-11-15 against CPython 3.11.7 (`LANG=en_US.UTF-8`, `DGX_SL_ROWS=1`, `DGX_SL_GIT=0`): rows 1-3 above.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-001, VP-003 | For every input that makes `Render` return `errDegraded` or panic, `Main` writes exactly the 29 degraded bytes and returns 0 | proptest/fuzz (Tier C differential) |
| VP-001, VP-003 | `Main` never returns non-zero for any stdin/argv routed to it | fuzz |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Architecture Module | `internal/statusline` guard (`guard.go`, design §2.2) (BC-COMPONENT-MAP: internal/statusline/guard.go (29-byte degraded line, recover backstop) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`__main__` guard (SL:1238-1245); degraded colors RESET SL:127, GREY SL:131-132 |
| Legacy contract | BC-SL-001 (P3 broad sweep; refined P3r1; index P3r4 §7.3) |
| Decisions | D4 (byte parity), OD-102/OD-114 (D4-EX-3 replaces CP-X01/X02), OD-136 (CP-X03 → named exclusion `cp-x03`, exit 0), OD-112, OD-14 |

## Related BCs (Recommended)

- BC-1.01.009 — composes with (writes before the fault persist)
- BC-1.01.008 — related to (CP-S17 lone-surrogate path ends here)
- BC-2.02.001 — related to (D4-EX-3 config-error line uses the same output path, different text)
- BC-4.01.002 — related to (unknown-flag line, same never-blank rule)
- BC-1.04.014, BC-1.04.015 — related to (CP-N02/N01 degrade via this guard)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#statusline-guard` — internal/statusline/guard.go (29-byte degraded line, recover backstop) (degraded ladder top level) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — status line frame (design step S2)

## VP Anchors (Recommended)

- VP-001, VP-003 — degraded output is exactly 29 bytes, exit 0

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1238-1245) |
| **Confidence** | high (pinned by CPython 3.11.7 runs; design §8 conf H) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `except Exception:` around `sys.exit(main())` (SL:1243-1245)
- **assertion**: pinned runs (P3r1 §B crash catalogue; re-run 2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | writes stdout |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | n.a. (single-shot process) |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Go maps the guard to `errDegraded` (wrapped at each CP site) plus a `recover()` backstop in `statusline.Main`; the
constant `degradedLine` is assembled from the theme defaults so it stays byte-identical (design IM-15).
