---
document_type: verification-property
level: L4
version: "1.8"
status: draft
producer: architect
timestamp: 2026-11-21T12:00:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-03-statusline.md, architecture/ARCH-06-pyfmt.md, behavioral-contracts/ss-01/BC-1.01.002.md, behavioral-contracts/ss-01/BC-1.01.008.md, domain-spec/invariants.md]
input-hash: "5406071"
traces_to: prd.md
source_bc: BC-1.01.002
bcs: [BC-1.01.002, BC-1.01.008, BC-1.07.002, BC-1.07.003]
module: internal/statusline (input.go, guard.go), internal/pyfmt
proof_method: fuzz
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 fixes — skeleton asserts utf8.Valid(stdout) (A2-25); added the --subagent stdin-absorb totality leg (BC-1.07.003) and the subagent.enabled=false zero-lines leg (BC-1.07.002)", "1.3 2026-11-18T09:06:00Z: ADV-P3 fixes — 3-arg pyfmt.Decode(b, mode, per-site budget) everywhere (A2-08); subagent fuzz leg asserts rows-or-zero-bytes and never-the-degraded-line-via-the-parse-path, with OD-168 (subagent config error = zero bytes) in the output set (A2-07); enabled=false recast as a non-default config value, not a DI-012 named deviation (A2-21)", "1.4 2026-11-18T14:10:00Z: ADV-P4 fix (A2-02) — the never-the-degraded-line assert is coded with its parse-path condition: a decoded JSON object reaches the renderer, where CP-A01..A05 faults legitimately end in the degraded line (BC-1.07.008); the prohibition now fires only for non-object stdin (parse-borne regime)", "1.5 2026-11-19T12:00:00Z: pass-6 fixes (A2-13: utf8.Valid([]byte(stdout)) cast so one of the two stdout uses compiles whichever type renderFromStdin returns)", "1.6 2026-11-20T12:00:00Z: pass-9 fix (A2-06) — the subagent parse-path oracle narrowed from 'rows or zero bytes' to EXACTLY ZERO stdout bytes for undecodable/non-object stdin (main_subagent absorbs to {} → zero rows, SL:928-936; BC-1.07.003, DI-008); the skeleton's parse-borne regime asserts len(stdout) == 0", "1.7 2026-11-18T17:50:00Z: pass-10 fix (A2-02 sibling, orchestrator call 10) — the subagent classifier's mode specified: isJSONObject classifies with pyfmt.Decode ModeText semantics and the subagent stdin site's 993 depth budget (legacy reads json.load(sys.stdin) in text mode, SL:930; a UTF-8 BOM, a UTF-16/32 payload or depth-994 nesting is undecodable → {} → zero bytes) — the property statement's boundary sentence and the skeleton's isJSONObject comment state it", "1.8 2026-11-21T12:00:00Z: pass-12 fix (A2-14) — the symmetric-UTF-8 sentence's attribution corrected: the degraded line is CONSTANT ASCII (the 29 fixed bytes, trivially valid UTF-8); BC-1.01.008's lone-surrogate encoding rules apply to RENDERED ROWS (widget bytes derived from decoded input values), which is where `utf8.Valid` does its work"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-005: stdio codec totality — stdin decode yields a render state; stdout is valid UTF-8

## Property Statement

