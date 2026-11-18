---
document_type: remediation-plan
phase: 1d
pass: 10
date: 2026-11-18
source: adversarial-reviews/pass-10.md, adversarial-reviews/ADV-P10-INDEX.md
---

# Pass-10 remediation plan (canonical calls)

Read with the Rules section of `pass-4-remediation-plan.md` and the gates of `pass-9-remediation-plan.md` (YAML parse after every edit; for-all properties derived from every PC/EC/exception and walked against legacy; state only what you measured; ASCII wire goldens; section anchors, never line numbers). Edit only your file set; list out-of-set hits as file:line. Every finding below is routed to the agent whose file set contains the file (L-PG-36). Synthetic test values use the pre-push hook's allowlist (example.com/.org/.net, 192.0.2.x, /home/example...) (L-PG-37).

New rule this pass: **no line-number pointers into BC files either** (C02): cite BCs by ID plus PC/EC/Inv/row number, never `BC-x:NN`.

No owner rulings this pass. Next free OD: OD-194.

## Orchestrator calls (binding; checked against the OD log)

1. **Harness metrics URL (D01):** the harness ALWAYS injects the fake metrics server's URL into both children, because its port is only known at run time: the oracle gets `DGX_SL_VM_URL=<fake>` and hylo gets the env key of `backends[0].metrics_url` set to the same URL, unless the case itself sets the metrics URL (then the case value wins). These keys are unconditional members of BC-6.01.002's exact key sets; its CTVs and ARCH-07 copy that.
2. **Subagent case ids (D02):** a subagent case is a case of the `subagent` family (`subagent-<nnn>[-<variant>]`), and the validator gives argv `["--subagent"]` to exactly that family. There is no `-sub` suffix rule. ARCH-07 and BC-6.01.001/6.02.003/6.03.001 state this one rule.
3. **Absolute cache dir (D03, D10):** only `statusline.paths.cache_dir` (HYLO_PATHS_CACHE_DIR) must be absolute; `HYLO_CONFIG` is reserved for P4 and printed as given. Absoluteness is `filepath.IsAbs` semantics computed in `internal/platform` per OS (Windows: drive + root or UNC; `\foo` and `C:foo` are relative). `config path` with a relative value reports the same config error (`not an absolute path`) and exits 1 (as pass-4 call 16 did for the empty path). A relative `HOME`, `LOCALAPPDATA` or `APPDATA` is treated as unset (as relative `XDG_*` is under OD-144), falling to the next source in BC-3.01.001's order, then to the existing "cannot be determined" error.
4. **Replay seeding for every session id (D04):** the harness seeds a fixed synthetic `proc_start` for every `session_id` that any step's stdin of a case or capture uses; the validator rejects a case whose step introduces a sid it cannot seed. No replay ever consults the real process tree.
5. **RoundN keeps ints (D05):** `RoundN(x Num, n int) Num`: an int (or bool, as int) input returns an exact int; a float input returns a float (Python `round(x, n)` semantics). ARCH-06 and BC-5.01.001 agree; BC-1.05.009 PC-3 stands.
6. **Default-layer value in an error line (D06):** when the value named in an error line comes from the default layer, `<value>` is the default's env spelling exactly as in the interface-definitions Default column, and `[from <ENVNAME>]` is omitted.
7. **Flat corpus ids (D07):** examples use flat `cases/<case-id>/` ids of the grammar (e.g. `cfgerr-001`, `cpt01-001`, `cache-003`).
8. **CI floor leg (D09):** the floor leg installs exactly `go-version: 1.26.0` (the go.mod floor), not `1.26.x`.
9. **Subagent output set (A2-01):** the `--subagent` entry legally prints zero or more NDJSON lines OR, on a catalogued renderer fault (CP-A01..A05), the 29-byte degraded line. VP-004 and the VP rows of BC-4.01.001 and BC-1.07.001 state exactly that output set.
10. **Subagent stdin classifier (A2-02):** classify subagent stdin with ModeText semantics and the 993 budget (BOM, UTF-16/32 and depth 994 → `{}` → zero bytes).
11. **Mix re-read loop owner (A10, C07, C08):** BC-1.03.021 owns the re-read loop; ARCH-03, ARCH-06 and BC-5.02.003 cite BC-1.03.021 by ID. Agent 6 measures once whether the loop holds for a transcript larger than one read step (524,288 bytes) and pins what it measures (constant size vs cycling).
12. **Git pointer chunk (B02; orchestrator-measured on CPython 3.11.7, macOS):** the text reader decodes the first 8192 bytes in one chunk: an invalid byte at file offset < 8192 fails `readline()`, at >= 8192 the first line reads; independent of `st_blksize` (4096 on the measuring filesystem). Pin 8192 with probes at 8191 and 8192; remove the "4096-byte prefetch" note. Also B06: `isdir`/`isfile` follow symlinks (stat semantics).
13. **CP-O07 canonical vector (C01):** the canonical CP-O07 vector is the transcript-reachable sequence (`input_tokens` 10^309, then -10^309, then 1.5: `tin` 0, then SL:1117 raises), under D4-EX-2; the int-`tin`/float-`pp` seed is a foreign-cache state and is labelled OD-160. Oracle-check the reachable vector.
14. **Surrogate range (C03):** POSIX surrogateescape maps only U+DC80..U+DCFF to bytes 0x80..0xFF; any other lone surrogate (including U+DC00..U+DC7F) fails before the syscall.
15. **CI census against committed manifests (A04, A05, A06):** Tier A / Tier B / timing compare their runtime counts against a committed expected count (manifest) as well as against zero; gitleaks compares its scanned-commit count with `git rev-list --count` over both refs; the coverage job fails when a gated package that exists in the committed package manifest is missing (renamed or moved) and prints `G of 3`; `G == 0` is allowed only before any `internal/` Go package exists.
16. **factory-artifacts hygiene scan (A03):** a scheduled (nightly) and manually dispatchable job on `main` checks out the `factory-artifacts` ref and runs the category pattern scan over it; the local pre-push hook stays the push-time guard. NFR-006 wording matches.
17. **Reason vocabulary (A07):** `not an absolute path` is added to BC-2.02.001's exact-strings table and error-taxonomy's reason table (path-grammar family); stale "not yet on disk" / "minting source of record" notes are removed (A15).
18. **Everything else** as reported, routed in the table below.

