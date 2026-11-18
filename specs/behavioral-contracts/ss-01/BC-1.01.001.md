---
document_type: behavioral-contract
level: L3
version: "1.4.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T06:25:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "7ea5e4f"
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
modified:
  - "1.3.2 pass-3 remediation (ADV-P3-B01/B11/B16): --subagent routes under this guard per OD-155 (supersedes OD-14); degraded-line SGR cites OD-113 not OD-162; second VP row is VP-003; 2026-11-18T02:00:00Z"
  - "1.3.3 pass-4 remediation (ADV-P4-B12/B07): config-error precondition carves out --subagent mode (OD-168: zero stdout bytes); DI-012 cited for the carried closed-set ids; 2026-11-18"
  - "1.3.4 pass-4 residual sweep (ADV-P4-D22): D4-EX-3 table-test name canonicalized to TestD4EX3_{Number,Boolean,URL,Enum}; 2026-11-18"
  - "1.3.5 pass-5 remediation (ADV-P5-B02): PC3 widens the guarded-site list to the E-REN-002-routed families (CP-N03, CP-O01..O05, CP-O10/O11; transcript CP-O06..O08/CP-O09 named as skip/no-write disciplines, not this guard); EC-003 no longer claims the parity diff always disagrees — mapped-degrade inputs agree on stdout; 2026-11-18T05:42:56Z"
  - "1.3.6 pass-5 residual sweep (ADV-P5-B14): EC-007's subagent crash-range corrected to CP-A01..A05; history re-dated ascending (the pass-4 stamps predated pass-3's); no behavioral change; 2026-11-18T06:25:00Z"
  - "1.3.7 2026-11-19T02:00:00Z: sync-check adv-p5 closure (SC-17 sibling sweep) — EC-004 register row respelled to the OD-178 canon (five canonical tests incl. TestD4EX3_Text; register closed at seven) and history labels version-prefixed ascending; no behavioral change"
  - "1.3.8 pass-6 remediation (ADV-P6-B11): PC3 guarded-site list now names the subagent crash family CP-A01..A05 (matching PC1's --subagent coverage and EC-007); no behavioral change; 2026-11-19T04:00:00Z"
  - "1.3.9 pass-7 remediation (ADV-P7-B03/B04/B09): PC3 guarded-site list gains the Windows MSVC localtime-domain OSError (CP-T09, ErrLocaltimeDomain — `_iso_ts` catches only ValueError, SL:984) per orchestrator call 8, and the CP-N03 anchor is corrected to BC-1.04.004/.005 (ADV-P7-B04; ARCH-03/error-taxonomy owners); EC-005 names the canonical test TestCPX03_WriteFailureExit0 (ADV-P7-B09); input-hash refreshed; no behavioral change; 2026-11-19T07:00:00Z"
  - "1.4 pass-9 remediation (orchestrator call 4 / ADV-P9-B03): PC3 guarded-site overflow list extended with CP-O12 (cost-pick equivalence overflow at the SL:633 multiply; owner BC-1.02.029 EC-009) — crash register now 49 paths (X4 S17 T8 N3 O12 A5); 2026-11-19T16:00:00Z"
  - "1.4.1 pass-11 remediation (ADV-P11-B04): PC3's CP-N anchor corrected — only CP-N03 belongs to BC-1.04.004/.005; CP-N01 and CP-N02 credited to their H1 owners BC-1.04.015 and BC-1.04.014 (matching the Related BCs line); the pass-9 label 1.3.10 respelled 1.4 so the patch sequence stays monotonic past nine (POLICY 14 leg 3); no behavioral change; 2026-11-21T12:00:00Z"
  - "1.4.2 pass-11 residual (OD-190 applied literally): Inv 2 respelled — the Windows LF comes from the comparator's open CRLF→LF conversion of the ORACLE's stdout before the byte comparison; hylo's bytes are never converted and the shim does no newline reconfigure; no behavioral change; 2026-11-21T12:30:00Z (re-dated ascending in 1.4.3: its original 09:00Z stamp predated 1.4.1's)"
  - "1.4.3 pass-12 remediation (ADV-P12-B08): the 1.4.1/1.4.2 history entries reordered ascending (1.4.2 was listed before 1.4.1) and the 1.4.2 stamp re-dated ascending per the pass-5 B14 precedent; no behavioral change; 2026-11-23T00:00:00Z"
  - "1.4.4 pass-12 residual sweep (orchestrator pass-12 residual call 8): the lone-surrogate display-name vector restates its window-start pin per the corrected cache-003 design (every corpus case seeds proc_start or is cache-003, no probe on either side, no fake process table); no behavioral change; 2026-11-23T14:00:00Z"
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
top-level guard, which writes exactly the 29-byte degraded line to stdout and exits 0. In the main render the status
line is never blank and never non-zero (DI-008); the `--subagent` mode carves out zero-stdout-bytes outcomes
(OD-155, OD-168). This is the outermost rung of the degraded ladder; config errors (D4-EX-3) and unknown flags
(OD-112) use their own one-line formats and are not this contract.

