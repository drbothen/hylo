---
document_type: verification-property
level: L4
version: "1.13"
status: draft
producer: architect
timestamp: 2026-11-18T21:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-01/BC-1.01.002.md, behavioral-contracts/ss-05/BC-5.02.003.md, behavioral-contracts/ss-01/BC-1.03.004.md, prd-supplements/nfr-catalog.md]
input-hash: "bdd7c3f"
traces_to: prd.md
source_bc: BC-5.02.003
bcs: [BC-5.02.003, BC-5.02.004, BC-1.01.002, BC-1.03.004, BC-1.07.003, BC-6.01.001]
module: internal/pyfmt (json.go)
proof_method: fuzz
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fixes — per-site table states both protocol sites at 993/994 (measured end to end on legacy 2026-11-17, superseding the 989/990 direct-probe figure); cache-load sites declared unmeasured/open, due before Phase 3 (A2-13); proof_file_hash field added (A2-29)", "1.3 2026-11-17: pass-2 follow-up — ADV-P2-A07 closed: governing formula limit = 999 − Python frames from <module> down to json.raw_decode recorded; all eight loader sites stated (stdin/transcript 993/994, session cache 991/992 and git cache 990/991 measured; get_sample, claude_window_start, mix cache and the cost-history loaders derived from equal chain depth); per-site measurement recipe added; harness asserts limit/limit+1 at every site", "1.4 2026-11-18T09:07:00Z: ADV-P3 fixes — main_subagent depth row added: same 6-frame chain as stdin, 993/994, over-limit input renders zero bytes (BC-1.07.003), not the degraded line (A2-22); line-number citations to BC-5.02.003 stripped in favor of content anchors (anchor drift, ADV-P3-D29)", "1.5 2026-11-18T14:38:00Z: ADV-P4 fixes — recipe observable corrected per BC-1.01.002: depth L+1 decodes to {} and renders the 45-byte default line, not the degraded line (A2-16); subagent chain re-labelled <module> → main_subagent (legacy calls main_subagent from <module>, SL:1240-1241); BC-1.07.003 added to bcs: to match the body's row (A2-11)", "1.6 2026-11-18T23:45:00Z: ADV-P5 fix (A2-05) — metrics-reply decode site added to the per-site table and harness: main → get_sample → fetch_sample → json.loads(resp.read()), 7 frames, 992 accepted / 993 rejected — MEASURED end to end (localhost HTTP reply carrying a nested list under an ignored metric key, isolated HOME/cwd per run, python3 -I, 2026-11-18), confirming the 7-frame derivation; BC-5.02.004 names metrics replies pyfmt.Value decodes, so a Go budget drift here is now detected", "1.7 2026-11-19T03:00:00Z: ADV-P5 residual fix — the ModeText cache-loader citation's line-number pointer replaced with the ARCH-04 heading fragment anchor (anchor-drift lesson, ADV-P3-D29)", "1.8 2026-11-19T12:00:00Z: pass-6 fixes (A2-17, OD-185: harness budgets are pinned literals (subagent row added; BC-5.02.004 in bcs:); production call sites reference named per-site constants; OD-185 oracle self-check leg re-measures the flip depths on the resolved 3.11.x oracle, fails closed, prints the resolved version)", "1.9 2026-11-19T18:00:00Z: pass-7 fixes (D04/call 7, A2-21) — the OD-185 self-check leg states BC-6.01.001 v1.2.4's ONE end-to-end definition and its measured constants (stdin decode 993 accepted / 994 rejected; session-cache save 991 writes / 992 skips; subagent wire 991 renders; unicodedata.unidata_version 14.0.0; CPython 3.11.7, default recursion limit 1000) instead of the skeleton's old helper-scope pair; Partial-coverage bullet names BC-5.02.004 and BC-1.07.003, matching bcs:", "1.10 2026-11-19T20:00:00Z: sync-check adv-p7 closure (SC-29) — bcs: gains BC-6.01.001, whose PC-4 states this VP pins the same measured self-check constants (reciprocity preferred over exception-listing, SC-13/SC-14 convention); no property or table change", "1.11 2026-11-20T12:00:00Z: pass-9 fix (A2-10) — the 'wrong budget at a production call site is a detected defect' claim given a mechanism that can fail: the harness table pins the SHARED production per-site constant symbols (not literal copies), so a drifted constant fails the pin row / ±1 boundary rows against the measured literals; the former all-literal rows compared two copies of the same number and could never fail; detection limits stated honestly — no end-to-end observable exists for the five derived sites, whose budgets are detected by the shared-symbol pin against the measured peer's flip (equal-chain-depth derivation, BC-5.02.003)", "1.12 2026-11-18T17:50:00Z: pass-10 fix (A2-05) — the 'wrong budget at a production call site is detected' claim given a mechanism that can fail ON GO: a call-site lint leg (TestDecode_CallSiteLint, AST scan via go/parser, the same offline mechanism as VP-012's test-registry correspondence) asserts each production pyfmt.Decode call site passes its OWN named per-site constant — the shared-symbol pin alone could not detect a mix-cache site passing BudgetStdin (993 instead of 991), and the OD-185 self-check runs on the Python oracle; the statement's honesty paragraph and Proof Method table state the two-leg detection (symbol pin + call-site lint)",
  "1.13 2026-11-18T21:00:00Z: pass-11 fix (B08, call 15) — the OD-185 oracle self-check gains the normpath-NUL probe: posixpath.normpath('a\\0b') and ntpath.normpath('a\\0b') must both KEEP the NUL (orchestrator-measured on CPython 3.11.7: both return 'a\\x00b'); a pre-gh-106242 CPython silently drops it, hollowing BC-1.02.022's PC3 `a\\0b` vector and EC-006; probe leg added to the self-check prose and the TestOracleSelfCheck_MeasuredConstants skeleton (BC-6.01.001's self-check definition carries the same probe, owner-agent 8)"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-006: Per-call-site JSON recursion depth budgets hold exactly

