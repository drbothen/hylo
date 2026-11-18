---
document_type: remediation-plan
phase: 1d
pass: 7
date: 2026-11-18
source: adversarial-reviews/pass-7.md, adversarial-reviews/ADV-P7-INDEX.md
---

# Pass-7 remediation plan (canonical rulings and calls)

Read with the Rules section of `pass-4-remediation-plan.md` and the header rules of `pass-6-remediation-plan.md` (OD-176 fix everything; check calls against settled ODs; one measurement per fact; Python `/opt/homebrew/anaconda3/bin/python3` only; verify fixes AND rejections on disk; OD-182 sketches are non-normative). Write repo-relative paths only in any file you create.

## Owner rulings (2026-11-18)

| ID | Ruling | Source |
|---|---|---|
| OD-188 | The Windows rename retry count becomes config key `statusline.cache.rename_retry_limit` (Int, default 2, range 0..10, judgment call), beside `statusline.cache.rename_retry_delay_ms`. Total attempts = 1 + limit. | A19, A2-07 |
| OD-189 | The dead-backend marker word reuses `statusline.pill.label_local` (OD-173). New Text keys with legacy defaults: `statusline.labels.vllm_down` (`vLLM down`), `statusline.labels.lmcache_down` (`LMCache down`), `statusline.subagent.name_fallback` (`?`). | C2-07, C11 |
| OD-190 | Extends OD-183: hylo writes LF line endings on every OS (UTF-8 + LF). The Windows oracle's LF normalization is named beside `PYTHONIOENCODING=utf-8`, not hidden in the shim. | A2-19 |
| OD-191 | The >512 KB timing fixture (OD-187) gets a ceiling: exempt from the 25 ms p95 target, but the gate fails if its p95 exceeds 100 ms (judgment call: 4x the target, well under the refresh interval). | A2-18 |
| OD-192 | ASM-007 (Claude Code 2.1.326 subagentStatusLine payload) must be validated by an owner capture into git-ignored `captures/` before Phase 2 writes the S1.07 stories; the rest of Phase 2 is not blocked. | A22 |

Next free OD: OD-193.

## Orchestrator calls (binding; checked against the OD log)

