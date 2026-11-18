---
document_type: sync-check
phase: 1d
pass: 11
date: 2026-11-18
producer: consistency-validator
traces_to: pass-11-remediation-plan.md
---

# Pass-11 sync check (Phase 1d, 2026-11-18)

Scope: the uncommitted `specs/` diff (97 files) checked against `pass-11-remediation-plan.md`
(owner ruling OD-194 and orchestrator calls 1-15). Read-only check; this report is the only
file written. All checks are REQUIRED-PRESENCE checks, not "where carried" checks.

## Result table

| # | Check | Result | Evidence / failures |
|---|-------|--------|---------------------|
| 1a | OD-194: nine `statusline.labels.*` keys in interface-definitions registry (defaults, env names, range) | PASS | prd-supplements/interface-definitions.md, registry rows for `statusline.labels.old` / `rate` / `queue` / `kv` / `host` / `tps` / `max` / `idle` / `na` — defaults exactly the legacy words, env names per the `EnvName` rule, range = the OD-194 label rule (non-empty, no control bytes, valid UTF-8, display width 1..16); pass-11 changelog entry records the registration |
| 1b | OD-194: nine keys in BC-2.01.004's registry (PC-13) | PASS | ss-02/BC-2.01.004.md PC-13 table — same nine keys, identical defaults, legacy sites, env names enumerated via PC-2's `EnvName`; punctuation/unit marks noted as named format constants with the why-not-config rationale |
| 1c | OD-194: every consuming BC's postconditions name its key | PASS | BC-1.04.004 (Po 2: `old`), BC-1.04.006 (Po 3: `rate` + `queue`), BC-1.04.007 (Po 5: `kv` + `host`), BC-1.04.008 (Po 1/Po 2: `tps`, both sites), BC-1.04.010 (Po 3: `max`), BC-1.04.012 (Po 4: `idle`), BC-1.04.017 (Po 4: `idle`), BC-1.04.018 (Po 4: `tps`), BC-1.05.003 (Po 2: `na`) — each names key + default + legacy site + OD-194 + the format-constant note |
| 1d | OD-194: consumer lists agree between interface-definitions and the BCs | PASS | interface-definitions consumer column = exactly the nine BCs above; BC-2.01.004 PC-13's column is deliberately narrower ("Inline-literal owner": `tps` → BC-1.04.008, `idle` → BC-1.04.012) and the two secondary consumers it omits (BC-1.04.018, BC-1.04.017) do name the key in their own postconditions, so no consumer is lost |
| 1e | OD-194 row in the owner-decisions log | PASS | specs/owner-decisions-log-2026-11-14.md — OD-194 row present with ruling text, the nine minted defaults/sites, and the agent routing |
| 2 | Calls 1-15: stated rule present in every file the plan names; no contradicting old wording remains | PASS | Per-call detail below. Residual old-wording greps hit only withdrawn/history/provenance text (see notes N1-N3) |
| 3 | Citations added this pass resolve | PASS | Sampled across the diff: CP-S02/03/04/05/08/10 defined in error-taxonomy's CP-S table with (id, site, owner BC/EC) and named in their owning ECs (BC-1.02.001 EC-007; BC-1.02.003 EC-006; BC-1.02.006 EC-008; BC-1.02.008 EC-006; BC-1.02.014 EC-010); BC-3.01.001 EC-004, BC-6.01.001 PC-7, BC-6.02.003 PC-5, BC-2.01.005 PC-6, BC-1.05.005 PC3/PC4, VP-013/VP-012 rows in BC-1.03.007 all exist as cited |
| 4 | No `BC-x.yy.zzz:NN` / `ARCH-xx:NN` line pointers added in the diff | PASS | Sole pattern hit on added lines is a byte-identical carry-over inside VP-011's modified-frontmatter history (entry 1.3, pass-2 provenance), present on both the removed and added sides of the line rewrite; nothing newly minted (note N4) |
| 5 | VP `bcs:` lists vs VP-INDEX coverage map; recount of directed VP→BC edges | PASS | Scripted recount over all 41 VP files: 285 directed `bcs:` edges (matches the expected 285 and VP-INDEX entry 1.23's claim); 154 BC coverage-map rows; 0 forward-only; 0 map-vs-frontmatter mismatch on either direction |
| 6 | Every changed file's frontmatter parses | PASS | All 97 diff files pass the prescribed yaml.safe_load check; zero failures |

## Per-call detail (check 2)

| Call | Rule located |
|------|--------------|
| 1 | BC-6.03.002 PC-1 + EC-006, VP-009 (normalization clause), VP-011, VP-034, BC-6.01.002 PC-4 (conversion named beside the encoding env pin): comparator converts the oracle's Windows CRLF to LF openly before byte comparison; hylo's bytes never converted; shim does no newline reconfigure |
| 2 | BC-6.01.002 body: canonical temp-file case declares the fake process table (fake `ps` on the conditional fake PATH for the oracle, a `ProcStarter` fake for Go), needs no `proc_start` seed, is the fake-PATH machinery's FIRST P1 consumer (old "no P1 consumer" note only in frontmatter history) |
| 3 | BC-6.02.003 PC-5, BC-6.01.002 PC-1/PC-2, VP-034: case-set metrics URL used on BOTH sides, admitted only as a placeholder resolving to the fake server (optional path suffix), one value per key |
| 4 | interface-definitions Default cells re-spelled to env spellings (reroute prefix list, both band pairs, percentiles, the rate-gate map); BC-2.01.004 PC-9 reroute default respelled (1.3.5); BC-2.01.004's lettered registry-defect list item (c): the default must pass the key's own type + range validation |
| 5 | prd.md section 3.2 and interface-definitions objects-read list rebuilt from every stdin `.get(` — fields legacy never reads removed, reads legacy makes added (both files enumerate the same set in their pass-11 changelog entries and the added fields are present in both bodies) |
| 6 | cicd-setup coverage job + gate rows, ARCH-08: committed manifest lists gated packages present and grows as each lands; `G == 0` allowed while none of the three gated packages exists; Go statement coverage named and the per-package figure derived from the merged `-coverpkg` profile; Tier B and machinery tests credited |
| 7 | cicd-setup, ARCH-08 hygiene bullet, VP-035, BC-6.04.001: scanned rev set = compared rev set, both pinned to exactly the two branch refs |
| 8 | BC-6.01.001 PC-7, BC-6.04.001 PC-3, ARCH-07 (bound selector table), ARCH-08, cicd-setup: single `ORACLE_TESTS` -run/-skip mechanism covers the Tier A corpus, shim canary, four-cache swap and any future oracle-dependent test; the minted `oracle` build tag withdrawn the same pass |
| 9 | ARCH-03 step 0 + struct comment, ARCH-04, ARCH-05 platform rows, BC-3.01.001 EC-004: a `CacheDir` error at startup wires the load-empty / save-no-op store (never a config error); `Env.Loc` derived exclusively from `LocalZone` with the error disposition stated |
| 10 | VP-021: percentile property derived from BC-1.05.005 exactly — two lists (dollar vs rate), per-src `api_ms` gate with both cap values, self-exclusion of the current sid, NaN finite restriction (EC-009) normative in the Method |
| 11 | BC-1.03.007 canonical CP-O07 vector: `lu` null pinned with the SL:1085 rationale, three timestamps stated (20-char Z stamps, byte sizes, total), row-107 code span closed; every expected-cache field re-walked |
| 12 | VP-031 (fallback `v` inserted AFTER `k` and `f`, SL:344-345; key-order table grown to 24 rows including the 8 fallback-v subsets) and BC-1.04.003 (names the four varied series v/k/f/p and pins the fallback position) |
| 13 | Left-closed `[1970-01-02T00:00:00 local wall, year 3001)` stated once and identically in BC-5.04.001, BC-5.04.002, BC-6.04.003; contradictory zone-offset wording dropped (under the TZ=UTC parity pin the boundary probe lands inside the MSVC domain) |
| 14 | error-taxonomy CP-S table defines the six range-only ids with (id, site, owner BC/EC); each owning EC names its id with trigger and raise site; ARCH-03 cites the taxonomy (inputs list + crash-path-register prose) |
| 15 | BC-6.01.001 PC-4 self-check adds the normpath NUL-retention probe (both path flavors keep the NUL, orchestrator-measured) and ARCH-07's self-check list carries it |

## Notes (hygiene-reviewed observations; no action required)

- N1: The `newline` grep hits are the withdrawal record itself (BC-6.01.002 "the former
  `newline=...`" clause; VP-034 "wording withdrawn"). No live shim-reconfigure claim remains.
- N2: The remaining "case value wins" phrasings are (a) frontmatter history entries dated to
  earlier passes and (b) live body text that already states BOTH sides. BC-6.02.003's 1.2.13
  history entry retains the older one-sided phrasing as provenance; its live PC-5 (1.2.14) and
  body state the both-sides rule.
- N3: `--log-opts="--all"` and a `1.26.x` toolchain mention survive only as (a) the cicd run
  log's historical account of the initial scan and (b) provenance quotations of the upstream
  design document (BC-6.04.001 Source row, toolchain-ordering note). Live rules everywhere
  state the two-ref scan and the 1.26.0 floor leg.
- N4: Diff-added lines were swept for `BC-*.yy.zzz:NN` and `ARCH-NN:NN` pointers; the single
  hit is unchanged pass-2 history text reflowed by a frontmatter append (SC-32 precedent:
  history entries are provenance, not rewritten).
- N5: Reading note for check 1 — env names are carried in the two registries
  (interface-definitions, BC-2.01.004 PC-13); the consuming postconditions name key, default,
  site and ruling but not the env name, which matches the plan's routing ("registers them ...
  with env names" = agent 2's registry).

## Closing fixes

None. No blocking finding; the gate is PASS. The diff is consistent with the pass-11 plan,
OD-194 is propagated to all three anchors (registries, log, consumers), and the VP coverage
recount independently reproduces 285.

Consistency score for this scope: 100% (6/6 checks pass, 15/15 calls verified present).
