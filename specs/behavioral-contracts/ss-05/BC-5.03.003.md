---
document_type: behavioral-contract
level: L3
version: "1.2"
status: draft
producer: product-owner
timestamp: 2026-11-17T11:45:00Z
phase: 1a
inputs: [domain-spec/L2-INDEX.md, behavioral-contracts/BC-ALLOCATION.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "7f728f2"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (greenfield helper; reproduces re.sub on the sid (SL:1017) and str.encode('utf-8','replace') (SL:405) of legacy/dgx_statusline.py)"
subsystem: "SS-05"
capability: "CAP-009"
legacy_id: "new"
parity_class: n.a.
confidence: "—"
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

# Behavioral Contract BC-5.03.003: SubNonWord per code point before truncation; EncodeUTF8Replace lone surrogate → ?

## Description

Two cache-file-name helpers whose output is part of the shared file-name format with legacy. `SubNonWord(s, '_')`
reproduces `re.sub(r"[^A-Za-z0-9_-]", "_", sid)`, replacing **each code point** outside the ASCII class (then the
caller truncates to 40 code points, SL:1017). `EncodeUTF8Replace(s)` reproduces `s.encode("utf-8", "replace")`,
writing `?` for each surrogate code point, before the git-cache key is hashed (SL:405, design IM-20).

## Preconditions

1. `s` is a Value string (code points, surrogates allowed, BC-5.02.004).

## Postconditions

1. `SubNonWord(s, '_')` returns `s` with every code point not in `A-Z`, `a-z`, `0-9`, `_`, `-` replaced by one `_`
   (one per code point, so `😀` → `_`, a lone surrogate → `_`, `é` → `_`). The class is ASCII-only.
2. The mix-cache name uses `Truncate(SubNonWord(sid, '_'), 40)` — substitution **before** truncation, both per code
   point (BC-1.03.013 owns the file name).
3. `EncodeUTF8Replace(s)` returns the UTF-8 bytes of `s` with each surrogate code point replaced by the single byte
   `?` (0x3F); all other code points encode normally.
4. The git-cache key is `hex(sha1(EncodeUTF8Replace(directory)))[:16]` (`crypto/sha1`, with
   `//nolint:gosec // non-cryptographic cache key, file-name format shared with legacy (T-062)`).

## Invariants

1. The 40-code-point cut (T-061) and the 16-hex sha1 prefix (T-062) are named constants with a "why not config"
   comment: they are file-name formats shared with legacy (design §2.4).
2. Both helpers are pure.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `SubNonWord("\ud800x")` | `"_x"` |
| EC-002 | `SubNonWord("a" × 45)` then truncate 40 | `"a" × 40` |
| EC-003 | Raw surrogate pair (two code points) in `EncodeUTF8Replace` | `"??"` (one `?` per code point) |
| EC-004 | `EncodeUTF8Replace("café😀")` (no surrogates) | `63 61 66 c3 a9 f0 9f 98 80` |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `Truncate(SubNonWord("é/😀 ab-c_D.1"), 40)` | `"____ab-c_D_1"` | happy-path |
| `SubNonWord("session-01_ok")` | unchanged | happy-path |
| `EncodeUTF8Replace("/tmp/\ud800x")` | bytes `/tmp/?x` | edge-case |
| git key for directory `"/tmp/\ud800x"` | `29de25ac9bde9ad0` | edge-case |
| `SubNonWord("")` | `""` | error (empty input stays empty; the caller substitutes `nosession` for a falsy sid, SL:1016) |

Verified 2026-11-15 against CPython 3.11.7 (`re.sub`, slicing, `str.encode("utf-8", "replace")`, `hashlib.sha1`).

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-025 | `Len(SubNonWord(s)) == Len(s)` and the output is ASCII | Go property test (testing/quick) |
| VP-025 | `EncodeUTF8Replace` equals the oracle on fuzzed strings with surrogates | fuzz + oracle |

## Traceability

| Field | Value |
|-------|-------|
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/pyfmt/str.go` (design §2.6) (BC-COMPONENT-MAP: internal/pyfmt/str.go (SubNonWord, EncodeUTF8Replace) — ARCH-06) |
| Stories | TBD (filled by story-writer) |
| Source | New contract. OD-103; design IM-11 (per-code-point substitution), IM-20 (sha1 key); pitfalls PR-11, PR-13. Legacy uses served: SL:1016-1017 (mix-cache name), SL:405 (git-cache key); OD-03 (raw sid in the session cache, sanitized mix cache) |

## Related BCs (Recommended)

- BC-1.03.013 — consumed by (mix-cache sid sanitized per code point)
- BC-1.02.005 — consumed by (git cache key)
- BC-5.03.001 — depends on (`Truncate`)

## Architecture Anchors (Recommended)

- `architecture/ARCH-06-pyfmt.md#pyfmt-str` — internal/pyfmt/str.go (SubNonWord, EncodeUTF8Replace) (file-name helpers) (BC-COMPONENT-MAP: ARCH-06 (ARCH-06-pyfmt.md))

## Story Anchor (Recommended)

TBD — pyfmt str (design step S1)

## VP Anchors (Recommended)

- VP-025 — substitution preserves code-point count

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | none |
| **Global state access** | none |
| **Deterministic** | yes |
| **Thread safety** | safe for concurrent use (stateless functions) |
| **Overall classification** | pure core |

Owning component `py/str.go (SubNonWord, EncodeUTF8Replace)` (BC-COMPONENT-MAP: py/str.go (SubNonWord, EncodeUTF8Replace) - ARCH-06); the ARCH-00 package table classifies `internal/pyfmt` pure core - bytes/values in, values out, no I/O, clock never read.