## Preconditions

1. `hylo statusline` is invoked with any argv that BC-4.01.001 routes to either render path — the main render or
   the `--subagent` render (OD-155; legacy runs `main_subagent` under the same top-level guard, SL:1238-1243) —
   excluding unknown flags (that case is BC-4.01.002).
2. Configuration resolved without error. In the main render an invalid value renders the D4-EX-3 line instead
   (BC-2.02.001); in `--subagent` mode a config error prints **zero stdout bytes** (diagnostic on stderr) per
   OD-168 — the PRD/DI-008 carve-out for the agent-panel mode.
3. During the refresh a fault occurs at any guarded site: a crash-path site CP-S01..S17 (stdin type confusion,
   lone surrogate at output), CP-N01/N02 (the row-2 NaN paths: KV NaN, BC-1.04.015; sparkline NaN/+Inf,
   BC-1.04.014) and CP-N03 (the metrics-borne numeric-`__name__` degrade, BC-1.04.004/.005 per ARCH-03), the
   Windows MSVC localtime-domain OSError on a naive transcript timestamp
   (**CP-T09** — `_iso_ts` catches only ValueError, SL:984, so the OSError escapes and degrades the line;
   `ErrLocaltimeDomain`, ARCH-06), the OD-156 overflow sites routed to E-REN-002 through this guard (CP-O01..O05 at the row-1
   render sites, CP-O10/O11/O12 in the cost segment — the transcript family CP-O06..O08 and CP-O09 resolve to the
   D4-EX-2 skip / no-write-save disciplines instead, not this guard; error-taxonomy E-REN-002), the subagent
   render family CP-A01..A05 (EC-007; BC-1.07.008), or any unexpected Go panic.

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
2. The line terminator is LF on every OS, including Windows (design IM-22; OD-190: on
   the Windows legs the comparator converts the ORACLE's stdout CRLF to LF before the
   byte comparison; hylo's bytes are never converted and the shim does no newline
   reconfigure).
3. Exactly one write to stdout per refresh: Go builds the output in a buffer and either writes the rendered rows
   or the degraded line, never both (design IM-15/IM-22).
4. The color code `\e[90m` and reset `\e[0m` are built-in named constants of the guard,
   independent of `statusline.theme.*` (OD-113; cf. BC-2.02.001 inv 2); the theme itself may be the invalid value
   on a config-error run, so the degraded line must not depend on it (same ruling in
   interface-definitions.md and ARCH-03).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Fault inside the row-1 widgets after the git-cache write (e.g. thermometer, CP-S06) | Degraded line; git cache and earlier writes kept (BC-1.01.009) |
| EC-002 | Fault at the final print: a rendered str holds a lone surrogate (CP-S17) | Degraded line after every cache write of the refresh (BC-1.01.008) |
| EC-003 | Go panic not mapped to any CP site (programming error) | `recover()` backstop prints the same 29 bytes, exit 0; the parity diff still flags the run on every input where legacy renders normally (legacy would not degrade). On an input matching a mapped degrade — the CP-S/CP-N/E-REN-002 families, e.g. a CP-O overflow input — both sides emit the 29-byte line and the stdout diff agrees; the closed, mutation-tested site register (VP-012) is what keeps such a panic from hiding |
| EC-004 | Legacy import-time env crash (CP-X01/X02: unparseable TTL/ROWS -> empty stdout, exit 1) | Not reachable in Go: invalid settings are config errors, approved deviation **D4-EX-3** (OD-102, OD-114) rendered by BC-2.02.001; excluded from the parity diff via the OD-105 exclusion entry `D4-EX-3` with dedicated tests `TestD4EX3_{Number,Boolean,URL,Enum,Text}` — one per class with its own dedicated grammar (number-range, boolean, URL, enum, text); the number-grammar (BC-2.02.003) and theme/SGR (BC-2.01.003) classes are pinned by their class contracts, and the register is closed at seven (OD-114 + OD-134 + OD-140 + OD-178) |
| EC-005 | Writing the degraded line itself fails (stdout closed / EPIPE; legacy CP-X03 exits 1 with no stdout) | Ruled OD-136: Go swallows the write error and still returns exit 0 (DI-008). This is the named exclusion `cp-x03` in the OD-105/OD-110 closed set, with its own dedicated table test `TestCPX03_WriteFailureExit0` (canonical name per the VP-012 row and VP-003; resolves the OD-145 provisional naming). Not observable by Claude Code (the consumer is gone); out of parity comparison (P3r1 §B marks CP-X03 not parity-relevant) |
| EC-006 | SIGINT/SIGTERM (legacy CP-X04) | Out of scope; no output contract |
| EC-007 | argv contains `--subagent` | This contract covers it: OD-155 (superseding OD-14 (a)) ports the subagent panel in P1; legacy guards `main_subagent` identically (SL:1238-1243), so a fault in the subagent render ends in the same 29 bytes, exit 0 (BC-1.07.008, CP-A01..A05). An *unknown* flag is the separate BC-4.01.002 line (OD-112) |

