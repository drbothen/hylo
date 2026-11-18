---
document_type: verification-property
level: L4
version: "1.6"
status: draft
producer: architect
timestamp: 2026-11-22T02:30:00Z
phase: 1b
inputs: [prd.md, architecture/ARCH-07-parity-harness.md, architecture/ARCH-08-build-ci-release.md, behavioral-contracts/ss-06/BC-6.02.001.md, prd-supplements/nfr-catalog.md]
input-hash: "d07f731"
traces_to: prd.md
source_bc: BC-6.02.001
bcs: [BC-6.02.001, BC-6.04.001]
module: internal/parity (corpus), CI hygiene legs
proof_method: manual
feasibility: feasible
verification_lock: false
proof_completed_date: null
proof_file_hash: null
lifecycle_status: active
introduced: "1.0"
modified: ["1.1 2026-11-18T09:10:00Z: ADV-P3 fixes (A2-06) — provenance test asserts a non-zero computed fixture count and logs “N fixtures validated” (POL-11)", "1.2 2026-11-19T12:00:00Z: pass-6 fixes (A2-27, A2-21: the provenance walk covers every committed testdata tree (statusline/config/pyfmt/cmd-hylo); planted-canary self-test for the scan leg)", "1.3 2026-11-21T00:00:00Z: pass-9 fix (ADV-P9-A2-11) — the planted-canary self-test now plants one canary per hygiene category the scan claims (IP, username, home path, hostname, email, token shape), each required to be flagged (VP-022's one-planted-violation-per-rule standard); all values synthetic and obviously fake (RFC 5737 TEST-NET-1, example.invalid)", "1.4 2026-11-21T09:00:00Z: pass-11 residual — the Property Statement's scan leg states the two-ref rev set: the CI gitleaks scan names exactly `main` and `factory-artifacts` (`--log-opts=\"main factory-artifacts\"`), its scanned-commit count compared with `git rev-list --count main factory-artifacts` (ARCH-08 hygiene bullet)", "1.5 2026-11-22T01:00:00Z: pass-12 residual (item 2, call 1) — the two-ref rev-set wording in the Property Statement is superseded (pass-12 call 1 supersedes pass-11 call 7): the CI scan is `gitleaks detect --source . --log-opts=\"--all\"` after checkout with `fetch-depth: 0`, its scanned-commit count equal to `git rev-list --count --all`; the 1.4 history entry above is provenance, not live text", "1.6 2026-11-22T02:30:00Z: pass-13 fixes (ADV-P13-A2-10 + orchestrator call 17 / ADV-P13-A12) — fixture-tree enumeration widened from the fixed four-tree list to RUNTIME DISCOVERY of every testdata/ directory plus the cmd/hylo fixture dir (platform/cost/parity fixtures cannot escape the walk; walked tree count compared with the runtime census) and the planted-canary self-test rebuilt: one RUNTIME-COMPOSED canary per pattern-scan category (IP, home path, username, hostname, email, UUID, session link), each composed at runtime from committed fragments into a shape the scan must FLAG; token-shape row dropped (gitleaks' surface, not the pattern scan's) and the exempt-shape rows (RFC 5737, example domains) removed from the positive set — exempt shapes are the negative controls, so a canary built from one was unfailable"]
deprecated: null
deprecated_by: null
replacement: null
retired: null
withdrawn: null
withdrawal_reason: null
removed: null
removal_reason: null
---

# VP-035: Corpus hygiene — synthetic committed fixtures only, secret-scan clean

## Property Statement

Every committed fixture in every committed fixture tree — the `testdata/` directory
of every landed package and the `cmd/hylo` fixture dir, DISCOVERED at runtime by
walking for `testdata/` directories rather than read from a hard-coded list
(A2-27 originally four trees; pass-13 ADV-P13-A2-10 widens the walk: fixtures under
`internal/platform/` (fake PID chains), `internal/cost/` or `internal/parity/` are
walked by the same discovery, so a fixture added there cannot escape
`TestCorpusHygiene`) — is synthetic; the
owner's real inputs exist only as git-ignored copies under `captures/` (OD-107) and are
never committed; the CI gitleaks scan runs `gitleaks detect --source .
--log-opts="--all"` after checkout with `fetch-depth: 0`, so its scanned-commit
count equals `git rev-list --count --all` (same rev set by construction — `--all`
includes HEAD, so a pull-request run scans the PR head and every fetched ref;
ARCH-08 hygiene bullet) plus the category
pattern scan are clean on every push and CI leg. The walked TREE count is tallied
and compared with the runtime census of `testdata/` directories, so a newly added
tree is walked without a code change and a renamed or dropped tree shrinks both
counts. `TestCorpusHygiene` enforces the
committed-corpus provenance in-tree. The planted-canary self-test plants one
RUNTIME-COMPOSED canary per category the pattern scan claims, and every composed
canary is a shape the scan must FLAG — never an exempt shape (RFC 5737 192.0.2.x,
`example` domains, no-reply identities): the exempt shapes are the negative
controls that must pass, so a canary built from an exempt shape proves nothing
(pass-13 orchestrator call 17).

## Source Contract

