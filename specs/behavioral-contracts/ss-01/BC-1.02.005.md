---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T18:00:00Z
phase: 1a
inputs: [prd.md, behavioral-contracts/BC-ALLOCATION.md, domain-spec/L2-INDEX.md, semport/hylo-legacy/hylo-legacy-pass-3-behavioral-contracts.md, semport/hylo-legacy/hylo-legacy-pass-3-deep-behavioral-contracts.md, semport/hylo-legacy/statusline-target-design.md, owner-decisions-log-2026-11-14.md]
input-hash: "5245403"
traces_to: domain-spec/L2-INDEX.md
origin: brownfield
extracted_from: "legacy/dgx_statusline.py:git_segment (SL:399-413)"
subsystem: "SS-01"
capability: "CAP-009"
legacy_id: BC-SL-010
parity_class: byte-exact
confidence: H
lifecycle_status: active
introduced: v0.1.0
modified: []
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-1.02.005: Branch segment cached with a 5 s TTL

## Description

The branch segment shows `⎇ <branch>` in grey between the model label and the project
label. The branch (BC-1.02.004) is cached per project directory in
`statusline-git-<key>.json`, where `<key>` is the first 16 hex digits of SHA-1 over the
raw directory string; it is recomputed only when the cache is older than the git TTL
(strictly greater than 5 s) or lacks a `branch` key. The segment is omitted when git is
disabled or the branch is empty.

Notation: `\e` is the byte 0x1B; `T` = the injected clock (`HYLO_TEST_NOW` /
`Env.Now`), `T = 1800000000.0` in the vectors.

## Preconditions

1. `proj_dir` is a non-empty string (BC-1.02.003); otherwise this behavior is not invoked.
2. `statusline.git.enabled` (bool, default `true`) and `statusline.git.ttl_s` (seconds,
   default `5.0`) are resolved (BC-2.01.001).
3. The cache directory is hylo's per-OS cache dir `paths.cache_dir` (OD-101,
   BC-3.01.001) — not the legacy `~/.cache/dgx-llm`; the parity harness compares cache
   files by file name (BC-6.03.002).
4. `now` is the render's single clock read (design IM-14).

## Postconditions

1. If git is disabled → no segment; no cache read or write; no filesystem walk.
2. `key = hex(sha1(EncodeUTF8Replace(proj_dir)))[:16]` (lone surrogates encoded as `?`,
   BC-5.03.003); path = `<cache dir>/statusline-git-<key>.json`.
3. `c` = the decoded cache file; a missing, unreadable or non-JSON file yields `{}`
   (BC-1.06.001).
4. If `now - c.ts > ttl_s` (missing `ts` counts as `0`) **or** `c` has no `branch` key →
   `c = {"ts": now, "branch": git_branch(proj_dir)}` and the cache is saved atomically
   (temp file + rename; save failures ignored). The written bytes are Python
   `json.dump` defaults, e.g. `{"ts": 1800000000.0, "branch": "main"}` (BC-5.02.001).
5. `b = c.branch` (default `""`). If `b` is truthy → segment `\e[90m⎇ ` + str(b) +
   `\e[0m` (Python `str()` for a non-string cached value); else no segment.
6. When emitted, the segment is placed after the model label and before the project
   label.

## Invariants

1. At most one filesystem walk per render, and none while the cache is fresh.
2. The cache key uses the raw directory string (`/x/p` and `/x/p/` are different
   entries); it is a non-cryptographic file-name format shared with legacy (named constant
   T-062, not config).
3. TTL comparison is strict `>`: an entry exactly `ttl_s` old is still fresh.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | cache age exactly 5.0 s | cache used (no recompute) |
| EC-002 | cache age 5.001 s and HEAD changed | recompute; new branch shown; cache rewritten with the new `ts` |
| EC-003 | cache `{"ts": T}` (no `branch` key) | recompute |
| EC-004 | cache file not JSON | treated as `{}` → recompute |
| EC-005 | cached `branch` `""` or `null` | no segment until the TTL expires |
| EC-006 | cached `branch` `5` (non-string) | segment `\e[90m⎇ 5\e[0m` |
| EC-007 | cached `ts` in the future (clock moved back) | negative age → fresh; cached branch kept until `now > ts + ttl_s` |
| EC-008 | cached `ts` `true` | counts as 1 → stale → recompute |
| EC-009 | cached `ts` a string (`"x"`) | legacy TypeError → guard line `\e[90mstatusline degraded\e[0m\n`, exit 0 |
| EC-010 | cache file holds a JSON array (`[1,2]`) | legacy AttributeError → guard line, exit 0 |
| EC-011 | `HYLO_STATUSLINE_GIT_ENABLED=no` | disabled under hylo's typed bool (OD-05); legacy `DGX_SL_GIT` disabled only on `"0"`. Config-layer difference only; harness cases translate settings (BC-6.02.003); invalid values are D4-EX-3 Boolean class (BC-2.02.001) |
| EC-012 | mkstemp temp names / Go temp cleanup | outside this BC's output; covered by the temp-file exclusion (BC-6.03.003, OD-110) |