## Canonical Test Vectors

Config: defaults with `HYLO_STATUSLINE_ROWS=1`, `HYLO_STATUSLINE_GIT_ENABLED=0`, COLUMNS unset, empty cache dir.

| Input | Expected Output | Category |
|-------|----------------|----------|
| stdin `{"model":{"display_name":"Opus 5.5"}}` | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97mOpus 5.5\e[0m\n`, exit 0 (no degrade) | happy-path |
| stdin `{"model":"x"}` (CP-S01: `.get` on a str) | exactly `\e[90mstatusline degraded\e[0m\n` (29 bytes), exit 0 | error |
| stdin `{"session_id":"s1","model":{"display_name":"\ud800"},"rate_limits":{"five_hour":{"used_percentage":1,"resets_at":9999999999}}}` (JSON escape, CP-S17) | degraded 29 bytes, exit 0; `statusline-s1.json` exists holding exactly `rl`/`rl_ts` (the seeded `proc_start` plus `rl`/`rl_ts`, the latter written before the fault). Window-start consult pinned by the corpus regime (BC-3.02.001 Inv 4, BC-6.03.004 D4-EX-1): every corpus case seeds `proc_start` or is `cache-003` (no probe on either side) — this case seeds `proc_start`, so the cached value short-circuits the consult and the cache content stays byte-pinned | edge-case |
| injected panic in a widget (Go unit test) | degraded 29 bytes, exit 0 | error |

Verified 2026-11-15 against CPython 3.11.7 (`LANG=en_US.UTF-8`, `DGX_SL_ROWS=1`, `DGX_SL_GIT=0`): rows 1-3 above.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-001 | For every input that makes `Render` return `errDegraded` or panic, `Main` writes exactly the 29 degraded bytes and returns 0 | unit/table test (go test; not fuzz — no Tier C fuzz VP exists yet for this property) |
| VP-003 | `Main` never returns non-zero for any stdin/argv routed to it — including the CP-X03 case where the degraded write itself fails (named exclusion `cp-x03`) | unit/table test (go test) |
| VP-012 | The named deviation this contract carries — exclusion id `cp-x03` (OD-136: degraded-line write failure still exits 0) — is covered by the exclusion-closure check: `TestParityExclusions_ClosedSet` validates the `cp-x03` entry and its riding table test `TestCPX03_WriteFailureExit0`, and the mutation test fails closed if that entry is dropped | property test (VP-012 `TestParityExclusions_ClosedSet` / `TestParityExclusions_MutationFailClosed`, go test) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008, DI-012 |
| Architecture Module | `internal/statusline` guard (`guard.go`, design §2.2) (BC-COMPONENT-MAP: internal/statusline/guard.go (29-byte degraded line, recover backstop) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`__main__` guard (SL:1238-1245); degraded colors RESET SL:127, GREY SL:131-132 |
| Legacy contract | BC-SL-001 (P3 broad sweep; refined P3r1; index P3r4 §7.3) |
| Decisions | D4 (byte parity), OD-102/OD-114 (D4-EX-3 replaces CP-X01/X02), OD-136 (CP-X03 → named exclusion `cp-x03`, exit 0), OD-112, OD-155 (supersedes OD-14 (a); `--subagent` valid in P1) |

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
- VP-012 — exclusion-closure cover for the named deviation `cp-x03`

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
constant `degradedLine` is assembled from built-in named constants, independent of the theme (OD-113; BC-2.02.001
inv 2), so it stays byte-identical (design IM-15).
