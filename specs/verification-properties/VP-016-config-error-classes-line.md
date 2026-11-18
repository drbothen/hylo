---
document_type: verification-property
level: L4
version: "1.4"
status: draft
producer: architect
timestamp: 2026-11-18T23:45:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-02-configuration.md, behavioral-contracts/ss-02/BC-2.02.001.md, behavioral-contracts/ss-02/BC-2.02.002.md, behavioral-contracts/ss-02/BC-2.02.003.md, behavioral-contracts/ss-02/BC-2.02.004.md, behavioral-contracts/ss-02/BC-2.02.005.md, behavioral-contracts/ss-02/BC-2.02.006.md, domain-spec/invariants.md, owner-decisions-log-2026-11-14.md]
input-hash: "ca42daa"
traces_to: prd.md
source_bc: BC-2.02.001
bcs: [BC-2.01.002, BC-2.01.003, BC-2.01.005, BC-2.02.001, BC-2.02.002, BC-2.02.003, BC-2.02.004, BC-2.02.005, BC-2.02.006, BC-2.03.001]
module: internal/config (errors.go), cmd/hylo
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-17: ADV-P1 pass-1 fixes", "1.2 2026-11-17: ADV-P2 pass-2 fixes — number-grammar (BC-2.02.003) got its own table and test name (A2-07); FirstErrorRegistryOrder rewritten as valid, failure-capable Go", "1.3 2026-11-18: ADV-P4 pass-4 fix (D22) — test names canonicalized to TestD4EX3_{Number,Boolean,URL,Enum}: the Number table covers both number-range and number-grammar rows; no Theme member (theme settings are rejected by the corpus validator, BC-6.02.003 EC-007)", "1.4 2026-11-18T23:45:00Z: ADV-P5 fixes (A2-03, A2-25) — class register is seven with the OD-178 Text class (composite-shape, pill-label, runtime glyph-rule, empty-text; own table TestD4EX3_Text, exact reason strings in the taxonomy vocabulary); BC-2.01.003's two homeless legs carried here: TestTheme_DefaultGolden (SL:127-134 golden table) and TestTheme_SGREscapeFree (quick property over accepted values) — legs, not a D4-EX-3 class table; FirstErrorRegistryOrder expects a PINED literal instead of the function under test, so a consistently wrong order can no longer pass"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-016: D4-EX-3 config-error classes, line format, and no-cache-writes guarantee

## Property Statement

Every invalid setting value falls into exactly one of the seven closed config-error
classes (number-range, number-grammar, enum, URL, boolean, theme/SGR, and Text —
OD-178 adds the seventh), and any invalid
value renders exactly `\e[90mhylo: config error: <key>=<value> (<reason>)\e[0m\n` on
stdout, exits 0, prints the full error list plus `[from <ENVNAME>]` on stderr, selects
the first error in registry order (order-stable selection), and — critically — writes
no cache files. The Text class (OD-178) covers the composite-shape
(`expected JSON <shape>`), pill-label, runtime glyph-rule (value not exactly
1 code point / 1 column) and empty-text errors, with exact reason strings in the
taxonomy vocabulary and its own table test `TestD4EX3_Text`. The same one-line
E-CFG-001 surface also carries the reason vocabulary
that has no dedicated class contract, mapped by the error taxonomy to its raising
contract: the path-grammar reasons (`empty path`, `home directory unknown`, raised by
BC-2.01.005) and the backends-cardinality reason (BC-2.01.002) ride the class
register; `control character` belongs to the URL class when raised
by BC-2.02.005 and to the theme/SGR reason (`not an SGR parameter list`) when raised
by BC-2.01.003. Representative rows
for each of these entries are inside the class tables. BC-2.01.003's two legs live
here: the default-theme-bytes golden (table test) and the ESC-free-SGR property
(testing/quick over accepted values) — neither is a D4-EX-3 class table (the parity
corpus validator rejects theme settings, pass-4 D22; that validator governs the
corpus, not in-tree unit tables). `hylo config validate` exits 1
for the same errors.

## Source Contract

- **Primary BC:** BC-2.02.001 — D4-EX-3 config-error line: exact format, exit 0,
  stderr detail, no cache writes.
- **Partial coverage:** BC-2.02.002 (number-range), BC-2.02.003 (number-grammar),
  BC-2.02.004 (enum), BC-2.02.005 (URL), BC-2.02.006 (boolean, OD-140); BC-2.03.001
  (validate exit 1); BC-2.01.005 (path-grammar reason rows on the same surface),
  BC-2.01.002 (backends-cardinality reason row on the same surface).
