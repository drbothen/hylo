---
document_type: behavioral-contract
level: L3
version: "1.2.10"
status: draft
producer: product-owner
timestamp: 2026-11-18T06:25:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "6e8f049"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-076"
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: "0.1"
modified: ["1.2.1 2026-11-17: VP citation reconciliation — VP-005 stdout leg", "1.2.3 2026-11-18T02:00:00Z: pass-3 remediation (ADV-P3-B13/B10): vector table merged (blank line removed); ARCH-03 anchor normalized to #statusline-guard", "1.2.4 2026-11-18T12:00:00Z: pass-4 remediation (ADV-P4-B07): DI-012 cited for the carried closed-set ids", "1.2.5 2026-11-18: pass-5 residual sweep (ADV-P5-B14) — 1.2.4 entry re-dated ascending (its stamp predated 1.2.3); no behavioral change", "1.2.6 2026-11-19T04:00:00Z: pass-6 remediation (ADV-P6-B06 + OD-183 wording): new EC-007 pins raw encoded-surrogate bytes (ED A0 80) on stdin as invalid UTF-8 -> {} with an oracle-verified vector; PC2 adds the pyfmt code-point-iteration (never plain rune ranges) discipline for WTF-8 values", "1.2.7 2026-11-19T08:00:00Z: pass-8 remediation (ADV-P8-B04): OD-183 propagated — Description states UTF-8 stdio on every OS, the Windows oracle's `PYTHONIOENCODING=utf-8` variable and the stdio-encoding-only table test; new Inv 3; PC2 names the Windows-oracle variables; verification note qualifies the `LANG` pin as POSIX-leg (BC-1.02.004); Decisions row cites OD-183 and OD-190 (LF on every OS)", "1.2.8 2026-11-20T18:00:00Z: pass-10 remediation (ADV-P10-B01): Inv 3 rewritten per the BC-1.01.003 PC5 carve-out — the renderer itself emits no CR; input-derived text stays verbatim, so CR/LF bytes from reachable stdin inside row 1 are parity, not violations", "1.2.9 pass-12 remediation (ADV-P12-B02): Architecture Anchors re-anchored from #statusline-guard (target guard.go) to the input.go family anchor #input; no behavioral change; 2026-11-23T00:00:00Z", "1.2.10 pass-12 residual sweep (orchestrator pass-12 residual call 8): the lone-surrogate display-name vector restates its window-start pin per the corrected cache-003 design (every corpus case seeds proc_start or is cache-003, no probe on either side, no fake process table); no behavioral change; 2026-11-23T14:00:00Z"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.01.008: Strict UTF-8 stdio; invalid stdin UTF-8 renders from {}

> Byte notation: `\e` = ESC (0x1B); `\n` = LF. `\ud800` in a stdin column means the six-character JSON escape, not a
> raw byte.

## Description

The status line reads stdin and writes stdout as strict UTF-8, matching the production locale (owner ruling (a):
`LANG=en_US.UTF-8`, no UTF-8 mode, no surrogateescape). By OD-183 hylo reads and writes UTF-8 on every OS; the Windows
parity oracle gets exactly one extra variable, `PYTHONIOENCODING=utf-8` (stdio only; `PYTHONUTF8` stays forbidden),
and a table test shows that variable changes stdio encoding only (BC-6.01.002). By OD-190 hylo writes LF line endings
on every OS (UTF-8 + LF), and the Windows oracle's LF normalization is named beside `PYTHONIOENCODING=utf-8`, not
hidden in the shim. Invalid UTF-8 anywhere in stdin is a decode failure, so the
refresh renders from `{}` (BC-1.01.002). A rendered string that holds a lone surrogate (reachable only through a
JSON `\uXXXX` escape) cannot be encoded at output and degrades the refresh (CP-S17), after all cache writes.

## Preconditions

1. stdin bytes as delivered by Claude Code; configuration resolved.
2. Parity mode is the strict column of P3r1 §A9; the harness pins legacy to it (BC-6.01.002). On Windows the oracle
   runs with exactly one extra variable, `PYTHONIOENCODING=utf-8` (OD-183), plus the oracle's named LF normalization
   (OD-190); the `LANG=en_US.UTF-8` pin is a POSIX-leg locale detail and has no effect on Windows (BC-1.02.004).

## Postconditions

1. stdin containing any invalid UTF-8 sequence (e.g. `{"model":{"id":"A\xffB"}}` with raw byte 0xFF) -> render input
   `{}` -> `?` defaults; exit 0. The bytes are never echoed back.
2. A JSON escape decoding to a lone surrogate (U+D800..U+DFFF, any sub-range incl. U+DC80..U+DCFF) is accepted by
   the decoder and kept (WTF-8 in Go, design IM-01); Go decodes and iterates these WTF-8 values by code point
   through pyfmt, never plain rune ranges (OD-183 stdio leg; design IM-01).
3. If such a string reaches stdout as a **str** (model display name or id, project label, or a cached git `branch` —
   a JSON `\udXXX` escape in `statusline-git-<key>.json` is returned as a str by the loader and rendered verbatim,
   SL:412-413), the refresh degrades: stdout is the 29-byte line (BC-1.01.001), exit 0, and every cache write of the
   refresh has already happened (the fault is at the final print, step 8 of BC-1.01.009). The cached-`branch` clause
   is a foreign-cache shape (Go authors well-formed caches; ruling Q-b): it carries exclusion id **OD-160**, so
   vectors relying on a hand-edited cache are Go table tests, not byte-parity obligations.
4. A lone surrogate that is rendered through Python `repr` of a container (e.g. a list display name) is escaped as
   text (`'\ud800'`) and does not degrade (BC-1.02 model-label contract).
5. Valid output is encoded UTF-8 with LF line ends; Go checks `pyfmt.HasSurrogate` over the output strings before
   the single write (design IM-22).

## Invariants

1. No raw invalid byte is ever written to stdout.
2. The surrogateescape behavior (`PYTHONUTF8=1` or C locale, which echoes `0xFF` back) is **not** the parity mode
   (CONTRA-3 resolved by owner ruling (a)).
3. OD-183's `PYTHONIOENCODING=utf-8` changes stdio encoding only — a table test (BC-6.01.002) shows it never alters
   the decode success/failure classes pinned in this contract (invalid stdin still fails, WTF-8 escapes still kept,
   surrogates still degrade at output). By OD-190 hylo writes LF on every OS; the renderer itself emits no CR —
   no CRLF appears in a row the renderer builds (BC-1.01.003 PC5 carve-out: input-derived text is emitted
   verbatim, so a reachable stdin `display_name` of `"a\r\nb"` prints the bytes 0D 0A inside row 1 at the
   single print, SL:442-443, 1234; a Go port must not strip or translate CR in input-derived text).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Raw `0xFF` inside a string value | `{}` -> defaults |
| EC-002 | UTF-8 BOM before `{` | `{}` (BC-1.01.002 EC-003) |
| EC-003 | `\ud800` escape in `model.display_name` | degraded 29 bytes |
| EC-004 | `\udcff` escape in `model.display_name` | degraded 29 bytes (strict mode) |
| EC-005 | `\ud800` escape in a key or field that is never rendered | no effect on output |
| EC-006 | Valid astral characters (e.g. emoji) in display name | rendered as UTF-8 bytes |
| EC-007 | Raw encoded-surrogate bytes on stdin — a UTF-8 sequence encoding a surrogate code point, e.g. `ED A0 80` (U+D800) inside a string value, structurally valid JSON | invalid UTF-8: CPython's strict text-mode decoder rejects it (`UnicodeDecodeError`; oracle-verified 2026-11-18) → `{}` -> defaults (45-byte line). Contrast with the same code point arriving as the six-ASCII-character JSON `\ud800` escape, which parses and is kept as WTF-8 (EC-003/PC2) |

## Canonical Test Vectors

Config: defaults, `HYLO_STATUSLINE_ROWS=1`, git disabled, COLUMNS unset, empty cache.

| Input (stdin bytes) | Expected Output | Category |
|-------|----------------|----------|
| `{"model":{"display_name":"Opus 5.5"}}` | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97mOpus 5.5\e[0m\n` | happy-path |
| `{"model":{"id":"A` `FF` `B"}}` | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97m?\e[0m\n` (45 bytes) | error |
| `{"model":{"id":"A` `ED A0 80` `B"}}` (raw encoded-surrogate bytes, EC-007) | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97m?\e[0m\n` (45 bytes), exit 0 | error |
| `{"model":{"display_name":"\ud800"}}` | `\e[90mstatusline degraded\e[0m\n` (29 bytes), exit 0 | edge-case |
| `{"session_id":"s1","model":{"display_name":"\ud800"},"rate_limits":{"five_hour":{"used_percentage":1,"resets_at":9999999999}}}` | degraded 29 bytes; `statusline-s1.json` holds exactly the seeded `proc_start` plus `rl`, `rl_ts` (`rl`, `rl_ts` written before the fault; corpus regime, BC-3.02.001 Inv 4: every corpus case seeds `proc_start` or is `cache-003` — no probe on either side — so the cached value short-circuits the window-start consult) | edge-case |
| `{"model":{"display_name":["\ud800"]}}` (list -> `repr`) | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97m['\ud800']\e[0m\n` (the six ASCII characters `\ud800` inside quotes; no degrade) | edge-case |
| `{"x\ud800":1,"model":{"display_name":"Z"}}` (surrogate in an unrendered key) | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97mZ\e[0m\n` | edge-case |

All rows verified 2026-11-15 on CPython 3.11.7 (`LANG=en_US.UTF-8`, a POSIX-leg pin — on Windows the oracle's codec
is fixed by `PYTHONIOENCODING=utf-8` per OD-183, since `LANG` has no effect there), plus EC-004 (`\udcff` -> degraded).
Contrast (not parity): the invalid-UTF-8 input under `PYTHONUTF8=1` printed `...\e[97mA` `FF` `B\e[0m\n`.

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-005 (stdout codec leg) | stdout is always valid UTF-8 — VP-005's symmetric stdout half ("stdout is valid UTF-8" for every render state) | fuzz |
| VP-005 | Any invalid-UTF-8 stdin yields the same output as `{}` with the same caches | go test -fuzz |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008, DI-012 |
| Architecture Module | `internal/statusline` input + guard (`input.go`, `guard.go`) (BC-COMPONENT-MAP: internal/statusline/input.go (strict UTF-8 stdio) — ARCH-03) |
| Stories | TBD (filled by story-writer) |
| Source | legacy/dgx_statusline.py:`main` (SL:1201-1206, 1234) |
| Legacy contract | BC-SL-076 (new P3r1 §A9; strict mode ruled P3r2 §0 (a); index P3r4 §7.3); crash path CP-S17 |
| Decisions | owner ruling (a) strict stdio; D4; OD-104/OD-109 (oracle and env from scratch); OD-183 (UTF-8 stdio on every OS; Windows oracle gets `PYTHONIOENCODING=utf-8`; table test stdio-encoding-only); OD-190 (LF on every OS; Windows-oracle LF normalization named) |

## Related BCs (Recommended)

- BC-1.01.002 — composes with (decode failure -> `{}`)
- BC-1.01.001 — composes with (CP-S17 degrades via the guard)
- BC-1.01.009 — related to (fault after all writes)
- BC-5.03.001 — depends on (`pyfmt.HasSurrogate`)
- BC-6.01.002 — related to (harness locale pin)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#input` — internal/statusline/input.go (strict UTF-8 stdio; CP-S17 ends in the guard) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — status line frame (design step S2)

## VP Anchors (Recommended)

- VP-005 — decode-failure equivalence and the stdout-always-valid-UTF-8 property (VP-005 1.1 spans both
  stdio halves; resolves pass-1 finding ADV-P1-B11)

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (SL:1202, 1234) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **type constraint**: strict text-mode stdio under the production locale
- **assertion**: pinned runs (P3r1 §A9; re-run 2026-11-15)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads stdin, writes stdout |
| **Global state access** | locale (legacy only) |
| **Deterministic** | yes (given the pinned locale) |
| **Thread safety** | n.a. |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Go reads raw bytes and validates UTF-8 in the decoder (no locale dependence); the surrogate check before the write
replaces Python's encode error.
