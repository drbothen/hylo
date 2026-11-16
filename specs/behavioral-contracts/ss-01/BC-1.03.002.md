---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, ../semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, ../semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "0000000"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:_mix_counts (SL:1016-1040)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: "BC-SL-031"
parity_class: "byte-exact"
confidence: "H"
priority: P0
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

# Behavioral Contract BC-1.03.002: Mix cache name and mixv6 reset rules

## Description

Once a transcript file exists, the parser loads its per-session mix cache `statusline-mix-<sid'>.json` from the
cache directory and decides between three paths before reading any transcript byte: **full reset** (re-parse
from byte 0 with all accumulators and the id memory cleared), **no new bytes** (return the cached values without
writing), or **incremental parse** from the cached offset. The reset decision is evaluated before the
no-new-bytes test.

## Preconditions

1. BC-1.03.001's checks passed: `transcript_path` names a regular file of size `size` (bytes).
2. `sid = d.session_id` if truthy, else the literal `"nosession"`; `sid'` is the sanitized, truncated form of
   BC-1.03.013.
3. The mix cache is loaded with never-raise semantics (BC-1.06.001): an unreadable, missing or non-JSON file
   loads as an empty object.
4. Cached fields are read with defaults: `size`→0 (the offset `off`), `res`,`conv`,`think`,`tin`,`tout`,`c_wr`,
   `c_rd`,`c_in`,`rb`→0; `lr`,`lu`,`cur`,`pp`→null; `ids`→`[]`. Values are taken **as stored** (any JSON type),
   via the ordered `pyfmt.Value` (design IM-01/IM-03).

## Postconditions