## Agent file sets and findings (routed by file)

| Agent | Role | Files | Findings |
|---|---|---|---|
| 1 | architect | specs/architecture/*, specs/cicd-setup.md | A01, A02, A03 (cicd/ARCH-08), A04, A05, A06, A10 (ARCH-03/06), A11 (declare `LoadOptions` incl. the EnvVars field), A12 (pyfmt helper for exact big ints at `{pct:>2d}`), A16; C07 and C08 (ARCH-03 side); C2-03, C2-04; D01 and D02 (ARCH-07 side); D05 (ARCH-06 RoundN) |
| 2 | product-owner | specs/prd.md, specs/prd-supplements/* | A03 (nfr-catalog, prd NFR-006), A07 (taxonomy), A08, A09, A13, A14, A15, A17; B05 (taxonomy CP-O10 row); C06, C09, C10; C2-07, C2-10 |
| 3 | architect | VP-001..VP-020 | A2-01 (VP-004), A2-02 (VP-001, VP-005), A2-05 (VP-006), A2-06 and A2-10 (VP-012), A2-07 (VP-014), A2-08 (VP-001); B03 and C2-11 (VP-001 `bcs:`); C2-05 (VP-001) |
| 4 | architect | VP-021..VP-041, VP-INDEX, domain-spec/*, product-brief, dtu, gene-transfusion, feasibility | A2-03 (VP-028), A2-04 (VP-INDEX title), A2-09 (VP-022); C2-09 (VP-030 generator); VP-INDEX sync for agent 3's `bcs:` deltas |
| 5 | product-owner | ss-01 BC-1.01.*, BC-1.02.* | B01, B02 + B06 (call 12), B03 (VP rows in BC-1.02.006/.011/.012/.014/.017/.020/.029), B04, B05, B07 |
| 6 | product-owner | ss-01 BC-1.03.*, BC-1.06.*, BC-1.07.* | C01 (call 13), C02, C03 (call 14), C04, C05, C08 (measure, call 11), C11, C12; A2-01 (BC-1.07.001 VP row) |
| 7 | product-owner | ss-01 BC-1.04.*, BC-1.05.* | C2-01 (incl. replacing the stale `http.Client`/`CheckRedirect` recipe text with the minimal-client loop), C2-02, C2-06, C2-08, C2-09 (BC-1.04.018), C2-11 (VP-001 rows), C2-12 |
| 8 | product-owner | ss-02..ss-06 BCs, BC-INDEX, BC-ALLOCATION | A07 (BC-2.02.001), A12 (BC-5.01.004 if needed), C07 (BC-5.02.003); D01..D11 (calls 1-8); A2-01 (BC-4.01.001 VP row) |
