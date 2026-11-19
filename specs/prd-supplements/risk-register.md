---
document_type: risk-register
level: L3
version: "1.10"
status: draft
producer: architect
timestamp: 2026-11-24T14:25:00Z
phase: 1b
inputs: [architecture-feasibility-report.md, prd.md, prd-supplements/nfr-catalog.md, architecture/ARCH-INDEX.md, verification-properties/VP-INDEX.md]
input-hash: "076100a"
traces_to: prd.md
modified:
  - "1.10 2026-11-18: pass-14 remediation - the open-NFR-candidates gate note names R-009's existing NFR-003 link beside R-001/R-008 (A09); no behavioral change"
---

# Risk Register: hylo P1

> Minted 2026-11-17 per owner ruling OD-152 (consistency audit CA-04, part 2; all-findings
> fix burst per OD-154). One R-NNN row per risk formerly held prose-only in the
> feasibility report's "Risks and Mitigations" table (R-001..R-005, same order), plus the
> two PRD-carried risks closed by spec decision (R-006, R-007; prd.md §10) and R-008,
> minted by the pass-2 remediation for the OD-156 transcript-borne overflow divergence.
> Impact per the de facto mapping in consistency-audit-2026-11-17.md §10.2. Companion of
> prd-supplements/assumptions-register.md (ASM-001..007).