- **Invariant verified:** DI-008 (config errors are one-line outputs, D4-EX-3);
  OD-102/OD-114/OD-134; approved-deviation closed set membership (D4-EX-3).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test — one table per class under the four canonical ARCH-07
  names (`TestD4EX3_{Number,Boolean,URL,Enum,Text}`, pass-4 D22 + OD-178's Text member;
  the `Number` table covers
  both number-range and number-grammar rows, BC-2.02.002/BC-2.02.003) with
  exact expected bytes; plus a registry-order property test (first-error selection is
  order-stable under permutation of invalid variables, against a PINED expected line);
  plus a no-cache-writes assert
  (empty temp dir after a config-error run); plus BC-2.01.003's two legs — the
  default-theme-bytes golden table and the ESC-free-SGR quick property.
- **Honesty:** testable-only; class closure is a ruling (OD-178 adds the Text class by
  owner decision), enumerated exhaustively because the registry domain is closed.

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Class tables | Go test, `cmd/hylo` + `internal/config` | yes — six classes | every class x representative + boundary values |
| Order property | Go test | yes — permutation check | registry-order stability |

## Proof Harness Skeleton

```go
func TestD4EX3_Number(t *testing.T)  { runClassTable(t, numberRangeRows); runClassTable(t, numberGrammarRows) } // range BC-2.02.002 + grammar BC-2.02.003 (A2-07)
func TestD4EX3_Boolean(t *testing.T) { runClassTable(t, booleanRows) }
func TestD4EX3_URL(t *testing.T)     { runClassTable(t, urlRows) } // incl. control-character rows
func TestD4EX3_Enum(t *testing.T)    { runClassTable(t, enumRows) }
func TestD4EX3_Text(t *testing.T)    { runClassTable(t, textRows) } // OD-178: composite-shape
// (`expected JSON <shape>`), pill-label, runtime glyph-rule (1 code point / 1 column)
// and empty-text rows — exact reason strings in the taxonomy vocabulary.
// No Theme member (pass-4 D22): theme settings are rejected by the corpus validator
// (BC-6.02.003 EC-007); the theme rows below are BC-2.01.003 legs, not a class table.
func TestConfigError_PathGrammarReasons(t *testing.T)  { runClassTable(t, pathGrammarRows) }       // taxonomy: BC-2.01.005 reasons
func TestConfigError_BackendsCardinalityReason(t *testing.T) { runClassTable(t, backendsCardinalityRows) } // taxonomy: BC-2.01.002 reason

func TestTheme_DefaultGolden(t *testing.T) { // BC-2.01.003 leg, carried here (ADV-P5-A2-03)
    runClassTable(t, themeDefaultBytesRows) // SL:127-134 literals, golden table
}

func TestTheme_SGREscapeFree(t *testing.T) { // BC-2.01.003 leg: any ACCEPTED SGR value
    quick.Check(func(sgr []string) bool { // renders ESC-free inside the parameter span
        out := renderPillWithTheme(sgr)
        // The accepted-value grammar is ESC-free; the rendered parameter span must
        // be exactly the ';' joined value — no ESC introduced by the splice.
        return bytes.Equal(out, pillPreamble+[]byte(strings.Join(sgr, ";"))+pillPostamble)
    }, nil)
}

func TestConfigError_FirstErrorRegistryOrder(t *testing.T) {
    base := InvalidVariablesOnePerClass() // one invalid variable per class + register riders
    want := pinnedFirstErrorLine          // A2-25: the expected line is a PINED literal
    // (authored from the registry, committed with the table), NOT computed by the
    // same FirstErrorLine call under test — a consistently wrong selection order
    // (alphabetical by env name, say) can no longer pass. The permutation loop
    // remains the stability check.
    for _, perm := range Permutations(base) {
        if got := FirstErrorLine(perm); got != want {
            t.Fatalf("first-error selection drifted under permutation: got %q, want %q", got, want)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestD4EX3_{Number,Boolean,URL,Enum,Text}` — the five-name canonical set (pass-4 D22
plus the OD-178 Text member): `Number` covers both number-range (BC-2.02.002) and
number-grammar (BC-2.02.003) rows; no Theme member (theme settings are rejected by
the corpus validator, BC-6.02.003 EC-007), superseding the earlier six-name list;
the theme legs are `TestTheme_DefaultGolden` and `TestTheme_SGREscapeFree`
(BC-2.01.003); order property named `TestConfigError_FirstErrorRegistryOrder`.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Six classes, small | registry-closed |
| Proof complexity | N/A | |
| Tool support | Full | |
| Estimated proof time | Days | boundary values per class (TTL nan/inf/neg, 4_0, Unicode digits, TRACE, URL scheme, bool spellings) |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