## Property Statement

`pyfmt.Decode` honours the per-call-site recursion budget exactly: the budget is an
explicit per-call-site argument (BC-5.02.003, depth-budget recipe), not baked into the decode mode.
Governing formula, validated end to end on the real legacy program with isolated HOME
(orchestrator, 2026-11-17): **limit at a call site = 999 − (number of Python frames
from `<module>` down to json's `raw_decode`)**. Each site flips at a single limit —
depth L accepted, L+1 rejected, no gap (BC-5.02.003, single-flip property); hylo's per-site budget
argument is derived from the observed flip depth, not a free constant.

| Call site (chain from `<module>`) | Frames | Accepted | Rejected | Status |
|---|---|---|---|---|
| stdin payload — main → json.load | 6 | 993 | 994 | measured |
| subagent stdin — <module> → main_subagent → json.load | 6 | 993 | 994 | measured; over-limit input renders zero bytes (BC-1.07.003), not the degraded line |
| transcript lines — main → _mix_counts → json.loads | 6 | 993 | 994 | measured |
| metrics reply — main → get_sample → fetch_sample → json.loads(resp.read()) | 7 | 992 | 993 | measured (localhost HTTP reply, 2026-11-18, ADV-P5-A2-05; BC-5.02.004 names metrics replies pyfmt.Value decodes) |
| session cache — main → effective_rl → load_cache | 8 | 991 | 992 | measured |
| get_sample loader (session-cache chain depth) | 8 | 991 | 992 | derived |
| claude_window_start loader (session-cache chain depth) | 8 | 991 | 992 | derived |
| mix cache — main → _mix_counts → load_cache | 8 | 991 | 992 | derived |
| git cache — main → render_lane → git_segment → load_cache | 9 | 990 | 991 | measured |
| cost history — record_cost / cost_thresholds (called from render_lane) | 9 | 990 | 991 | derived |

(stdin: BC-1.01.002 EC-005/EC-006; subagent stdin: same chain depth as stdin — the
observable over the wire is zero bytes at depth 994; transcript: re-measured end to
end 2026-11-17, superseding the 989/990 direct-probe figure quoted in an earlier
revision of BC-5.02.003. Cache loaders:
ADV-P2-A07 closed — session and git caches measured end to end; peer loaders derived
from equal chain depth; sites are ModeText ([ARCH-04, byte-exact cache-writer
decision](../architecture/ARCH-04-data-files.md#decision-go-is-byte-exact-cache-writer-and-reader-across-pythongo-swaps-ad-08).) Each measured site is tested
at exactly L accepted / L+1 rejected. Boundary values behave identically to CPython
3.11 `json.load`/`json.loads(bytes)`.

Measurement recipe (isolated HOME; a nested list grown under a key until the flip):
stdin — pipe the payload; depth L renders, L+1 decodes to {} and renders the 45-byte
default line (BC-1.01.002 — a decode-to-empty, not the degraded ladder). Transcript —
deep JSON line;
acceptance observable: the count shows in the mix-cache tin. Session cache — deep key
accepted: the key is kept after a run with rate_limits. Git cache — deep cache
accepted: the cached branch is shown. Metrics reply — a localhost HTTP server serves
the /api/v1/query reply with a nested list grown under an ignored `metric` key until
the flip; the observable is the row-2 telemetry regime (sample present vs no-sample);
isolated HOME and cwd per run, ADV-P5-A2-05, measured 992/993 on 2026-11-18.

## Source Contract

- **Primary BC:** BC-5.02.003 — json.loads(bytes) acceptance set (depth bounds).
- **Partial coverage:** BC-1.01.002 (stdin text-mode budget via Decode ModeText),
  BC-1.03.004 (transcript bytes-mode consumption), BC-5.02.004 (metrics replies are
  pyfmt.Value decodes — the metrics-reply row of the table), BC-1.07.003 (subagent
  stdin over-limit renders zero bytes — the subagent row's observable).
- **Invariant verified:** NFR-003 plumbing (hand-written decoder, banned stdlib codecs
  on protocol inputs, cannot silently change the budget).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** fuzz + boundary tables — generate deeply nested Values around each
  budget; assert accept/reject at budget-1, budget, budget+1 for both modes; fuzz for
  the absence of stack exhaustion below budget. Production call sites reference the
  SAME named per-site budget constants the harness table pins — shared symbols, not
  copies — so the boundary rows assert the production constants themselves against
  the measured flips: a drifted constant fails the pin row or the ±1 boundary
  assertion; a call-site lint (AST scan, skeleton below) additionally asserts each
  production call site passes its OWN named constant (pass-10 A2-05).
  Detection limits stated honestly (A2-10): an end-to-end observable
  exists only for the measured sites; the five derived sites (get_sample,
  claude_window_start, mix-cache and the cost-history loaders) ride the
  equal-chain-depth derivation (BC-5.02.003). Detection of a wrong budget has two
  legs (pass-10 A2-05): the shared-symbol pin proves the constant's VALUE equals the
  measured flip, and the call-site lint (AST scan, skeleton below) proves each
  production call site passes its OWN named constant — the pin alone cannot detect
  a mix-cache site passing `BudgetStdin` (993 instead of 991), and the OD-185
  self-check runs on the Python oracle, not on Go. No separate end-to-end depth leg
  exists for the derived sites, open since pass-2 and stated here.
  OD-185 + pass-7 D04: the harness self-checks the pinned constants
  against the resolved 3.11.x oracle at start, by BC-6.01.001's ONE end-to-end
  definition (drive the real oracle with the case argv and a temp HOME/cwd; assert
  stdin decode 993/994, save 991/992, wire 991 renders, `unidata_version` 14.0.0,
  and the normpath-NUL probe — `posixpath.normpath('a\0b')` and
  `ntpath.normpath('a\0b')` both KEEP the NUL, orchestrator-measured on CPython
  3.11.7: both return `'a\x00b'`, pass-11 call 15; a pre-gh-106242 CPython silently
  drops it, hollowing BC-1.02.022's PC3 `a\0b` vector and EC-006, pass-11 B08);
  fail closed on any
  mismatch, printing the resolved version; golden metadata records the resolved patch,
  VP-010/RK-4).
- **Honesty:** testable-only; the budget parameterisation is statically checkable
  (no global), the boundary rows are exact.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Boundary tables | Go test | yes — ±1 around each budget | both modes |
| Call-site lint (AST) | `go test ./internal/pyfmt -run TestDecode_CallSiteLint` | yes — finite call-site set | every production `pyfmt.Decode` call site passes its own named per-site constant (A2-05) |
| Fuzz | `go test -fuzz` | bounded runs | nested-input robustness below budget |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestDecode_DepthBudgetsPerCallSite(t *testing.T) { // A2-17: budgets are PINNED
    // literals in this table, not looked up from the test's own label (budgetOf) —
    // the flip assertions then fail any budget drift, not just Decode's obedience to
    // whatever it is handed. Production call sites reference the same named per-site
    // constants (below), so a call site passing the wrong budget is a compile-time
    // fix, and the harness asserts the constants equal the measured flips.
    cases := []struct{ name string; mode pyfmt.DecodeMode; budget, ok, reject int }{
        // budget: the PRODUCTION constant (shared symbol imported from its package);
        // ok/reject: the measured law's literals. A2-10: the former rows compared two
        // copies of the same number and could never fail.
        {"stdin site", pyfmt.ModeText, statusline.BudgetStdin, 993, 994},
        {"subagent stdin site", pyfmt.ModeText, statusline.BudgetSubagentStdin, 993, 994}, // A2-17: the :48 row is in the harness
        {"transcript site", pyfmt.ModeBytes, statusline.BudgetTranscript, 993, 994},
        {"metrics reply (get_sample → fetch_sample)", pyfmt.ModeBytes, statusline.BudgetMetricsReply, 992, 993}, // ADV-P5-A2-05, measured 2026-11-18
        {"session cache (+ get_sample, claude_window_start, mix cache)", pyfmt.ModeText, statusline.BudgetSessionCache, 991, 992},
        {"git cache (+ record_cost, cost_thresholds)", pyfmt.ModeText, statusline.BudgetGitCache, 990, 991},
    }
    for _, c := range cases {
        if c.budget != c.ok { t.Fatalf("%s: production constant %d ≠ measured flip %d", c.name, c.budget, c.ok) } // OD-185-style fail-closed pin; CAN fail now — production symbol vs measured literal (A2-10)
        if _, err := pyfmt.Decode(nested(c.ok), c.mode, c.budget); err != nil {
            t.Fatalf("%s: depth %d rejected", c.name, c.ok)
        }
        if _, err := pyfmt.Decode(nested(c.reject), c.mode, c.budget); err == nil {
            t.Fatalf("%s: depth %d accepted", c.name, c.reject)
        }
    }
}

func TestDecode_CallSiteLint(t *testing.T) { // pass-10 A2-05: the pin rows prove the
    // SYMBOL'S VALUE, not that each call site passes its symbol — a mix-cache site
    // passing BudgetStdin (993 instead of 991) passed every leg, and the OD-185
    // self-check runs on the Python oracle, not on Go. The lint walks the AST of the
    // packages owning the production Decode call sites (go/parser, the same offline
    // mechanism as VP-012's test-registry correspondence) and asserts each call's
    // budget argument is the named per-site constant its row declares; a literal or
    // a foreign package's constant fails the leg.
    for _, site := range DecodeCallSites() { // (pkg, ident) pairs mirroring the row table
        if got := CallSiteBudgetIdent(site); got != site.BudgetConst {
            t.Fatalf("%s: budget argument %q, want the named constant %q", site.Name, got, site.BudgetConst)
        }
    }
}

func TestOracleSelfCheck_MeasuredConstants(t *testing.T) { // OD-185 + pass-7 D04 (call 7):
    // ONE definition, stated in BC-6.01.001 v1.2.4 PC-4: the committed probe drives
    // the REAL oracle END TO END — the same argv as every case (PC-5), an isolated
    // temp HOME and cwd, deep stdin serialized by concatenation — never a
    // helper-scope surrogate. The constants are the LAWS' own constants
    // (BC-5.02.003/BC-5.02.006); BC-6.01.001, VP-006 and ARCH-07 state the same
    // values. Measured under this method: CPython 3.11.7, recursion limit 1000.
    v := resolvedOracleVersion() // printed once per Tier A run; Tier B golden
                                 // metadata records it (VP-010, RK-4)
    // stdin decode (BC-5.02.003 law, F = 6): 993 accepted, 994 rejected.
    if d := oracleStdinDecode(resolvedOracle, "--subagent"); d.accept != 993 || d.reject != 994 {
        t.Fatalf("resolved oracle %s disagrees with the pinned stdin decode flip 993/994", v)
    }
    // session-cache save (BC-5.02.006 json.dump law, s = 4): a rate_limits chain
    // nesting 991 writes the "rl" member; 992 skips the deep write (the observer
    // is the member, not the file — the later flat save still persists it).
    if s := oracleSessionSave(resolvedOracle); s.writesAt != 991 || s.skipsAt != 992 {
        t.Fatalf("resolved oracle %s disagrees with the pinned save boundary 991/992", v)
    }
    // subagent wire (BC-5.02.006 json.dumps law, s = 3): an id chain of 990
    // (wire object 991, stdin document 993) renders its row — the attainable
    // boundary; the next chain overruns the stdin decoder first (document 994).
    if !oracleWireRendersAt(resolvedOracle, 990) {
        t.Fatalf("resolved oracle %s disagrees with the pinned wire boundary 991", v)
    }
    if u := oracleUnicodeVersion(resolvedOracle); u != "14.0.0" {
        t.Fatalf("resolved oracle %s reports unicodedata %q, pinned 14.0.0", v, u)
    }
    // pass-11 B08 (call 15): normpath NUL retention — a pre-gh-106242 CPython drops
    // the NUL and would hollow BC-1.02.022's PC3 `a\0b` / EC-006 vectors.
    // Orchestrator-measured on 3.11.7: both path flavors return 'a\x00b'.
    if p, n := oracleNormpathNul(resolvedOracle); !p || !n {
        t.Fatalf("resolved oracle %s drops NUL in normpath — gh-106242 fix missing", v)
    }
}
```

## Named Tests (OD-145 table where applicable)

Not in the OD-145 harness table (pyfmt scope); restaged per BC-5.02.003's canonical
tables; fuzz target `FuzzDecode_depth` (in-tree pyfmt fuzz set, ARCH-06 §2.6 hom_set).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Small (boundary) + infinite (fuzz) | |
| Proof complexity | Low | recursion is budget-guarded |
| Tool support | Full | stdlib fuzzing |
| Estimated proof time | Hours | generator must emit WTF-8-safe nesting |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