For every possible stdin byte string (valid JSON, non-JSON, non-object, empty, invalid
UTF-8), the stdin decode step produces a defined `pyfmt.Value` — an empty object on any
decode failure per the legacy semantics — and the render completes (never blank, exit
0). No stdin input can crash the decode step or abort the refresh. The `--subagent`
entry absorbs stdin faults the same way (BC-1.07.003): for every byte string the
subagent entry exits 0 — a decoded JSON object reaches the renderer (its rows, a
renderer fault's degraded line, or zero bytes on an empty task list), while
undecodable or non-object stdin is absorbed to {} and yields EXACTLY ZERO stdout
bytes, never rows and never the degraded line via the parse path (A2-06:
main_subagent maps every undecodable or non-object stdin to {}, SL:928-936). The
parse/renderer boundary is the ModeText decode with the subagent stdin site's 993
depth budget (pass-10 A2-02: legacy reads `json.load(sys.stdin)` in text mode,
SL:930; a UTF-8 BOM, a UTF-16/32 payload or depth-994 nesting is undecodable → {}
→ zero bytes — the detections ModeBytes would apply do not run on this site);
a subagent config error is likewise zero bytes (OD-168); and with
`statusline.subagent.enabled=false` (BC-1.07.002 — a non-default config value, not a
DI-012 parity exclusion; the DI-012 machinery governs parity exclusions and no
exclusion id covers this; default `true` = legacy) the render is zero JSON lines for every
stdin. Symmetrically,
whatever the fault, the stdout bytes are always valid UTF-8 (A2-14): the degraded
line is constant ASCII — the 29 fixed bytes, trivially valid — while lone surrogates
decoded from input values are encoded per the BC-1.01.008 rules when RENDERED ROWS
are built, so `utf8.Valid`
holds on every rendered output (BC-1.01.008 stdout property, formerly "no VP yet").

## Source Contract

- **Primary BC:** BC-1.01.002 — Non-JSON or non-object stdin decodes to an empty
  object.
- **Partial coverage:** BC-1.01.008 (strict UTF-8 stdio; invalid stdin UTF-8 renders
  from {}), BC-1.07.003 (subagent stdin absorb: unparseable or non-object stdin
  renders zero rows — exactly zero bytes, never the degraded
  line via the parse path), BC-1.07.002 (`subagent.enabled=false` suppresses the
  entire subagent render — zero JSON lines, exit 0; the `enabled=true` parity leg rides
  the Tier A corpus, VP-009, and the Tier B goldens, VP-010).
- **Invariant verified:** DI-008 (stdin faults are on the degraded ladder's safe side).

## Property Class and Verification Method

- **Class:** safety.
- **Method:** property-based/fuzz test — `go test -fuzz` over arbitrary stdin byte
  strings through `pyfmt.Decode(ModeText)` plus the render completion and
  `utf8.Valid(stdout)` asserts; plus boundary tables (BOM, truncated objects, arrays,
  scalars, invalid UTF-8, CP-S17 surrogate shapes).
- **Honesty:** testable-only; the fuzz oracle is totality itself (defined decode
  outcome + non-blank valid-UTF-8 stdout), not a live CPython call — equivalence rows
  come from the committed oracle tables and the BC-1.01.008 vector table.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Fuzz | `go test -fuzz` (stdlib), CI-seeded, nightly-extensible | no (fuzzer), bounded runs | arbitrary stdin byte strings |
| Boundary tables | Go test | yes | BOM/scalar/truncated/invalid-UTF-8 rows |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func FuzzStdinDecodeTotality(f *testing.F) {
    for _, s := range SeedStdinCorpus { f.Add(s) }
    f.Fuzz(func(t *testing.T, stdin []byte, subagent bool, enabled bool) {
        // 3-arg Decode: per-call-site budget argument (VP-006), never a free constant
        v, err := pyfmt.Decode(stdin, pyfmt.ModeText, stdinSiteBudget)
        _ = v
        _ = err                                       // error allowed, panic is not
        stdout, _, exit := renderFromStdin(stdin, subagent, enabled)
        if exit != 0 { t.Fatal("render not total") }
        if !subagent && len(stdout) == 0 { t.Fatal("blank render on main entry") }
        if subagent && enabled { // BC-1.07.003 (A2-06, strengthened pass-9): undecodable
            // or non-object stdin is absorbed to {} and yields EXACTLY ZERO bytes
            // (main_subagent, SL:928-936); a decoded JSON object reaches the renderer,
            // where a CP-A01..A05 fault ends in the degraded line (BC-1.07.008, A2-02).
            // OD-168: config error = zero bytes
            // isJSONObject: pyfmt.Decode ModeText semantics + the 993 subagent-stdin
            // budget (pass-10 A2-02: text-mode json.load, SL:930 — BOM, UTF-16/32
            // and depth-994 stdin decode to {} → zero bytes).
            if !isJSONObject(stdin) { // parse-borne regime
                if len(stdout) != 0 {
                    t.Fatal("subagent parse-path stdout is not exactly zero bytes")
                }
            }
        }
        if subagent && !enabled && len(stdout) != 0 { // BC-1.07.002 off switch
            t.Fatal("subagent render with enabled=false must be zero JSON lines")
        }
        if !utf8.Valid([]byte(stdout)) { t.Fatal("stdout is not valid UTF-8 (BC-1.01.008)") } // A2-13: utf8.Valid takes []byte — cast so one of the two stdout uses compiles whichever type renderFromStdin returns
    })
}
```

## Named Tests (OD-145 table where applicable)

stdin decode rows ride the `frame` parity-case family (ARCH-07); fuzz target named
`FuzzStdinDecodeTotality` (in-tree; Tier C extension optional).

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Infinite | mitigated by fuzzing |
| Proof complexity | Low | decode is total by construction |
| Tool support | Full | stdlib fuzzing |
| Estimated proof time | Hours | seed corpus from BC tables |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
