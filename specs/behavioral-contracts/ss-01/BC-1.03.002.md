---
document_type: behavioral-contract
level: L3
version: "1.3.4"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:45:10Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, domain-spec/capabilities.md, domain-spec/invariants.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts-r4.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "05d958d"
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
modified:
  - "1.2.1 2026-11-17: EC-008/009 float+negative cached-size classification (OD-160); dropped uncited DI-012 (ADV-P2-C09/C11)"
  - "1.2.2 2026-11-17: pass-3 remediation (ADV-P3-C13/C18): float cached size classified per path (equality path never seeks), DI-012 cited for the OD-160 legs"
  - "1.2.3 2026-11-18T23:45:00Z: pass-6 remediation (ADV-P6-C13) — EC-007 carves JSON bool `size` out of the crash class: Python bool is an int (`size == 1` compare, `seek(true)` = `seek(1)`, oracle-verified 2026-11-18); the crash class keeps string/array/object/null"
  - "1.2.4 2026-11-19T23:59:00Z: pass-8 remediation (ADV-P8-C03) — VP table and VP Anchors gain the OD-160 closure row (VP-012) mirroring sibling BC-1.03.015's OD-161 row"
  - "1.3.0 2026-11-20T18:00:00Z: pass-9 remediation (ADV-P9-C09) — EC-008 gains the NaN cached-size leg: NaN fails all comparisons, never resets, and raises TypeError at fh.seek(nan) (SL:1043) on either grow or shrink (OD-160 class; json.load accepts the token per BC-1.06.001 EC-002)"
  - "1.3.1 2026-11-24T12:00:00Z: pass-13 remediation (ADV-P13-C05, BC half of the pass-13 call 1) — EC-007 names the string-size site (comparison/seek SL:1033); new EC-010 (mix-cache top level not an object, SL:1019) and EC-011 (non-iterable cached ids, list(...) split SL:1033) name the remaining mix-cache foreign shapes for the error-taxonomy register; CP-C ids are minted by error-taxonomy (residual sweep), not here"
  - "1.3.2 2026-11-24T18:00:00Z: pass-13 residual (orchestrator residual sweep, CP-C register alignment): EC-007 cites CP-C26, EC-010 cites CP-C25 and EC-011 cites CP-C27 beside the legacy sites, minted by error-taxonomy 1.20; no behavioral change"
  - "1.3.3 2026-11-26T13:00:00Z: pass-14 remediation (ADV-P14-C04) — EC-007 names both string-size raise sites (measured with the pinned oracle interpreter, -I, isolated temp HOME/cwd): with a post-launch key (tin, c_wr, mixv6) missing the reset loop's off > 0 probe raises TypeError first (SL:1027), with all three present the TypeError moves to the size < off comparison (SL:1033); both paths degrade identically; the misplaced 1.3.2 stamp re-dated 2026-11-24T18:00:00Z to restore non-decreasing order (E2 gate, pass-14 C2-08 class)"
  - "1.3.4 2026-11-26T15:00:00Z: pass-14 residual sweep (OD-160 owner id-range alignment): EC-009 states the measured seek nuance (fitting negative int → OSError; giant int → ValueError, CP-C51) and EC-007 gains the CP-C51 giant-size leg; no behavioral change"
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
| EC-007 | Cached `size` is a non-number (foreign cache) | foreign-cache crash class CP-C (ruling b): out of byte-parity scope; not specified here. ADV-P6-C13: a JSON bool `size` is **not** in this class — Python bool is an int (`isinstance(true, int)`), so `off = true` compares (`size == 1`) and `fh.seek(true)` = `seek(1)` cleanly; bool behaves as the integer it denotes (OD-160 table test). String `size` (call-1 nameable site, ADV-P13-C05): two raise sites, both `TypeError` (crash id **CP-C26**), measured with the pinned oracle interpreter 2026-11-18 (-I, isolated temp HOME/cwd) — (a) a post-launch key (`tin`, `c_wr`, `mixv6`) missing lets the reset loop's `off > 0` probe raise first (SL:1027, `'>'` between str and int); (b) all three keys present move the raise to the `size < off` comparison (SL:1033, `'<'` between int and str; the seek is never reached) — legacy degrades the refresh either way (DI-008 ladder, exit 0, no save); hylo degrades identically (Go table test, same outcome class); a negative exact-GIANT `size` (both signs — the `size < off` and `==` comparisons stay exact and pinned non-raising) raises ValueError at `fh.seek(off)` instead (SL:1046, \"cannot fit 'int' into an offset-sized integer\", measured pass-14; crash id **CP-C51** — a fitting negative int is EC-009's OSError case) |
| EC-010 | Mix cache top level is not an object (e.g. `[]`, `"x"`, `5`) (foreign cache; ADV-P13-C05) | the first `.get` consult raises `AttributeError`/`TypeError` (SL:1019; crash id **CP-C25**) — legacy degrades the refresh (DI-008 ladder, exit 0, no save); hylo degrades identically (Go table test, CP-C family, OD-160; trigger id minted in error-taxonomy — BC-1.06.001 EC-001 is the loader-side citation) |
| EC-011 | Cached `ids` is not iterable (e.g. an int) (foreign cache; ADV-P13-C05) | the `list(...)` split raises `TypeError` (SL:1033; crash id **CP-C27**) — legacy degrades the refresh (DI-008 ladder, exit 0, no save); iterable wrong-element shapes and write-side dispositions stay with BC-1.03.005 PC5 (OD-160 legs). hylo degrades identically (Go table test, CP-C family, OD-160) |
| EC-008 | Cached `size` is a float (foreign cache) | path-dependent (SL:1027-1043): a float equal to the file size (cached `39.0`, file 39 B) hits `size == off` and returns the cached values with **no seek and no crash** (39 == 39.0, oracle-verified); a file that **grew** (`size > off`) reaches `fh.seek(off)` and the float raises `TypeError` (oracle-verified), uncaught by the OSError-only handler (SL:1053) → legacy degraded refresh, no save; a file that **shrank** (`size < off`) or a missing key with `off > 0` takes the reset path (postcondition 3) and re-parses from 0 with no crash. foreign-cache class (ruling b, exclusion id `OD-160`); hylo replicates the classification and degrades only on the grow path, out of byte-parity scope. Outside that path split: a cached `size` of NaN — which `json.load` accepts (BC-1.06.001 EC-002) — fails all of `<`, `==` and `>`, so it never takes the reset or no-new-bytes path and reaches `fh.seek(nan)` (SL:1043), raising `TypeError` whether the file grew or shrank; the grow-path-only wording does not hold for NaN (OD-160 class) |
| EC-009 | Cached `size` is negative (foreign cache) | `size < off` false, `seek(negative)` raises `OSError` (oracle-verified), caught at SL:1053 → return without write; measured seek nuance (pass-14 matrix): a FITTING negative int seeks to OSError, while a giant negative int (magnitude >= 2**1024 - 2**970, unrepresentable in an offset-sized integer) raises ValueError instead (\"cannot fit 'int' into an offset-sized integer\", **CP-C51**); nothing is saved, so the parse makes no progress on every later refresh; foreign-cache class (ruling b, exclusion id `OD-160`) |

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
| VP-029 | `need_reset ⇔ off > 0 ∧ ∃k∈{tin,c_wr,mixv6}: k ∉ cache` | Go property test (testing/quick) over random key subsets and offsets |
| VP-029 (no dedicated write-scope VP yet) | `size == off` after the reset step ⇒ zero Save calls | table test with fake `CacheStore` |
| VP-029, VP-019 | Written cache key order is the fixed 16-key sequence (byte equality of the swapped caches) | golden byte comparison |
| VP-012 | The named deviation this contract carries — exclusion id `OD-160` (foreign-cache crash class; EC-008 float and EC-009 negative cached size) — is covered by the exclusion-closure check over the `OD-160` entry and its riding table tests (mirrors sibling BC-1.03.015's OD-161 row; ADV-P8-C03) | property test (VP-012 `TestParityExclusions_ClosedSet` / `TestParityExclusions_MutationFailClosed`, go test) |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-007, DI-008; DI-012 (the OD-160 foreign-cache legs are named, tested deviations) |
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

- `architecture/ARCH-03-statusline.md#interfaces-design-doc-22-reused-as-the-contract` — internal/statusline/mixcache.go (name, mixv6 reset) (`internal/statusline/mixcache.go`) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

S-TBD — transcript parser and mix cache

## VP Anchors (Recommended)

- VP-029, VP-019 — reset predicate (family table); key order → VP-019 swap parity
- VP-012 — exclusion-closure cover for the named deviation `OD-160` (EC-008/EC-009 legs)

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