## Canonical Test Vectors

Verified against the oracle (CPython 3.11.7) on 2026-11-15.

| Input | Expected Output | Category |
|-------|----------------|----------|
| repo at dir `D` with HEAD `ref: refs/heads/main`; no cache; `T` | segment `\e[90m⎇ main\e[0m`; cache bytes `{"ts": 1800000000.0, "branch": "main"}` | happy-path |
| then HEAD → `other`; render at `T+5.0` | `\e[90m⎇ main\e[0m` (fresh cache) | edge-case |
| render at `T+5.001` | `\e[90m⎇ other\e[0m`; cache `{"ts": 1800000005.001, "branch": "other"}` | edge-case |
| dir with no repo | no segment; cache `{"ts": <now>, "branch": ""}` written | edge-case |
| key for `/x/p` | `5a3006e969bd95e3` | happy-path |
| key for `/x/p/` | `09d4733efe0f2c7f` | edge-case |
| key for `/x/\udcff` (lone surrogate) | `a77db2f8cb13007e` | edge-case |
| git disabled | no segment, no cache file | edge-case |
| cache `{"ts": "x", "branch": "m"}` | stdout `\e[90mstatusline degraded\e[0m\n`, exit 0 | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-028 | Multi-step sequence (T, T+5, T+5.001) reproduces oracle stdout and cache bytes | parity harness stdin-sequence replay (BC-6.02.002) |
| VP-028 | Cache key equals the oracle for ASCII, non-ASCII and lone-surrogate dirs | table test |
| VP-028 | Python-written cache read by Go and vice versa yields identical output | cache-swap test (BC-6.02.004) |

## Traceability

| Field | Value |
|-------|-------|
| Source | Source: legacy/dgx_statusline.py:git_segment (SL:399-413; allocation cites SL:405-411); GIT_TTL SL:99; GIT_ON SL:77; call site SL:454-457 |
| Legacy contract | BC-SL-010 |
| Parity class | byte-exact (no exclusion-list entry; temp-file handling belongs to BC-6.03.003) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-008 |
| Owner decisions | OD-101 (cache dir), OD-05 (typed bool, no `DGX_*`), OD-110 (temp-file exclusion is cache-only) |
| Config keys | `statusline.git.enabled` (default true), `statusline.git.ttl_s` (default 5.0 s, operator `>`; rationale: convention — "docs' example pattern", T-013), `paths.cache_dir` |
| Architecture Module | `internal/statusline/git.go` |
| Stories | TBD |

## Related BCs (Recommended)

- BC-1.02.004 — depends on (branch walk)
- BC-1.02.003 — composes with (segment precedes the project label)
- BC-1.06.001 — depends on (never-raise cache load/save)
- BC-3.01.001 — depends on (per-OS cache dir)
- BC-5.02.001 — depends on (json.dump bytes, float repr)
- BC-5.03.003 — depends on (EncodeUTF8Replace)
- BC-6.03.003 — related to (temp-file exclusion)

## Architecture Anchors (Recommended)

- `architecture/ARCH-03-statusline.md#git` — internal/statusline/git.go (5 s TTL git cache) (BC-COMPONENT-MAP: ARCH-03 (ARCH-03-statusline.md))

## Story Anchor (Recommended)

TBD — branch segment story

## VP Anchors (Recommended)

- VP-028 — TTL sequence parity

---

### Brownfield-Specific Sections

#### Source Evidence

| Property | Value |
|----------|-------|
| **Path** | `legacy/dgx_statusline.py` (`git_segment`, SL:399-413) |
| **Confidence** | high (pass-3 HIGH-R #3.4; re-run 2026-11-15) |
| **Extraction Date** | 2026-11-15 |

#### Evidence Types Used

- **guard clause**: `if not GIT_ON` (SL:400); TTL test (SL:409)
- **documentation**: comment SL:402-404 (review #3.4)

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | reads + writes (cache file), reads (git walk) |
| **Global state access** | reads config and clock |
| **Deterministic** | yes under an injected clock and filesystem |
| **Thread safety** | n.a. (one writer per render; atomic rename) |
| **Overall classification** | effectful shell |

#### Refactoring Notes

Split into a pure decision `(cache, now, ttl) -> recompute?` and an I/O shell; the clock is
passed in once per render.
