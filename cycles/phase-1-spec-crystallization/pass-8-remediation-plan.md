---
document_type: remediation-plan
phase: 1d
pass: 8
date: 2026-11-18
source: adversarial-reviews/pass-8.md, adversarial-reviews/ADV-P8-INDEX.md
---

# Pass-8 remediation plan (canonical rulings and calls)

Read with the Rules section of `pass-4-remediation-plan.md` and the header rules of `pass-6-remediation-plan.md` and `pass-7-remediation-plan.md` (OD-176 fix everything; check calls against settled ODs; one measurement per fact; Python `/opt/homebrew/anaconda3/bin/python3 -I` only; verify fixes AND rejections on disk; OD-182 sketches are non-normative). Write repo-relative paths only. Edit ONLY files in your assigned set; list out-of-set hits as file:line (L-PG-24). When a fix renames or respells something, re-check what the renamed thing MEANS at every use (pass-8 B01 lesson). Before copying a citation, check it resolves (L-PG-26).

## Owner ruling (2026-11-18)

| ID | Ruling | Source |
|---|---|---|
| OD-193 | OD-158 stands unchanged: the P1 >=95% line-coverage gate covers S1 (`internal/statusline`, `internal/cost`) and S5 (`internal/pyfmt`) only. `internal/parity` (S6) coverage is reported, not gated. Pass-7 call 12's addition of `internal/parity` to the gate is withdrawn. | A04 |

Next free OD: OD-194.

## Orchestrator calls (binding; checked against the OD log)

1. **Coverage job (A03, A05, A06, OD-193):** the required `coverage` job runs on ubuntu with the same Tier A exclusion as the plain test step (Tier A runs only in its dedicated job), so it needs no Python and keeps its timeout. S1/S5 coverage must come from in-process tests; drop the premise that parity runs count toward statusline coverage (Tier A drives the built binary as a subprocess, which `-coverpkg` does not profile). The gate fails if either gated package set is absent or reports `[no statements]` — state the gated packages by name, no count word. cicd-setup.md matches ARCH-08: the macOS/Windows test legs install no Python; lag note 1's superseded rationale is removed.
2. **CP-T09 everywhere (A02, A2-02):** NFR-002 trigger lists (prd.md, nfr-catalog.md) end with CP-T09; ARCH-07 case-id grammar adds family `cpt09`; VP-001's closed trigger catalogue and test families add CP-T09 / `cpt09` (Windows-only leg).
3. **Overflow skip wording (A2-01):** CP-O06..O08 skip the line and render normally (OD-156/OD-167); they do not degrade. VP-001 and any sibling saying otherwise are corrected. The OD-166 record guard: state precisely what it does (not recorded) and whether the refresh degrades, per BC-1.05.004.
4. **OD-160 rider anchors (A2-05, A2-06):** BC-6.03.004's register is corrected first, then VP-012 copies it: the OD-160 riders are BC-1.02.017 EC-004..006 and BC-1.01.008 PC3 (verify on disk before writing). `TestWindowAge_D4EX1_Windows_AncestorFound` is the D4-EX-1 rider, never "the OD-160 rider" (VP-INDEX, VP-012).
5. **Reroute-all trigger (B01):** reroute-all holds when any configured model prefix, with trailing `*` stripped, is a member of `statusline.lane.reroute_all_prefixes` (SL:487-488: `any(p.rstrip("*") in (...) for p in prefixes)`). The marker key is the membership set, not the trigger. BC-1.02.030 (PC, EC-007, EC-010 with default `model_prefixes=claude-sonnet` → legacy degrades on `{"five_hour":"x"}`), and its config-keys row lists both `backends[0].model_prefixes` and the marker key.
6. **Glyph keys named (C2-01, B03):** every BC that BC-2.01.004 PC-6 lists as a consumer of a glyph key names that key in its postconditions (default shown in parentheses), as BC-1.04.004 does. The dead marker's `?` is a literal `" ?"` after `label_local` (OD-189, BC-1.04.004 owns it); BC-1.01.003 is corrected; `label_unknown` is consumed by BC-1.02.001 only.
7. **Platform signatures (A07, D01, D12, D13):** `CacheDir(env EnvVars) (string, error)`, `StateDir(env EnvVars) (string, error)`, `ConfigDir(env EnvVars) (string, error)`, `LocalZone(env EnvVars) (*time.Location, error)` everywhere. ARCH-05 currently omits the error results on the three directory resolvers; agent 1 adds them (BC-3.01.001 EC-004 requires an error when a directory cannot be determined, and `config path` exits 1 on it per pass-5 call 4). `run(args, env EnvVars, stdin, stdout, stderr)` and `runStatusline(env, stdin, stdout, stderr)` per ARCH-01; the env seam's method is `Lookup(name) (string, bool)`.
8. **Localtime domain home (D02):** the MSVC-domain rule lives in pure pyfmt (`ErrLocaltimeDomain`, `msvcDomain bool`); statusline passes `platform.IsWindows()`. BC-5.04.002 Inv 2 corrected.
9. **Golden-default exceptions (D08):** `statusline.cache.rename_retry_delay_ms` and `statusline.cache.rename_retry_limit` have no legacy analog (legacy never retries, SL:198-206); BC-2.01.004 PC-3(f) lists them by name as exceptions beside the existing two, and BC-3.01.001 Inv 1 says so.
10. **Units ranges (B05):** per pass-7 call 5: `statusline.units.lines` range {`k`}, `statusline.units.tokens` range {`M`} (each default-only); BC-1.02.014 and BC-1.02.025 match interface-definitions.
11. **Env spellings in the registry (D06):** interface-definitions Default column uses the env spelling: `limits.windows` `5h,7d`, `theme.heat` `[0.22,0.85,0.80]`.
12. **For-all legs need a VP home (A2-07, C2-07, C2-08):** no new VPs. Every BC VP-table row that routes a for-all/fuzz/testing-quick leg to a VP gets a matching property leg in that VP (method updated, `bcs:` and VP-INDEX synced), or is re-routed to an existing VP that already has such a leg. Specifically: VP-004 (argv/env/stdin for-all incl. subagent NDJSON), VP-016 (every env map; config-error line iff validate exits non-zero), VP-029/VP-013 (delete-the-line equivalence fuzz), VP-024 gains BC-1.05.009 (pyfmt.Dumps differential), VP-020 (testing/quick rows from BC-1.05.004/006), VP-030 quick leg lists BC-1.04.003/008/015/018/019 (and VP-031 rows re-routed or given a leg).
13. **Metrics client (C2-02, C2-03, C2-13, C2-12):** verified on CPython 3.11.7 by agent 7 (one measurement each): a followed 3xx body is drained (`fp.read()`) under the same framing before the next hop; a drain failure gives no sample. Chunked iff `tr_enc.lower() == "chunked"` exactly (orchestrator verified in source); any other value falls to Content-Length/EOF. Pin `_MAXHEADERS` = 100 (orchestrator verified) → no sample when exceeded, the 65536-byte line limit → no sample, and interim 1xx handling as http.client does. Request header order is the one BC-1.04.001 pins (Accept-Encoding first). OD-181 scope = redirect targets and TLS trust only; a non-http(s) configured URL is D4-EX-3 URL class.
14. **Whole-input decodes (D03):** stdin (`json.load(sys.stdin)`) and the cache loaders (`json.load(fh)`) read the whole input; only the transcript is line-split. BC-5.02.003 corrected.
15. **Measurements (one owner each):** agent 6: C02 (a transcript whose `cur.id`/`cur.out` makes the mix cache exceed its 991 save budget: run legacy in an isolated HOME and temp cwd and pin what happens: write skipped, temp leaked, repeat per refresh) and C04 (legacy exit status when stdout is a closed pipe while printing subagent rows). Agent 8: D20 (`str()` of a deep list at the SL:442/453 sites near depth 991) D09 needs no measurement: the PID-reuse guard is a hylo-native Windows probe with no legacy analog (legacy uses `ps`), and ARCH-05's pass-5 D22 walk rule is the ruled design: when the guard rejects a candidate parent, the walk TERMINATES (result None). BC-3.02.001 and its table leg follow ARCH-05.
16. **OD-76 vectors (D10):** per pass-6 call 3, all OD-76 D1-D4 vectors are Go table tests; the corpus stays UTC-only with no OD-76 corpus case. Remove contrary wording; keep the conditional fake-`PATH` machinery only if another consumer exists, else state it has none in P1.
17. **Timing threshold unit (D19):** ">512 KB" means more than 524,288 bytes (512 KiB, equal to the `transcript.read_cap_bytes` default).
18. **Rename-retry citation (C05):** BC-1.06.001 EC-009 cites the OD-186 widening of the `temp-file` exclusion.
19. **DTU timing (A2-12):** ASSUMP-107-1 capture is due before Phase 2 writes the S1.07 stories (OD-192).

