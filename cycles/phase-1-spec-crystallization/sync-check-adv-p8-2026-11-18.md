---
document_type: consistency-report
level: ops
version: "1.0"
status: "pass"
producer: consistency-validator
timestamp: 2026-11-18T15:38:08Z
phase: 1
input-hash: "dd17643"
inputs: [specs/behavioral-contracts/, specs/verification-properties/, specs/architecture/, specs/domain-spec/, specs/prd-supplements/, specs/prd.md, specs/cicd-setup.md, specs/dtu-assessment.md, specs/owner-decisions-log-2026-11-14.md, adversarial-reviews/pass-8.md, adversarial-reviews/ADV-P8-INDEX.md, pass-8-remediation-plan.md]
traces_to: ../../STATE.md
---

# Consistency Validation Report: hylo pass-8 fix-burst sync check

## Report Metadata

| Field | Value |
|-------|-------|
| **Product** | hylo (status line + hybrid routing, P1 spec crystallization) |
| **Generated** | 2026-11-18T15:38:08Z |
| **Generator** | consistency-validator (fresh context; scripted sweeps under `/opt/homebrew/anaconda3/bin/python3 -I` 3.11.7 plus targeted file reads) |
| **Artifacts Scanned** | 112 dirty spec files vs `HEAD` (+1392/−681); 244 spec `.md` files (behavioral-contracts 156 incl. allocation/index, verification-properties 42 incl. index, architecture 10, domain-spec 9, prd-supplements 7, root 7+1) |

## Summary

| # | Check | Result |
|---|-------|--------|
| 1 | L2 to L3 Requirement Coverage | pass (registry/anchor closures: C2-01, D14, D11) |
| 2 | L3 to L4 Verification Property Coverage | pass (269-edge union bijection; check 7) |
| 3 | Dependency Acyclicity | N.A. at Phase 1 — no story graph yet; spec cross-references untouched by cycles (append-only ID minting) |
| 4 | Architecture Alignment | pass (signature identity, walk rule, metrics trio; checks 3, 8) |
| 5 | Acceptance Criteria Quality | pass at spec stage (BC postcondition completions: C2-04, C04, B-series) |
| 6 | Story Sizing (all <= 13 points) | N.A. — Phase 1 precedes story decomposition |
| 7 | Priority Consistency | N.A. at story level; PRD priorities unchanged by the burst |
| 8 | L1 to L2 to L3 to L4 Chain Completeness | pass (no orphans introduced; edge recount clean; title quadruple 154/154) |
| 9 | AC Completeness Coverage | pass at spec stage (clause-level reciprocity: C03, VP-INDEX union) |
| 10 | ASM/R Traceability | pass (OD-192 capture-timing wording landed: A2-12, D10) |

Detail for every row: sections "Burst-sync check matrix" (rows 1-10) and "Finding
disposition" below. Story-graph rows (3, 6, 7) are explicitly out of scope for a
Phase 1 spec-crystallization artifact and are marked N.A. rather than assumed.

**Scope note.** Fresh-context post-remediation sync check for adversarial pass 8, before
the pass-9 decision. Inputs: `adversarial-reviews/pass-8.md` (88 verbatim findings:
HIGH 12 / MEDIUM 36 / LOW 33 / COSMETIC 7), `adversarial-reviews/ADV-P8-INDEX.md`,
and the ruling/calls in `pass-8-remediation-plan.md` (OD-193; calls 1-19). The one
owner ruling is verified in `specs/owner-decisions-log-2026-11-14.md` (next free
OD-194) and, per instructions, every fix is spot-verified **on disk in the current
working tree**, not from history lines. The orchestrator's pre-declared dispositions
(C02 REJECTED, D06 already fixed, D20 corrected wording, D09 per ARCH-05, C05 rides
OD-186) are verified as reflected, not re-litigated. Read-only on specs; nothing
committed. Findings continue the sync-check numbering lineage (SC-01..31 consumed
by passes 3-7). Repo-relative paths throughout.

## Headline result