1. **Lone-surrogate file names (C01):** reproduce legacy, no exclusion. On POSIX, path values are encoded with Python's filesystem rule (surrogateescape: U+DC80..DCFF become the raw byte 0x80..0xFF; derive with the interpreter what legacy does for other lone surrogates at each site, SL:191/201-204/1010, and pin it). On Windows the path keeps lone surrogates as UTF-16 units (pass-6 call 16). Applies to the session-cache name and the transcript probe.
2. **Oracle env allowlists (A01, D05):** BC-6.01.002 is authoritative. ARCH-07 and VP-034 copy its exact per-OS key sets (incl. the conditional `PATH`, `HOME`/`USERPROFILE`, `HYLO_TEST_NOW`, `COLUMNS`, translated settings, the Go-binary list, Windows `PYTHONIOENCODING=utf-8` and the OD-190 LF note). If BC-6.01.002 itself is incomplete, fix it first and copy.
3. **Timing exemption (A02, OD-187, OD-191):** BC-6.04.002, ARCH-08, PRD NFR-001 state the conditional exemption and the 100 ms ceiling. The exempt fixture is identified by a validated case flag (`timing_exempt: large-transcript`, exactly one case, and its transcript must exceed 512 KB), and the job prints one report line when the exemption is used.
4. **Platform signatures (A03, D12):** `LocalZone(env EnvVars) (*time.Location, error)`, `CacheDir(env EnvVars)`, `HomeDir(env EnvVars)`; no platform function reads the real process environment. BC-3.01.001 home source goes through `EnvVars`; BC-6.01.002 drops `Env.Getenv`/`Home` for the `EnvVars` seam.
5. **Default-only env names and defaults (D01, A04, A05):** env names follow `EnvName`: `HYLO_STATUSLINE_LIMITS_WINDOWS`, `HYLO_STATUSLINE_UNITS_LINES`, `HYLO_STATUSLINE_UNITS_TOKENS`, `HYLO_STATUSLINE_UNITS_CONTEXT`. Each key's default value equals its single accepted spelling; derive the letters from legacy (e.g. lines `k`, tokens `M`, context `K`) and state why they differ.
6. **Reason vocabulary (D02, D03, A13, A16):** BC-2.02.001 is the canonical home of every reason string; error-taxonomy mirrors it byte for byte. Add the pass-6 strings, define the reason for each numeric-range failure by type (Int, Float, composite; use the existing strings `out of range`, `not finite`, `negative` with a stated precedence), give the descending `cost.percentiles` pair its own ascending-pair reason, and correct the glyph reasons to `expected exactly 1 code point` (and `expected exactly 8 code points` for `statusline.glyphs.sparkline`) per OD-184. `control character` belongs to the Text class for non-theme free text.
7. **Self-check constants (D04):** ONE definition, measured end to end through the oracle shim exactly as the pinned decode/encode limits were (stdin 993/994 etc.), not a helper-scope probe. BC-6.01.001, VP-006 and ARCH-07 state the same constants. Agent 5 owns this measurement.
8. **Windows localtime domain (D06, B03):** every MSVC call in CPython's local-to-UTC conversion (t, u1, u1 - 86400, u2) is checked against the domain, so a naive wall time on or before 1970-01-01 (and from year 3001) degrades. Fix the BC-5.04.001 Description, ARCH-06, BC-6.04.003 and BC-5.04.002. New crash id **CP-T09** = "Windows MSVC localtime domain OSError on a naive transcript timestamp" (append-only; CP-T08 is a retired id); the register becomes 48 paths (T family 8); BC-1.01.009 step 2 and BC-1.01.001 PC3 list it.
9. **Metrics client (C2-01, C2-02, C2-04, C2-05, C2-08, A11):** response body framing exactly as `http.client`: chunked decoding, then `Content-Length`, else read to EOF; header values = `value.lstrip(' \t')` then `rstrip('\r\n')` (I verified `Location: \t /x ` parses to `'/x '`); the next GET drops the fragment; https goes through `crypto/tls` over the same `net.Conn` with SNI, ALPN `http/1.1` only and the OS trust store (system roots on Linux), parity cases are plain http only (OD-181); VP-030's transport table uses a raw `net.Listener`, not `httptest`.
10. **Exclusion closure (C2-03, A2-02, A2-03, A2-04, C05):** BC-6.03.004's rider register is authoritative; VP-012 copies it exactly; the closure check also verifies that a rider test exists for EVERY closed id, including ids with no parity entries (OD-181, Text). Reciprocity: BC-1.04.001, BC-1.04.002, BC-1.06.001 get VP-012 rows and appear in VP-012 `bcs:`.
11. **Go file naming (A10):** the pure, always-compiled matchers are named without an OS suffix (e.g. `envfold_nt.go`, `envfold_posix.go`, `localtime_domain.go`); only real syscall wrappers use `_windows.go` / `_unix.go` with explicit build tags.
12. **CI (A07, A08, A09, A18, A20):** coverage is its own job on ubuntu with `-coverpkg=./internal/...` so `internal/parity` exercising statusline counts, and it is the required check; release.yml runs Tier A only via the dedicated job, never inside its plain `go test`; R-004's P1 mitigation names only real gates (include `internal/parity` in the coverage gate); Tier B's census counts only the host OS's golden set; the timing job checks its case count against the corpus.
13. **VP fixes:** VP-018 temp pattern is `<basename>.XXXXXXXX` (mkstemp prefix, SL:201), no `.tmp` suffix; VP-031 names the config keys and default-vs-non-default behaviour; VP-016 gains a theme-rejection leg (BC-2.01.003 EC-002/003); VP-007's second render runs on a fresh copy of the recorded env; VP-041 P-b's live oracle moves to Tier C; VP-014 and the DTU assessment use `TestWindowAge_D4EX1_Windows_AncestorFound`.
14. **Titles (B01, D11):** BC-1.01.003 and BC-1.01.007 H1s describe the `rows > 2` override; BC-2.02.002 H1 admits the `git.ttl_s` exception. Sync BC-INDEX and PRD.
15. **Subagent wire escapes (C02):** `json.dumps` short escapes are `\"`, `\\`, `\b`, `\f`, `\n`, `\r`, `\t`; every other control and non-ASCII code point is `\uXXXX`.
