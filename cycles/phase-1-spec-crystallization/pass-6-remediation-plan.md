---
document_type: remediation-plan
phase: 1d
pass: 6
date: 2026-11-18
source: adversarial-reviews/pass-6.md, adversarial-reviews/ADV-P6-INDEX.md
---

# Pass-6 remediation plan (canonical rulings and calls)

Read with the Rules section of `pass-4-remediation-plan.md`. OD-176: fix every assigned finding, any severity. Before applying a call, check it does not contradict a settled OD; if it seems to, stop and report (L-PG-13). One measurement per fact, by the agent named for it (L-PG-18). Python: use `/opt/homebrew/anaconda3/bin/python3` (CPython 3.11.7); NEVER `/usr/bin/python3` (Apple 3.9.6) (L-PG-17). Check every claimed fix AND every rejection on disk before reporting (L-PG-15; the pass-5 rejection of ADV-P5-D16 was wrong, see ADV-P6-D07).

## Owner rulings (2026-11-18)

| ID | Ruling | Source |
|---|---|---|
| OD-181 | New closed-set exclusion id `OD-181` "metrics transport beyond plain http": non-http(s) redirect targets (hylo: no sample) and TLS trust-store differences for https (hylo: OS trust store). Parity cases use plain http only; table tests pin hylo's behaviour. Closed set = 12 ids. | C2-07, C2-08 |
| OD-182 | VP Go blocks are non-normative: each is labelled "Illustrative sketch (non-normative, not compiled; OD-182)". Normative VP content = property statement, oracle, method, inputs, pass/fail rule, reviewed at full severity. A sketch that contradicts its property is a defect in the sketch; sketch-only defects (syntax, API spelling) are cosmetic. A property that is only clear from its sketch is a HIGH defect against the statement. Phase 3 test-writers write real tests from the property. | A2 sketch class |
| OD-183 | OD-159 (UTF-8 everywhere) extends to stdin and stdout: hylo reads and writes UTF-8 on every OS. The Windows oracle gets exactly one extra variable, `PYTHONIOENCODING=utf-8` (stdio only; `PYTHONUTF8` stays forbidden). Stated in BC-6.01.002, ARCH-07, VP-034, BC-1.01.008, with a table test that it changes stdio encoding only. | A03 |
| OD-184 | Glyph columns are measured in legacy's render width (code points, the count legacy's layout uses): every `statusline.glyphs.*` / `statusline.subagent.glyphs.*` member is exactly 1 code point, except `statusline.glyphs.sparkline` = exactly 8 ordered code points. The East-Asian-Width validation width (OD-170 tables) applies only to the pill-label 1..16 bound (OD-173). | A04, D02, D03 |
| OD-185 | OD-104 stands: CI installs Python 3.11.x (latest patch); the exact-3.11.7 pin from pass-5 call 6 is withdrawn. Because measured constants (JSON depth limits, Unicode 14.0 tables) were taken on 3.11.7, the harness self-checks them against the resolved oracle at start (measure the depth boundaries and `unicodedata.unidata_version`; fail closed on any mismatch, printing the resolved version), and golden metadata records the resolved patch. | A02, D16 |
| OD-186 | The `temp-file` exclusion's scope is widened by ruling to cover the Windows sharing-violation rename-retry outcome (hylo may persist a write legacy would not). The retry delay becomes config key `statusline.cache.rename_retry_delay_ms` (Int, default 10, range 1..1000, judgment call). Attempt count: state one number consistently (initial attempt + retries) in ARCH-04, VP-018 and the BC. | A09 |
| OD-187 | VP-036: the >512 KB timing-fixture exemption is conditional per the brief: it applies only when that fixture misses the 25 ms target, and its use is reported. | A2-19 |

Next free OD: OD-188.

## Orchestrator calls (binding; checked against the OD log)