| R ID | Risk | Category | Status | Impact | Mitigation | NFR Link | ARCH / ADR Anchor |
|------|------|----------|--------|--------|------------|----------|-------------------|
| R-001 | Python/Go cache-swap byte divergence across the four caches | Correctness (parity) | open | HIGH | Byte-exact writers over ordered `pyfmt.Value`; Tier B goldens + four-cache swap tier (VP-019); failed-replace semantics pinned by the AD-03 decision — the in-memory overlay OPTION was rejected there as having the wrong persistence semantics (ARCH-03 options 1/2; pure widgets + one ordered-effect orchestrator chosen; pass-9 A09) | NFR-003 | ARCH-04 / AD-08 (byte-exact writers, atomic write + Windows retry + temp cleanup); swap tier exercised in ARCH-07 |
| R-002 | p95 <= 25 ms render-latency miss on the owner's Mac | Performance | open | MEDIUM | Legacy baseline measured (median 84.5 ms, 2026-11-15); hot-path allocation discipline; per-OS timing report; gate binds only where OD-117 says | NFR-001 | ARCH-08 timing gate (binds only with `HYLO_TIMING_GATE=1`); VP-036 |
| R-003 | Windows-only edge cases marked "not executed" (BC-1.06.001 EC-008, BC-1.06.002 EC-003/EC-005; sitecustomize shim) | Portability | open (disclosed) | MEDIUM | Pinned on the windows-2025 CI leg and the harness canary (ASM-005); disclosed, not hidden | NFR-004 | ARCH-08 3-OS CI matrix (AD-11); VP-037 |
| R-004 | Fake-pass parity: harness weaker than refereed | Verification integrity | open | HIGH | AD-09 fail-closed machinery, canary (BC-6.01.003), exclusion-closure property test (VP-012). P1 restatement (pass-6 A17/call 13; OD-158; corrected pass-7 A09, orchestrator call 12; gate scope per OD-193; propagated to this register pass-9 A08, mirroring ARCH-08's restatement): throughout P1 the mitigation is the differential harness itself — Tier A cache-swap corpus WITH its runtime census (the job fails unless its census line `parity: N cases compared, M exclusions validated, K caches swapped` prints `N >= 1` with `N` equal to the committed corpus-case manifest — checking a subset of the corpus, or only the timing job's nonzero line, must not pass; pass-10 A08, census line per ARCH-08, manifest comparison per call 15), Tier C differential fuzz, one clean Tier C nightly run as the P1 exit condition (OD-149) — plus the >= 95% Go statement-coverage gate over the gated packages (S1/S5 per OD-193; metric name aligned pass-12 A12, mirroring the pass-11 A03 rename in prd.md, nfr-catalog and module-criticality) and the fail-closed integrity machinery; the mutation kill-rate >= 95% tier is a Phase 6 gate, not a P1 gate, so no P1 claim rests on kill rate | n.a. | ARCH-07 / AD-09 |
| R-005 | Purity-annotation drift across BC files | Documentation consistency | closed (remediated) | LOW | Per-BC Purity Classification sections annotated during Pass 3 — 154/154 on disk (recount per pass-4 A19; re-verified 2026-11-17, CA-07; count includes the eight OD-155 subagent contracts and BC-5.01.007); module-level boundary carried in the ARCH-00 purity table | n.a. | ARCH-00 purity table |
| R-006 | RK-5: HYLO_TEST_NOW stderr warning leaking outside the harness | Operational (determinism) | closed (spec decision) | LOW | Env seam set: HYLO_TEST_NOW is a harness hook, not a setting (AD-10); reserved names are never warned as unknown keys (BC-2.01.001 postcondition 6) | n.a. | ARCH-03 / AD-10 |
| R-007 | RK-6: inert key `statusline.window_age.ps_timeout_s` confusing the config surface | Operational (config surface) | closed (owner ruling) | LOW | Key removed from the registry by OD-147 (owner, 2026-11-16); setting it now draws only the unknown-setting stderr warning, is ignored, and never changes the output or exit status (BC-2.01.001 PC-6, VP-015) — there is no unknown-key config-error class | n.a. | ARCH-02 key registry (OD-147) |
| R-008 | Transcript-borne overflow skip (OD-156, extended D4-EX-2) diverges cache bytes from legacy: on the offending refresh legacy degrades sticky and saves nothing, while hylo skips the line (OD-167: and drops the in-flight turn) and saves the rest | Correctness (parity) | open (accepted by ruling) | MEDIUM | Named exclusion: the D4-EX-2 W-predicate family gains a numeric-overflow predicate with table tests (BC-1.03.018/.019 extension; triggers CP-O06..O08 in error-taxonomy.md — CP-O09 is the save-time no-write case, no divergence, temp-file id; pass-5 A21); Tier A expects the diff and cites the entry | NFR-003 | ARCH-04 cache writers / ARCH-07 exclusion machinery |
| R-009 | The hand-written HTTP/1.1 + crypto/tls client over net.Conn (ARCH-03 metrics-client family) parses untrusted network bytes — status line, headers, chunked framing, redirects, read-to-EOF bodies; malformed or hostile replies reach a hand-rolled parser, not a hardened stdlib one (ADV-P13-A11, orchestrator call 16) | Security | open (mitigations named) | MEDIUM | Parser limits pinned at legacy's stdlib constants in BC-1.04.001 (http.client `_MAXLINE`=65536 / `_MAXHEADERS`=100; urllib `max_repeats`=4 / `max_redirections` — each request reads at most those); a Go fuzz target on the response parser joins the Phase 6 formal-hardening pipeline | NFR-003 | ARCH-03 metrics client / BC-1.04.001 / Phase 6 hardening |

## Gate Notes

- HIGH-impact risks: R-001, R-004. Both carry an architecture mitigation (ARCH-04 / AD-08
  and ARCH-07 / AD-09 respectively), matching the audit's 2/2 substance pass
  (consistency-audit-2026-11-17.md §10.3).
- Security-category risks: R-009 (hand-written HTTP/1.1 + TLS client over untrusted
  bytes; minted pass-13 A11/call 16) — the audit's vacuous pass predates it.
- Open NFR candidates with no matching NFR: none. R-001 and R-008 link to existing
  NFR-003, R-002 to NFR-001 and R-003 to NFR-004; R-009 likewise links to NFR-003 (its
  fuzz-target and parser-limit mitigations ride the parity/hardening machinery the NFR
  already gates; pass-14 A09); R-004, R-005, R-006 and R-007 are not
  NFR candidates — their mitigations are verification machinery, documentation, and spec
  decisions, not missing non-functional targets.
- Holdout scenarios are a Phase 2 artifact; HIGH/HIGH holdout coverage is n/a until
  stories exist.
