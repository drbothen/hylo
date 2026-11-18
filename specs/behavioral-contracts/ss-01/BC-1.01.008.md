---
document_type: behavioral-contract
level: L3
version: "1.2.5"
status: draft
producer: product-owner
timestamp: 2026-11-18T06:25:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r2.md, semport/hylo-legacy/statusline-target-design.md]
input-hash: "3ee40d0"
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
modified: ["1.2.1 2026-11-17: VP citation reconciliation — VP-005 stdout leg", "1.2.3 2026-11-18T02:00:00Z: pass-3 remediation (ADV-P3-B13/B10): vector table merged (blank line removed); ARCH-03 anchor normalized to #statusline-guard", "1.2.4 2026-11-18T12:00:00Z: pass-4 remediation (ADV-P4-B07): DI-012 cited for the carried closed-set ids", "1.2.5 2026-11-18: pass-5 residual sweep (ADV-P5-B14) — 1.2.4 entry re-dated ascending (its stamp predated 1.2.3); no behavioral change"]
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
`LANG=en_US.UTF-8`, no UTF-8 mode, no surrogateescape). Invalid UTF-8 anywhere in stdin is a decode failure, so the
refresh renders from `{}` (BC-1.01.002). A rendered string that holds a lone surrogate (reachable only through a
JSON `\uXXXX` escape) cannot be encoded at output and degrades the refresh (CP-S17), after all cache writes.

## Preconditions

1. stdin bytes as delivered by Claude Code; configuration resolved.
2. Parity mode is the strict column of P3r1 §A9; the harness pins legacy to it (BC-6.01.002).

## Postconditions

1. stdin containing any invalid UTF-8 sequence (e.g. `{"model":{"id":"A\xffB"}}` with raw byte 0xFF) -> render input
   `{}` -> `?` defaults; exit 0. The bytes are never echoed back.
2. A JSON escape decoding to a lone surrogate (U+D800..U+DFFF, any sub-range incl. U+DC80..U+DCFF) is accepted by
   the decoder and kept (WTF-8 in Go, design IM-01).
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

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Raw `0xFF` inside a string value | `{}` -> defaults |
| EC-002 | UTF-8 BOM before `{` | `{}` (BC-1.01.002 EC-003) |
| EC-003 | `\ud800` escape in `model.display_name` | degraded 29 bytes |
| EC-004 | `\udcff` escape in `model.display_name` | degraded 29 bytes (strict mode) |
| EC-005 | `\ud800` escape in a key or field that is never rendered | no effect on output |
| EC-006 | Valid astral characters (e.g. emoji) in display name | rendered as UTF-8 bytes |

## Canonical Test Vectors

Config: defaults, `HYLO_STATUSLINE_ROWS=1`, git disabled, COLUMNS unset, empty cache.

| Input (stdin bytes) | Expected Output | Category |
|-------|----------------|----------|
| `{"model":{"display_name":"Opus 5.5"}}` | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97mOpus 5.5\e[0m\n` | happy-path |
| `{"model":{"id":"A` `FF` `B"}}` | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97m?\e[0m\n` (45 bytes) | error |
| `{"model":{"display_name":"\ud800"}}` | `\e[90mstatusline degraded\e[0m\n` (29 bytes), exit 0 | edge-case |
| `{"session_id":"s1","model":{"display_name":"\ud800"},"rate_limits":{"five_hour":{"used_percentage":1,"resets_at":9999999999}}}` | degraded 29 bytes; `statusline-s1.json` written with exactly `rl`, `rl_ts` before the fault (window-start probe pinned: harness fake `ps` with no `claude` ancestor, BC-3.02.002 case I4 — no `proc_start` key) | edge-case |
| `{"model":{"display_name":["\ud800"]}}` (list -> `repr`) | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97m['\ud800']\e[0m\n` (the six ASCII characters `\ud800` inside quotes; no degrade) | edge-case |
| `{"x\ud800":1,"model":{"display_name":"Z"}}` (surrogate in an unrendered key) | `\e[100;37;1m ◨ ? \e[0m\e[2m · \e[0m\e[97mZ\e[0m\n` | edge-case |

All rows verified 2026-11-15 on CPython 3.11.7 (`LANG=en_US.UTF-8`), plus EC-004 (`\udcff` -> degraded).
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
| Decisions | owner ruling (a) strict stdio; D4; OD-104/OD-109 (oracle and env from scratch) |

## Related BCs (Recommended)

- BC-1.01.002 — composes with (decode failure -> `{}`)
- BC-1.01.001 — composes with (CP-S17 degrades via the guard)
- BC-1.01.009 — related to (fault after all writes)
- BC-5.03.001 — depends on (`pyfmt.HasSurrogate`)
- BC-6.01.002 — related to (harness locale pin)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#statusline-guard` — internal/statusline/input.go (strict UTF-8 stdio; CP-S17 ends in the guard) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

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