1. **Seven D4-EX-3 classes everywhere (A01, A2-08, D04, D14):** ARCH-02 (text and anchors `#classes`, `#seconds`), BC-2.01.002, BC-2.01.005, VP-016, feasibility report, and any other "six-class" live text. Text keys have no legacy analog, so `TestD4EX3_Text` is a Go table test only, not a parity exclusion entry; say so beside the Theme note.
2. **Windows `localtime` failure (A05, D06):** stays in pure pyfmt with no platform import: `LocalToUnix(fields, loc, msvcDomain bool) (int64, error)` returns a distinct `ErrLocaltimeDomain` when `msvcDomain` and the instant is outside MSVC's domain; `FromISOFormat` gains an error result so the caller can tell None (`ErrValue`) from degrade (`ErrLocaltimeDomain`). statusline passes `msvcDomain = platform.IsWindows()`. Propagate to BC-1.03.010, BC-1.03.018 (Inv3 and the crash-path count), ARCH-03 step 2, ARCH-05, ARCH-06, BC-5.04.001.
3. **OD-76 rows (D05):** OD-76's difference table (incl. the America/Chicago DST rows) is a Go table test closing the exclusion, not parity corpus cases; the corpus stays UTC-only.
4. **Redirects (C2-02, C2-03, C2-05, C2-11, C2-12):** an empty `Location` resolves by `urljoin(<URL of the request that received this 3xx>, "")`; 37 is the worst-case hop count, not a hop budget (the rule is urllib's visited/max_repeats/max_redirections). Because Go's net/http trims header values and rejects `%` without two hex digits, the metrics client is a minimal HTTP/1.1 client over `net.Conn` for plain http (OD-181 limits parity to http): it sends exactly urllib's request headers (method GET, `Host`, `User-Agent: Python-urllib/3.11`, `Accept-Encoding: identity`, `Connection: close`, in urllib's order; verify against CPython 3.11.7 source) and parses status line and headers as `http.client` does (compat32: values keep inner and trailing spaces, only CR/LF stripped). Empty fragment is dropped by `urlunsplit`.
5. **Metrics reply decoding (A07, C2-06):** `json.loads(resp.read())` on bytes = ModeBytes (BOM/UTF-16/32 detection); depth 992 accepted / 993 rejected (measured, VP-006); BC-5.02.003's one-line precondition gains the multi-line body case.
6. **Turn identity (C03):** BC-1.03.010 pins Python `==` for `cur.id` (no identity shortcut; NaN ids open a new turn each line) vs set membership for dedup; add the reviewer's NaN-id vector, oracle-run.
7. **Subagent id encoder (D08, C04, C05, C14):** the subagent `json.dumps` at SL:924 gets a measured budget. ONE agent (agent 5) measures end to end on legacy with an isolated HOME, a deeply nested `task.id`, interpreter as above. BC-1.07.004 PC3/PC4 wording: the id is the decoded value re-serialized by `pyfmt.Dumps`; exact escaping rules for `"`, `\`, controls and ESC.
8. **Composite and default-only spellings (D01, A13, A14):** `statusline.theme.heat` env spelling is the JSON array `[0.22,0.85,0.80]`; a default-only key compares the parsed value to the default. Write the exact env spelling of every default-only key (`limits.windows` comma list `5h,7d`; `units.lines` `k`; `units.tokens` `M`; any others). Reasons for list-entry violations (e.g. `lane.reroute_all_prefixes`) and for a control byte in `subagent.joiner` go to the Text class with exact strings in the vocabulary.
9. **Config Load warnings (A08):** `Load` returns `(*Config, []Warning, *ErrorSet)` (or equivalent stated once); the caller prints warnings before errors. The env seam is named `EnvVars` everywhere (not `platform.Environ`).
10. **VP-041 for-all coverage (B01):** VP-041 gains properties for the BCs listed in ADV-P6-B01 (or those BC rows are re-routed to existing golden legs if no for-all claim is meant); `bcs:` and VP-INDEX updated.
11. **Effect order (B04):** BC-1.01.009 PC2 adds the within-step exception: history-borne CP-O10/O11 in `cost_thresholds` raises after step 7c's `record_cost` write.
12. **Surrogates (B05, B06, C09, C15):** Windows lone-surrogate paths and raw encoded-surrogate stdin bytes (rejected by CPython's strict decoder → `{}`); Go uses pyfmt code-point iteration, never plain rune ranges, for WTF-8 values.
13. **CI (A10, A11, A12, A17, A2-21):** Tier A fails when K (caches swapped) == 0 for cases that declare swaps; Tier C fails when N or M == 0; required-checks list includes coverage, govulncheck and lint (staticcheck); one authoritative Tier A run with one timeout; R-004 mitigation restated for P1.
14. **Python 3.11.x (OD-185):** revert every "3.11.7 exact" CI/ARCH-08/cicd-setup/BC-6.04.001 text to 3.11.x with the self-check.
15. **Width example (D17):** under the validation width `中文` measures 4.
16. **Windows lone-surrogate paths (B05, added after the burst):** reproduce legacy, no exclusion: `internal/platform` encodes WTF-8 path values to UTF-16 itself, keeping lone surrogates as single 16-bit units (never Go's U+FFFD substitution), so a path with a lone surrogate stats the same directory CPython's wide-string call does. Table-tested on Windows.