## Agent file sets (disjoint)

| Agent | Role | Files | Findings |
|---|---|---|---|
| 1 | architect | specs/architecture/* , specs/cicd-setup.md | A02(ARCH-07), A03, A05, A06, A07, A08, A10, A13, C2-12, D01(ARCH-02/05 signatures), D02(ARCH-05), D22, C02(ARCH-03 wording, after agent 6's measurement is known — residual sweep) |
| 2 | product-owner | specs/prd.md, specs/prd-supplements/*, specs/owner-decisions-log-2026-11-14.md (add OD-193) | A01, A02(NFR-002), A04(PRD/NFR text consistent with OD-193), A09, A11, A12, C2-11, D06, D19 |
| 3 | architect | VP-001..VP-020 | A2-01, A2-02, A2-03, A2-04, A2-05(VP-012), A2-06(VP-012), A2-07(VP-004/013/016), A2-08, A2-09, A2-10, A2-11, A2-15, A2-16, C2-06, C2-07(VP-020), C03(VP-012/013) |
| 4 | architect | VP-021..VP-041, VP-INDEX, domain-spec/*, product-brief.md, dtu-assessment.md, gene-transfusion-assessment.md, architecture-feasibility-report.md | A2-06(VP-INDEX), A2-07(VP-029), A2-12, A2-13, A2-14, A2-17(VP-022), A2-18, A2-19, C2-07(VP-024), C2-08, C2-09, all VP-INDEX syncs from agents 3/4 |
| 5 | product-owner | ss-01 BC-1.01.*, BC-1.02.* | B01-B11 |
| 6 | product-owner | ss-01 BC-1.03.*, BC-1.06.*, BC-1.07.* | C01-C06, A2-07 BC-1.03.018 row |
| 7 | product-owner | ss-01 BC-1.04.*, BC-1.05.* | C2-01..C2-05, C2-07(BC rows), C2-08(BC rows), C2-10, C2-13, C2-14, C2-15, A2-17(BC-1.04.001) |
| 8 | product-owner | ss-02..ss-06 BCs, BC-INDEX.md, BC-ALLOCATION.md | D01, D03-D24, A2-05(BC-6.03.004 register first), A2-07 (BC-4.01.001, BC-2.02.001 rows) |

VP `bcs:` changes from agent 3 are reported to agent 4's VP-INDEX sync in the residual sweep, not edited in VP-INDEX by agent 3.