1. **File name.** The cache path is `<cache_dir>/statusline-mix-<sid'>.json`. `cache_dir` is `paths.cache_dir`
   (OD-101: hylo's own location from P1; the harness compares by file name, BC-6.03.002). The name format is a
   named constant, not config (design §2.4, T-061).
2. **Reset condition.** `need_reset` is true iff `off > 0` and at least one of the keys `tin`, `c_wr`, `mixv6`
   is absent from the cache object. A shrink is `size < off`.
3. **Full reset** (when `need_reset` or `size < off`): `off`, `res`, `conv`, `think`, `tin`, `tout`, `c_wr`,
   `c_rd`, `c_in`, `rb` become integer 0; `lr`, `lu`, `cur`, `pp` become null; the id memory (`recent_ids`, and
   the set built from it) becomes empty. The parse then proceeds from byte 0 (BC-1.03.003).
4. **No new bytes** (evaluated after step 3, so a reset with `size == 0` lands here): if `size == off`, the parser
   returns the (possibly just-reset) values and **does not write** the mix cache.
5. Otherwise the parse proceeds incrementally from `off` with the cached accumulators and id memory.
6. Every completed parse writes the cache with key order exactly `size, res, conv, think, tin, tout, c_wr, c_rd,
   mixv6, c_in, rb, pp, ids, lr, lu, cur`, `mixv6` = integer 1, `ids` = last N of `recent_ids` (N =
   `statusline.transcript.dedup_memory`, default 256; BC-1.03.005), serialized with Python `json.dump` defaults
   (`", "` / `": "`, `ensure_ascii`, float repr, no trailing newline; design IM-03).

## Invariants

1. A missing key with `off == 0` never triggers a reset; the cached values of present keys are carried.
2. The reset decision never reads the transcript.
3. `mixv6` is a format marker: its presence, not its value, is tested.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Cache lacks `mixv6`, `size` equals the file size (> 0) | reset, then full re-parse from 0 and a write (reset precedes the size test) |
| EC-002 | Cache has `mixv6`, `tin`, `c_wr`, `size` equals file size | no read, no write; cached tuple returned verbatim (even `conv: 999`) |
| EC-003 | Cache `{"size": 0, "conv": 999}` (no `tin`/`c_wr`/`mixv6`, off 0) | **no** reset; `conv` carried: parsing a 10-char line gives `conv` 1009 |
| EC-004 | File truncated below the cached offset | reset including id memory; only post-shrink content counts |
| EC-005 | Cache file is not JSON / unreadable | loads as `{}` → off 0 → behaves as first run |
| EC-006 | `size == off == 0` (empty transcript, no cache) | zeros returned, no cache file created |
| EC-007 | Cached `size` is a non-number (foreign cache) | foreign-cache crash class CP-C (ruling b): out of byte-parity scope; not specified here |

## Canonical Test Vectors

Line `L1` = `{"message": {"content": "aaaaaaaaaa"}}` + LF (39 bytes, conv 10). Re-pinned 2026-11-15 with the
legacy oracle (CPython 3.11).

| Input | Expected Output | Category |
|-------|----------------|----------|
| transcript = `L1`, no cache, sid `eq`; refresh twice | refresh 1 writes `statusline-mix-eq.json` = `{"size": 39, "res": 0, "conv": 10, "think": 0, "tin": 0, "tout": 0, "c_wr": 0, "c_rd": 0, "mixv6": 1, "c_in": 0, "rb": 0, "pp": null, "ids": [], "lr": null, "lu": null, "cur": null}`; refresh 2: no write, same bytes | happy-path |
| transcript = `L1`×3 (117 B) parsed; then file rewritten as `L1` (39 B) | after refresh 2 the cache is exactly the refresh-1 bytes of the row above (size 39, conv 10) | edge-case |
| transcript = `L1`; seed cache `{"size": 39, "res": 0, "conv": 999, "think": 0, "tin": 5, "tout": 0, "c_wr": 0, "c_rd": 0, "c_in": 0, "rb": 0, "pp": null, "ids": ["zz"], "lr": null, "lu": null, "cur": null}` (no `mixv6`) | reset → cache = size 39, conv 10, tin 0, `ids []` (bytes as row 1) | edge-case |
| same seed but with `"mixv6": 1` after `c_rd` | no write; parser returns `conv` 999, `tin` 5 | edge-case |
| transcript = `L1`; seed `{"size": 0, "conv": 999}` | cache written with `"conv": 1009`, rest as row 1 | edge-case |
| seed is the bytes `not json` | behaves as row 1 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | `need_reset ⇔ off > 0 ∧ ∃k∈{tin,c_wr,mixv6}: k ∉ cache` | proptest over random key subsets and offsets |
| VP-TBD | `size == off` after the reset step ⇒ zero Save calls | table test with fake `CacheStore` |
| VP-TBD | Written cache key order is the fixed 16-key sequence | golden byte comparison |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007, DI-008, DI-012 |
| Source | legacy/dgx_statusline.py:_mix_counts (SL:1016-1040), write at SL:1150-1153 |
| Legacy contract | BC-SL-031 (pass-3 base; confirmed pass-3 r1: reset precedes the size test, reset clears id memory) |
| Parity class | byte-exact (mix cache compared by name, ruling b) |
| Decisions | OD-101 (cache dir), OD-03 (sanitized mix-cache name kept) |
| Architecture Module | `internal/statusline/mixcache.go` (design §2.2) |
| Stories | S-TBD |

## Related BCs (Recommended)

- BC-1.03.013 — composes with: the sanitized `sid'` in the file name
- BC-1.03.003 — depends on this BC: the read step starts at the offset chosen here
- BC-1.03.005 — composes with: id memory cleared on reset, trimmed on write
- BC-1.03.020 — related to: the OD-32 reader rule applied to a loaded `cur`
- BC-1.06.001 — depends on: never-raise load/save
- BC-3.01.001 — depends on: per-OS cache directory

## Architecture Anchors (Recommended)

- `architecture/TBD.md#mix-cache` — `internal/statusline/mixcache.go` (filled by architect)

## Story Anchor (Recommended)

S-TBD — transcript parser and mix cache

## VP Anchors (Recommended)

- VP-TBD — reset predicate; no write on `size == off`

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`_mix_counts`, SL:1016-1040, 1150-1153) |
| **Confidence** | high |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: reset loop SL:1026-1028; `size < off` SL:1033, 1035; `size == off` SL:1039-1040
- **documentation**: comment SL:1026-1028 names the post-launch fields that force a re-parse

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads + writes (mix cache) |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | unknown |
| **Overall classification** | mixed |

#### Refactoring Notes

Split into a pure `decideStart(cache Value, size int64) (state, path)` returning reset / no-new-bytes / incremental,
plus the `CacheStore` load/save shell. The cache must stay a `pyfmt.Value` (not a Go struct) so foreign values
round-trip verbatim (design IM-03).