- **Primary BC:** BC-6.02.001 — Committed corpus synthetic-only; owner real inputs
  replayed from git-ignored captures/.
- **Partial coverage:** BC-6.04.001 (gitleaks leg on every change).
- **Invariant verified:** NFR-006 / policy 21 (public-repo hygiene: synthetic paths
  only — examples use /home/user shapes, never machine-specific details).

## Property Class and Verification Method

- **Class:** invariant.
- **Method:** unit/table test + CI gate — `TestCorpusHygiene` asserts fixture
  provenance markers and rejects committed captures; the CI hygiene leg runs gitleaks
  with the category scan (push-gate, not a proof).
- **Honesty:** in-tree part is table-tested; overall cleanliness is a push-gate
  assertion, honestly weaker than a proof (ARCH-08 feasibility note).

## Proof Method

| Method | Tool | Bounded? | Coverage |
|--------|------|----------|----------|
| Provenance test | `TestCorpusHygiene` | yes — every committed testdata tree | synthetic markers, no committed captures |
| Secret scan | gitleaks + category pattern scan | process gate | every push and CI leg |
| Scan self-test | `TestHygieneScan_PlantedCanary` | 1 RUNTIME-COMPOSED canary per pattern-scan category (IP, home path, username, hostname, email, UUID, session link), each a flagged (non-exempt) shape, fragments committed, composed value appears in no committed file | the scan leg can check nothing and pass (A2-21, ADV-P9-A2-11; pass-13 call 17) |

## Proof Harness Skeleton

*Illustrative sketch (non-normative, not compiled; OD-182).*
```go
func TestCorpusHygiene(t *testing.T) {
    n := 0
    for _, fx := range CommittedFixtures() { // A2-27, widened pass-13 A2-10: walks EVERY
        // committed fixture tree, DISCOVERED at runtime (every testdata/ directory of
        // every landed package plus the cmd/hylo fixture dir — statusline (incl.
        // parity/), config, pyfmt, platform, cost, parity, cmd/hylo) — never a
        // hard-coded list.
        if !fx.ProvenanceSynthetic() { t.Fatalf("%s: not marked synthetic", fx.Path) }
        n++
    }
    if n == 0 { // POL-11 (A2-06): a mis-pathed fixture load must not pass green
        t.Fatal("zero committed fixtures found — mis-pathed load passes nothing")
    }
    t.Logf("%d committed fixtures validated", n)
    if committedCapturesExist() { t.Fatal("captures/ content committed") }
}

func TestHygieneScan_PlantedCanary(t *testing.T) { // A2-21 (P11) + ADV-P9-A2-11; pass-13
    // call 17: ONE PLANTED CANARY PER CATEGORY THE PATTERN SCAN CLAIMS (VP-022's
    // one-planted-violation-per-rule discipline). Each canary VALUE is composed AT
    // RUNTIME from fragments — the innocent fragments are the committed text; the
    // composed flagged shape appears in no committed file — and every composed
    // value is a shape the scan must FLAG: a private-LAN IPv4, a POSIX home path
    // with a non-exempt username, a home-path username, a personal e-mail on a
    // non-exempt domain, an infra hostname, a session-ID UUID, a session-link
    // trailer. Never an EXEMPT shape (RFC 5737 192.0.2.x, example domains,
    // no-reply): exempt shapes are the negative controls that must pass, so a
    // canary planted with an exempt shape makes the self-test unfailable
    // (ADV-P13-A12). Never a real-looking personal value.
    join := func(sep string, ss ...string) string { return strings.Join(ss, sep) }
    dir := t.TempDir()
    canaries := []struct{ category, canary string }{
        {"ip", join(".", "192", "168", "1", "2")},                       // RFC 1918, flagged
        {"home-path", join("", "/home/", "xu", "ser", "/notes")},         // non-exempt username
        {"username", join("", "bxoes", "@", "bh", "-07", ".", "corp", ".", "internal")}, // username@host shape
        {"hostname", join(".", "bh", "-07", ".", "corp", ".", "internal")},
        {"email", join("", "u1", "@corp", ".", "invalid")},               // non-exempt domain
        {"uuid", join("-", "0f0e0d0c", "0b0a", "4321", "8765", "fedcba987654")}, // session-marker shape
        {"session-link", join("", "Claude", "-Session: ", "sess-0001")},  // trailer, composed
    }
    for _, tc := range canaries {
        plantCanary(dir, tc.category, tc.canary)
        if !categoryScanFlags(dir, tc.category) {
            t.Fatalf("category scan did not flag the planted %s canary — scan checks nothing", tc.category)
        }
    }
}
```

## Named Tests (OD-145 table where applicable)

`TestCorpusHygiene` (settled, NFR-006); CI hygiene leg per ARCH-08 workflow.

## Feasibility Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Input space size | Whole testdata tree | static |
| Proof complexity | N/A | gate + test |
| Tool support | Full | gitleaks |
| Estimated proof time | Hours | |

## Lifecycle

| Event | Date | Actor |
|-------|------|-------|
| Created | 2026-11-16 | architect |
| Proof harness committed | — | formal-verifier |
| Proof first passed | — | formal-verifier |
| Locked (VERIFIED) | — | formal-verifier |
