---
document_type: remediation-plan
phase: 1d
pass: 13
date: 2026-11-18
source: adversarial-reviews/pass-13.md, adversarial-reviews/ADV-P13-INDEX.md
---

# Pass-13 remediation plan (canonical calls)

Read with the Rules section of `pass-4-remediation-plan.md` and the gates of passes 9-12 (YAML parse after every edit; for-all properties derived from every PC/EC/exception and walked against legacy; state only what you measured, bracketing boundaries on both sides; ASCII wire goldens; cite by section/ID + PC/EC/Inv/row, never line numbers; synthetic values on the pre-push hook allowlist; edit only your file set, list out-of-set hits; when a fix changes a rule, grep every sibling that states it and list each hit; escape-bearing text is written with a script and verified). New this pass: **a vector's setup text (config, seeded files, inputs) is part of the vector** and is walked against legacy together with its expected output (pass-13 B01: setup said "empty cache" while the expected output assumed a seed). **New ids and anchors are minted only by the file that owns them** (CP-C ids by error-taxonomy); other agents cite the legacy site and the residual sweep adds the id.

No owner rulings this pass. Next free OD: OD-195.

## Orchestrator calls (binding; checked against the OD log)

1. **CP-C family scope (C2-03, C05).** OD-160 names the foreign-cache CLASS: every hand-edited cache shape is under OD-160, and "CP-C01..C10" was the register when OD-160 was ruled, not a membership cap. Agent 2 catalogues every foreign-cache crash trigger the BCs name that lacks a row (session-cache sample type faults and KeyError at SL:324-337/356; giant-int OverflowError legs; sparkline faults at SL:664/671/674; mix-cache `lr[0]` at SL:778-779; mix-cache top-level non-object at SL:1019, string `size` and non-iterable `ids` at SL:1033), appending CP-C11 onward, one row per distinct legacy site and fault; text that presents "CP-C01..C10" as the whole family says "the CP-C family (OD-160)". hylo's disposition for each new row copies the existing CP-C rows' disposition (Go table test; same hylo outcome class as its nearest existing row). BC agents name the legacy site in their ECs; the residual sweep adds the ids.
2. **Windows oracle stdout (D01).** Every comparison of oracle stdout on the Windows legs (case comparator, clock canary, version probe, any other) applies the same open CRLF→LF conversion before comparing; BC-6.03.002 PC-1 defines it once, and BC-6.01.001 and BC-6.01.003 cite it.
3. **Shim canary, BC side (D02).** Pass-12 call 7 applies to BC-6.01.003 PC-4/PC-5 and BC-6.01.002 PC-4: the clock leg is the gating shim detector; the stdio leg checks the UTF-8 round trip only; "discriminates the LF half", the PC-5 no-shim negative control and any claim that the shim prevents CRLF are removed.
4. **cache-003 hylo key (D03, D04).** `HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0` is a conditional member of the hylo child's exact key set, present exactly when the case declares the empty-bin fake PATH (cache-003); BC-6.01.002's key-set CTV and PC-3 say so; ARCH-07's conditional-PATH trigger is the cache-003 empty-bin declaration only (no subprocess-fake table in any parity case).
5. **Tier A and timing OS matrix (A04, D06).** The Tier A job and the timing job each run on all three OSes, and every leg of each installs setup-python (CPython 3.11) and prints the resolved patch. Tier B runs in the plain test legs only (no separate Tier B job); the plain legs own the `tier-b: N goldens compared` census. The per-OS timing report comes from the timing job.
6. **govulncheck ordering (A03).** govulncheck is its own job. It runs and reports on every change, and it becomes a required check in the same change that adds go.mod's `toolchain` line (ARCH-08 ordering rule). The lint job runs `gofmt -l` only and is required. The branch-protection list names exactly the contexts the jobs emit.
7. **internal/cost interface (A02).** `internal/cost` does no I/O: it exposes pure functions over values passed in (the loaded cost history, the current session's numbers, `now`) that return the new history and the thresholds; `internal/statusline` loads and saves the cost-history file through its `CacheStore` (depth constant 990 lives with that cache file). ARCH-00's "writes via injected `Store`" is replaced; the architect declares the cost API (function names, parameters, results) in ARCH-03 (or ARCH-04) and step 7c cites it.
8. **`config path` exit (A01).** The directory-undetermined exit 1 of `hylo config path` is added to error-taxonomy's closed exit table with the next free code in the CLI/config family; prd.md §5 and ARCH-00 list it as the one non-zero exit outside validate/usage/harness.
9. **VP-001 membership oracle (A2-01, A2-03).** No "render-grammar classifier". The main-entry legal set is: the 29-byte degraded line; the unknown-flag line(s) matched by VP-002's grammar (parameterised `<flag>`); the config-error line matched by VP-016's grammar (parameterised key/value/reason); or a normal render = one or two non-empty LF-terminated rows. Zero bytes is NOT in the main-entry set. Each parameterised surface is matched by a regex stated in the VP.
10. **Timing unit (A05, A2-02, D10).** VP-036, ARCH-08 and BC-6.04.002's VP row state the pass-12 call-4 unit (per (case, step), cold-start replay from committed seeds, large-transcript exemption 100 ms ceiling); "steady-state" and "binds per case" are removed. The 100 ms ceiling fails when p95 > 100.0 ms; the brief says "at most 100 ms".
11. **Coverage exclusion (A07).** The coverage figure excludes exactly the five `ORACLE_TESTS` members (pass-12 call 6); every other test under `./internal/...` counts.
12. **Session-cache save/load depth (C04).** Agent 6 measures once with legacy in an isolated temporary HOME and cwd (CPython 3.11.7, the oracle interpreter): stdin whose `rate_limits` nests to the deepest depth stdin accepts, then a second refresh; pin whether the session cache saves and whether it reloads, and fix BC-1.03.021's "Save budget = Load budget" sentence to what was measured.
13. **Public GitHub owner (A17).** The usernames scan category covers the private terms file and home-path usernames; the public GitHub owner segment of the D1 module path is public by D1 and is not a finding. cicd-setup states this exemption explicitly.
14. **NFR-005 caps (A08, A09).** The four render-state caps are the read step, dedup memory, history cap and sparkline max age (`statusline.sparkline.max_age_s`); `window_age.max_depth` is listed separately as a walk bound. NFR-005 states that an LF-less transcript tail is buffered whole and re-read every refresh (bounded by file size, legacy behavior), so no memory cap is invented.
15. **Rename-retry bounds (A10).** Keep the defaults; set the upper bounds so that limit × delay is at most 1000 ms per Save, and state the rationale as a labelled judgment call (not "inside the refresh budget").
16. **Network parser risk (A11).** risk-register gains a security row for the hand-written HTTP/1.1 + TLS client parsing untrusted bytes, mitigated by the pinned limits (`_MAXLINE`, `_MAXHEADERS`, redirect cap) and a Go fuzz target on the response parser.
17. **Hygiene canary (A12).** VP-035's per-category canaries are constructed at runtime from fragments and use only flagged (non-allowlisted) shapes; no flagged literal is committed.
18. **CI timeouts (A13).** Tier A and timing job timeouts are derived from corpus size (cases × steps × runs × a measured per-run ceiling, with headroom) and the formula is written beside each.
19. **Windows cache dir (C01).** `%LOCALAPPDATA%\hylo\cache` per OD-144 everywhere.
20. **Everything else** as reported, routed below.

## Agent file sets and findings (routed by file)

| Agent | Role | Files | Findings |
|---|---|---|---|
| 1 | architect | specs/architecture/*, specs/cicd-setup.md | A02 (call 7), A03 (call 6), A04 (call 5), A05 (call 10), A13 (call 18), A14 (call 5), A16, A17 (call 13), A19; A01 (ARCH-00 half, call 8); A10 (ARCH-04 half, call 15); C2-02; D04 (call 4) |
| 2 | product-owner | specs/prd.md, specs/prd-supplements/*, specs/owner-decisions-log-2026-11-14.md | A01 (call 8), A06, A07 (call 11), A08, A09 (call 14), A10 (call 15), A11 (call 16), A15, A18; B07; C2-03 + C05 (call 1, mint CP-C11+), C2-04, C08 |
| 3 | architect | VP-001..VP-020 | A2-01 + A2-03 (call 9), A2-04 (VP-014), A2-06, A2-09; B04 (VP-019) |
| 4 | architect | VP-021..VP-041, VP-INDEX, domain-spec/*, product-brief, dtu, gene-transfusion, feasibility | A2-02 + A2-08 (call 10, VP-036 and brief), A2-05 (VP-033), A2-07, A2-10 (VP-035 incl. call 17), A2-11; A12 (call 17, VP-035); VP-INDEX sync for agent 3's and BC agents' VP deltas |
| 5 | product-owner | ss-01 BC-1.01.*, BC-1.02.* | B01, B02, B03, B05, B06, B08 |
| 6 | product-owner | ss-01 BC-1.03.*, BC-1.06.*, BC-1.07.* | C01 (call 19), C02, C03, C04 (call 12, measure), C05 (BC half: name the legacy sites), C06, C07, C09, C10 |
| 7 | product-owner | ss-01 BC-1.04.*, BC-1.05.* | C2-01 (BC side; name legacy sites, VP-012 reciprocity reported to agent 4), C2-05, C2-06, C2-07, C2-08, C2-09 |
| 8 | product-owner | ss-02..ss-06 BCs, BC-INDEX, BC-ALLOCATION | D01 (call 2), D02 (call 3), D03 (call 4), D05, D06 (call 5), D07, D08, D09, D10 (call 10), D11, D12, D13, D14, D15; A2-04 (BC-3.02.001 VP rows) |