**87 of 88 pass-8 findings verified CLOSED on disk; 1 REJECTED-with-evidence (C02,
the orchestrator's re-measurement, now reflected in the specs); 0 OPEN.** OD-193 is
logged and propagated at all six sites. All 10 orchestrator-declared checks pass
clean. One new cosmetic sync-check finding is recorded (SC-32, provenance history
only). Validation gate: **PASS**.

## 1. Finding disposition (87 CLOSED / 1 REJECTED / 0 OPEN)

Perimeter A — A01 specs/prd-supplements/interface-definitions.md:316 (denominator
owner re-anchored to BC-1.02.006; no BC-2.01.006 remains); A02 specs/prd.md:488 +
specs/prd-supplements/nfr-catalog.md:25 (NFR-002 trigger lists end CP-T09) +
specs/architecture/ARCH-07-parity-harness.md:179 (case-id grammar gains `cpt09`,
Windows-only note, cpt08 retired-not-reused); A03 specs/architecture/ARCH-08-build-ci-release.md:48,85-95 +
specs/cicd-setup.md:58 (coverage job ubuntu, same Tier A exclusion as the plain test
step, no interpreter, 10-minute timeout kept, in-process S1/S5 coverage, fail-on-absent
or `[no statements]`); A04 specs/prd.md:136 + nfr-catalog.md:76-81 (S1/S5-only gate,
parity reported-not-gated — see section 2); A05 ARCH-08:147-152 (fail condition names
the gated packages by name — `internal/statusline`, `internal/cost`, `internal/pyfmt` —
no count word); A06 specs/cicd-setup.md:52 (macOS/Windows test legs install no
interpreter; superseded "Tier A inside the plain test step" rationale removed; matches
ARCH-08:60-63); A07 specs/architecture/ARCH-02-configuration.md:46 + specs/architecture/ARCH-05-platform.md:82
(no-argument resolver forms eliminated); A08 specs/architecture/ARCH-01-binary-cli.md:156 +
ARCH-02:154 + ARCH-05:19 + ARCH-07:20 + ARCH-03:42-43 ("Phase 6 target, not a P1 gate"
qualifier at all five loci); A09 specs/prd-supplements/test-vectors.md:46 (BC-1.05.005
in the OD-156 owner list); A10 specs/architecture/ARCH-07-parity-harness.md:156
(metrics fake = raw net.Listener, "not httptest", citing ARCH-03's TEST SEAM ruling); A11
specs/prd-supplements/error-taxonomy.md:87 + interface-definitions.md:219-226 (whole-key
D4-EX-3 naming rule); A12 interface-definitions.md:125 (`Float triple` shape name for
`statusline.theme.heat`); A13 specs/architecture/ARCH-00-overview.md:21 (prd.md:68) +
specs/architecture/ARCH-06-pyfmt.md:195 ("Two width functions" pointer fixed).

Perimeter A2 — A2-01 specs/verification-properties/VP-001-never-blank-exit0.md:63
(CP-O06..O08 skip-and-render per OD-156/OD-167; no degrade); A2-02 VP-001:38 + :192
(closed trigger catalogue and cpt families gain CP-T09/`cpt09`); A2-03
specs/verification-properties/VP-008-effect-order-preservation.md:40 (step-7c
record_cost persistence and step-2 skip promoted from sketch to statement); A2-04
specs/verification-properties/VP-026-pyfmt-time-equivalence.md:41 (third outcome
msvcDomain + ErrLocaltimeDomain stated; sketch err-handling fixed); A2-05
specs/verification-properties/VP-012-exclusion-set-closure.md:113 (riders =
BC-1.02.017 EC-004..006 + BC-1.01.008 PC3; see check 5); A2-06
specs/verification-properties/VP-INDEX.md:31 + VP-012:40 ("the D4-EX-1 rider",
never "the OD-160 rider"); A2-07 VP-004:51 (for-all argv/env/stdin incl. subagent
NDJSON), specs/verification-properties/VP-016-config-error-classes-line.md:43 (every
env map; config-error line iff validate exits non-zero, subagent exception named),
specs/verification-properties/VP-029-transcript-parse-tables.md:65 +
specs/verification-properties/VP-013-d4ex2-wrong-shape-tables.md:38 (delete-the-line
equivalence fuzz legs), specs/verification-properties/VP-024-pyfmt-json-equivalence.md
(bcs: gains BC-1.05.009 per VP-INDEX 1.18/1.19), specs/verification-properties/VP-020-cost-history-integrity.md:58
(testing/quick rows), specs/verification-properties/VP-030-telemetry-row2-tables.md:56
(quick leg lists BC-1.04.003/.008/.015/.018/.019); A2-08 VP-016:43 (OD-168 subagent
zero-stdout exception); A2-09 specs/verification-properties/VP-019-four-cache-swap-parity.md:41
(exclusion carve-out on byte-identical claim); A2-10
specs/verification-properties/VP-013-d4ex2-wrong-shape-tables.md:38 (CP-O row placement
clarified); A2-11 specs/verification-properties/VP-007-render-determinism-seams.md:95
(sketch measures the rendering copy and asserts the single clock read); A2-12
specs/dtu-assessment.md:55 (ASSUMP-107-1 before the Phase 2 S1.07 stories, per OD-192); A2-13
specs/domain-spec/invariants.md:46 (DI-008 cited by 85); A2-14 invariants.md:30
(revisit-flag wording per OD-125); A2-15 VP-004:39 (bare `hylo`/unknown verb exit-2
surface and subagent states); A2-16 VP-016:135 (`TestTheme_RejectionLines` in Named
Tests); A2-17 specs/verification-properties/VP-022-ledger-read-scope-absence.md:70 +
specs/behavioral-contracts/ss-01/BC-1.04.001.md:172 ("minimal HTTP/1.1 client over
net.Conn", Proxy-nil residue removed); A2-18
specs/verification-properties/VP-011-tier-c-differential-fuzz.md:47 (OD-190 Windows
oracle LF normalization stated normatively); A2-19 VP-030:152
(`TestMetricsClient_OD181_TransportTable` in Named Tests).

Perimeter B — B01 specs/behavioral-contracts/ss-01/BC-1.02.030.md:58,92,125,141
(trigger = any configured prefix, trailing `*` stripped, a member of
`statusline.lane.reroute_all_prefixes`; the marker key is the membership set, not the
trigger; config-keys row carries both `backends[0].model_prefixes` and the marker key;
EC-010 states legacy degrades on `{"five_hour":"x"}` under the default prefixes); B02
specs/behavioral-contracts/ss-01/BC-1.01.007.md:52 (row-2 omission conditioned on
`narrow_cols`); B03 specs/behavioral-contracts/ss-01/BC-1.01.003.md:93 (dead-marker `?`
= `label_local` + literal " ?" per OD-189/BC-1.04.004; `label_unknown` consumer =
BC-1.02.001 only); B04 specs/behavioral-contracts/ss-01/BC-1.01.008.md:38,45,117 (OD-183
triplet stated; PYTHONIOENCODING, UTF-8/LF everywhere, variable-changes-stdio-only
table test; OD-190 cited); B05 BC-1.02.014.md:85 + BC-1.02.025.md:71 (ranges {`k`},
{`M`} default-only, matching the registry; the alternate spelling a registered render
semantic, not an accepted value); B06 BC-1.01.009.md:71 (CP-C09 faults BEFORE the
write; PC2 lists only CP-C10 as the within-step exception); B07 BC-1.01.009.md:116
(shrunk-transcript reset/save and grown-no-complete-line no-save distinguished); B08
BC-1.02.012.md:69 + BC-1.02.016.md:53 + BC-1.02.007.md:55 (named-format-constant,
not-config rationale on the three display literals); B09 BC-1.02.006.md:148 (percent
width counts the trailing `%`); B10 BC-1.02.011.md:90 + BC-1.02.012.md:88 (drop at the
SL:510 `any(...)` check); B11 BC-1.02.017.md:90 (EC-007 anchor/tag) +
BC-1.01.009.md:141 (VP-022 row mirrored in VP Anchors).

Perimeter C — C01 specs/behavioral-contracts/ss-01/BC-1.07.007.md:125 (Infinity row
re-pinned pure-ASCII with the CTV byte-notation note at :112-113, `\e` = ESC, as
BC-1.07.001; wire never carries raw non-ASCII); C02 **REJECTED** (see below); C03
BC-1.03.014.md:99 + BC-1.03.016.md:73 (dedicated-test lists and VP rows gained
VP-013/VP-012) + BC-1.03.002.md:87 + BC-1.03.005.md:65 (OD-160 foreign-cache legs cite
VP-012; reciprocity delivered in VP-012/VP-013 `bcs:` per VP-INDEX 1.19); C04
specs/behavioral-contracts/ss-01/BC-1.07.008.md:89 (end-to-end closed-stdout oracle:
buffered rows exit 120 at shutdown flush, guard not entered; OD-172 unchanged); C05
specs/behavioral-contracts/ss-01/BC-1.06.001.md:120 (EC-009 cites the OD-186 temp-file
widening — rides the ruling, no new id); C06 BC-1.03.018.md:101 (raise-site list
reconciled with BC-1.03.010 EC-009).

Perimeter C2 — C2-01 all nine consumer BCs name their glyph keys:
BC-1.04.005.md:57, BC-1.04.007.md:62, BC-1.04.008.md:52, BC-1.04.010.md:54,
BC-1.04.011.md:52, BC-1.04.012.md:58, BC-1.04.017.md:53, BC-1.04.018.md:54,
BC-1.05.003.md:70 (see check 6); C2-02 BC-1.04.001.md:128 + :161 (followed-3xx body
drained under the same framing; drain failure = no sample); C2-03 BC-1.04.001.md:107
(chunked iff `tr_enc.lower() == "chunked"` exactly; other values fall to
Content-Length/EOF); C2-04 BC-1.04.002.md:78 (SL:335 comprehension and SL:356
fetch-failure sites added to Inv 1); C2-05 BC-1.04.003.md:131 + BC-1.05.005.md:135
(DI-008 lifted into both); C2-06 specs/verification-properties/VP-020-cost-history-integrity.md:58
(positive-huge api_ms degrades CP-O11; usd degrade at the `.2f` format SL:616); C2-07
BC-1.05.009.md:121 (row rerouted to VP-024 with the pass-8 call-12 rationale) +
BC-1.05.004.md:133 + BC-1.05.006.md:121 (testing/quick rows to VP-020); C2-08
VP-030:56 (quick leg carries all five BCs); C2-09 VP-030:94 (transport table pins the
crypto/tls client; only the parity corpus is plain http); C2-10 BC-1.04.001.md:292
(ARCH-03 anchors 187/266); C2-11 specs/prd-supplements/test-vectors.md:14,45
(BC-1.04.004 HAS a CP-N03 vector row stated); C2-12
specs/architecture/ARCH-03-statusline.md:196 (Accept-Encoding-first order) + :211
(non-http(s) = D4-EX-3 URL class, out of OD-181 scope); C2-13 BC-1.04.001.md:95,107
(`_MAXHEADERS` 100, 65536-byte line limit, interim-1xx skip); C2-14
BC-1.05.006.md:92 (`statusline-True.json` Python-str spelling pinned); C2-15
BC-1.05.008.md:52 (lane defaults pinned in PC-3).

Perimeter D — D01 specs/behavioral-contracts/ss-03/BC-3.01.001.md:59-64 (all three
resolvers `(env EnvVars) (string, error)`, Inv 1 exceptions) +
specs/behavioral-contracts/ss-02/BC-2.03.002.md:74-79 (env-seam signatures) +
ARCH-02:46 + ARCH-05:27; D02 specs/behavioral-contracts/ss-05/BC-5.04.002.md:89 (rule
lives in pure pyfmt, no platform import; ARCH-05:34 agrees); D03
specs/behavioral-contracts/ss-05/BC-5.02.003.md:52 (stdin and cache loaders are
whole-input reads; only the transcript is line-split); D04
specs/behavioral-contracts/ss-02/BC-2.01.005.md:73,156 (List-entry validation and the
Text-class control-byte reason made normative; BC-2.02.001.md:116 agrees); D05
BC-2.01.005.md:136-156 (reason strings enumerated without the stale count; PC-6 gains
the control-byte rule) + BC-2.02.001.md:148-151 ("the six `expected ...` reasons";
"BC-2.02.003 mints only number-grammar reasons"); D06
specs/prd-supplements/interface-definitions.md:239,242 (Default cells re-spelled to the
env spellings `5h,7d` and `[0.22,0.85,0.80]` — landed by agent 2, verified); D07
BC-2.01.005.md:41 (H1/Description/Pre-1 cover PC-5/PC-6/PC-7); D08
specs/behavioral-contracts/ss-02/BC-2.01.004.md:108 (PC-3(f) names
`rename_retry_delay_ms`/`rename_retry_limit` as the no-legacy-analog exceptions) +
BC-3.01.001.md:98 (Inv 1 says so); D09 specs/behavioral-contracts/ss-03/BC-3.02.001.md:91-97
(walk TERMINATES with result None on guard rejection — ruled design per ARCH-05, pass-8
call 15; table leg matches); D10 BC-3.02.002.md:55 (all OD-76 D1-D4 vectors are Go
table tests; corpus stays UTC-only) + BC-6.01.002.md:91-96 (fake-`PATH` machinery has
no P1 consumer); D11 specs/behavioral-contracts/BC-ALLOCATION.md:267 (title =
BC-3.01.001 H1 = BC-INDEX:231 = prd:325); D12 specs/behavioral-contracts/ss-04/BC-4.01.001.md:52
(`run(os.Args[1:], env, stdin, stdout, stderr)`; `runStatusline(env, stdin, stdout,
stderr)` takes no arg slice) matching ARCH-01:44-45; D13
specs/behavioral-contracts/ss-06/BC-6.01.002.md:137 (`EnvVars.Lookup(name) (string,
bool)`); D14 BC-6.03.004.md:147 (union claim reconciled with BC-2.02.002:138 case
list, `1e400` as EC-004); D15 BC-2.01.005.md:93 (strict-JSON overflow classification;
`FloatQuad` in the PC-5 type list); D16 BC-3.01.001.md:94 (TZ-unset leg oracle
qualified runner-relative: assert non-nil zone + nil error); D17
specs/behavioral-contracts/ss-02/BC-2.01.002.md:88 (Windows case-fold tie-break and
index-≠-0 field validation pinned); D18
specs/behavioral-contracts/ss-02/BC-2.03.001.md:55 (own emission order stated, no
borrowed statusline claim); D19 specs/behavioral-contracts/ss-06/BC-6.04.002.md:103
(">512 KB" = more than 524,288 bytes, 512 KiB, equal to the `transcript.read_cap_bytes`
default); D20 specs/behavioral-contracts/ss-05/BC-5.02.005.md:75-86 (**corrected to
"no `Str` recursion outcome is reachable from stdin"** per the orchestrator end-to-end
measurement: document depth 987..991 renders normally with full repr, exit 0; 992
(depth 994) fails the stdin decode to `{}`; the 989 degraded-line vector withdrawn;
Str must not impose a lower nesting limit than the decode allows); D21
specs/behavioral-contracts/ss-05/BC-5.04.003.md:75 (whole-second branch noted, 2^62
bound); D22 specs/architecture/ARCH-06-pyfmt.md:32 (per-flavor owner re-anchored to
BC-1.02.004); D23 specs/behavioral-contracts/ss-04/BC-4.01.002.md:108 (VP-002 row
carries the `--subagent` carve-out); D24 specs/behavioral-contracts/ss-06/BC-6.01.003.md:124
(non-ASCII code point).

### The one REJECTED finding

| ID | Disposition | Evidence on disk |
|----|-------------|------------------|
| ADV-P8-C02 | REJECTED per the orchestrator's re-measurement: a 993-deep transcript line saves cleanly — the perimeter's reachability arithmetic was wrong, and the two target documents now state the corrected, measured basis instead of the old "flat payload" wording | specs/architecture/ARCH-03-statusline.md:168-170 ("mix … 991 / 994 — cur.id/cur.out carry input nesting; save failure unreachable: payload 994 saves / 995 fails, above the 993 transcript decode edge (pass-8 residual sweep)") and specs/behavioral-contracts/ss-05/BC-5.02.006.md:93 ("pass-8 re-measurement, agent 6 + orchestrator re-verification: payload 994 saves / 995 fails; NOT flat — cur.id/cur.out carry input nesting; the save failure is unreachable from stdin because the transcript decode edge 993 binds below this save boundary"). VP-029's property is therefore correct as scoped to stdin-decodable lines; BC-1.03.021's tables needed no new edge case. |

## 2. OD-193 propagation (task check 2)

OD-193 (owner, 2026-11-18): OD-158 stands unchanged — the P1 >=95% line-coverage gate
covers S1 (`internal/statusline`, `internal/cost`) and S5 (`internal/pyfmt`) only;
`internal/parity` (S6) coverage is reported, not gated; pass-7 call 12's addition of
`internal/parity` to the gate is withdrawn.

| Site | Line(s) | Wording |
|---|---|---|
| specs/owner-decisions-log-2026-11-14.md | pass-8 ruling block | Full ruling; "next free OD-194" advanced |
| specs/prd.md | 23 (v0.2.17 note), 134-136 (§1 gate-scope sentence) | "records OD-193: S6 internal/parity coverage is reported, not gated" |
| specs/prd-supplements/nfr-catalog.md | 76-81 (NFR-002 gate prose), 65 (S1/S5-restricted "only additional P1 exit gate") | "Gate scope is settled by OD-193 … reported, not gated; pass-7 call 12's addition … is withdrawn" |
| specs/prd-supplements/module-criticality.md | 37-40 | identical S1/S5-only scope, parity "reported, not gated" |
| specs/architecture/ARCH-08-build-ci-release.md | 48 (job graph), 85-95 (narrative), 147-152 (fail scope), 170 (mitigation) | S1/S5 packages gated by name; "internal/parity (S6) coverage is PROFILED AND REPORTED, not gated — OD-193 withdraws pass-7 call 12's addition" |
| specs/cicd-setup.md | 58 (job row), 87 (gate row), 144-149 (binding prose) | same scope; "OD-193 withdraws pass-7 call 12's addition of the referee to the gate" |

No contradicting wording anywhere in the tree; the mutated gate rows all name the three
gated packages and mark the parity figure informational.

## 3. Burst-sync check matrix (10/10 executed)

| # | Check (orchestrator wording) | Result |
|---|------------------------------|--------|
| 1 | Every finding CLOSED / REJECTED-with-evidence / OPEN | PASS — 87 CLOSED (table above), 1 REJECTED (C02, disposition verified reflected in ARCH-03 and BC-5.02.006), 0 OPEN; every fix verified in current working-tree content, none from history lines |
| 2 | OD-193 consistent everywhere (gate = S1 + S5 only; parity reported not gated) | PASS — all six sites agree (section 2); the withdrawn pass-7 widening is named and reversed at every site that had it |
| 3 | Platform signatures (call 7) identical across ARCH-01/02/04/05, BC-3.01.001, BC-2.03.002, BC-4.01.001, BC-6.01.002 | PASS — `CacheDir(env EnvVars) (string, error)`, `StateDir(env EnvVars) (string, error)`, `ConfigDir(env EnvVars) (string, error)`, `LocalZone(env EnvVars) (*time.Location, error)` byte-identical at ARCH-02:46-47, ARCH-04:23, ARCH-05:27/34/82, BC-3.01.001:59-64, BC-2.03.002:74-79, BC-6.01.002:139-141; `run(args, env EnvVars, stdin, stdout, stderr)` and `runStatusline(env, stdin, stdout, stderr)` at ARCH-01:44-45 = BC-4.01.001:52; `Lookup(name) (string, bool)` at ARCH-01 = ARCH-02:41 = BC-6.01.002:137 |
| 4 | CP-T09 / cpt09 present wherever the trigger catalogue or case-id families are listed; register 48 paths | PASS — prd.md:488 (NFR-002 list ends CP-T09), nfr-catalog.md:25, ARCH-07:179 (families `cpt01..cpt07, cpt09`, cpt08 retired), VP-001:38/:192, E-REN-002 (prd.md:504) with BC-5.04.001 as carrier; register arithmetic 48 = 4+17+8+3+11+5 stated in error-taxonomy (1.11 history, "48-path" prose at :263) and VP-011:60 |
| 5 | OD-160 rider citations identical in BC-6.03.004 and VP-012 and resolving on disk | PASS — register row "riders: BC-1.02.017 EC-004..006, BC-1.01.008 PC3 directional tests" copied exactly into VP-012:113ff; EC-004/005/006 exist in BC-1.02.017 and the OD-160 clause lives in BC-1.01.008 PC3 (both read on disk); the `TestWindowAge_D4EX1_Windows_AncestorFound` label is "the D4-EX-1 rider" in both, no "the OD-160 rider" conflation survives |
| 6 | Glyph keys: every consumer BC named in BC-2.01.004 PC-6 names its key | PASS — scripted sweep of the PC-6 consumer set (telemetry_dot, cell_on/cell_off, box_rate, ttft, watts, idle, sess_rate, host, cost_pick, pill labels): every consumer BC names its key with the default in parentheses; zero misses (C2-01's eleven loci enumerated above) |
| 7 | VP `bcs:` ↔ BC VP-table reciprocity; VP-INDEX map = union of `bcs:` (edges recounted); 154 BCs, 41 VPs; title quadruple | PASS — independent recount: 154 BC files, 41 VP files, **269 directed `bcs:` edges** (= VP-INDEX v1.19's claim), coverage map = union exactly (0 diffs over 154 map rows), 0 forward-only, reverse-only residue exactly the standing 8 (3 design references VP-022/BC-1.06.001, VP-024/BC-1.07.004, VP-034/BC-1.01.004 + 3 removal-note citations VP-026 in BC-3.01.001/BC-6.01.002/BC-6.02.003 + 2 VP-041 scope-split mentions BC-1.02.008/.014); catalog class split invariant 33 / safety 7 / performance 1 re-derives; H1 = BC-INDEX = PRD §2 = BC-ALLOCATION title equality 154/154 escape-aware (D11's BC-3.01.001 row included) |
| 8 | Metrics-client statements (call 13) consistent across BC-1.04.001, ARCH-03, VP-030; all metrics fakes raw net.Listener | PASS — raw net.Listener fake ruling at ARCH-03:248 ("not httptest, whose server canonicalises"), BC-1.04.001:394, VP-030:99/113/161 and ARCH-07:157 (all remaining httptest mentions are negations or history); framing ladder, exact `lower() == "chunked"` rule, followed-3xx drain with no-sample-on-failure, `_MAXHEADERS` 100, 65536-byte line limit, interim-1xx skip, Accept-Encoding-first header order, and OD-181 scope (redirect targets and TLS trust only; non-http(s) = D4-EX-3) agree across the trio with no contradicting statement |
| 9 | Frontmatter: exactly one version and one modified key per changed file (block-style modified lists allowed); no duplicate keys | PASS — 112 changed spec files scanned; exactly one `version` key each; zero files with duplicate keys; zero files with more than one `modified` key; 48 files use block-style `modified:` lists (explicitly allowed); the rulings log carries no frontmatter (established design, unchanged) |
| 10 | Hygiene on the diff (added lines) | PASS — 1374 added lines reviewed: no absolute paths; no IPv4 outside 192.0.2.x/127.0.0.1; no email addresses; no hostname/domain leakage beyond allowlisted documentation domains; no carriage returns. Non-ASCII inventory (42 distinct characters) is typography and mathematics (em-dash, arrows, minus, ≤/≥/≈/≠/±/×, superscripts), the legacy glyph defaults the specs are required to name (◉ ◔ ⚡ ☾ ▣ ▰ ▱ » ⛏ ↺ ✔ and the bar ramps), and the Arabic-Indic and ░-style test-vector digits D15/D19 fixes must carry; no emoji-block characters, no non-English prose |

## 1. L2 to L3 Requirement Coverage

Registry and anchor closures hold: the L2-adjacent registry (specs/prd-supplements/interface-definitions.md)
re-anchors its unit-selector owner to BC-1.02.006 (A01), names the glyph-key consumer set
exhaustively against BC-2.01.004 PC-6 (check 6), and its Default cells carry the env
spellings (D06). BC-ALLOCATION title sync restored (D11). No capability loses its owning
contract in this burst; the CAP→BC spine is untouched apart from anchor repairs.

## 2. L3 to L4 Verification Property Coverage

Verified by independent recount (check 7): 154 BCs ↔ 41 VPs, 269 directed `bcs:` edges,
VP-INDEX coverage map exactly the union of `bcs:` (0 diffs), 0 forward-only, reverse-only
residue exactly the standing 8 enumerated residuals. Burst-specific closures: C03 (VP-012
gains BC-1.03.002/.005/.014/.016; VP-013 gains BC-1.03.014/.016), C2-07 (VP-024 gains
BC-1.05.009; VP-020 gains the testing/quick rows), A2-07 leg homes (VP-004/016/029/013/030),
A2-19 (VP-030 Named Tests). Every pass-8 VP change is reciprocated.

## 3. Dependency Acyclicity

N.A. at Phase 1 — no story dependency graph exists yet (story decomposition is Phase 2).
Nothing in this burst introduces a cycle in the spec cross-reference graph: all ID minting
in the touched files is append-only (CP-T09 appended, CP-T08 retired-not-reused, no suffixed
IDs), and the directed `bcs:` relation re-verified as a clean bipartite coverage relation
(check 7), not a cyclic one.

## 4. Architecture Alignment

Signature identity across eight documents (check 3): the four resolver/quartet signatures,
`run`/`runStatusline` and `EnvVars.Lookup` now agree byte-for-byte at every site (A07, D01,
D12, D13). The ARCH-05 walk-terminate rule is adopted by BC-3.02.001 (D09). The metrics
trio (BC-1.04.001 ↔ ARCH-03 ↔ VP-030) is coherent over the raw-net.Listener seam (check 8).
Kill-rate qualifiers (A08) and the coverage-gate fail scope (A03/A05, OD-193) align
architecture with the CI documents.

## 5. Acceptance Criteria Quality

At spec stage the AC-equivalent surfaces are BC postconditions and VP properties: both were
the objects of the burst (C2-04 invariant completion; B-series postcondition repairs; C04's
oracle-measured EC-009). Each remediated BC names testable outcomes (no "should" residue
found in the touched loci); the one untestable-rule finding (D08) closes by naming the
no-legacy-analog exceptions in the golden check.

## 6. Story Sizing

N.A. — Phase 1 precedes story decomposition; no story files exist to size. (Phase 2 will
bound stories at ≤ 13 points.)

## 7. Priority Consistency

N.A. at story level (no story dependencies in Phase 1). At spec level the burst introduces
no priority changes: PRD priority columns are untouched by the remediation diffs, and the
OD-193 gate-scope repair removes the inconsistency A04 identified between the architecture
gate and the PRD/NFR texts.

## 8. L1 to L2 to L3 to L4 Chain Completeness

No orphans introduced: the chain anchors (brief → domain spec → PRD/BCs → VPs →
architecture/CI) verify at every layer touched by the burst — PRD §2 title rows, BC-INDEX,
BC-ALLOCATION and H1s agree 154/154 (D11 included); CP-T09 propagates brief-ward through
E-REN-002 and NFR-002 into the parity grammar (check 4); the register stands at 48 paths
with CP-T08 retired-only everywhere found.

## 9. AC Completeness Coverage

Clause-level reciprocity is maintained: BC-2.01.005 PC-6 now mints every Text-class reason
its consumers (BC-2.02.001) derive tests from (D04/D05, with the control-byte rule
normative); the exclusion-set closure check in VP-012 covers every closed id and its riders
resolve on disk (check 5); the VP-030 quick leg carries all five routed BCs (C2-08). The
VP-INDEX union bijection (check 7) is the AC-completeness instrument at VP granularity.

## 10. ASM/R Traceability

The burst's only assumption-linked item closes cleanly: A2-12 re-words the ASSUMP-107-1
capture deadline to "before Phase 2 writes the S1.07 stories" per OD-192 (specs/dtu-assessment.md:55,
with the matching residual respells in BC-1.07.007 and BC-1.07.008 histories), agreeing with
assumptions-register.md and the OD log. Risk-linked knobs are otherwise untouched by the
diff; no ASM/R regressions found.

## Cross-Reference Validation

ID-vocabulary and cross-reference repairs verified byte-precise: the Text-class reason
counts (D05), the six-vs-five `expected ...` reconciliation (BC-2.02.001:148-151), CP-T09
in every catalogue that lists families (check 4), `cpt09` in the ARCH-07 case-id grammar
alongside retired-only CP-T08, and the env-spelling registry cells (D06). No stale count
survives as a live claim; the sole stale count resides in provenance history (SC-32).

## Spec vs Implementation Drift

N.A. — P1 spec crystallization precedes implementation (parity-first port not started).
The drift surface monitored at this stage is spec-vs-legacy parity, adjudicated by the
pass-8 perimeters themselves; the two legacy-behavior disputes this burst re-measured
(C02, C04, D20) now carry their measurements in the specs, keeping future drift auditable
against pinned evidence.

## 3a. New sync-check findings

| SC-NN | Severity | File:line | Inconsistency | Owner |
|-------|----------|-----------|---------------|-------|
| SC-32 | Cosmetic | `specs/verification-properties/VP-012-exclusion-set-closure.md:38` (v1.16 history entry only) | The pass-7 history entry still records the superseded OD-160 anchors ("BC-1.02.017 EC-010 and BC-1.01.008 EC-011"), corrected to EC-004..006/PC3 by the 1.19 entry. Provenance only, and the standing convention keeps history as-of-its-date (cf. SC-31a); the live register copy is correct. Remedy: none required; if touched, add "(superseded 1.19)" beside the old anchors. | architect |

### Critical
None.

### Major
None.

### Minor
None.

### Cosmetic
SC-32.

## Validation Gate Result

**PASS** — no blocking findings. The pass-8 remediation burst is fully propagated on
disk: 87 of 88 findings verified closed at their cited loci, the single rejection (C02)
is realized in the specs as a measured, dated reachability statement rather than a bare
dismissal, and OD-193 lands identically at every site the remediation plan names. The
machine-checked invariants all hold: 154/154/154/154 title quadruple-equality, the
269-edge `bcs:` bijection with the VP-INDEX coverage map exactly the union (0 diffs, 0
forward-only, residue exactly the standing 8), platform-signature identity across eight
documents, register 48 with CP-T09/`cpt09` at every catalogue, rider registers
identical and disk-resolving, glyph-key consumer closure, metrics-client trio
coherence over the raw-net.Listener seam, and clean frontmatter and hygiene sweeps.
SC-32 is a one-line cosmetic provenance note that can ride the next wording touch.

## Overall Metrics

| Metric | Value |
|--------|-------|
| **Pass-8 findings verified closed** | 87/88 (HIGH 11, MEDIUM 36, LOW 33, COSMETIC 7) |
| **Rejected with evidence** | 1 (ADV-P8-C02; disposition reflected in specs/architecture/ARCH-03-statusline.md:168-170 and specs/behavioral-contracts/ss-05/BC-5.02.006.md:93) |
| **Open** | 0 |
| **New sync-check findings** | 1 (SC-32 Cosmetic) |
| **Machine checks** | 95 scripted anchor batteries + structural/union/title/edge battery + frontmatter and hygiene sweeps, all adjudicated; 244 spec files swept, digest `1f4961d` (working tree) |

## Appendix: Validation Methodology

Fresh-context scripted sweep of the factory worktree's uncommitted spec tree
(`git diff HEAD` under `specs/`, 112 files, +1392/−681). Interpreter
`/opt/homebrew/anaconda3/bin/python3 -I` (CPython 3.11.7). Scripts (scratchpad, not
committed): (1) finding-by-finding anchor battery — 95 scripted loci tests against
`ADV-P8-INDEX.md`, the findings text and the remediation plan's calls, each PASS
requiring an on-disk regex hit at the cited locus; four initial misses were manually
adjudicated (A05 line-spanning regex, B05 backticked range spelling, C01 CTV note, D05
rewritten enumeration) and close; (2) structural battery — BC/VP file counts, `bcs:`
edge recount (269), VP-INDEX coverage-map union regeneration, forward/reverse residue
classification, and escape-aware title quadruple-equality across 154 H1s, BC-INDEX,
prd.md §2 and BC-ALLOCATION rows; (3) rider register cross-check (BC-6.03.004 ↔ VP-012)
with on-disk resolution of BC-1.02.017 EC-004..006 and BC-1.01.008 PC3; (4) glyph-key
consumer sweep from BC-2.01.004 PC-6; (5) metrics-trio coherence greps (ARCH-03 ↔
BC-1.04.001 ↔ VP-030 ↔ ARCH-07); (6) frontmatter duplicate-key/version/modified scans
over all changed files; (7) hygiene regexes over all 1374 added lines with a full
non-ASCII census. Manual reads adjudicated every scripted anomaly. The four
orchestrator dispositions were verified as reflected on disk (C02/D20 measurements,
D09 walk rule, C05 OD-186 rider, D06 agent-2 spellings). Nothing outside the report
path was written; nothing committed.
